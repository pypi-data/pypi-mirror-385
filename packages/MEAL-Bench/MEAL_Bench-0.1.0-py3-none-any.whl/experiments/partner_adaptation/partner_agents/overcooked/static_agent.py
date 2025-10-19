from functools import partial
from typing import Tuple, Dict, Any

import jax
import jax.numpy as jnp

from meal.env.overcooked import Actions
from experiments.partner_adaptation.partner_agents.overcooked.base_agent import BaseAgent, AgentState


class StaticAgent(BaseAgent):
    """A static agent that always takes the stay action."""

    def __init__(self, layout: Dict[str, Any]):
        super().__init__(layout)

    @partial(jax.jit, static_argnums=(0,))
    def _get_action(self, obs: jnp.ndarray, agent_state: AgentState) -> Tuple[int, AgentState]:
        """Always return the stay action and unchanged state.

        Args:
            obs: Flattened observation array (not used)
            agent_state: AgentState containing agent's internal state

        Returns:
            Tuple of (action, agent_state)
        """
        return Actions.stay, agent_state
