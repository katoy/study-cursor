"""
完全な戦略を実装した三目並べAIエージェント。

このエージェントは、事前に計算された全ての盤面状態を使用して、
常に最適な手を選択します。
"""

import sqlite3
import random
from pathlib import Path
from typing import List, Optional
from .base_agent import BaseAgent


class PerfectAgent(BaseAgent):
    """完全な戦略を実装したエージェント。

    事前に計算された全ての盤面状態をデータベースから読み込み、
    常に最適な手を選択します。これにより、このエージェントは
    決して負けることがありません。
    """

    def __init__(self) -> None:
        """エージェントの初期化。"""
        super().__init__("完全戦略")
        self.db_path = Path(__file__).parent.parent / "database" / "game_history.db"

    def get_move(self, board: List[str], player: str) -> Optional[int]:
        """最適な手を選択します。

        Args:
            board: 現在の盤面状態
            player: プレイヤーの記号（"X" または "O"）

        Returns:
            選択した手の位置（0-8）
        """
        state_id = self._generate_state_id(board, player)
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                SELECT best_move
                FROM board_states
                WHERE state_id = ?
                """, (state_id,))
                
                result = cursor.fetchone()
                if result and result[0] is not None:
                    move = result[0]
                    # 選択された手が有効（空きマス）かチェック
                    if 0 <= move < len(board) and board[move] == "":
                        return move
                    else:
                        print(f"警告: データベースから無効な手が返されました: {move}")
                        return self._get_random_move(board)

        except sqlite3.Error as e:
            print(f"データベースエラー: {e}")
            return self._get_random_move(board)

        print(f"警告: 状態が見つかりません: {state_id}")
        return self._get_random_move(board)

    def _generate_state_id(self, board: List[str], player: str) -> str:
        """盤面状態のユニークIDを生成します。

        Args:
            board: 現在の盤面状態
            player: プレイヤーの記号（"X" または "O"）

        Returns:
            状態ID
        """
        # 空のマスを'-'に置き換えて状態IDを生成
        board_str = ''.join(cell if cell != "" else "-" for cell in board)
        return f"{board_str}_{player}"

    def _get_random_move(self, board: List[str]) -> Optional[int]:
        """ランダムな手を選択します。

        Args:
            board: 現在の盤面状態

        Returns:
            選択した手の位置（0-8）、または空きマスがない場合はNone
        """
        empty_cells = [i for i, cell in enumerate(board) if cell == ""]
        return random.choice(empty_cells) if empty_cells else None 