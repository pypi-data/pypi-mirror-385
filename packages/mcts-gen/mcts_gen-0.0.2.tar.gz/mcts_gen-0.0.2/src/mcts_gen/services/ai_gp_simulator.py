
import importlib
# import math
from typing import Dict, Any, List

from fastmcp import FastMCP

from ..services.mcts_engine import McpMcts
# from ..models.game_state import GameStateBase

class AiGpSimulator:
    """
    A stateful simulator that encapsulates an MCTS engine and provides a set of
    generic, game-agnostic tools for an AI agent.
    """
    def __init__(self, mcp_instance: FastMCP):
        self.mcp = mcp_instance
        self.engine: McpMcts | None = None
        self.simulation_state: Dict[str, Any] = {}
        self._reset_simulation_state()

        self.mcp.tool(self.reinitialize_mcts)
        self.mcp.tool(self.run_mcts_round)
        self.mcp.tool(self.get_best_move)
        self.mcp.tool(self.get_simulation_stats)
        self.mcp.tool(self.get_possible_actions)

    def _reset_simulation_state(self):
        """Resets the state variables for a single evaluation run."""
        self.simulation_state = {
            'eaten': 0.0,
            'previous_eaten': 0.0,
            'improvement': 0,
        }

    def reinitialize_mcts(self, state_module: str, state_class: str, state_kwargs: Dict[str, Any] = {}, iteration_limit: int = 100) -> Dict[str, Any]:
        """Starts a new MCTS simulation for a given game."""
        try:
            module = importlib.import_module(state_module)
            game_class = getattr(module, state_class)
            initial_state = game_class(**state_kwargs)
            self.engine = McpMcts(initial_state=initial_state, iterationLimit=iteration_limit)
            self._reset_simulation_state()
            return {"status": "MCTS re-initialized successfully."}
        except Exception as e:
            return {"error": f"Failed to re-initialize MCTS: {e}"}

    def run_mcts_round(self, exploration_constant: float, actions_to_expand: List[str] | None = None) -> Dict[str, Any]:
        """Executes a single MCTS round and updates the simulation state."""
        if not self.engine:
            return {"error": "MCTS engine not initialized."}

        self.simulation_state['previous_eaten'] = self.simulation_state['eaten']
        self.engine.pruned_actions = actions_to_expand

        # --- MCTS 1-Round Logic ---
        node = self.engine.selectNode_num(self.engine.root, exploration_constant)
        reward = self.engine.mctsSolver(node)
        self.engine.backpropogate(node, reward)
        # --- End of 1-Round Logic ---

        # --- State Update Logic ---
        if self.engine.root.children:
            best_child = self.engine.getBestChild(self.engine.root, 0) # Use 0 exploration for pure exploitation
            if best_child.numVisits > 0:
                self.simulation_state['eaten'] = best_child.totalReward / best_child.numVisits
            else:
                self.simulation_state['eaten'] = 0.0
        else:
            self.simulation_state['eaten'] = 0.0

        if self.simulation_state['eaten'] > self.simulation_state['previous_eaten']:
            self.simulation_state['improvement'] = 2
        elif self.simulation_state['eaten'] == self.simulation_state['previous_eaten']:
            self.simulation_state['improvement'] = 1
        else:
            self.simulation_state['improvement'] = 0

        return {
            "status": "1 round executed.",
            "root_visits": self.engine.root.numVisits,
            "simulation_stats": self.simulation_state
        }

    def get_best_move(self) -> Dict[str, Any]:
        """Retrieves the best move found so far."""
        if not self.engine or not self.engine.root.children:
            return {"error": "No search performed yet."}
        best_child = self.engine.getBestChild(self.engine.root, 0)
        for action, node in self.engine.root.children.items():
            if node is best_child:
                return {"best_move": str(action)}
        return {"error": "Could not determine best move."}

    def get_simulation_stats(self) -> Dict[str, Any]:
        """Returns the current state of the simulation variables."""
        return self.simulation_state

    def get_possible_actions(self) -> Dict[str, Any]:
        """Retrieves the list of all possible actions from the current root state."""
        if not self.engine:
            return {"error": "MCTS engine not initialized."}
        try:
            actions = self.engine.root.state.getPossibleActions()
            return {"possible_actions": actions}
        except Exception as e:
            return {"error": f"Failed to get possible actions: {e}"}
