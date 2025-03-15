"""
AIエージェントの基底クラス

このモジュールは、三目並べゲームのAIエージェントの基底クラスを定義します。
すべてのAIエージェントはこのクラスを継承して実装する必要があります。
"""

from typing import List, Optional
from abc import ABC, abstractmethod


class BaseAgent(ABC):
    """AIエージェントの基底クラス。

    このクラスは、三目並べゲームのAIエージェントが実装すべきインターフェースを定義します。
    すべてのAIエージェントはこのクラスを継承し、get_moveメソッドを実装する必要があります。

    Attributes:
        name (str): エージェントの名前
    """

    def __init__(self, name: str) -> None:
        """初期化メソッド。

        Args:
            name: エージェントの名前
        """
        self.name = name

    @abstractmethod
    def get_move(self, board: List[str], player_mark: str) -> Optional[int]:
        """次の手を決定します。

        Args:
            board: 現在の盤面（空文字は空きマス）
            player_mark: AIプレイヤーのマーク（'X' または 'O'）

        Returns:
            選択したマスのインデックス。有効な手がない場合はNone。
        """
        pass 