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
- 統計情報の表示機能

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
    └── generate_all_states.py # 完全戦略データ生成

```

## 開発環境

- [Cursor](https://cursor.sh/) - AIパワードエディタ
- Python 3.8+
- Git

## ライセンス

このプロジェクトは[MITライセンス](LICENSE)の下で公開されています。

## 作者

[Your Name]
