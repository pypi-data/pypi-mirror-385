# src/mcts_gen/games/chess_mcts.py

from copy import deepcopy
import chess
from typing import List, Any, Dict

from mcts_gen.models.game_state import GameStateBase

class ChessGameState(GameStateBase):
    """
    Implements the game state for Chess using the python-chess library.
    This implementation uses a perspective-based reward system based on an initial color.
    """

    def __init__(self, fen: str = None):
        if fen:
            self.board = chess.Board(fen)
        else:
            self.board = chess.Board()
        # self.color is the perspective of this game state. It is set once
        # at initialization and does not change.
        self.color = self.board.turn

    def getCurrentPlayer(self) -> int:
        """Returns 1 if it is the turn of the color this state was created for, -1 otherwise."""
        return 1 if self.board.turn == self.color else -1

    def getPossibleActions(self) -> List[str]:
        """Returns a list of legal moves in UCI string format."""
        return [move.uci() for move in self.board.legal_moves]

    def takeAction(self, action: str) -> "ChessGameState":
        """Takes a UCI move string and returns the new state."""
        newState = deepcopy(self)
        newState.board.push_uci(action)
        return newState

    def isTerminal(self) -> bool:
        """Checks if the game is over."""
        return self.board.is_game_over()

    def getReward(self) -> float:
        """
        Calculates the reward from the perspective of self.color.
        Returns 1 for a win, -1 for a loss, 0 for a draw.
        """
        if not self.isTerminal():
            return 0.0

        result = self.board.result()

        if self.color == chess.WHITE:
            if result == "1-0":
                return 1.0
            elif result == "0-1":
                return -1.0
            else: # Draw
                return 0.0
        else: # self.color == chess.BLACK
            if result == "1-0":
                return -1.0
            elif result == "0-1":
                return 1.0
            else: # Draw
                return 0.0

    def to_dict(self) -> Dict[str, Any]:
        """Serializes the game state to a dictionary."""
        return {"fen": self.board.fen()}

    def __str__(self) -> str:
        """Returns a string representation of the board."""
        return str(self.board)