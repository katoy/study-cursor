# 三目並べゲーム (Tic-tac-toe)

Cursorを使用して開発した三目並べゲームプロジェクトです。人間とコンピュータが対戦できる、GUIベースの三目並べゲームを実装しています。

## 特徴

- GUIインターフェース（tkinter使用）
- 先手/後手の選択が可能
- 3種類のAIアルゴリズム
  - ランダム選択
  - ミニマックス（アルファベータ枝刈り付き）
  - 完全戦略（データベース使用）
- 対戦履歴のデータベース保存

## 必要条件

- Python 3.8以上
- tkinter（GUIライブラリ）
- SQLite3（データベース）

## インストール

```bash
git clone https://github.com/yourusername/study-cursor.git
cd study-cursor
```

## 使用方法

```bash
python tictactoe_tk.py
```

## データベース設計

このプロジェクトでは2つのSQLiteデータベースを使用しています：

1. 完全戦略データベース（perfect_strategy.db）
   - 全ての可能な盤面とその最適手を格納
   - 完全な戦略を実現するための参照テーブル
   - テーブル構造：
     - board: 盤面の状態（例: "XO  O X  "）
     - next_mark: 次の手番のマーク（X/O）
     - best_move: 最適な手の位置（0-8）
     - score: 評価値（-1/0/1）

2. 対戦履歴データベース（game_history.db）
   - 各対戦の結果と手順を記録
   - 統計情報の生成に使用
   - テーブル構造：
     - game_id: ゲームID（自動採番）
     - played_at: 対戦日時
     - is_human_first: 人間が先手か
     - winner: 勝者（HUMAN/COMPUTER/DRAW）
     - moves: 手順履歴（JSON形式）

詳細なER図は `database/er_diagram.png` を参照してください。

## プロジェクト構成

```
.
├── tictactoe_tk.py      # メインゲームファイル
├── agents/              # AIエージェント
│   ├── base_agent.py    # 基底エージェントクラス
│   ├── minimax_agent.py # ミニマックスアルゴリズム
│   ├── perfect_agent.py # 完全戦略
│   └── random_agent.py  # ランダム選択
└── database/           # データベース関連
    ├── db_manager.py   # データベース管理
    ├── init_db.py      # 初期化スクリプト
    ├── er_diagram.mmd  # ER図（Mermaid形式）
    ├── er_diagram.png  # ER図（PNG形式）
    └── generate_all_states.py # 完全戦略データ生成
```

## ER図の生成

データベース設計のER図は[Mermaid](https://mermaid.js.org/)形式で作成しています。
ER図を更新する場合は以下の手順で行います：

1. `database/er_diagram.mmd`を編集
2. mermaid-cliをインストール
   ```bash
   npm init -y
   npm install @mermaid-js/mermaid-cli
   ```
3. PNGファイルを生成
   ```bash
   ./node_modules/.bin/mmdc -i database/er_diagram.mmd -o database/er_diagram.png -c database/config.json -b transparent -w 1200 -H 800
   ```

## 開発環境

- [Cursor](https://cursor.sh/) - AIパワードエディタ
- Python 3.8+
- Git

## ライセンス

このプロジェクトは[MITライセンス](LICENSE)の下で公開されています。
