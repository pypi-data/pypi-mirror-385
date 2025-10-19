from abc import ABC, abstractmethod
from typing import Any, List

class GameStateBase(ABC):
    """
    Abstract base class for any game environment that can be used with McpMcts.
    """

    @abstractmethod
    def getCurrentPlayer(self) -> int:
        """
        Return +1 if it's player one's turn, -1 if it's player two's turn.
        """
        pass

    @abstractmethod
    def getPossibleActions(self) -> List[Any]:
        """
        Return a list of all possible actions from this state.
        The actions MUST be serializable and preferably human-readable strings
        (e.g., USI for shogi) to allow AI agents to process them.
        """
        pass

    @abstractmethod
    def takeAction(self, action: Any) -> "GameStateBase":
        """
        Return the new GameState after applying the given action.
        """
        pass

    @abstractmethod
    def isTerminal(self) -> bool:
        """
        Return True if this state is terminal (game over).
        """
        pass

    @abstractmethod
    def getReward(self) -> float:
        """
        Return the reward for the current player if the game is terminal.
        Convention: +1 (win), -1 (loss), 0 (draw).
        """
        pass
