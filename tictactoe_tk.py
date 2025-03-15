"""
三目並べゲーム (Tic-tac-toe)

このプログラムは、人間とコンピュータが対戦できる三目並べゲームを実装しています。
コンピュータの思考にはミニマックスアルゴリズムとアルファベータ枝刈りを使用しています。

特徴:
- GUIインターフェース（tkinter使用）
- 先手後手の選択が可能
- 最適な手を選択するAI
- 白背景に青のX、黒のOで表示

作者: Your Name
作成日: 2024/03/09
バージョン: 1.0

プロンプト例:
1. 基本機能の実装:
   "Pythonとtkinterを使用して、人間とコンピュータが対戦できる三目並べゲームを作成してください。
    以下の機能を実装してください：
    - 3x3のグリッドボード
    - プレイヤーは'X'、コンピュータは'O'を使用
    - クリックでプレイヤーが手を打てる
    - 勝敗判定機能
    - リセットボタン"

2. AIの実装:
   "三目並べゲームのコンピュータプレイヤーに、ミニマックスアルゴリズムとアルファベータ枝刈りを
    実装してください。以下の要件を満たすようにしてください：
    - 最適な手を選択できる
    - 探索の深さを考慮した評価関数
    - パフォーマンスを考慮した実装"

3. UI/UXの改善:
   "三目並べゲームのUIを改善してください：
    - ボタンのサイズを100x100ピクセルに統一
    - プレイヤーの'X'は青色、コンピュータの'O'は黒色で表示
    - 背景色を白に統一
    - 先手/後手を選択できるドロップダウンメニューの追加
    - ゲーム終了時の結果表示をダイアログで実装"

4. コードの整理:
   "三目並べゲームのコードを以下の方針でリファクタリングしてください：
    - データクラスを使用した設定の分離
    - 型ヒントの追加
    - メソッドの責務を明確に分割
    - ドキュメンテーションの充実
    - 定数の適切な管理
    - エラー処理の改善"
"""

from __future__ import annotations
from dataclasses import dataclass
import tkinter as tk
from tkinter import messagebox
import math
from typing import Dict, List, Optional, Any
import random


@dataclass
class GameConfig:
    """ゲームの設定を保持するデータクラス。

    Attributes:
        BOARD_SIZE: ボードの一辺のマス数
        CELL_SIZE: 各マスのサイズ（ピクセル）
        FONT_SIZE: フォントサイズ
        PLAYER_X: プレイヤーXのマーク
        PLAYER_O: プレイヤーOのマーク
        COLOR_X: プレイヤーXの色
        COLOR_O: プレイヤーOの色
        COLOR_BG: 背景色
        FONT_FAMILY: フォントファミリー
    """
    BOARD_SIZE: int = 3
    CELL_SIZE: int = 100
    FONT_SIZE: int = 36
    PLAYER_X: str = "X"
    PLAYER_O: str = "O"
    COLOR_X: str = "blue"
    COLOR_O: str = "black"
    COLOR_BG: str = "white"
    FONT_FAMILY: str = "Helvetica"


class TicTacToe:
    """三目並べゲームのメインクラス。

    このクラスは、GUIインターフェース、ゲームロジック、AIの実装を含みます。
    ミニマックスアルゴリズムとアルファベータ枝刈りを使用して、
    最適な手を選択するAIを実装しています。

    Attributes:
        config: ゲームの設定
        window: メインウィンドウ
        board: ゲームボードの状態
        buttons: ボードのボタンリスト
        human_is_first: 人間が先手かどうか
        first_player_var: 先手プレイヤーの選択値
        algorithm_var: アルゴリズム選択用の変数を追加
    """

    def __init__(self) -> None:
        """ゲームの初期化とGUIの設定を行います。"""
        self.config = GameConfig()
        self.window = tk.Tk()
        self.window.title("三目並べ")
        self.board: List[str] = [""] * (self.config.BOARD_SIZE ** 2)
        self.buttons: List[tk.Button] = []
        self.human_is_first = True
        self.first_player_var: tk.StringVar
        self.algorithm_var: tk.StringVar  # アルゴリズム選択用の変数を追加

        self._setup_gui()
        self.window.resizable(False, False)

    def _setup_gui(self) -> None:
        """GUIコンポーネントの設定を行います。"""
        self._create_menu_bar()  # メニューバーを追加
        main_frame = self._create_main_frame()
        self._create_player_selection(main_frame)
        self._create_algorithm_selection(main_frame)  # アルゴリズム選択を追加
        board_frame = self._create_board_frame(main_frame)
        self._create_game_board(board_frame)
        self._create_reset_button(main_frame)

    def _create_menu_bar(self) -> None:
        """メニューバーを作成します。"""
        menu_bar = tk.Menu(self.window)
        self.window.config(menu=menu_bar)

        # ゲームメニュー
        game_menu = tk.Menu(menu_bar, tearoff=0)
        menu_bar.add_cascade(label="ゲーム", menu=game_menu)
        game_menu.add_command(label="リセット", command=self.reset_game)
        game_menu.add_separator()
        game_menu.add_command(label="終了", command=self.window.quit)

    def _create_main_frame(self) -> tk.Frame:
        """メインフレームを作成します。

        Returns:
            作成されたメインフレーム
        """
        main_frame = tk.Frame(self.window)
        main_frame.pack(padx=10, pady=10)
        return main_frame

    def _create_board_frame(self, parent: tk.Frame) -> tk.Frame:
        """ゲームボードフレームを作成します。

        Args:
            parent: 親フレーム

        Returns:
            作成されたボードフレーム
        """
        board_frame = tk.Frame(parent, bg=self.config.COLOR_BG)
        board_frame.pack()
        return board_frame

    def _create_player_selection(self, parent: tk.Frame) -> None:
        """先手選択部分のGUIを作成します。

        Args:
            parent: 親フレーム
        """
        select_frame = tk.Frame(parent)
        select_frame.pack(pady=(0, 10))

        tk.Label(select_frame, text="先手: ").pack(side=tk.LEFT)
        self.first_player_var = tk.StringVar(value="人間")
        first_player_menu = tk.OptionMenu(
            select_frame,
            self.first_player_var,
            "人間",
            "コンピュータ",
            command=self.change_first_player
        )
        first_player_menu.pack(side=tk.LEFT)

    def _create_algorithm_selection(self, parent: tk.Frame) -> None:
        """アルゴリズム選択部分のGUIを作成します。

        Args:
            parent: 親フレーム
        """
        select_frame = tk.Frame(parent)
        select_frame.pack(pady=(0, 10))

        tk.Label(select_frame, text="アルゴリズム: ").pack(side=tk.LEFT)
        self.algorithm_var = tk.StringVar(value="ミニマックス")
        algorithm_menu = tk.OptionMenu(
            select_frame,
            self.algorithm_var,
            "ミニマックス",
            "ランダム"
        )
        algorithm_menu.pack(side=tk.LEFT)

    def _create_game_board(self, parent: tk.Frame) -> None:
        """ゲームボードのGUIを作成します。

        Args:
            parent: 親フレーム
        """
        for i in range(self.config.BOARD_SIZE):
            for j in range(self.config.BOARD_SIZE):
                cell_frame = self._create_cell_frame(parent, i, j)
                button = self._create_cell_button(cell_frame, i, j)
                self.buttons.append(button)

    def _create_cell_frame(self, parent: tk.Frame, row: int, col: int) -> tk.Frame:
        """マスのフレームを作成します。

        Args:
            parent: 親フレーム
            row: 行番号
            col: 列番号

        Returns:
            作成されたマスのフレーム
        """
        cell_frame = tk.Frame(
            parent,
            width=self.config.CELL_SIZE,
            height=self.config.CELL_SIZE,
            borderwidth=1,
            relief="solid",
            bg=self.config.COLOR_BG
        )
        cell_frame.grid(row=row, column=col, padx=2, pady=2)
        cell_frame.grid_propagate(False)
        return cell_frame

    def _create_cell_button(self, parent: tk.Frame, row: int, col: int) -> tk.Button:
        """マスのボタンを作成します。

        Args:
            parent: 親フレーム
            row: 行番号
            col: 列番号

        Returns:
            作成されたボタン
        """
        button = tk.Button(
            parent,
            text="",
            font=(self.config.FONT_FAMILY, self.config.FONT_SIZE),
            borderwidth=0,
            command=lambda r=row, c=col: self.button_click(r, c),
            **self._get_button_colors()
        )
        button.place(relx=0.5, rely=0.5, anchor="center")
        return button

    def _get_button_colors(self) -> Dict[str, str]:
        """ボタンの色設定を取得します。

        Returns:
            ボタンの色設定を含む辞書
        """
        return {
            'bg': self.config.COLOR_BG,
            'activebackground': self.config.COLOR_BG,
            'highlightbackground': self.config.COLOR_BG,
            'highlightcolor': self.config.COLOR_BG
        }

    def _create_reset_button(self, parent: tk.Frame) -> None:
        """リセットボタンを作成します。

        Args:
            parent: 親フレーム
        """
        reset_button = tk.Button(
            parent,
            text="リセット",
            command=self.reset_game,
            bg=self.config.COLOR_BG
        )
        reset_button.pack(pady=(10, 0))

    def change_first_player(self, *_args: Any) -> None:
        """先手プレイヤーの変更とゲームのリセットを行います。"""
        self.human_is_first = self.first_player_var.get() == "人間"
        self.reset_game()

    def button_click(self, row: int, col: int) -> None:
        """プレイヤーの手を処理します。

        Args:
            row: 行番号
            col: 列番号
        """
        index = self._get_index(row, col)
        if self.board[index] == "":
            self._make_move(index, is_human=True)
            if not self._check_game_end():
                self.computer_move()

    def _get_index(self, row: int, col: int) -> int:
        """行と列からインデックスを計算します。

        Args:
            row: 行番号
            col: 列番号

        Returns:
            一次元配列のインデックス
        """
        return row * self.config.BOARD_SIZE + col

    def _make_move(self, index: int, is_human: bool) -> None:
        """手を打つ処理を行います（人間とコンピュータ共通）。

        Args:
            index: 手を打つ位置のインデックス
            is_human: 人間の手かどうか
        """
        mark = self._get_player_mark(is_human)
        color = self._get_mark_color(mark)

        self.board[index] = mark
        self.buttons[index].config(
            text=mark,
            fg=color,
            disabledforeground=color,
            state='disabled',
            **self._get_button_colors()
        )
        self.window.update()

    def _get_mark_color(self, mark: str) -> str:
        """マークの色を取得します。

        Args:
            mark: プレイヤーのマーク（X/O）

        Returns:
            マークの色
        """
        return self.config.COLOR_X if mark == self.config.PLAYER_X else self.config.COLOR_O

    def _get_player_mark(self, is_human: bool) -> str:
        """プレイヤーのマーク（XまたはO）を取得します。

        Args:
            is_human: 人間の手かどうか

        Returns:
            プレイヤーのマーク
        """
        if is_human:
            return self.config.PLAYER_X if self.human_is_first else self.config.PLAYER_O
        return self.config.PLAYER_O if self.human_is_first else self.config.PLAYER_X

    def _check_game_end(self) -> bool:
        """ゲーム終了判定を行います。

        Returns:
            ゲームが終了したかどうか
        """
        winner = self.check_winner()
        if winner:
            self._show_winner_message(winner)
            return True
        if self._is_board_full():
            self._show_draw_message()
            return True
        return False

    def _is_board_full(self) -> bool:
        """盤面が埋まっているかどうかを判定します。

        Returns:
            盤面が埋まっているかどうか
        """
        return "" not in self.board

    def _show_winner_message(self, winner: str) -> None:
        """勝者メッセージを表示します。

        Args:
            winner: 勝者のマーク
        """
        winner_text = "プレイヤー" if winner == self._get_player_mark(True) else "コンピュータ"
        messagebox.showinfo("ゲーム終了", f"{winner_text}の勝ち!")
        self.reset_game()

    def _show_draw_message(self) -> None:
        """引き分けメッセージを表示します。"""
        messagebox.showinfo("ゲーム終了", "引き分け!")
        self.reset_game()

    def computer_move(self) -> None:
        """コンピュータの手を処理します。"""
        if self.algorithm_var.get() == "ミニマックス":
            move = self.find_best_move()
        else:  # ランダム
            empty_cells = [i for i, mark in enumerate(self.board) if mark == ""]
            if empty_cells:
                move = random.choice(empty_cells)
            else:
                move = -1

        if move != -1:
            self._make_move(move, is_human=False)
            self._check_game_end()

    def evaluate_board(self) -> int:
        """盤面を評価します。

        Returns:
            盤面の評価値（10: コンピュータの勝ち, -10: 人間の勝ち, 0: その他）
        """
        winner = self.check_winner()
        if winner == self._get_player_mark(False):
            return 10
        if winner == self._get_player_mark(True):
            return -10
        return 0

    def is_moves_left(self) -> bool:
        """残りの手があるかどうかを判定します。

        Returns:
            残りの手があるかどうか
        """
        return "" in self.board

    def minimax(self, depth: int, is_max: bool, alpha: float, beta: float) -> float:
        """ミニマックスアルゴリズム（アルファベータ枝刈り付き）を実行します。

        Args:
            depth: 探索の深さ
            is_max: 最大化プレイヤーのターンかどうか
            alpha: アルファ値
            beta: ベータ値

        Returns:
            評価値
        """
        score = self.evaluate_board()

        if score == 10:
            return score - depth
        if score == -10:
            return score + depth
        if not self.is_moves_left():
            return 0

        return self._maximize(depth, alpha, beta) if is_max else self._minimize(depth, alpha, beta)

    def _maximize(self, depth: int, alpha: float, beta: float) -> float:
        """最大化処理を行います。

        Args:
            depth: 探索の深さ
            alpha: アルファ値
            beta: ベータ値

        Returns:
            最大評価値
        """
        best = -math.inf
        for i, value in enumerate(self.board):
            if value == "":
                self.board[i] = self._get_player_mark(False)
                best = max(best, self.minimax(depth + 1, False, alpha, beta))
                self.board[i] = ""
                alpha = max(alpha, best)
                if beta <= alpha:
                    break
        return best

    def _minimize(self, depth: int, alpha: float, beta: float) -> float:
        """最小化処理を行います。

        Args:
            depth: 探索の深さ
            alpha: アルファ値
            beta: ベータ値

        Returns:
            最小評価値
        """
        best = math.inf
        for i, value in enumerate(self.board):
            if value == "":
                self.board[i] = self._get_player_mark(True)
                best = min(best, self.minimax(depth + 1, True, alpha, beta))
                self.board[i] = ""
                beta = min(beta, best)
                if beta <= alpha:
                    break
        return best

    def find_best_move(self) -> int:
        """最適な手を探索します。

        Returns:
            最適な手の位置（インデックス）
        """
        best_val = -math.inf
        best_move = -1
        alpha = -math.inf
        beta = math.inf

        for i, value in enumerate(self.board):
            if value == "":
                self.board[i] = self._get_player_mark(False)
                move_val = self.minimax(0, False, alpha, beta)
                self.board[i] = ""
                if move_val > best_val:
                    best_move = i
                    best_val = move_val
                alpha = max(alpha, best_val)

        return best_move

    def check_winner(self) -> Optional[str]:
        """勝者を判定します。

        Returns:
            勝者のマーク（勝者がいない場合はNone）
        """
        win_patterns = self._get_win_patterns()
        for pattern in win_patterns:
            if self._is_winning_pattern(pattern):
                return self.board[pattern[0]]
        return None

    def _get_win_patterns(self) -> List[List[int]]:
        """勝利パターンのリストを取得します。

        Returns:
            勝利パターンのリスト
        """
        size = self.config.BOARD_SIZE
        # 横のパターン
        rows = [[i * size + j for j in range(size)] for i in range(size)]
        # 縦のパターン
        cols = [[i + j * size for j in range(size)] for i in range(size)]
        # 斜めのパターン
        diag1 = [[i * (size + 1) for i in range(size)]]
        diag2 = [[i * (size - 1) for i in range(1, size + 1)]]
        return rows + cols + diag1 + diag2

    def _is_winning_pattern(self, pattern: List[int]) -> bool:
        """指定したパターンが勝利条件を満たすかどうかを判定します。

        Args:
            pattern: 判定するパターン

        Returns:
            勝利条件を満たすかどうか
        """
        return (self.board[pattern[0]] != "" and
                all(self.board[pattern[0]] == self.board[i] for i in pattern[1:]))

    def reset_game(self) -> None:
        """ゲームをリセットします。"""
        self.board = [""] * (self.config.BOARD_SIZE ** 2)
        for button in self.buttons:
            button.config(
                text="",
                state='normal',
                **self._get_button_colors()
            )
        if not self.human_is_first:
            self.computer_move()

    def run(self) -> None:
        """ゲームを実行します。"""
        self.window.mainloop()


def main() -> None:
    """メイン関数。"""
    game = TicTacToe()
    game.run()


if __name__ == "__main__":
    main()
