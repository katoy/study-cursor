"""
データベースの初期化スクリプト

このスクリプトは、ゲーム履歴を保存するためのデータベースを初期化します。
"""

import sqlite3
from pathlib import Path


def init_database() -> None:
    """データベースを初期化し、必要なテーブルを作成します。"""
    # データベースディレクトリの作成
    db_dir = Path(__file__).parent
    db_dir.mkdir(exist_ok=True)
    
    # データベースファイルへの接続
    db_path = db_dir / "game_history.db"
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # ゲーム履歴テーブルの作成
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS game_history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        human_is_first BOOLEAN NOT NULL,
        algorithm TEXT NOT NULL,
        winner TEXT NOT NULL,
        moves TEXT NOT NULL
    )
    """)

    # インデックスの作成
    cursor.execute("""
    CREATE INDEX IF NOT EXISTS idx_algorithm 
    ON game_history(algorithm)
    """)

    conn.commit()
    conn.close()


if __name__ == "__main__":
    init_database()
    print("データベースの初期化が完了しました。") 