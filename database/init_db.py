"""
データベースの初期化スクリプト

このスクリプトは、三目並べゲームのデータベースを初期化します。
以下の2つのデータベースを作成します：

1. perfect_strategy.db
- 完全戦略AIのための盤面状態と最適手を管理
- board_statesテーブルを含む

2. game_history.db
- 対戦履歴を管理
- gamesテーブルを含む
"""

import sqlite3
from pathlib import Path


def init_database() -> None:
    """データベースを初期化します。"""
    # データベースディレクトリの作成
    db_dir = Path(__file__).parent
    db_dir.mkdir(exist_ok=True)

    # 完全戦略データベースの初期化
    perfect_strategy_path = db_dir / "perfect_strategy.db"
    with sqlite3.connect(perfect_strategy_path) as conn:
        cursor = conn.cursor()
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS board_states (
            board TEXT NOT NULL CHECK(length(board) = 9),
            next_mark TEXT NOT NULL CHECK(next_mark IN ('X', 'O')),
            best_move INTEGER CHECK(best_move BETWEEN 0 AND 8),
            score INTEGER NOT NULL CHECK(score BETWEEN -1 AND 1),
            PRIMARY KEY (board, next_mark)
        )
        """)
        conn.commit()


if __name__ == "__main__":
    init_database()
    print("完全戦略データベースの初期化が完了しました。")