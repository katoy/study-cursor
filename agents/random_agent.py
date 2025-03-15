"""
ランダムエージェント

このモジュールは、ランダムに手を選択するAIエージェントを実装します。
空いているマスからランダムに1つを選択する単純な戦略を採用しています。

作者: Your Name
作成日: 2024/03/09
バージョン: 1.0
"""

import random
from typing import List, Optional
from .base_agent import BaseAgent


class RandomAgent(BaseAgent):
    """ランダムに手を選択するAIエージェント。

    このエージェントは、空いているマスからランダムに1つを選択します。
    初心者向けの対戦相手として使用できます。
    """

    def __init__(self) -> None:
        """初期化メソッド。"""
        super().__init__("ランダム")

    def get_move(self, board: List[str], player_mark: str) -> Optional[int]:
        """ランダムに手を選択します。

        Args:
            board: 現在の盤面（空文字は空きマス）
            player_mark: AIプレイヤーのマーク（'X' または 'O'）

        Returns:
            選択したマスのインデックス。有効な手がない場合はNone。
        """
        empty_cells = [i for i, mark in enumerate(board) if mark == ""]
        return random.choice(empty_cells) if empty_cells else None 