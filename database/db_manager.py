"""
データベース管理モジュール

このモジュールは、三目並べゲームの対戦履歴と完全戦略データをSQLiteデータベースで管理します。

データベーススキーマ:

1. algorithms テーブル（アルゴリズムマスタ）
   - id: INTEGER PRIMARY KEY
     アルゴリズムの一意の識別子
   - name: TEXT NOT NULL UNIQUE
     アルゴリズム名（"ランダム"/"ミニマックス"/"完全戦略"）

2. game_results テーブル（対戦履歴）
   - id: INTEGER PRIMARY KEY AUTOINCREMENT
     対戦履歴の一意の識別子
   - played_at: TIMESTAMP NOT NULL
     対戦が行われた日時
   - algorithm_id: INTEGER NOT NULL
     使用したアルゴリズムのID（外部キー：algorithms.id）
   - human_is_first: BOOLEAN NOT NULL
     人間が先手かどうか
   - winner: CHAR(1) NOT NULL
     勝者（'H':人間, 'C':コンピュータ, 'D':引き分け）
   - INDEX idx_algorithm_date (algorithm_id, played_at)
     アルゴリズムと日付による検索用インデックス

3. moves テーブル（手順履歴）
   - game_id: INTEGER NOT NULL
     対戦履歴ID（外部キー：game_results.id）
   - move_number: INTEGER NOT NULL
     手番（1から始まる連番）
   - position: INTEGER NOT NULL
     配置位置（0-8）
   - mark: CHAR(1) NOT NULL
     マーク（'X' または 'O'）
   - PRIMARY KEY (game_id, move_number)
     ゲームIDと手番の複合主キー

4. perfect_moves テーブル（完全戦略データ）
   - state: CHAR(9) NOT NULL
     盤面状態（'-XO'の9文字）
   - next_player: CHAR(1) NOT NULL
     次の手番（'X' または 'O'）
   - best_move: INTEGER
     最適な手の位置（0-8、終局状態の場合はNULL）
   - score: INTEGER NOT NULL
     評価値（1:X勝ち, 0:引分, -1:O勝ち）
   - PRIMARY KEY (state, next_player)
     盤面状態と手番の複合主キー
"""

import sqlite3
from datetime import datetime
from typing import List, Optional, Tuple, Dict


class DatabaseManager:
    """データベース管理クラス"""

    def __init__(self, db_path: str = "game_history.db") -> None:
        """初期化メソッド。

        Args:
            db_path: データベースファイルのパス
        """
        self.db_path = db_path
        self._create_tables()
        self._initialize_algorithms()

    def _create_tables(self) -> None:
        """必要なテーブルを作成します。"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            # アルゴリズムマスタ
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS algorithms (
                    id INTEGER PRIMARY KEY,
                    name TEXT NOT NULL UNIQUE
                )
            ''')

            # 対戦履歴
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS game_results (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    played_at TIMESTAMP NOT NULL,
                    algorithm_id INTEGER NOT NULL,
                    human_is_first BOOLEAN NOT NULL,
                    winner CHAR(1) NOT NULL,
                    FOREIGN KEY (algorithm_id) REFERENCES algorithms(id)
                )
            ''')

            # インデックスの作成
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_algorithm_date
                ON game_results (algorithm_id, played_at)
            ''')

            # 手順履歴
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS moves (
                    game_id INTEGER NOT NULL,
                    move_number INTEGER NOT NULL,
                    position INTEGER NOT NULL,
                    mark CHAR(1) NOT NULL,
                    PRIMARY KEY (game_id, move_number),
                    FOREIGN KEY (game_id) REFERENCES game_results(id)
                )
            ''')

            # 完全戦略データ
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS perfect_moves (
                    state CHAR(9) NOT NULL,
                    next_player CHAR(1) NOT NULL,
                    best_move INTEGER,
                    score INTEGER NOT NULL,
                    PRIMARY KEY (state, next_player)
                )
            ''')

            conn.commit()

    def _initialize_algorithms(self) -> None:
        """アルゴリズムマスタを初期化します。"""
        algorithms = [
            (1, "ランダム"),
            (2, "ミニマックス"),
            (3, "完全戦略")
        ]

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.executemany(
                'INSERT OR IGNORE INTO algorithms (id, name) VALUES (?, ?)',
                algorithms
            )
            conn.commit()

    def save_game(self, human_is_first: bool, algorithm: str,
                winner: str, moves: List[Tuple[int, str]]) -> None:
        """ゲームの結果を保存します。

        Args:
            human_is_first: 人間が先手かどうか
            algorithm: 使用したアルゴリズム名
            winner: 勝者（"プレイヤー"/"コンピュータ"/"引き分け"）
            moves: 手順のリスト（(位置, マーク)のタプルのリスト）
        """
        winner_map = {
            "プレイヤー": "H",
            "コンピュータ": "C",
            "引き分け": "D"
        }

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            # アルゴリズムIDの取得
            cursor.execute('SELECT id FROM algorithms WHERE name = ?', (algorithm,))
            algorithm_id = cursor.fetchone()[0]

            # ゲーム結果の保存
            cursor.execute('''
                INSERT INTO game_results (
                    played_at, algorithm_id, human_is_first, winner
                ) VALUES (?, ?, ?, ?)
            ''', (
                datetime.now(),
                algorithm_id,
                human_is_first,
                winner_map[winner]
            ))

            game_id = cursor.lastrowid

            # 手順の保存
            move_data = [
                (game_id, i + 1, pos, mark)
                for i, (pos, mark) in enumerate(moves)
            ]
            cursor.executemany('''
                INSERT INTO moves (game_id, move_number, position, mark)
                VALUES (?, ?, ?, ?)
            ''', move_data)

            conn.commit()

    def get_game_history(self, limit: Optional[int] = None) -> List[Dict]:
        """ゲーム履歴を取得します。

        Args:
            limit: 取得する履歴の数（Noneの場合は全件取得）

        Returns:
            ゲーム履歴のリスト（辞書形式）
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            query = '''
                SELECT
                    r.id,
                    r.played_at,
                    a.name as algorithm,
                    r.human_is_first,
                    CASE r.winner
                        WHEN 'H' THEN 'プレイヤー'
                        WHEN 'C' THEN 'コンピュータ'
                        ELSE '引き分け'
                    END as winner
                FROM game_results r
                JOIN algorithms a ON r.algorithm_id = a.id
                ORDER BY r.played_at DESC
            '''

            if limit is not None:
                query += f" LIMIT {limit}"

            cursor.execute(query)
            columns = [desc[0] for desc in cursor.description]
            results = []

            for row in cursor.fetchall():
                game_dict = dict(zip(columns, row))

                # 手順の取得
                cursor.execute('''
                    SELECT position, mark
                    FROM moves
                    WHERE game_id = ?
                    ORDER BY move_number
                ''', (game_dict['id'],))

                game_dict['moves'] = cursor.fetchall()
                results.append(game_dict)

            return results

    def get_statistics(self) -> dict:
        """統計情報を取得します。

        Returns:
            統計情報を含む辞書
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            cursor.execute('''
                SELECT
                    a.name as algorithm,
                    COUNT(*) as total_games,
                    SUM(CASE WHEN r.winner = 'H' THEN 1 ELSE 0 END) as human_wins,
                    SUM(CASE WHEN r.winner = 'C' THEN 1 ELSE 0 END) as computer_wins,
                    SUM(CASE WHEN r.winner = 'D' THEN 1 ELSE 0 END) as draws
                FROM game_results r
                JOIN algorithms a ON r.algorithm_id = a.id
                GROUP BY a.name
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