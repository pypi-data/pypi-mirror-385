"""
A dummy game implementation (Tic-Tac-Toe) for testing and demonstration.
"""
from typing import List, Any, Optional

from ..models.game_state import GameStateBase

class TicTacToeDummy(GameStateBase):
    """A simplified Tic-Tac-Toe game state for testing the MCTS engine."""
    def __init__(self, board: Optional[List[int]] = None, player: int = 1):
        """Initializes the dummy game state.

        Args:
            board: A list of 9 integers representing the board (0=empty, 1=p1, -1=p2).
            player: The current player (1 or -1).
        """
        self.board = board or [0] * 9
        self.player = player

    def getCurrentPlayer(self) -> int:
        """Returns the current player."""
        return self.player

    def getPossibleActions(self) -> List[int]:
        """Returns a list of possible moves (empty squares)."""
        return [i for i, p in enumerate(self.board) if p == 0]

    def takeAction(self, action: int) -> "TicTacToeDummy":
        """Applies a move and returns the new game state."""
        new_board = self.board[:]
        new_board[action] = self.player
        return TicTacToeDummy(board=new_board, player=-self.player)

    def isTerminal(self) -> bool:
        """Checks if the game is over (no more moves)."""
        # This is a simplified terminal condition for testing.
        # A real implementation would check for wins.
        return not self.getPossibleActions()

    def getReward(self) -> float:
        """Returns the reward for the game outcome."""
        # Simplified reward: the previous player is considered the winner.
        return 1.0 if self.player == -1 else -1.0