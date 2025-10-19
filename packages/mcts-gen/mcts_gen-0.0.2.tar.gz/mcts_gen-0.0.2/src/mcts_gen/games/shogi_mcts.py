from copy import deepcopy
import shogi
from typing import List, Any, Dict

from mcts_gen.models.game_state import GameStateBase

class ShogiGameState(GameStateBase):
    """
    Implements the game state for Shogi using the python-shogi library.
    """

    def __init__(self, sfen: str = ""):
        if not sfen:
            self.board = shogi.Board()
        else:
            self.board = shogi.Board(sfen)

    def getCurrentPlayer(self) -> int:
        return 1 if self.board.turn == shogi.BLACK else -1

    # def getPossibleActions(self) -> List[shogi.Move]:
    #     possibleActions = list(self.board.legal_moves)
    #     return possibleActions

    def getPossibleActions(self) -> List[str]:
        """Returns a list of legal moves in USI string format."""
        return [move.usi() for move in self.board.legal_moves]

    # def takeAction(self, action: shogi.Move) -> "ShogiGameState":
    def takeAction(self, action) -> "ShogiGameState":
        """Takes a shogi.Move object and returns the new state."""
        newState = deepcopy(self)
        # newState.board.push(action)
        newState.board.push_usi(action)
        # print(f"[DEBUG] Type of newState in takeAction: {type(newState)}")
        return newState

    def isTerminal(self) -> bool:
        return self.board.is_game_over()

    def getReward(self) -> float:
        if not self.isTerminal():
            # return None   # Falseや0でも良いがMCTSフレームワークと要相談
            # return False
            return 0.0

        # 勝者判定ロジック例
        if self.board.is_checkmate():
            # 手番が負けたなら
            return -1.0 if self.board.turn == shogi.BLACK else 1.0
        elif self.board.is_stalemate() or self.board.is_fourfold_repetition():
            return 0.0  # 引き分け
        else:
            # それ以外は要件次第（持将棋・その他エッジケース）
            return 0.0

    def to_dict(self) -> Dict[str, Any]:
        """Serializes the game state to a dictionary for logging."""
        return {"sfen": self.board.sfen()}

    def __str__(self) -> str:
        return self.board.kif_str()
