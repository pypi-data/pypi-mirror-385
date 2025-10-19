
import math
import random
from typing import Dict, Any, Optional

from mcts_solver.mcts_solver import AntLionMcts, AntLionTreeNode

from ..models.game_state import GameStateBase

# ======================================================================
# Node Class Definition
# ======================================================================
class MCTSNode(AntLionTreeNode):
    """
    Represents a node in the Monte Carlo Search Tree.
    Inherits from AntLionTreeNode to ensure full compatibility.
    """
    def __init__(self, state, parent):
        super().__init__(state, parent)

# ======================================================================
# Engine Class Definition (Corrected Plan B)
# ======================================================================
class McpMcts(AntLionMcts):
    """
    An MCTS engine that uses UCT (from parent) and AI value estimation.
    """

    def __init__(self, initial_state: GameStateBase, **kwargs):
        """
        Initializes the MCTS engine.
        """
        super().__init__(iterationLimit=kwargs.get("iterationLimit", 100))
        self.explorationConstant = kwargs.get("explorationConstant", 1.4)
        self.root = MCTSNode(initial_state, None)
        self.value: Optional[float] = None
        self.pruned_actions: Optional[List[str]] = None
        self.pruned_actions: Optional[List[Any]] = None # Hook for AI policy pruning

    def expand(self, node: MCTSNode) -> MCTSNode:
        """
        Uses a pre-filtered list of actions if provided, otherwise gets all actions.
        """
        actions = self.pruned_actions if self.pruned_actions is not None else node.state.getPossibleActions()
        
        # Clear the pruned list after using it for one expansion
        self.pruned_actions = None

        for action in actions:
            if action not in node.children:
                newNode = MCTSNode(node.state.takeAction(action), node)
                node.children[action] = newNode
                if len(actions) == len(node.children):
                    node.isFullyExpanded = True
                return newNode
        raise Exception("Should never reach here")

    def dl_method(self, state) -> float: # type: ignore
        """
        Overrides parent to use the AI's value prediction.
        """
        if self.value is not None:
            reward = self.value
            self.value = None
            return reward
        return self.rollout(state)

