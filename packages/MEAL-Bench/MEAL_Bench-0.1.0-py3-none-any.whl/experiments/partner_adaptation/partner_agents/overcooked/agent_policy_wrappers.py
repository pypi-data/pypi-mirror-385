'''Wrap heuristic agent policies in AgentPolicy interface.
TODO: clean up logic by vectorizing init_hstate. See HeuristicPolicyPopulation.
'''
import jax

from experiments.partner_adaptation.partner_agents.agent_interface import AgentPolicy
from experiments.partner_adaptation.partner_agents.overcooked.independent_agent import IndependentAgent
from experiments.partner_adaptation.partner_agents.overcooked.onion_agent import OnionAgent
from experiments.partner_adaptation.partner_agents.overcooked.plate_agent import PlateAgent
from experiments.partner_adaptation.partner_agents.overcooked.random_agent import RandomAgent
from experiments.partner_adaptation.partner_agents.overcooked.static_agent import StaticAgent


class OvercookedIndependentPolicyWrapper(AgentPolicy):
    """Policy wrapper for the Independent heuristic agent."""

    def __init__(self, layout, using_log_wrapper=False,
                 p_onion_on_counter=0.0, p_plate_on_counter=0.0):
        super().__init__(action_dim=6, obs_dim=None)  # Action dim 6 for Overcooked
        self.policy = IndependentAgent(
            layout, p_onion_on_counter, p_plate_on_counter)
        self.using_log_wrapper = using_log_wrapper

    def get_action(self, params, obs, done, avail_actions, hstate, rng,
                   env_state, env_id_idx=0, aux_obs=None, test_mode=False):
        if self.using_log_wrapper:
            env_state = env_state.env_state
        # hstate represents the agent state
        action, new_hstate = self.policy.get_action(obs, env_state, hstate)

        # if done, reset the hstate
        new_hstate = jax.lax.cond(done.squeeze(),
                                  lambda: self.policy.init_agent_state(
                                      hstate.agent_id),
                                  lambda: new_hstate)
        return action, new_hstate

    def init_hstate(self, batch_size: int, aux_info=None):
        return self.policy.init_agent_state(aux_info["agent_id"])


class OvercookedOnionPolicyWrapper(AgentPolicy):
    """Policy wrapper for the Onion heuristic agent."""

    def __init__(self, layout, p_onion_on_counter=0., using_log_wrapper=False):
        super().__init__(action_dim=6, obs_dim=None)
        self.policy = OnionAgent(layout, p_onion_on_counter)
        self.using_log_wrapper = using_log_wrapper

    def get_action(self, params, obs, done, avail_actions, hstate, rng,
                   env_state, env_id_idx=0, aux_obs=None, test_mode=False):
        if self.using_log_wrapper:
            env_state = env_state.env_state
        action, new_hstate = self.policy.get_action(obs, env_state, hstate)
        # if done, reset the hstate
        new_hstate = jax.lax.cond(done.squeeze(),
                                  lambda: self.policy.init_agent_state(
                                      hstate.agent_id),
                                  lambda: new_hstate)
        return action, new_hstate

    def init_hstate(self, batch_size: int, aux_info=None):
        return self.policy.init_agent_state(aux_info["agent_id"])


class OvercookedPlatePolicyWrapper(AgentPolicy):
    """Policy wrapper for the Plate heuristic agent."""

    def __init__(self, layout, p_plate_on_counter=0., using_log_wrapper=False):
        super().__init__(action_dim=6, obs_dim=None)
        self.policy = PlateAgent(layout, p_plate_on_counter)
        self.using_log_wrapper = using_log_wrapper

    def get_action(self, params, obs, done, avail_actions, hstate, rng,
                   env_state, env_id_idx=0, aux_obs=None, test_mode=False):
        if self.using_log_wrapper:
            env_state = env_state.env_state
        action, new_hstate = self.policy.get_action(obs, env_state, hstate)
        # if done, reset the hstate
        new_hstate = jax.lax.cond(done.squeeze(),
                                  lambda: self.policy.init_agent_state(
                                      hstate.agent_id),
                                  lambda: new_hstate)
        return action, new_hstate

    def init_hstate(self, batch_size: int, aux_info=None):
        return self.policy.init_agent_state(aux_info["agent_id"])


class OvercookedStaticPolicyWrapper(AgentPolicy):
    """Policy wrapper for the Static heuristic agent."""

    def __init__(self, layout, using_log_wrapper=False):
        super().__init__(action_dim=6, obs_dim=None)
        self.policy = StaticAgent(layout)
        self.using_log_wrapper = using_log_wrapper

    def get_action(self, params, obs, done, avail_actions, hstate, rng,
                   env_state, env_id_idx=0, aux_obs=None, test_mode=False):
        if self.using_log_wrapper:
            env_state = env_state.env_state
        action, new_hstate = self.policy.get_action(obs, env_state, hstate)
        return action, new_hstate

    def init_hstate(self, batch_size: int, aux_info=None):
        return self.policy.init_agent_state(aux_info["agent_id"])


class OvercookedRandomPolicyWrapper(AgentPolicy):
    """Policy wrapper for the Random heuristic agent."""

    def __init__(self, layout, using_log_wrapper=False):
        super().__init__(action_dim=6, obs_dim=None)
        self.policy = RandomAgent(layout)
        self.using_log_wrapper = using_log_wrapper

    def get_action(self, params, obs, done, avail_actions, hstate, rng,
                   env_id_idx=0, aux_obs=None, env_state=None, test_mode=False):
        if self.using_log_wrapper:
            env_state = env_state.env_state
        action, new_hstate = self.policy.get_action(obs, env_state, hstate)
        return action, new_hstate

    def init_hstate(self, batch_size: int, aux_info=None):
        return self.policy.init_agent_state(aux_info["agent_id"])
