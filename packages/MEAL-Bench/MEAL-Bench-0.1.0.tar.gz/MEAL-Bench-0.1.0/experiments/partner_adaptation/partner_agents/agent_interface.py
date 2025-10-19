import abc
from functools import partial
from typing import Tuple, Dict

import chex
import jax
import jax.numpy as jnp

from experiments.partner_adaptation.partner_agents.mlp_actor_critic import ActorCritic
from experiments.partner_adaptation.partner_agents.mlp_actor_critic import ActorWithConditionalCritic
from experiments.partner_adaptation.partner_agents.mlp_actor_critic import ActorWithDoubleCritic


class AgentPolicy(abc.ABC):
    '''Abstract base class for a policy.'''

    def __init__(self, action_dim, obs_dim):
        '''
        Args:
            action_dim: int, dimension of the action space
            obs_dim: int, dimension of the observation space
        '''
        self.action_dim = action_dim
        self.obs_dim = obs_dim

    @abc.abstractmethod
    @partial(jax.jit, static_argnums=(0,))
    def get_action(self, params, obs, done, avail_actions, hstate, rng,
                   aux_obs=None, env_state=None, test_mode=False) -> Tuple[int, chex.Array]:
        """
        Only computes an action given an observation, done flag, available actions, hidden state, and random key.

        Args:
            params (dict): The parameters of the policy.
            obs (chex.Array): The observation.
            done (chex.Array): The done flag.
            avail_actions (chex.Array): The available actions.
            hstate (chex.Array): The hidden state.
            key (jax.random.PRNGKey): The random key.
            env_state (chex.Array): The environment state.
            aux_obs (chex.Array): an optional auxiliary vector to append to the observation
        Returns:
            Tuple[int, chex.Array]: A tuple containing the action and the new hidden state.
        """
        pass

    @partial(jax.jit, static_argnums=(0,))
    def get_action_value_policy(self, params, obs, done, avail_actions, hstate, rng,
                                aux_obs=None, env_state=None) -> Tuple[int, chex.Array, chex.Array, chex.Array]:
        """
        Computes the action, value, and policy given an observation,
        done flag, available actions, hidden state, and random key.

        Args:
            params (dict): The parameters of the policy.
            obs (chex.Array): The observation.
            done (chex.Array): The done flag.
            avail_actions (chex.Array): The available actions.
            hstate (chex.Array): The hidden state.
            key (jax.random.PRNGKey): The random key.
            aux_obs (chex.Array): an optional auxiliary vector to append to the observation
        Returns:
            Tuple[int, chex.Array, chex.Array, chex.Array]:
                A tuple containing the action, value, policy, and new hidden state.
        """
        pass

    def init_hstate(self, batch_size, aux_info: dict = None) -> chex.Array:
        """Initialize the hidden state for the policy.
        Args:
            batch_size: int, the batch size of the hidden state
            aux_info: any auxiliary information needed to initialize the hidden state at the
            start of an episode (e.g. the agent id).
        Returns:
            chex.Array: the initialized hidden state
        """
        return None

    def init_params(self, rng) -> Dict:
        """Initialize the parameters for the policy."""
        return None


class MLPActorCriticPolicyCL(AgentPolicy):
    """Policy wrapper for MLP Actor-Critic for continual learning"""

    def __init__(self, ac, obs_dim):
        """
        Args:
            action_dim: int, dimension of the action space
            obs_dim: int, dimension of the observation space
            activation: str, activation function to use
        """
        super().__init__(6, obs_dim)
        # self.activation = activation
        self.network = ac

    @partial(jax.jit, static_argnums=(0, 7))
    def get_action(self, params, obs, done, avail_actions, hstate, rng,
                   env_id_idx=0, aux_obs=None, env_state=None, test_mode=False):
        """Get actions for the MLP policy."""
        pi, _, _ = self.network.apply(params, obs, env_idx=env_id_idx)
        action = jax.lax.cond(test_mode,
                              lambda: pi.mode(),
                              lambda: pi.sample(seed=rng))
        return action, None  # no hidden state

    @partial(jax.jit, static_argnums=(0, 7))
    def get_action_value_policy(self, params, obs, done, avail_actions, hstate, rng,
                                env_id_idx=0, aux_obs=None, env_state=None):
        """Get actions, values, and policy for the MLP policy."""
        pi, val, _ = self.network.apply(params, obs, env_idx=env_id_idx)
        action = pi.sample(seed=rng)
        return action, val, pi, None  # no hidden state

    def init_params(self, rng):
        """Initialize parameters for the MLP policy."""
        dummy_obs = jnp.zeros((1, self.obs_dim,))
        return self.network.init(rng, dummy_obs, env_idx=0)


class MLPActorCriticPolicy(AgentPolicy):
    """Policy wrapper for MLP Actor-Critic"""

    def __init__(self, action_dim, obs_dim, activation="tanh"):
        """
        Args:
            action_dim: int, dimension of the action space
            obs_dim: int, dimension of the observation space
            activation: str, activation function to use
        """
        super().__init__(action_dim, obs_dim)
        # self.activation = activation
        self.network = ActorCritic(action_dim, activation=activation)

    @partial(jax.jit, static_argnums=(0,))
    def get_action(self, params, obs, done, avail_actions, hstate, rng,
                   aux_obs=None, env_state=None, test_mode=False):
        """Get actions for the MLP policy."""
        pi, _ = self.network.apply(params, (obs, avail_actions))
        action = jax.lax.cond(test_mode,
                              lambda: pi.mode(),
                              lambda: pi.sample(seed=rng))
        return action, None  # no hidden state

    @partial(jax.jit, static_argnums=(0,))
    def get_action_value_policy(self, params, obs, done, avail_actions, hstate, rng,
                                aux_obs=None, env_state=None):
        """Get actions, values, and policy for the MLP policy."""
        pi, val = self.network.apply(params, (obs, avail_actions))
        action = pi.sample(seed=rng)
        return action, val, pi, None  # no hidden state

    def init_params(self, rng):
        """Initialize parameters for the MLP policy."""
        dummy_obs = jnp.zeros((self.obs_dim,))
        dummy_avail = jnp.ones((self.action_dim,))
        init_x = (dummy_obs, dummy_avail)
        return self.network.init(rng, init_x)


class ActorWithDoubleCriticPolicy(AgentPolicy):
    """Policy wrapper for Actor with Double Critics"""

    def __init__(self, action_dim, obs_dim, activation="tanh"):
        """
        Args:
            action_dim: int, dimension of the action space
            obs_dim: int, dimension of the observation space
            activation: str, activation function to use
        """
        super().__init__(action_dim, obs_dim)
        self.network = ActorWithDoubleCritic(action_dim, activation=activation)

    @partial(jax.jit, static_argnums=(0,))
    def get_action(self, params, obs, done, avail_actions, hstate, rng,
                   aux_obs=None, env_state=None, test_mode=False):
        """Get actions for the policy with double critics.
        """
        pi, _, _ = self.network.apply(params, (obs, avail_actions))
        action = jax.lax.cond(test_mode,
                              lambda: pi.mode(),
                              lambda: pi.sample(seed=rng))
        return action, None  # no hidden state

    @partial(jax.jit, static_argnums=(0,))
    def get_action_value_policy(self, params, obs, done, avail_actions, hstate, rng,
                                aux_obs=None, env_state=None):
        """Get actions, values, and policy for the policy with double critics."""
        # convention: val1 is value of of ego agent, val2 is value of best response agent
        pi, val1, val2 = self.network.apply(params, (obs, avail_actions))
        action = pi.sample(seed=rng)
        return action, (val1, val2), pi, None  # no hidden state

    def init_params(self, rng):
        """Initialize parameters for the policy with double critics."""
        dummy_obs = jnp.zeros((self.obs_dim,))
        dummy_avail = jnp.ones((self.action_dim,))
        init_x = (dummy_obs, dummy_avail)
        return self.network.init(rng, init_x)


class PseudoActorWithDoubleCriticPolicy(ActorWithDoubleCriticPolicy):
    """Enables ActorWithDoubleCritic to masquerade as an actor with a single critic."""

    def __init__(self, action_dim, obs_dim, activation="tanh"):
        super().__init__(action_dim, obs_dim, activation)

    def get_action_value_policy(self, params, obs, done, avail_actions, hstate, rng,
                                aux_obs=None, env_state=None):
        action, (val1, _), pi, hidden_state = super().get_action_value_policy(
            params, obs, done, avail_actions, hstate, rng,
            aux_obs, env_state)
        return action, val1, pi, hidden_state


class ActorWithConditionalCriticPolicy(AgentPolicy):
    """Policy wrapper for ActorWithConditionalCritic
    """

    def __init__(self, action_dim, obs_dim, pop_size, activation="tanh"):
        """
        Args:
            action_dim: int, dimension of the action space
            obs_dim: int, dimension of the observation space
            pop_size: int, number of agents in the population that the critic was trained with
            activation: str, activation function to use
        """
        super().__init__(action_dim, obs_dim)
        # self.activation = activation
        self.pop_size = pop_size
        self.network = ActorWithConditionalCritic(
            action_dim, activation=activation)

    @partial(jax.jit, static_argnums=(0,))
    def get_action(self, params, obs, done, avail_actions, hstate, rng,
                   env_id_idx=0, aux_obs=None, env_state=None, test_mode=False):
        """Get actions."""
        # The agent id is only used by the critic, so we pass in a
        # dummy vector to represent the one-hot agent id
        dummy_agent_id = jnp.zeros(obs.shape[:-1] + (self.pop_size,))
        pi, _ = self.network.apply(
            params, (obs, dummy_agent_id, avail_actions))
        action = jax.lax.cond(test_mode,
                              lambda: pi.mode(),
                              lambda: pi.sample(seed=rng))
        return action, None  # no hidden state

    @partial(jax.jit, static_argnums=(0,))
    def get_action_value_policy(self, params, obs, done, avail_actions, hstate, rng,
                                env_id_idx=0, aux_obs=None, env_state=None):
        """Get actions, values, and policy for the policy with conditional critics.
        The auxiliary observation should be used to pass in the agent ids that we wish to predict
        values for.
        """
        pi, value = self.network.apply(params, (obs, aux_obs, avail_actions))
        action = pi.sample(seed=rng)
        return action, value, pi, None  # no hidden state

    def init_params(self, rng):
        """Initialize parameters for the policy with conditional critics."""
        dummy_obs = jnp.zeros((self.obs_dim,))
        dummy_ids = jnp.zeros((self.pop_size,))
        dummy_avail = jnp.ones((self.action_dim,))
        init_x = (dummy_obs, dummy_ids, dummy_avail)
        return self.network.init(rng, init_x)


class PseudoActorWithConditionalCriticPolicy(ActorWithConditionalCriticPolicy):
    """Enables PseudoActorWithConditionalCriticPolicy to act as an MLPActorCriticPolicy.
    by passing in a dummy agent id.
    """

    def __init__(self, action_dim, obs_dim, pop_size, activation="tanh"):
        super().__init__(action_dim, obs_dim, pop_size, activation)

    def get_action_value_policy(self, params, obs, done, avail_actions, hstate, rng,
                                aux_obs=None, env_state=None):
        dummy_agent_id = jnp.zeros(obs.shape[:-1] + (self.pop_size,))
        action, val, pi, hidden_state = super().get_action_value_policy(
            params, obs, done, avail_actions, hstate, rng,
            dummy_agent_id, env_state)
        return action, val, pi, hidden_state


class RNNActorCriticPolicy(AgentPolicy):
    """Policy wrapper for RNN Actor-Critic"""

    def __init__(self, action_dim, obs_dim,
                 activation="tanh", fc_hidden_dim=64, gru_hidden_dim=64):
        """
        Args:
            action_dim: int, dimension of the action space
            obs_dim: int, dimension of the observation space
            activation: str, activation function to use
            fc_hidden_dim: int, dimension of the feed-forward hidden layers
            gru_hidden_dim: int, dimension of the GRU hidden state
        """
        super().__init__(action_dim, obs_dim)
        self.network = RNNActorCritic(
            action_dim,
            fc_hidden_dim=fc_hidden_dim,
            gru_hidden_dim=gru_hidden_dim,
            activation=activation
        )
        self.gru_hidden_dim = gru_hidden_dim

    @partial(jax.jit, static_argnums=(0,))
    def get_action(self, params, obs, done, avail_actions, hstate, rng,
                   aux_obs=None, env_state=None, test_mode=False):
        """Get actions for the RNN policy.
        Shape of obs, done, avail_actions should correspond to (seq_len, batch_size, ...)
        Shape of hstate should correspond to (1, batch_size, -1). We maintain the extra first dimension for
        compatibility with the learning codes.
        """
        batch_size = obs.shape[1]
        new_hstate, pi, _ = self.network.apply(
            params, hstate.squeeze(0), (obs, done, avail_actions))
        action = jax.lax.cond(test_mode,
                              lambda: pi.mode(),
                              lambda: pi.sample(seed=rng))
        return action, new_hstate.reshape(1, batch_size, -1)

    @partial(jax.jit, static_argnums=(0,))
    def get_action_value_policy(self, params, obs, done, avail_actions, hstate, rng,
                                aux_obs=None, env_state=None):
        """Get actions, values, and policy for the RNN policy.
        Shape of obs, done, avail_actions should correspond to (seq_len, batch_size, ...)
        Shape of hstate should correspond to (1, batch_size, -1). We maintain the extra first dimension for
        compatibility with the learning codes.
        """
        batch_size = obs.shape[1]
        new_hstate, pi, val = self.network.apply(
            params, hstate.squeeze(0), (obs, done, avail_actions))
        action = pi.sample(seed=rng)
        return action, val, pi, new_hstate.reshape(1, batch_size, -1)

    def init_hstate(self, batch_size, aux_info=None):
        """Initialize hidden state for the RNN policy."""
        hstate = ScannedRNN.initialize_carry(batch_size, self.gru_hidden_dim)
        hstate = hstate.reshape(1, batch_size, self.gru_hidden_dim)
        return hstate

    def init_params(self, rng):
        """Initialize parameters for the RNN policy."""
        batch_size = 1
        # Initialize hidden state
        init_hstate = self.init_hstate(batch_size)

        # Create dummy inputs - add time dimension
        dummy_obs = jnp.zeros((1, batch_size, self.obs_dim))
        dummy_done = jnp.zeros((1, batch_size))
        dummy_avail = jnp.ones((1, batch_size, self.action_dim))
        dummy_x = (dummy_obs, dummy_done, dummy_avail)

        # Initialize model
        return self.network.init(rng, init_hstate.reshape(batch_size, -1), dummy_x)


class S5ActorCriticPolicy(AgentPolicy):
    """Policy wrapper for S5 Actor-Critic"""

    def __init__(self, action_dim, obs_dim,
                 d_model=16, ssm_size=16,
                 ssm_n_layers=2, blocks=1,
                 fc_hidden_dim=64,
                 fc_n_layers=2,
                 s5_activation="full_glu",
                 s5_do_norm=True,
                 s5_prenorm=True,
                 s5_do_gtrxl_norm=True,
                 s5_no_reset=False):
        """
        Args:
            action_dim: int, dimension of the action space
            obs_dim: int, dimension of the observation space
            d_model: int, dimension of the model
            ssm_size: int, size of the SSM
            n_layers: int, number of S5 layers
            blocks: int, number of blocks to split SSM parameters
            fc_hidden_dim: int, dimension of the fully connected hidden layers
            s5_activation: str, activation function to use in S5
            s5_do_norm: bool, whether to apply normalization in S5
            s5_prenorm: bool, whether to apply pre-normalization in S5
            s5_do_gtrxl_norm: bool, whether to apply gtrxl normalization in S5
            s5_no_reset: bool, whether to ignore reset signals
        """
        super().__init__(action_dim, obs_dim)
        self.d_model = d_model
        self.ssm_size = ssm_size
        self.ssm_n_layers = ssm_n_layers
        self.blocks = blocks
        self.fc_hidden_dim = fc_hidden_dim
        self.fc_n_layers = fc_n_layers
        self.s5_activation = s5_activation
        self.s5_do_norm = s5_do_norm
        self.s5_prenorm = s5_prenorm
        self.s5_do_gtrxl_norm = s5_do_gtrxl_norm
        self.s5_no_reset = s5_no_reset

        # Initialize SSM parameters
        block_size = int(ssm_size / blocks)
        Lambda, _, _, V, _ = make_DPLR_HiPPO(ssm_size)
        block_size = block_size // 2
        ssm_size_half = ssm_size // 2
        Lambda = Lambda[:block_size]
        V = V[:, :block_size]
        Vinv = V.conj().T

        self.ssm_init_fn = init_S5SSM(
            H=d_model,
            P=ssm_size_half,
            Lambda_re_init=Lambda.real,
            Lambda_im_init=Lambda.imag,
            V=V,
            Vinv=Vinv
        )

        # Initialize the network instance once
        self.network = S5ActorCritic(
            action_dim,
            ssm_init_fn=self.ssm_init_fn,
            fc_hidden_dim=self.fc_hidden_dim,
            fc_n_layers=self.fc_n_layers,
            ssm_hidden_dim=self.ssm_size,
            s5_d_model=self.d_model,
            s5_n_layers=self.ssm_n_layers,
            s5_activation=self.s5_activation,
            s5_do_norm=self.s5_do_norm,
            s5_prenorm=self.s5_prenorm,
            s5_do_gtrxl_norm=self.s5_do_gtrxl_norm,
            s5_no_reset=self.s5_no_reset
        )

    @partial(jax.jit, static_argnums=(0,))
    def get_action(self, params, obs, done, avail_actions, hstate, rng,
                   aux_obs=None, env_state=None, test_mode=False):
        """Get actions for the S5 policy."""
        new_hstate, pi, _ = self.network.apply(
            params, hstate, (obs, done, avail_actions))
        action = jax.lax.cond(test_mode,
                              lambda: pi.mode(),
                              lambda: pi.sample(seed=rng))
        return action, new_hstate

    @partial(jax.jit, static_argnums=(0,))
    def get_action_value_policy(self, params, obs, done, avail_actions, hstate, rng,
                                aux_obs=None, env_state=None):
        """Get actions, values, and policy for the S5 policy.
        Shape of obs, done, avail_actions should correspond to (seq_len, batch_size, ...)
        Shape of hstate should correspond to (1, batch_size, -1)
        """
        new_hstate, pi, val = self.network.apply(
            params, hstate, (obs, done, avail_actions))
        action = pi.sample(seed=rng)
        return action, val, pi, new_hstate

    def init_hstate(self, batch_size, aux_info=None):
        """Initialize hidden state for the S5 policy."""

        init_hstate = StackedEncoderModel.initialize_carry(
            batch_size, self.ssm_size // 2, self.ssm_n_layers)
        return init_hstate

    def init_params(self, rng):
        """Initialize parameters for the S5 policy."""
        batch_size = 1
        # Initialize hidden state
        init_hstate = self.init_hstate(batch_size)

        # Create dummy inputs
        dummy_obs = jnp.zeros((1, batch_size, self.obs_dim))
        dummy_done = jnp.zeros((1, batch_size))
        dummy_avail = jnp.ones((1, batch_size, self.action_dim))
        dummy_x = (dummy_obs, dummy_done, dummy_avail)

        # Initialize model using the pre-initialized network
        return self.network.init(rng, init_hstate, dummy_x)
