'''Implementation of the LBRDiv teammate generation algorithm (Rahman et al., AAAI 2024)
https://ojs.aaai.org/index.php/AAAI/article/view/29702

Command to run LBRDiv only on LBF: 
python teammate_generation/run.py algorithm=lbrdiv/lbf task=lbf label=test_lbrdiv run_heldout_eval=false train_ego=false

Suggested Debug command: 
python teammate_generation/run.py algorithm=lbrdiv/lbf task=lbf logger.mode=disabled label=debug algorithm.TOTAL_TIMESTEPS=1e5 algorithm.PARTNER_POP_SIZE=2 train_ego=false run_heldout_eval=false

Limitations: does not support recurrent actors.
'''
import logging
import shutil
import time
from functools import partial

import hydra
import jax
import jax.numpy as jnp
import numpy as np
import optax
import wandb
from agents.agent_interface import ActorWithConditionalCriticPolicy
from agents.population_interface import AgentPopulation
from common.plot_utils import get_metric_names
from common.run_episodes import run_episodes
from common.save_load_utils import save_train_run
from envs import make_env
from envs.log_wrapper import LogWrapper
from flax.training.train_state import TrainState
from marl.ppo_utils import unbatchify, _create_minibatches
from teammate_generation.BRDiv import _get_all_ids, XPTransition, gather_params

log = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


def train_lbrdiv_partners(train_rng, env, config, conf_policy, br_policy):
    num_agents = env.num_agents
    assert num_agents == 2, "This code assumes the environment has exactly 2 agents."

    # Define different minibatch sizes for interactions with ego agent and one with BR agent
    config["NUM_GAME_AGENTS"] = num_agents
    config["NUM_CONF_ACTORS"] = config["NUM_ENVS"]
    config["NUM_BR_ACTORS"] = config["NUM_ENVS"]
    config["NUM_UPDATES"] = config["TOTAL_TIMESTEPS"] // (num_agents * config["ROLLOUT_LENGTH"] * config["NUM_ENVS"])

    def make_lbrdiv_agents(config):
        def linear_schedule(count):
            frac = 1.0 - (count // (config["NUM_MINIBATCHES"] * config["UPDATE_EPOCHS"])) / config["NUM_UPDATES"]
            return config["LR"] * frac

        def train(rng):
            rng, init_conf_rng, init_br_rng = jax.random.split(rng, 3)
            all_conf_init_rngs = jax.random.split(init_conf_rng, config["PARTNER_POP_SIZE"])
            all_br_init_rngs = jax.random.split(init_br_rng, config["PARTNER_POP_SIZE"])
            identity_matrix = jnp.eye(config["PARTNER_POP_SIZE"])

            init_conf_hstate = conf_policy.init_hstate(config["NUM_CONF_ACTORS"])
            init_br_hstate = br_policy.init_hstate(config["NUM_BR_ACTORS"])

            def init_train_states(rng_agents, rng_brs):
                def init_single_pair_optimizers(rng_agent, rng_br):
                    init_params_conf = conf_policy.init_params(rng_agent)
                    init_params_br = br_policy.init_params(rng_br)
                    return init_params_conf, init_params_br

                init_all_networks_and_optimizers = jax.vmap(init_single_pair_optimizers)
                all_conf_params, all_br_params = init_all_networks_and_optimizers(rng_agents, rng_brs)

                # Define optimizers for both confederate and BR policy
                tx = optax.chain(
                    optax.clip_by_global_norm(config["MAX_GRAD_NORM"]),
                    optax.adam(learning_rate=linear_schedule if config["ANNEAL_LR"] else config["LR"],
                               eps=1e-5),
                )
                tx_br = optax.chain(
                    optax.clip_by_global_norm(config["MAX_GRAD_NORM"]),
                    optax.adam(learning_rate=linear_schedule if config["ANNEAL_LR"] else config["LR"],
                               eps=1e-5),
                )

                train_state_conf = TrainState.create(
                    apply_fn=conf_policy.network.apply,
                    params=all_conf_params,
                    tx=tx,
                )

                train_state_br = TrainState.create(
                    apply_fn=br_policy.network.apply,
                    params=all_br_params,
                    tx=tx_br,
                )

                return train_state_conf, train_state_br

            all_conf_optims, all_br_optims = init_train_states(
                all_conf_init_rngs, all_br_init_rngs
            )

            def forward_pass_conf(params, obs, id, done, avail_actions, hstate, rng):
                act, val, pi, new_hstate = conf_policy.get_action_value_policy(
                    params=params,
                    obs=obs[jnp.newaxis, ...],
                    done=done[jnp.newaxis, ...],
                    avail_actions=avail_actions,
                    hstate=hstate,
                    rng=rng,
                    aux_obs=id[jnp.newaxis, ...]
                )
                return act, val, pi, new_hstate

            def forward_pass_br(params, obs, id, done, avail_actions, hstate, rng):
                act, val, pi, new_hstate = br_policy.get_action_value_policy(
                    params=params,
                    obs=obs[jnp.newaxis, ...],
                    done=done[jnp.newaxis, ...],
                    avail_actions=avail_actions,
                    hstate=hstate,
                    rng=rng,
                    aux_obs=id[jnp.newaxis, ...]
                )
                return act, val, pi, new_hstate

            def _env_step(runner_state, unused):
                """
                agent_0 = confederate, agent_1 = br
                Returns updated runner_state, and Transitions for agent_0 and agent_1
                """
                (
                    all_train_state_conf, all_train_state_br, last_conf_ids, last_br_ids,
                    env_state, last_obs, last_done, last_conf_h, last_br_h, rng
                ) = runner_state
                rng, act0_rng, act1_rng, step_rng, conf_sampling_rng, br_sampling_rng = jax.random.split(rng, 6)

                # For done envs, resample both conf and brs 
                needs_resample = last_done["__all__"]
                resampled_conf_ids = jax.random.randint(conf_sampling_rng, (config["NUM_CONF_ACTORS"],), 0,
                                                        config["PARTNER_POP_SIZE"])
                resampled_br_ids = jax.random.randint(br_sampling_rng, (config["NUM_BR_ACTORS"],), 0,
                                                      config["PARTNER_POP_SIZE"])

                # Determine final indices based on whether resampling was needed for each env
                updated_conf_ids = jnp.where(
                    needs_resample,
                    resampled_conf_ids,  # Use newly sampled index if True
                    last_conf_ids  # Else, keep index from previous step
                )

                updated_br_ids = jnp.where(
                    needs_resample,
                    resampled_br_ids,  # Use newly sampled index if True
                    last_br_ids  # Else, keep index from previous step
                )

                # Reset the hidden states for resampled conf and br if they are not None
                # WARNING: (L)BRDiv was not tested with recurrent actors, so the code for if the hstate is not None may not work
                if last_conf_h is not None:
                    updated_conf_h = jnp.where(
                        needs_resample,
                        init_conf_hstate,
                        last_conf_h
                    )
                else:
                    updated_conf_h = last_conf_h

                if last_br_h is not None:
                    updated_br_h = jnp.where(
                        needs_resample,
                        init_br_hstate,
                        last_br_h
                    )
                else:
                    updated_br_h = last_br_h

                # Get the corresponding conf and br params
                updated_conf_params = gather_params(all_train_state_conf.params, updated_conf_ids)
                updated_br_params = gather_params(all_train_state_br.params, updated_br_ids)

                updated_conf_onehot_ids = identity_matrix[updated_conf_ids]
                updated_br_onehot_ids = identity_matrix[updated_br_ids]

                # Get available actions for agent 0 from environment state
                avail_actions = jax.vmap(env.get_avail_actions)(env_state.env_state)
                avail_actions = jax.lax.stop_gradient(avail_actions)
                avail_actions_0 = avail_actions["agent_0"].astype(jnp.float32)
                avail_actions_1 = avail_actions["agent_1"].astype(jnp.float32)

                # Agent_0 action
                act0_rng = jax.random.split(act0_rng, config["NUM_ENVS"])
                act_0, val_0, pi_0, new_conf_h = jax.vmap(forward_pass_conf)(updated_conf_params,
                                                                             last_obs["agent_0"], updated_br_onehot_ids,
                                                                             last_done["agent_0"], avail_actions_0,
                                                                             updated_conf_h, act0_rng)
                logp_0 = pi_0.log_prob(act_0)
                act_0, val_0, logp_0 = act_0.squeeze(), val_0.squeeze(), logp_0.squeeze()

                # Agent_1 action
                act1_rng = jax.random.split(act1_rng, config["NUM_ENVS"])
                act_1, val_1, pi_1, new_br_h = jax.vmap(forward_pass_br)(updated_br_params,
                                                                         last_obs["agent_1"], updated_conf_onehot_ids,
                                                                         last_done["agent_1"], avail_actions_1,
                                                                         updated_br_h, act1_rng)
                logp_1 = pi_1.log_prob(act_1)
                act_1, val_1, logp_1 = act_1.squeeze(), val_1.squeeze(), logp_1.squeeze()

                # Combine actions into the env format
                combined_actions = jnp.concatenate([act_0, act_1], axis=0)
                env_act = unbatchify(combined_actions, env.agents, config["NUM_ENVS"], num_agents)
                env_act = {k: v.flatten() for k, v in env_act.items()}

                # Step env
                step_rngs = jax.random.split(step_rng, config["NUM_ENVS"])
                obs_next, env_state_next, reward, done, info = jax.vmap(env.step, in_axes=(0, 0, 0))(
                    step_rngs, env_state, env_act
                )
                # note that num_actors = num_envs * num_agents
                info_0 = jax.tree.map(lambda x: x[:, 0], info)
                info_1 = jax.tree.map(lambda x: x[:, 1], info)

                # Store agent_0 data in transition
                transition_0 = XPTransition(
                    done=done["agent_0"],
                    action=act_0,
                    value=val_0,
                    self_onehot_id=updated_conf_onehot_ids,
                    oppo_onehot_id=updated_br_onehot_ids,
                    reward=reward["agent_1"],
                    log_prob=logp_0,
                    obs=last_obs["agent_0"],
                    info=info_0,
                    avail_actions=avail_actions_0
                )

                transition_1 = XPTransition(
                    done=done["agent_1"],
                    action=act_1,
                    value=val_1,
                    self_onehot_id=updated_br_onehot_ids,
                    oppo_onehot_id=updated_conf_onehot_ids,
                    reward=reward["agent_1"],
                    log_prob=logp_1,
                    obs=last_obs["agent_1"],
                    info=info_1,
                    avail_actions=avail_actions_1
                )
                new_runner_state = (all_train_state_conf, all_train_state_br, updated_conf_ids, updated_br_ids,
                                    env_state_next, obs_next, done, new_conf_h, new_br_h, rng)
                return new_runner_state, (transition_0, transition_1)

            def _calculate_gae(traj_batch, last_val):
                def _get_advantages(gae_and_next_value, transition):
                    gae, next_value = gae_and_next_value
                    done, value, reward = (
                        transition.done,
                        transition.value,
                        transition.reward,
                    )
                    delta = reward + config["GAMMA"] * next_value * (1 - done) - value
                    gae = (
                            delta
                            + config["GAMMA"] * config["GAE_LAMBDA"] * (1 - done) * gae
                    )
                    return (gae, value), gae

                _, advantages = jax.lax.scan(
                    _get_advantages,
                    (jnp.zeros_like(last_val), last_val),
                    traj_batch,
                    reverse=True,
                    unroll=16,
                )
                return advantages, advantages + traj_batch.value

            def run_all_episodes(rng, train_state_conf, train_state_br):
                conf_ids, br_ids = _get_all_ids(config["PARTNER_POP_SIZE"])
                gathered_conf_model_params = gather_params(train_state_conf.params, conf_ids)
                gathered_br_model_params = gather_params(train_state_br.params, br_ids)

                rng, eval_rng = jax.random.split(rng)

                def run_episodes_fixed_rng(conf_param, br_param):
                    return run_episodes(
                        eval_rng, env,
                        conf_param, conf_policy,
                        br_param, br_policy,
                        config["ROLLOUT_LENGTH"], config["NUM_EVAL_EPISODES"],
                    )

                ep_infos = jax.vmap(run_episodes_fixed_rng)(
                    gathered_conf_model_params, gathered_br_model_params,
                    # leaves where shape is (pop_size*pop_size, ...)
                )
                return ep_infos

            def _update_epoch(update_state, unused):
                def _update_minbatch(all_train_states, all_data):
                    train_state_conf, train_state_br = all_train_states
                    minbatch_conf, minbatch_br, lms_vertical, lms_horizontal = all_data

                    def _loss_fn(param, agent_policy, minbatch, agent_id, lms_vertical, lms_horizontal):
                        '''Compute loss for agent corresponding to agent_id.
                        '''
                        init_hstate, traj_batch, gae, target_v = minbatch
                        # get policy and value of confederate versus ego and best response agents respectively
                        squeezed_param = jax.tree.map(lambda x: jnp.squeeze(x, 0), param)
                        _, value, pi, _ = agent_policy.get_action_value_policy(
                            params=squeezed_param,
                            obs=traj_batch.obs,
                            done=traj_batch.done,
                            avail_actions=traj_batch.avail_actions,
                            hstate=init_hstate,
                            rng=jax.random.PRNGKey(0),  # only used for action sampling, which is not used here
                            aux_obs=traj_batch.oppo_onehot_id
                        )
                        log_prob = pi.log_prob(traj_batch.action)

                        is_relevant = jnp.equal(
                            jnp.argmax(traj_batch.self_onehot_id, axis=-1),
                            agent_id
                        )
                        loss_weights = jnp.where(is_relevant, 1, 0).astype(jnp.float32)
                        int_self_id = jnp.argmax(traj_batch.self_onehot_id, axis=-1)
                        int_oppo_id = jnp.argmax(traj_batch.oppo_onehot_id, axis=-1)

                        # Given a pair of policies that generate SP trajectories, 
                        # compute the pair's total Lagrange multiplier in the Lagrange dual.
                        # Assuming the SP data is generated by population i, the total LMs
                        # amounts to \sum_{j}*lms_vertical[i][j] + \sum_{j}*lms_horizontal[i][j]

                        def _gather_sp_weights(ids):
                            s_id, _ = ids
                            return jnp.sum(lms_vertical, axis=-1)[s_id], jnp.sum(lms_horizontal, axis=-1)[s_id]

                        # Given a pair of policies that generate XP trajectories, 
                        # compute the pair's total Lagrange multiplier in the Lagrange dual.
                        # Assuming the XP data is generated by the i^th conf policy and the j^th BR policy, 
                        # the total LMs amounts to 
                        # -lms_vertical[j][i] -lms_horizontal[i][j]

                        def _gather_xp_weights(ids):
                            s_id, o_id = ids
                            return -lms_vertical[s_id][o_id], -lms_horizontal[o_id][s_id]

                        def _get_weights(s_id, o_id):
                            return jax.lax.cond(
                                jnp.equal(s_id, o_id),
                                _gather_sp_weights,
                                _gather_xp_weights,
                                (s_id, o_id)
                            )

                        # Value loss
                        value_pred_clipped = traj_batch.value + (
                                value - traj_batch.value
                        ).clip(
                            -config["CLIP_EPS"], config["CLIP_EPS"])
                        value_losses = jnp.square(value - target_v)
                        value_losses_clipped = jnp.square(value_pred_clipped - target_v)
                        value_loss = jax.lax.cond(
                            loss_weights.sum() == 0,
                            lambda x: jnp.zeros_like(x).astype(jnp.float32),
                            lambda x: x,
                            (loss_weights * jnp.maximum(value_losses, value_losses_clipped)).sum() / (
                                        loss_weights.sum() + 1e-8)
                        )

                        # # Apply different loss weights for SP and XP data
                        # # Loss weights consist of two parts: the first term is the weighting from the (L)BRDiv loss fucntion
                        # # which is based on the sum of Lagrange multipliers for a given confederate-ego pair expected returns 
                        # # in the Lagrange dual formulation. This is indicated by weights1 + weights2 in the code below.

                        # # The second term is a reweighting term to compensate for the data collection process, which uniformly and independently 
                        # # samples the conf and br ids from 1, ..., n, resulting in P(SP) = 1/n and P(XP) = (n-1)/n.
                        # # To prevent the XP loss term from dominating the SP loss term, we would like P(SP) = P(XP) = 1/2.
                        # # Thus, we set the 2nd term of the SP weight to n/2, and the 2nd term of the XP weight to n/(2 * (n-1)).

                        n = config["PARTNER_POP_SIZE"]
                        is_sp = jnp.equal(jnp.argmax(traj_batch.self_onehot_id, axis=-1),
                                          jnp.argmax(traj_batch.oppo_onehot_id, axis=-1))
                        weights1, weights2 = jax.vmap(jax.vmap(_get_weights))(int_self_id, int_oppo_id)
                        actor_weights_sp = (weights1 + weights2) * (n / 2)
                        actor_weights_xp = (weights1 + weights2) * (n / (2 * (n - 1)))
                        actor_weights = jnp.where(is_sp, actor_weights_sp, actor_weights_xp)

                        # Policy gradient loss
                        ratio = jnp.exp(log_prob - traj_batch.log_prob)
                        gae_norm = (gae - gae.mean()) / (gae.std() + 1e-8)
                        pg_loss_1 = ratio * actor_weights * gae_norm
                        pg_loss_2 = jnp.clip(
                            ratio,
                            1.0 - config["CLIP_EPS"],
                            1.0 + config["CLIP_EPS"]) * actor_weights * gae_norm
                        pg_loss = jax.lax.cond(
                            loss_weights.sum() == 0,
                            lambda x: jnp.zeros_like(x).astype(jnp.float32),
                            lambda x: x,
                            -(
                                    loss_weights * jnp.minimum(pg_loss_1, pg_loss_2)
                            ).sum() / (loss_weights.sum() + 1e-8)
                        )

                        # Weight entropy based on actor weights
                        all_sp_weights1, all_sp_weights2 = jax.vmap(_gather_sp_weights)((int_self_id, int_self_id))
                        entropy_scaler = jnp.maximum(all_sp_weights1, all_sp_weights2)

                        # Compute entropy loss
                        entropy = jax.lax.cond(
                            loss_weights.sum() == 0,
                            lambda x: jnp.zeros_like(x).astype(jnp.float32),
                            lambda x: x,
                            (loss_weights * entropy_scaler * pi.entropy()).sum() / (loss_weights.sum() + 1e-8)
                        )

                        total_loss = pg_loss + config["VF_COEF"] * value_loss - config["ENT_COEF"] * entropy
                        return total_loss, (value_loss, pg_loss, entropy)

                    possible_agent_ids = jnp.expand_dims(jnp.arange(config["PARTNER_POP_SIZE"]), 1)
                    grad_fn = jax.value_and_grad(_loss_fn, has_aux=True)

                    def gather_conf_params_and_return_grads(agent_id):
                        # transposing the lm matrices only on the confederate agent side
                        # ensures that both the confederate and br policy that interact
                        # to generate a trajectory have the same weights when computing 
                        # the policy gradient loss.
                        param_vector = gather_params(train_state_conf.params, agent_id)
                        (loss_val_conf, aux_vals_conf), grads_conf = grad_fn(
                            param_vector, conf_policy, minbatch_conf, agent_id,
                            jnp.transpose(lms_vertical), jnp.transpose(lms_horizontal)
                        )
                        return (loss_val_conf, aux_vals_conf), grads_conf

                    def gather_br_params_and_return_grads(agent_id):
                        param_vector = gather_params(train_state_br.params, agent_id)
                        (loss_val_br, aux_vals_br), grads_br = grad_fn(
                            param_vector, br_policy, minbatch_br, agent_id,
                            lms_vertical, lms_horizontal
                        )
                        return (loss_val_br, aux_vals_br), grads_br

                    (loss_val_conf, aux_vals_conf), grads_conf = jax.vmap(gather_conf_params_and_return_grads)(
                        possible_agent_ids)
                    (loss_val_br, aux_vals_br), grads_br = jax.vmap(gather_br_params_and_return_grads)(
                        possible_agent_ids)

                    grads_conf_new = jax.tree.map(lambda x: jnp.squeeze(x, 1), grads_conf)
                    grads_br_new = jax.tree.map(lambda x: jnp.squeeze(x, 1), grads_br)
                    train_state_conf = train_state_conf.apply_gradients(grads=grads_conf_new)
                    train_state_br = train_state_br.apply_gradients(grads=grads_br_new)
                    return (train_state_conf, train_state_br), ((loss_val_conf, aux_vals_conf),
                                                                (loss_val_br, aux_vals_br))

                (
                    train_state_conf, train_state_br,
                    traj_batch_conf, traj_batch_br,
                    advantages_conf, advantages_br,
                    targets_conf, targets_br,
                    rng, lms_vertical, lms_horizontal
                ) = update_state
                rng, perm_rng_conf, perm_rng_br = jax.random.split(rng, 3)

                minibatches_conf = _create_minibatches(traj_batch_conf, advantages_conf, targets_conf, init_conf_hstate,
                                                       config["NUM_CONF_ACTORS"], config["NUM_MINIBATCHES"],
                                                       perm_rng_conf)
                minibatches_br = _create_minibatches(traj_batch_br, advantages_br, targets_br, init_br_hstate,
                                                     config["NUM_BR_ACTORS"], config["NUM_MINIBATCHES"], perm_rng_br)

                # Update both policies
                num_minibatches = minibatches_br[1].obs.shape[0]

                repeated_lms_vertical = lms_vertical[jnp.newaxis, ...].repeat(num_minibatches, axis=0)
                repeated_lms_horizontal = lms_horizontal[jnp.newaxis, ...].repeat(num_minibatches, axis=0)

                (train_state_conf, train_state_br), all_losses = jax.lax.scan(
                    _update_minbatch, (train_state_conf, train_state_br),
                    (minibatches_conf, minibatches_br, repeated_lms_vertical, repeated_lms_horizontal)
                )

                def compute_lagrange_grads_same(params_br, batch, target_value, ids):
                    '''
                    conf_id: int
                    br_id: int
                    batch: a pytree where all leaves have shape (rollout_len, num_envs, -1)
                    target_value: (rollout_len, num_envs)
                    '''
                    conf_id, br_id = ids

                    all_target_value = jnp.reshape(
                        target_value, (-1, 1)
                    )

                    repeated_value_sp = jnp.repeat(
                        jnp.reshape(all_target_value, (1, -1)),
                        config["PARTNER_POP_SIZE"],
                        axis=0
                    )

                    ##### Compute grad_sp_vary_conf
                    relevant_conf_params = gather_params(params_br, jnp.reshape(conf_id, (1,)))
                    relevant_conf_params = jax.tree.map(lambda x: jnp.squeeze(x, 0), relevant_conf_params)

                    def _get_value_xp_vary_conf(param, agent_onehot_id):
                        ts, bs = batch.obs.shape[:2]
                        agent_onehot_id = agent_onehot_id[jnp.newaxis, jnp.newaxis, ...].repeat(ts, axis=0).repeat(bs,
                                                                                                                   axis=1)
                        _, value_xp_vary_conf, _, _ = br_policy.get_action_value_policy(
                            params=param,
                            obs=batch.obs,
                            done=batch.done,
                            avail_actions=batch.avail_actions,
                            hstate=init_br_hstate,
                            rng=jax.random.PRNGKey(0),  # only used for action sampling, which is not used here
                            aux_obs=agent_onehot_id
                        )
                        return value_xp_vary_conf.reshape(ts * bs)

                    # For a given trajectory, identify the BR policy that generates that trajectory
                    # For every state in the trajectory, estimate (using the value function) the ego agent's returns
                    # when they follow the identified BR policy. Do this assuming various possible partner
                    # confederate policies (thus, why we basically "vary" the conf policy).
                    all_possible_value_xp_vary_conf = jax.vmap(
                        lambda agent_id: _get_value_xp_vary_conf(relevant_conf_params, agent_id)
                    )(jnp.eye(config["PARTNER_POP_SIZE"]))

                    all_possible_value_xp_vary_conf = all_possible_value_xp_vary_conf.at[conf_id].set(
                        repeated_value_sp[conf_id]
                    )

                    offsetting_thresholds = jnp.zeros_like(repeated_value_sp)
                    offsetting_thresholds = offsetting_thresholds.at[conf_id].set(
                        config["TOLERANCE_FACTOR"] * jnp.ones_like(offsetting_thresholds[conf_id])
                    )
                    grad_sp_vary_conf = repeated_value_sp + offsetting_thresholds - (
                            all_possible_value_xp_vary_conf + config["TOLERANCE_FACTOR"] * jnp.ones_like(
                        offsetting_thresholds)
                    )

                    ##### Compute grad_sp_vary_br
                    # This code tries to measure the expected returns of the ego agent had the BR policy been 
                    # substituted by another BR policy

                    # Lets say that R_{i,-j} is the ego agent's returns when following the BR policy of the i^th pair
                    # againts the confederate policy of the j^th pair. 

                    # Then grad_sp_vary_conf computes R_{i,-i} - R_{i,-j} - tolerance factor 
                    # for all possible j (note for j=i, we sub in <repeated_value_sp + offsetting_thresholds above> 
                    # R_{i,-i} with the target returns + tolerance factor so that R_{i,-i} - R_{i,-j} = 0)

                    # Meanwhile grad_sp_vary_br below computes R_{i,-i} - R_{j,-i} - tolerance factor 
                    # for all possible j.

                    # Vary the BR policy parameters (j) used in value computation
                    # Use the experience generating pop id (batch.self_onehot_id) <i> as the conf ID.

                    relevant_params = gather_params(params_br, jnp.arange(config["PARTNER_POP_SIZE"]))

                    def _get_value_xp_vary_br(param):
                        ts, bs = batch.obs.shape[:2]
                        conf_one_hot = jnp.eye(config["PARTNER_POP_SIZE"])[conf_id]
                        conf_one_hot = conf_one_hot[jnp.newaxis, jnp.newaxis, ...].repeat(ts, axis=0).repeat(bs, axis=1)
                        _, value_xp_vary_br, _, _ = br_policy.get_action_value_policy(
                            params=param,
                            obs=batch.obs,
                            done=batch.done,
                            avail_actions=batch.avail_actions,
                            hstate=init_br_hstate,
                            rng=jax.random.PRNGKey(0),  # only used for action sampling, which is not used here
                            aux_obs=conf_one_hot
                        )
                        return value_xp_vary_br.reshape(ts * bs)

                    all_possible_value_xp_vary_br = jax.vmap(
                        lambda param: _get_value_xp_vary_br(param)
                    )(relevant_params)

                    all_possible_value_xp_vary_br = jnp.reshape(
                        all_possible_value_xp_vary_br, (config["PARTNER_POP_SIZE"], -1)
                    )
                    all_possible_value_xp_vary_br = all_possible_value_xp_vary_br.at[conf_id].set(
                        repeated_value_sp[conf_id]
                    )

                    grad_sp_vary_br = repeated_value_sp + offsetting_thresholds - (
                            all_possible_value_xp_vary_br + config["TOLERANCE_FACTOR"] * jnp.ones_like(
                        offsetting_thresholds)
                    )

                    #### Compute loss weights
                    all_self_id_int = jnp.reshape(
                        batch.self_onehot_id, (-1, jnp.shape(batch.self_onehot_id)[-1])
                    ).argmax(axis=-1)

                    all_oppo_id_int = jnp.reshape(
                        batch.oppo_onehot_id, (-1, jnp.shape(batch.oppo_onehot_id)[-1])
                    ).argmax(axis=-1)

                    # check if self and oppo ids both correspond to the confederate for the self-play update
                    self_is_conf = jnp.equal(all_self_id_int, conf_id).astype(jnp.float32)
                    oppo_is_conf = jnp.equal(all_oppo_id_int, conf_id).astype(jnp.float32)
                    loss_weights = self_is_conf * oppo_is_conf
                    repeated_loss_weights = jnp.repeat(
                        jnp.expand_dims(loss_weights, axis=0),
                        config["PARTNER_POP_SIZE"],
                        axis=0
                    )

                    # Compute vertical and horizontal gradients
                    vertical_grads = jnp.sum(grad_sp_vary_conf * repeated_loss_weights, axis=-1) / (
                                jnp.sum(loss_weights) + 1e-8)
                    horizontal_grads = jnp.sum(grad_sp_vary_br * repeated_loss_weights, axis=-1) / (
                                jnp.sum(loss_weights) + 1e-8)

                    output_grad_matrix_vertical = jnp.zeros((config["PARTNER_POP_SIZE"], config["PARTNER_POP_SIZE"]))
                    output_grad_matrix_horizontal = jnp.zeros((config["PARTNER_POP_SIZE"], config["PARTNER_POP_SIZE"]))

                    output_grad_matrix_vertical = output_grad_matrix_vertical.at[conf_id].set(vertical_grads)
                    output_grad_matrix_horizontal = output_grad_matrix_horizontal.at[conf_id].set(horizontal_grads)

                    return output_grad_matrix_vertical, output_grad_matrix_horizontal

                def compute_lagrange_grads_diff(params_br, batch, target_returns, ids):
                    conf_id, br_id = ids
                    param_conf_id = gather_params(params_br, jnp.reshape(conf_id, (1,)))
                    param_br_id = gather_params(params_br, jnp.reshape(br_id, (1,)))

                    param_br_id = jax.tree.map(lambda x: jnp.squeeze(x, 0), param_br_id)
                    param_conf_id = jax.tree.map(lambda x: jnp.squeeze(x, 0), param_conf_id)

                    all_self_id_int = jnp.reshape(
                        batch.self_onehot_id, (-1, jnp.shape(batch.self_onehot_id)[-1])
                    ).argmax(axis=-1)

                    all_oppo_id_int = jnp.reshape(
                        batch.oppo_onehot_id, (-1, jnp.shape(batch.oppo_onehot_id)[-1])
                    ).argmax(axis=-1)

                    all_target_returns = jnp.reshape(
                        target_returns, (-1)
                    )

                    # Compute data weights based on whether selected ID
                    # is relevant for the gradient computation process
                    oppo_is_conf = jnp.equal(all_oppo_id_int, conf_id).astype(jnp.float32)
                    self_is_br = jnp.equal(all_self_id_int, br_id).astype(jnp.float32)
                    loss_weights = oppo_is_conf * self_is_br

                    ts, bs = batch.obs.shape[:2]

                    conf_one_hot = jnp.eye(config["PARTNER_POP_SIZE"])[conf_id]
                    conf_one_hot = conf_one_hot[jnp.newaxis, jnp.newaxis, ...].repeat(ts, axis=0).repeat(bs, axis=1)
                    br_one_hot = jnp.eye(config["PARTNER_POP_SIZE"])[br_id]
                    br_one_hot = br_one_hot[jnp.newaxis, jnp.newaxis, ...].repeat(ts, axis=0).repeat(bs, axis=1)

                    _, value_sp_pop_is_br, _, _ = br_policy.get_action_value_policy(
                        params=param_br_id,
                        obs=batch.obs,
                        done=batch.done,
                        avail_actions=batch.avail_actions,
                        hstate=init_br_hstate,
                        rng=jax.random.PRNGKey(0),  # only used for action sampling, which is not used here
                        aux_obs=br_one_hot
                    )
                    value_sp_pop_is_br = value_sp_pop_is_br.reshape(bs * ts)

                    _, value_sp_pop_is_not_br, _, _ = br_policy.get_action_value_policy(
                        params=param_conf_id,
                        obs=batch.obs,
                        done=batch.done,
                        avail_actions=batch.avail_actions,
                        hstate=init_br_hstate,
                        rng=jax.random.PRNGKey(0),  # only used for action sampling, which is not used here
                        aux_obs=conf_one_hot
                    )
                    value_sp_pop_is_not_br = value_sp_pop_is_not_br.reshape(bs * ts)
                    # Compute V_{b_id, b_id} - V_{c_id, br_id} - tolerance_factor
                    # which will be the gradient for lm_vertical[b_id][c_id] in the Lagrange dual objective
                    vertical_diff = value_sp_pop_is_br - all_target_returns - config["TOLERANCE_FACTOR"]

                    # Compute V_{c_id, c_id} - V_{c_id, br_id} - tolerance_factor
                    # which will be the gradient for lm_horizontal[b_id][c_id] in the Lagrange dual objective
                    horizontal_diff = value_sp_pop_is_not_br - all_target_returns - config["TOLERANCE_FACTOR"]

                    total_grad_vertical = (loss_weights * vertical_diff).sum() / (loss_weights.sum() + 1e-8)
                    total_grad_horizontal = (loss_weights * horizontal_diff).sum() / (loss_weights.sum() + 1e-8)

                    output_grad_matrix_vertical = jnp.zeros((config["PARTNER_POP_SIZE"], config["PARTNER_POP_SIZE"]))
                    output_grad_matrix_horizontal = jnp.zeros((config["PARTNER_POP_SIZE"], config["PARTNER_POP_SIZE"]))

                    output_grad_matrix_vertical = output_grad_matrix_vertical.at[br_id, conf_id].set(
                        total_grad_vertical)
                    output_grad_matrix_horizontal = output_grad_matrix_horizontal.at[conf_id, br_id].set(
                        total_grad_horizontal)

                    return output_grad_matrix_vertical, output_grad_matrix_horizontal

                def _compute_indiv_lagrange_grads(conf_id, br_id):
                    return jax.lax.cond(
                        conf_id == br_id,
                        lambda ids: compute_lagrange_grads_same(train_state_br.params, traj_batch_br, targets_br, ids),
                        lambda ids: compute_lagrange_grads_diff(train_state_br.params, traj_batch_br, targets_br, ids),
                        (conf_id, br_id)
                    )

                all_conf_ids, all_br_ids = _get_all_ids(config["PARTNER_POP_SIZE"])
                all_lagrange_grads = jax.vmap(_compute_indiv_lagrange_grads)(all_conf_ids, all_br_ids)
                averaged_grad_vertical = jnp.sum(all_lagrange_grads[0], axis=0)
                averaged_grad_horizontal = jnp.sum(all_lagrange_grads[1], axis=0)

                lms_vertical_new = jnp.maximum(
                    lms_vertical - config["LAGRANGE_LR"] * averaged_grad_vertical,
                    0.5 * jnp.eye(config["PARTNER_POP_SIZE"])
                )
                lms_vertical_new = jnp.fill_diagonal(
                    lms_vertical_new, 0.5 * jnp.ones((config["PARTNER_POP_SIZE"]), dtype=jnp.float32),
                    inplace=False
                )

                lms_horizontal_new = jnp.maximum(
                    lms_horizontal - config["LAGRANGE_LR"] * averaged_grad_horizontal,
                    0.5 * jnp.eye(config["PARTNER_POP_SIZE"]),
                )
                lms_horizontal_new = jnp.fill_diagonal(
                    lms_horizontal_new, 0.5 * jnp.ones((config["PARTNER_POP_SIZE"]), dtype=jnp.float32),
                    inplace=False
                )

                update_state = (train_state_conf, train_state_br,
                                traj_batch_conf, traj_batch_br,
                                advantages_conf, advantages_br,
                                targets_conf, targets_br,
                                rng, lms_vertical_new, lms_horizontal_new
                                )
                return update_state, all_losses

            def _update_step(update_runner_state, unused):
                """
                1. Collect rollouts
                2. Compute advantage
                3. PPO updates
                """
                (
                    all_train_state_conf, all_train_state_br,
                    last_env_state, last_obs, last_done, last_conf_h, last_br_h,
                    rng, update_steps, lms_vertical, lms_horizontal
                ) = update_runner_state

                rng, conf_sampling_rng, br_sampling_rng = jax.random.split(rng, 3)

                conf_ids = jax.random.randint(conf_sampling_rng, (config["NUM_ENVS"],), 0, config["PARTNER_POP_SIZE"])
                br_ids = jax.random.randint(br_sampling_rng, (config["NUM_ENVS"],), 0, config["PARTNER_POP_SIZE"])

                runner_state = (
                    all_train_state_conf, all_train_state_br, conf_ids, br_ids,
                    last_env_state, last_obs, last_done, last_conf_h, last_br_h, rng
                )
                runner_state, traj_batch = jax.lax.scan(
                    _env_step, runner_state, None, config["ROLLOUT_LENGTH"])
                (all_train_state_conf, all_train_state_br, last_conf_ids, last_br_ids,
                 last_env_state, last_obs, last_done, last_conf_h, last_br_h, rng) = runner_state

                # Get the last conf and br params and ids
                last_conf_params = gather_params(all_train_state_conf.params, last_conf_ids)
                last_br_params = gather_params(all_train_state_br.params, last_br_ids)

                last_conf_one_hots = identity_matrix[last_conf_ids]
                last_br_one_hots = identity_matrix[last_br_ids]

                # Get agent 0 and agent 1 trajectories from interaction between conf policy and its BR policy.
                traj_batch_conf, traj_batch_br = traj_batch

                # Compute advantage for confederate agent from interaction with br policy
                avail_actions_0 = jax.vmap(env.get_avail_actions)(last_env_state.env_state)["agent_0"].astype(
                    jnp.float32)
                _, last_val_conf, _, _ = jax.vmap(forward_pass_conf)(
                    params=last_conf_params,
                    obs=last_obs["agent_0"],
                    id=last_br_one_hots,
                    done=last_done["agent_0"],
                    avail_actions=avail_actions_0,
                    hstate=last_conf_h,
                    rng=jax.random.split(jax.random.PRNGKey(0), config["NUM_ENVS"])
                    # Dummy key since we're just extracting the value
                )
                last_val_conf = last_val_conf.squeeze()
                advantages_conf, targets_conf = _calculate_gae(traj_batch_conf, last_val_conf)

                # Compute advantage for br policy from interaction with confederate agent
                avail_actions_1 = jax.vmap(env.get_avail_actions)(last_env_state.env_state)["agent_1"].astype(
                    jnp.float32)
                _, last_val_br, _, _ = jax.vmap(forward_pass_br)(
                    params=last_br_params,
                    obs=last_obs["agent_1"],
                    id=last_conf_one_hots,
                    done=last_done["agent_1"],
                    avail_actions=avail_actions_1,
                    hstate=last_br_h,
                    rng=jax.random.split(jax.random.PRNGKey(0), config["NUM_ENVS"])
                    # Dummy key since we're just extracting the value
                )
                last_val_br = last_val_br.squeeze()
                advantages_br, targets_br = _calculate_gae(traj_batch_br, last_val_br)

                # 3) PPO update
                rng, update_rng = jax.random.split(rng, 2)
                update_state = (
                    all_train_state_conf, all_train_state_br,
                    traj_batch_conf, traj_batch_br,
                    advantages_conf, advantages_br,
                    targets_conf, targets_br,
                    update_rng, lms_vertical, lms_horizontal
                )

                update_state, all_losses = jax.lax.scan(
                    _update_epoch, update_state, None, config["UPDATE_EPOCHS"])
                all_train_state_conf, all_train_state_br = update_state[:2]
                lms_vertical, lms_horizontal = update_state[-2:]
                (_, (value_loss_conf, pg_loss_conf, entropy_conf)), (_, (value_loss_br, pg_loss_br,
                                                                         entropy_br)) = all_losses

                # Metrics
                metric = traj_batch_conf.info
                metric["lms_vertical"] = lms_vertical
                metric["lms_horizontal"] = lms_horizontal
                metric["update_steps"] = update_steps
                metric["value_loss_conf_agent"] = value_loss_conf
                metric["value_loss_br_agent"] = value_loss_br

                metric["pg_loss_conf_agent"] = pg_loss_conf
                metric["pg_loss_br_agent"] = pg_loss_br

                metric["entropy_conf"] = entropy_conf
                metric["entropy_br"] = entropy_br

                new_runner_state = (
                    all_train_state_conf, all_train_state_br,
                    last_env_state, last_obs, last_done, last_conf_h, last_br_h,
                    rng, update_steps + 1,
                    lms_vertical, lms_horizontal
                )
                return (new_runner_state, metric)

            # --------------------------
            # PPO Update and Checkpoint saving
            # --------------------------
            ckpt_and_eval_interval = config["NUM_UPDATES"] // max(1, config[
                "NUM_CHECKPOINTS"] - 1)  # -1 because we store a ckpt at the last update
            num_ckpts = config["NUM_CHECKPOINTS"]

            # Build a PyTree that holds parameters for all conf agent checkpoints
            def init_ckpt_array(params_pytree):
                return jax.tree.map(
                    lambda x: jnp.zeros((num_ckpts,) + x.shape, x.dtype),
                    params_pytree)

            def _update_step_with_ckpt(state_with_ckpt, unused):
                (update_runner_state, checkpoint_array_conf, checkpoint_array_br, ckpt_idx,
                 eval_info) = state_with_ckpt

                # Single PPO update
                new_runner_state, metric = _update_step(update_runner_state, None)

                (
                    train_state_conf, train_state_br,
                    last_env_state, last_obs, last_done, last_conf_h, last_br_h,
                    rng, update_steps, lms_vertical, lms_horizontal
                ) = new_runner_state

                # Decide if we store a checkpoint
                # update steps is 1-indexed because it was incremented at the end of the update step
                to_store = jnp.logical_or(jnp.equal(jnp.mod(update_steps - 1, ckpt_and_eval_interval), 0),
                                          jnp.equal(update_steps, config["NUM_UPDATES"]))

                def store_and_eval_ckpt(args):
                    ckpt_arr_and_ep_infos, rng, cidx = args
                    ckpt_arr_conf, ckpt_arr_br, _ = ckpt_arr_and_ep_infos
                    new_ckpt_arr_conf = jax.tree.map(
                        lambda c_arr, p: c_arr.at[cidx].set(p),
                        ckpt_arr_conf, train_state_conf.params
                    )
                    new_ckpt_arr_br = jax.tree.map(
                        lambda c_arr, p: c_arr.at[cidx].set(p),
                        ckpt_arr_br, train_state_br.params
                    )

                    rng, eval_rng = jax.random.split(rng)
                    ep_last_info = run_all_episodes(eval_rng, train_state_conf, train_state_br)

                    return ((new_ckpt_arr_conf, new_ckpt_arr_br, ep_last_info), rng, cidx + 1)

                def skip_ckpt(args):
                    return args

                (checkpoint_array_and_infos, rng, ckpt_idx) = jax.lax.cond(
                    to_store,
                    store_and_eval_ckpt,
                    skip_ckpt,
                    ((checkpoint_array_conf, checkpoint_array_br, eval_info), rng, ckpt_idx)
                )
                checkpoint_array_conf, checkpoint_array_br, eval_ep_last_info = checkpoint_array_and_infos

                metric["eval_ep_last_info"] = eval_ep_last_info  # return of confederate

                return ((train_state_conf, train_state_br,
                         last_env_state, last_obs, last_done, last_conf_h, last_br_h,
                         rng, update_steps, lms_vertical, lms_horizontal),
                        checkpoint_array_conf, checkpoint_array_br, ckpt_idx,
                        eval_ep_last_info), metric

            # Initialize checkpoint array
            checkpoint_array_conf = init_ckpt_array(all_conf_optims.params)
            checkpoint_array_br = init_ckpt_array(all_br_optims.params)
            ckpt_idx = 0

            # Initialize state for scan over _update_step_with_ckpt
            update_steps = 0

            rng, rng_eval = jax.random.split(rng, 2)
            eval_ep_last_info = run_all_episodes(rng_eval, all_conf_optims, all_br_optims)

            # Initialize environment
            rng, reset_rng = jax.random.split(rng)
            reset_rngs = jax.random.split(reset_rng, config["NUM_ENVS"])
            init_obs, init_env_state = jax.vmap(env.reset, in_axes=(0,))(reset_rngs)
            init_done = {k: jnp.zeros((config["NUM_ENVS"]), dtype=bool) for k in env.agents + ["__all__"]}

            # Initialize conf and br hstates
            init_conf_h = conf_policy.init_hstate(config["NUM_CONF_ACTORS"])
            init_br_h = br_policy.init_hstate(config["NUM_BR_ACTORS"])

            # Initialize LMs
            # lm_vertical[i, j] stores the lagrange multiplier for upholding
            # R_{conf(i), BR(i)} >= R_{conf(j), BR(i)} + tolerance_factor

            # lm_horizontal[i, j] stores the lagrange multiplier for upholding
            # R_{conf(i), BR(i)} >= R_{conf(i), BR(j)} + tolerance_factor

            # Diagonal elements of both matrices sum up to 1.
            # Providing a weight of 1 to maximize the SP return from any population
            lagrange_multipliers_vertical = 0.5 * jnp.eye(config["PARTNER_POP_SIZE"])
            lagrange_multipliers_horizontal = 0.5 * jnp.eye(config["PARTNER_POP_SIZE"])

            update_runner_state = (
                all_conf_optims, all_br_optims,
                init_env_state, init_obs, init_done, init_conf_h, init_br_h,
                rng, update_steps,
                lagrange_multipliers_vertical, lagrange_multipliers_horizontal
            )

            state_with_ckpt = (
                update_runner_state, checkpoint_array_conf,
                checkpoint_array_br, ckpt_idx, eval_ep_last_info
            )

            # run training
            state_with_ckpt, metrics = jax.lax.scan(
                _update_step_with_ckpt,
                state_with_ckpt,
                xs=None,
                length=config["NUM_UPDATES"]
            )

            (
                final_runner_state, checkpoint_array_conf, checkpoint_array_br,
                final_ckpt_idx, all_ep_infos
            ) = state_with_ckpt

            out = {
                "final_params_conf": final_runner_state[0].params,
                "final_params_br": final_runner_state[1].params,
                "checkpoints_conf": checkpoint_array_conf,
                "checkpoints_br": checkpoint_array_br,
                "metrics": metrics,
                # metrics is from the perspective of the confederate agent (averaged over population)
                "all_pair_returns": all_ep_infos
            }
            return out

        return train

    # ------------------------------
    # Actually run the adversarial teammate training
    # ------------------------------
    train_fn = make_lbrdiv_agents(config)
    out = train_fn(train_rng)
    return out


def get_lbrdiv_population(config, out, env):
    '''
    Get the partner params and partner population for ego training.
    '''
    pop_size = config["algorithm"]["PARTNER_POP_SIZE"]

    # partner_params has shape (num_seeds, pop_size, ...)
    partner_params = out['final_params_conf']

    partner_policy = ActorWithConditionalCriticPolicy(
        action_dim=env.action_space(env.agents[1]).n,
        obs_dim=env.observation_space(env.agents[1]).shape[0],
        pop_size=pop_size,  # used to create onehot agent id
        activation=config["algorithm"].get("ACTIVATION", "tanh")
    )

    # Create partner population
    partner_population = AgentPopulation(
        pop_size=pop_size,
        policy_cls=partner_policy
    )

    return partner_params, partner_population


def run_lbrdiv(config, wandb_logger):
    algorithm_config = dict(config["algorithm"])

    env = make_env(algorithm_config["ENV_NAME"], algorithm_config["ENV_KWARGS"])
    env = LogWrapper(env)

    log.info("Starting LBRDiv training...")
    start = time.time()

    # Generate multiple random seeds from the base seed
    rng = jax.random.PRNGKey(algorithm_config["TRAIN_SEED"])
    rngs = jax.random.split(rng, algorithm_config["NUM_SEEDS"])

    # Initialize br and conf policies
    conf_policy = ActorWithConditionalCriticPolicy(
        action_dim=env.action_space(env.agents[0]).n,
        obs_dim=env.observation_space(env.agents[0]).shape[0],
        pop_size=algorithm_config["PARTNER_POP_SIZE"],
    )
    br_policy = ActorWithConditionalCriticPolicy(
        action_dim=env.action_space(env.agents[0]).n,
        obs_dim=env.observation_space(env.agents[0]).shape[0],
        pop_size=algorithm_config["PARTNER_POP_SIZE"],
    )

    # Create a vmapped version of train_lbrdiv_partners
    with jax.disable_jit(False):
        vmapped_train_fn = jax.jit(
            jax.vmap(
                partial(train_lbrdiv_partners, env=env, config=algorithm_config, conf_policy=conf_policy,
                        br_policy=br_policy)
            )
        )
        out = vmapped_train_fn(rngs)

    end = time.time()
    log.info(f"LBRDiv training complete in {end - start} seconds")

    metric_names = get_metric_names(algorithm_config["ENV_NAME"])
    log_metrics(config, out, wandb_logger, metric_names)

    partner_params, partner_population = get_lbrdiv_population(config, out, env)

    return partner_params, partner_population


def log_metrics(config, outs, logger, metric_names: tuple):
    metrics = outs["metrics"]
    # metrics now has shape (num_seeds, num_updates, _, _, pop_size)
    num_seeds, num_updates, _, _, pop_size = metrics["pg_loss_conf_agent"].shape  # number of trained pairs

    ### Log evaluation metrics
    all_returns = np.asarray(metrics["eval_ep_last_info"]["returned_episode_returns"])
    xs = list(range(num_updates))

    all_conf_ids, all_br_ids = _get_all_ids(pop_size)
    sp_mask = (all_conf_ids == all_br_ids)
    sp_returns = all_returns[:, :, sp_mask]
    xp_returns = all_returns[:, :, ~sp_mask]

    # Average over seeds, then over agent pairs, episodes and num_agents_per_game
    sp_return_curve = sp_returns.mean(axis=(0, 2, 3, 4))
    xp_return_curve = xp_returns.mean(axis=(0, 2, 3, 4))

    for step in range(num_updates):
        logger.log_item("Eval/AvgSPReturnCurve", sp_return_curve[step], train_step=step)
        logger.log_item("Eval/AvgXPReturnCurve", xp_return_curve[step], train_step=step)
    logger.commit()

    # log final XP matrix to wandb - average over seeds
    last_returns_array = all_returns[:, -1].mean(axis=(0, 2, 3))
    last_returns_array = np.reshape(last_returns_array, (pop_size, pop_size))
    logger.log_xp_matrix("Eval/LastXPMatrix", last_returns_array)

    ### Log population loss as multi-line plots, where each line is a different population member
    # shape (num_seeds, num_updates, update_epochs, num_minibatches, pop_size)
    # Average over seeds
    processed_losses = {
        "ConfPGLoss": np.asarray(metrics["pg_loss_conf_agent"]).mean(axis=(0, 2, 3)).transpose(),
        "BRPGLoss": np.asarray(metrics["pg_loss_br_agent"]).mean(axis=(0, 2, 3)).transpose(),
        "ConfValLoss": np.asarray(metrics["value_loss_conf_agent"]).mean(axis=(0, 2, 3)).transpose(),
        "BRValLoss": np.asarray(metrics["value_loss_br_agent"]).mean(axis=(0, 2, 3)).transpose(),
        "ConfEntropy": np.asarray(metrics["entropy_conf"]).mean(axis=(0, 2, 3)).transpose(),
        "BREntropy": np.asarray(metrics["entropy_br"]).mean(axis=(0, 2, 3)).transpose(),
    }

    xs = list(range(num_updates))
    keys = [f"pair {i}" for i in range(pop_size)]
    for loss_name, loss_data in processed_losses.items():
        if np.isnan(loss_data).any():
            raise ValueError(f"Found nan in loss {loss_name}")
        logger.log_item(f"Losses/{loss_name}",
                        wandb.plot.line_series(xs=xs, ys=loss_data, keys=keys,
                                               title=loss_name, xname="train_step")
                        )

    # Average over seeds for Lagrange multipliers
    lm_keys = [f"pair {i}, {j}" for i in range(pop_size) for j in range(pop_size)]
    lm_horizontal = np.asarray(metrics["lms_horizontal"]).mean(axis=0)
    lm_vertical = np.asarray(metrics["lms_vertical"]).mean(axis=0)
    lagrange_multipliers = {
        "LMs_Horizontal": np.reshape(lm_horizontal, (lm_horizontal.shape[0], -1)).transpose(),
        "LMs_Vertical": np.reshape(lm_vertical, (lm_vertical.shape[0], -1)).transpose()
    }

    for array_name, array_data in lagrange_multipliers.items():
        if np.isnan(array_data).any():
            raise ValueError(f"Found nan in loss {array_name}")
        logger.log_item(
            f"Losses/{array_name}",
            wandb.plot.line_series(xs=xs, ys=array_data, keys=lm_keys,
                                   title=array_name, xname="train_step")
        )
        wandb.commit()

    ### Log artifacts
    savedir = hydra.core.hydra_config.HydraConfig.get().runtime.output_dir
    # Save train run output and log to wandb as artifact
    out_savepath = save_train_run(outs, savedir, savename="saved_train_run")
    if config["logger"]["log_train_out"]:
        logger.log_artifact(name="saved_train_run", path=out_savepath, type_name="train_run")

    # Cleanup locally logged out files
    if not config["local_logger"]["save_train_out"]:
        shutil.rmtree(out_savepath)
