"""
データベース管理モジュール

このモジュールは、三目並べゲームのデータベースを管理します。

データベース構造:

1. perfect_strategy.db
完全戦略AIのための盤面状態と最適手を管理するデータベース

[board_states]
+------------+--------------+------------+-------------------------------------------+
| カラム名    | 型           | 制約       | 説明                                      |
+------------+--------------+------------+-------------------------------------------+
| board      | TEXT        | PK        | 盤面状態 ('-XO'の9文字)                    |
| next_mark  | TEXT        | PK        | 次の手番 ('X' or 'O')                     |
| best_move  | INTEGER     | -         | 最適な手の位置 (0-8, 終局状態はNULL)       |
| score      | INTEGER     | NOT NULL  | 評価値 (1:X勝ち, 0:引分, -1:O勝ち)        |
+------------+--------------+------------+-------------------------------------------+

制約:
- PRIMARY KEY (board, next_mark)
- CHECK (length(board) = 9)
- CHECK (next_mark IN ('X', 'O'))
- CHECK (best_move BETWEEN 0 AND 8)
- CHECK (score BETWEEN -1 AND 1)

2. game_history.db
対戦履歴を管理するデータベース

[games]
+---------------+-----------+------------+-------------------------------------------+
| カラム名       | 型        | 制約       | 説明                                      |
+---------------+-----------+------------+-------------------------------------------+
| game_id       | INTEGER   | PK        | 対戦ID                                    |
| played_at     | TIMESTAMP | NOT NULL  | 対戦日時                                  |
| is_human_first| BOOLEAN   | NOT NULL  | 先手/後手 (true:人間が先手)               |
| winner        | TEXT      | NOT NULL  | 勝者 ('HUMAN','COMPUTER','DRAW')         |
| moves         | TEXT      | NOT NULL  | 手順（JSON形式）                          |
+---------------+-----------+------------+-------------------------------------------+

制約:
- PRIMARY KEY (game_id)
- CHECK (winner IN ('HUMAN', 'COMPUTER', 'DRAW'))

最適化のポイント:
1. 自然な複合主キー (board, next_mark) を使用
2. 必要最小限のカラムと制約のみを保持
3. 対戦履歴は別データベースで管理し、アクセスパターンを分離
"""

import sqlite3
import json
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict


class PerfectStrategyDB:
    """完全戦略データベース管理クラス"""

    def __init__(self) -> None:
        """初期化メソッド。"""
        self.db_path = Path(__file__).parent / "perfect_strategy.db"
        self._create_tables()

    def _create_tables(self) -> None:
        """必要なテーブルを作成します。"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            cursor.execute('''
                CREATE TABLE IF NOT EXISTS board_states (
                    board TEXT NOT NULL CHECK(length(board) = 9),
                    next_mark TEXT NOT NULL CHECK(next_mark IN ('X', 'O')),
                    best_move INTEGER CHECK(best_move BETWEEN 0 AND 8),
                    score INTEGER NOT NULL CHECK(score BETWEEN -1 AND 1),
                    PRIMARY KEY (board, next_mark)
                )
            ''')

            conn.commit()

    def get_best_move(self, board: str, next_mark: str) -> Optional[int]:
        """最適な手を取得します。

        Args:
            board: 現在の盤面（'-XO'の9文字）
            next_mark: 次の手番のマーク（'X'または'O'）

        Returns:
            最適な手の位置（0-8）、見つからない場合はNone
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT best_move
                FROM board_states
                WHERE board = ? AND next_mark = ?
            ''', (board, next_mark))
            result = cursor.fetchone()
            return result[0] if result else None


class DatabaseManager:
    """対戦履歴データベース管理クラス"""

    def __init__(self) -> None:
        """初期化メソッド。"""
        self.db_path = Path(__file__).parent / "game_history.db"
        self._create_tables()

    def _create_tables(self) -> None:
        """必要なテーブルを作成します。"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            cursor.execute('''
                CREATE TABLE IF NOT EXISTS games (
                    game_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    played_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    is_human_first BOOLEAN NOT NULL,
                    winner TEXT NOT NULL CHECK(winner IN ('HUMAN', 'COMPUTER', 'DRAW')),
                    moves TEXT NOT NULL
                )
            ''')

            conn.commit()

    def save_game(self, is_human_first: bool, winner: str, moves: List[Dict]) -> None:
        """対戦結果を保存します。

        Args:
            is_human_first: 人間が先手かどうか
            winner: 勝者（'HUMAN', 'COMPUTER', 'DRAW'のいずれか）
            moves: 手順のリスト
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO games (is_human_first, winner, moves)
                VALUES (?, ?, ?)
            ''', (is_human_first, winner, json.dumps(moves)))
            conn.commit()

    def get_game_history(self, limit: int = 10) -> List[Dict]:
        """対戦履歴を取得します。

        Args:
            limit: 取得する履歴の最大数

        Returns:
            対戦履歴のリスト
        """
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute('''
                SELECT *
                FROM games
                ORDER BY played_at DESC
                LIMIT ?
            ''', (limit,))
            return [dict(row) for row in cursor.fetchall()]

    def get_statistics(self) -> Dict:
        """対戦成績の統計情報を取得します。

        Returns:
            Dict: 以下の統計情報を含む辞書
            - total_games: 総対戦数
            - human_wins: 人間の勝利数
            - computer_wins: コンピュータの勝利数
            - draws: 引き分け数
            - human_win_rate: 人間の勝率（%）
            - recent_results: 直近の対戦結果（最大5件）
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # 総対戦数と勝敗数を取得
            cursor.execute('''
                SELECT 
                    COUNT(*) as total_games,
                    SUM(CASE WHEN winner = 'HUMAN' THEN 1 ELSE 0 END) as human_wins,
                    SUM(CASE WHEN winner = 'COMPUTER' THEN 1 ELSE 0 END) as computer_wins,
                    SUM(CASE WHEN winner = 'DRAW' THEN 1 ELSE 0 END) as draws
                FROM games
            ''')
            row = cursor.fetchone()
            total_games = row[0] or 0
            human_wins = row[1] or 0
            computer_wins = row[2] or 0
            draws = row[3] or 0

            # 直近の対戦結果を取得
            cursor.execute('''
                SELECT 
                    winner,
                    is_human_first,
                    played_at
                FROM games
                ORDER BY played_at DESC
                LIMIT 5
            ''')
            recent_results = [
                {
                    'winner': row[0],
                    'is_human_first': bool(row[1]),
                    'played_at': row[2]
                }
                for row in cursor.fetchall()
            ] or []  # 対戦記録がない場合は空リストを返す

            # 勝率を計算（総対戦数が0の場合は0%）
            human_win_rate = (human_wins / total_games * 100) if total_games > 0 else 0

            return {
                'total_games': total_games,
                'human_wins': human_wins,
                'computer_wins': computer_wins,
                'draws': draws,
                'human_win_rate': round(human_win_rate, 1),
                'recent_results': recent_results
            }