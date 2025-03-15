"""
すべての三目並べの戦況を生成し、データベースに保存するスクリプト。

このスクリプトは、可能なすべての盤面とその評価値を計算し、
データベースに保存します。これにより、完全な戦略を実現できます。
"""

import sqlite3
from pathlib import Path
from typing import List, Tuple, Optional
from itertools import product


def create_states_table(cursor: sqlite3.Cursor) -> None:
    """盤面状態を保存するテーブルを作成します。"""
    cursor.execute("""
    DROP TABLE IF EXISTS board_states
    """)
    
    cursor.execute("""
    CREATE TABLE board_states (
        state_id TEXT PRIMARY KEY,
        board_state TEXT NOT NULL,
        next_player TEXT NOT NULL,
        best_move INTEGER,
        evaluation INTEGER NOT NULL,
        is_terminal BOOLEAN NOT NULL
    )
    """)


def get_win_patterns() -> List[List[int]]:
    """勝利パターンのリストを取得します。"""
    size = 3
    # 横のパターン
    rows = [[i * size + j for j in range(size)] for i in range(size)]
    # 縦のパターン
    cols = [[i + j * size for j in range(size)] for i in range(size)]
    # 斜めのパターン
    diag1 = [[i * (size + 1) for i in range(size)]]
    diag2 = [[i * (size - 1) for i in range(1, size + 1)]]
    return rows + cols + diag1 + diag2


def check_winner(board: List[str]) -> Optional[str]:
    """勝者を判定します。"""
    win_patterns = get_win_patterns()
    for pattern in win_patterns:
        if (board[pattern[0]] != "-" and
            all(board[pattern[0]] == board[i] for i in pattern[1:])):
            return board[pattern[0]]
    return None


def evaluate_state(board: List[str], next_player: str) -> Tuple[int, Optional[int]]:
    """盤面を評価し、最適な手を決定します。

    Returns:
        Tuple[評価値, 最適な手のインデックス]
    """
    winner = check_winner(board)
    if winner == "X":
        return 1, None
    elif winner == "O":
        return -1, None
    elif "-" not in board:
        return 0, None

    moves = []
    for i, cell in enumerate(board):
        if cell == "-":
            board[i] = next_player
            next_mark = "O" if next_player == "X" else "X"
            eval_val, _ = evaluate_state(board, next_mark)
            moves.append((eval_val, i))
            board[i] = "-"

    if next_player == "X":
        best_eval = max(moves, key=lambda x: x[0])
        return best_eval[0], best_eval[1]
    else:
        best_eval = min(moves, key=lambda x: x[0])
        return best_eval[0], best_eval[1]


def generate_state_id(board: List[str], next_player: str) -> str:
    """盤面状態のユニークIDを生成します。"""
    return f"{''.join(board)}_{next_player}"


def is_valid_board(board: List[str]) -> bool:
    """盤面が有効かどうかを判定します。"""
    x_count = board.count("X")
    o_count = board.count("O")
    return x_count - o_count in [0, 1]  # Xの数はOの数と同じか1つ多い


def generate_all_states() -> None:
    """すべての可能な盤面状態を生成し、データベースに保存します。"""
    db_path = Path(__file__).parent / "game_history.db"
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # テーブルの作成
    create_states_table(cursor)

    # すべての可能な盤面を生成
    marks = ["-", "X", "O"]
    processed_states = set()
    count = 0

    for board_tuple in product(marks, repeat=9):
        board = list(board_tuple)
        
        # 無効な盤面をスキップ
        if not is_valid_board(board):
            continue

        # 勝者がいる場合はその時点で終了
        winner = check_winner(board)
        if winner:
            is_terminal = True
            evaluation = 1 if winner == "X" else -1
            best_move = None
        else:
            is_terminal = "-" not in board
            if is_terminal:
                evaluation = 0
                best_move = None
            else:
                # 次のプレイヤーを決定
                x_count = board.count("X")
                o_count = board.count("O")
                next_player = "O" if x_count > o_count else "X"
                
                # 状態を評価
                evaluation, best_move = evaluate_state(board.copy(), next_player)
                
                # 状態を保存
                state_id = generate_state_id(board, next_player)
                if state_id not in processed_states:
                    cursor.execute("""
                    INSERT INTO board_states 
                    (state_id, board_state, next_player, best_move, evaluation, is_terminal)
                    VALUES (?, ?, ?, ?, ?, ?)
                    """, (
                        state_id,
                        str(board),
                        next_player,
                        best_move,
                        evaluation,
                        is_terminal
                    ))
                    processed_states.add(state_id)
                    count += 1

                    # 定期的にコミット
                    if count % 1000 == 0:
                        conn.commit()
                        print(f"進捗: {count}状態を処理済み")

    conn.commit()
    conn.close()
    print(f"完了: 合計{count}状態を保存しました。")


if __name__ == "__main__":
    generate_all_states() 