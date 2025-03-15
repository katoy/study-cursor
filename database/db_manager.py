"""
データベース管理モジュール

このモジュールは、三目並べゲームの対戦履歴と完全戦略データをSQLiteデータベースで管理します。

データベーススキーマ:

1. game_history テーブル（対戦履歴）
   - id: INTEGER PRIMARY KEY AUTOINCREMENT
     対戦履歴の一意の識別子
   - played_at: TIMESTAMP NOT NULL
     対戦が行われた日時
   - human_is_first: BOOLEAN NOT NULL
     人間が先手かどうか（true: 人間が先手、false: コンピュータが先手）
   - algorithm: TEXT NOT NULL
     使用したアルゴリズム（"ランダム"/"ミニマックス"/"完全戦略"）
   - winner: TEXT NOT NULL
     勝者（"プレイヤー"/"コンピュータ"/"引き分け"）
   - moves: TEXT NOT NULL
     手順の記録（[(位置, マーク), ...]の文字列形式）

2. board_states テーブル（完全戦略用の盤面データ）
   - state_id: TEXT PRIMARY KEY
     盤面状態の一意の識別子（"盤面文字列_次の手番"形式）
   - board_state: TEXT NOT NULL
     盤面の状態（空きマスは"-"で表現）
   - next_player: TEXT NOT NULL
     次の手番（"X" または "O"）
   - best_move: INTEGER
     最適な手の位置（0-8、終局状態の場合はNULL）
   - evaluation: INTEGER NOT NULL
     状態の評価値（1: Xの勝ち、0: 引分、-1: Oの勝ち）
   - is_terminal: BOOLEAN NOT NULL
     終局状態かどうか
"""

import sqlite3
from datetime import datetime
from typing import List, Optional, Tuple


class DatabaseManager:
    """データベース管理クラス。

    このクラスは、対戦履歴の保存と取得を担当します。
    SQLiteデータベースを使用して、以下の情報を管理します：
    - 対戦日時
    - プレイヤーの手番（先手/後手）
    - 使用したAIアルゴリズム
    - 勝者
    - 対戦内容（手順）
    """

    def __init__(self, db_path: str = "game_history.db") -> None:
        """初期化メソッド。

        Args:
            db_path: データベースファイルのパス
        """
        self.db_path = db_path
        self._create_tables()

    def _create_tables(self) -> None:
        """必要なテーブルを作成します。"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            # ゲーム履歴テーブル
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS game_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    played_at TIMESTAMP NOT NULL,
                    human_is_first BOOLEAN NOT NULL,
                    algorithm TEXT NOT NULL,
                    winner TEXT NOT NULL,
                    moves TEXT NOT NULL
                )
            ''')

            conn.commit()

    def save_game(self, human_is_first: bool, algorithm: str,
                winner: str, moves: List[Tuple[int, str]]) -> None:
        """ゲームの結果を保存します。

        Args:
            human_is_first: 人間が先手かどうか
            algorithm: 使用したアルゴリズム
            winner: 勝者（"プレイヤー"/"コンピュータ"/"引き分け"）
            moves: 手順のリスト（(位置, マーク)のタプルのリスト）
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            cursor.execute('''
                INSERT INTO game_history (
                    played_at, human_is_first, algorithm, winner, moves
                ) VALUES (?, ?, ?, ?, ?)
            ''', (
                datetime.now(),
                human_is_first,
                algorithm,
                winner,
                str(moves)  # 手順をテキストとして保存
            ))

            conn.commit()

    def get_game_history(self, limit: Optional[int] = None) -> List[Tuple]:
        """ゲーム履歴を取得します。

        Args:
            limit: 取得する履歴の数（Noneの場合は全件取得）

        Returns:
            ゲーム履歴のリスト
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            query = "SELECT * FROM game_history ORDER BY played_at DESC"
            if limit is not None:
                query += f" LIMIT {limit}"

            cursor.execute(query)
            return cursor.fetchall()

    def get_statistics(self) -> dict:
        """統計情報を取得します。

        Returns:
            統計情報を含む辞書
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            # アルゴリズムごとの勝敗数
            cursor.execute('''
                SELECT
                    algorithm,
                    COUNT(*) as total_games,
                    SUM(CASE WHEN winner = 'プレイヤー' THEN 1 ELSE 0 END) as human_wins,
                    SUM(CASE WHEN winner = 'コンピュータ' THEN 1 ELSE 0 END) as computer_wins,
                    SUM(CASE WHEN winner = '引き分け' THEN 1 ELSE 0 END) as draws
                FROM game_history
                GROUP BY algorithm
            ''')

            stats = {}
            for row in cursor.fetchall():
                algorithm, total, human_wins, computer_wins, draws = row
                stats[algorithm] = {
                    'total_games': total,
                    'human_wins': human_wins,
                    'computer_wins': computer_wins,
                    'draws': draws,
                    'human_win_rate': (human_wins / total) if total > 0 else 0
                }

            return stats