"""
ミニマックスエージェント

このモジュールは、ミニマックスアルゴリズムとアルファベータ枝刈りを使用するAIエージェントを実装します。
探索の深さを考慮した評価関数を使用し、効率的な探索を実現しています。
"""

import math
from typing import List, Optional, Tuple
from .base_agent import BaseAgent


class MinimaxAgent(BaseAgent):
    """ミニマックスアルゴリズムを使用するAIエージェント。

    このエージェントは、ミニマックスアルゴリズムとアルファベータ枝刈りを使用して、
    最適な手を選択します。探索の深さを考慮した評価関数を使用し、
    効率的な探索を実現しています。
    """

    def __init__(self) -> None:
        """初期化メソッド。"""
        super().__init__("ミニマックス")

    def get_move(self, board: List[str], player_mark: str) -> Optional[int]:
        """ミニマックスアルゴリズムを使用して最適な手を選択します。

        Args:
            board: 現在の盤面（空文字は空きマス）
            player_mark: AIプレイヤーのマーク（'X' または 'O'）

        Returns:
            選択したマスのインデックス。有効な手がない場合はNone。
        """
        best_val = -math.inf
        best_move = None
        opponent_mark = "O" if player_mark == "X" else "X"

        for i, mark in enumerate(board):
            if mark == "":
                board[i] = player_mark
                move_val = self._minimax(board, 0, False, -math.inf, math.inf, player_mark, opponent_mark)
                board[i] = ""

                if move_val > best_val:
                    best_move = i
                    best_val = move_val

        return best_move

    def _minimax(self, board: List[str], depth: int, is_max: bool, alpha: float, beta: float,
                player_mark: str, opponent_mark: str) -> float:
        """ミニマックスアルゴリズム（アルファベータ枝刈り付き）を実行します。

        Args:
            board: 現在の盤面
            depth: 探索の深さ
            is_max: 最大化プレイヤーのターンかどうか
            alpha: アルファ値
            beta: ベータ値
            player_mark: AIプレイヤーのマーク
            opponent_mark: 相手のマーク

        Returns:
            評価値
        """
        score = self._evaluate_board(board, player_mark, opponent_mark)

        if score == 10:
            return score - depth
        if score == -10:
            return score + depth
        if not self._is_moves_left(board):
            return 0

        return self._maximize(board, depth, alpha, beta, player_mark, opponent_mark) if is_max \
            else self._minimize(board, depth, alpha, beta, player_mark, opponent_mark)

    def _maximize(self, board: List[str], depth: int, alpha: float, beta: float,
                player_mark: str, opponent_mark: str) -> float:
        """最大化処理を行います。

        Args:
            board: 現在の盤面
            depth: 探索の深さ
            alpha: アルファ値
            beta: ベータ値
            player_mark: AIプレイヤーのマーク
            opponent_mark: 相手のマーク

        Returns:
            最大評価値
        """
        best = -math.inf
        for i, mark in enumerate(board):
            if mark == "":
                board[i] = player_mark
                best = max(best, self._minimax(board, depth + 1, False, alpha, beta,
                                            player_mark, opponent_mark))
                board[i] = ""
                alpha = max(alpha, best)
                if beta <= alpha:
                    break
        return best

    def _minimize(self, board: List[str], depth: int, alpha: float, beta: float,
                player_mark: str, opponent_mark: str) -> float:
        """最小化処理を行います。

        Args:
            board: 現在の盤面
            depth: 探索の深さ
            alpha: アルファ値
            beta: ベータ値
            player_mark: AIプレイヤーのマーク
            opponent_mark: 相手のマーク

        Returns:
            最小評価値
        """
        best = math.inf
        for i, mark in enumerate(board):
            if mark == "":
                board[i] = opponent_mark
                best = min(best, self._minimax(board, depth + 1, True, alpha, beta,
                                            player_mark, opponent_mark))
                board[i] = ""
                beta = min(beta, best)
                if beta <= alpha:
                    break
        return best

    def _evaluate_board(self, board: List[str], player_mark: str, opponent_mark: str) -> int:
        """盤面を評価します。

        Args:
            board: 現在の盤面
            player_mark: AIプレイヤーのマーク
            opponent_mark: 相手のマーク

        Returns:
            評価値（10: AIの勝ち, -10: 相手の勝ち, 0: その他）
        """
        # 横のパターン
        for i in range(0, 9, 3):
            if board[i] == board[i+1] == board[i+2] != "":
                if board[i] == player_mark:
                    return 10
                elif board[i] == opponent_mark:
                    return -10

        # 縦のパターン
        for i in range(3):
            if board[i] == board[i+3] == board[i+6] != "":
                if board[i] == player_mark:
                    return 10
                elif board[i] == opponent_mark:
                    return -10

        # 斜めのパターン
        if board[0] == board[4] == board[8] != "":
            if board[0] == player_mark:
                return 10
            elif board[0] == opponent_mark:
                return -10

        if board[2] == board[4] == board[6] != "":
            if board[2] == player_mark:
                return 10
            elif board[2] == opponent_mark:
                return -10

        return 0

    def _is_moves_left(self, board: List[str]) -> bool:
        """残りの手があるかどうかを判定します。

        Args:
            board: 現在の盤面

        Returns:
            残りの手があるかどうか
        """
        return "" in board 