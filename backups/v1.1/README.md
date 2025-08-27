# instant-search-db

ローグライクゲーム用リアルタイム検索データベース

## 🚀 最も簡単な起動方法

### 方法1: Docker（推奨・最も確実）

```bash
# 1. プロジェクトディレクトリに移動
cd instant-search-db

# 2. Docker起動（これだけ！）
docker-compose up --build

# 3. ブラウザでアクセス
# http://localhost:5000
```

**停止方法:**
```bash
# Ctrl+C で停止、または
docker-compose down
```

### 方法2: Python直接実行

```bash
# 1. プロジェクトディレクトリに移動
cd instant-search-db

# 2. 依存関係インストール
pip install flask

# 3. アプリケーション起動
python run_app.py

# 4. ブラウザでアクセス
# http://localhost:5000
```

### 方法3: 自動セットアップスクリプト

```bash
# Windows (PowerShell)
.\scripts\setup.ps1

# Mac/Linux
./scripts/setup.sh
```

## 🧪 動作確認

アプリケーション起動後、ブラウザで http://localhost:5000 にアクセスして以下を試してください：

- 検索ボックスに「武器」と入力 → 5件の武器が表示
- 「つるはし」と入力 → 2件のつるはしが表示  
- 「壺」と入力 → 2件の壺が表示

## ❗ トラブルシューティング

### Dockerが使えない場合

**1. Dockerがインストールされていない**
- [Docker Desktop](https://www.docker.com/products/docker-desktop/) をインストール

**2. ポート5000が使用中**
```bash
# 使用中のプロセスを確認
netstat -ano | findstr :5000

# プロセスを終了（WindowsのPowerShell）
taskkill /PID <プロセスID> /F
```

### Python実行でエラーが出る場合

**1. Pythonがインストールされていない**
- Windows: [python.org](https://www.python.org/downloads/) からダウンロード
- Mac: `brew install python3`
- Ubuntu: `sudo apt install python3 python3-pip`

**2. Flaskがインストールされていない**
```bash
pip install flask
```

**3. 仮想環境を使いたい場合**
```bash
# 仮想環境作成・有効化
python -m venv venv

# Windows
venv\Scripts\activate

# Mac/Linux  
source venv/bin/activate

# 依存関係インストール
pip install -r requirements.txt

# アプリ起動
python run_app.py
```

## 📋 詳細な起動手順（上記で動かない場合）

### Docker使用（最も確実）

```bash
# 1. Dockerがインストールされているか確認
docker --version
docker-compose --version

# 2. プロジェクトディレクトリで実行
docker-compose up --build

# 3. ブラウザで http://localhost:5000 にアクセス
```

### Python仮想環境使用

```bash
# 1. 仮想環境作成
python -m venv venv

# 2. 仮想環境有効化
# Windows PowerShell
venv\Scripts\Activate.ps1
# Windows CMD  
venv\Scripts\activate.bat
# Mac/Linux
source venv/bin/activate

# 3. 依存関係インストール
pip install -r requirements.txt

# 4. アプリ起動
python -m instant_search_db
# または
python run_app.py

# 5. ブラウザで http://localhost:5000 にアクセス
```

## 📖 プロジェクト概要

ローグライクゲームのアイテム情報をリアルタイム検索できるWebアプリケーションです。

### 主な機能
- リアルタイム検索（入力と同時に検索結果を表示）
- 武器、盾、壺、草・種などのアイテム情報を検索
- 日本語対応の全文検索

### 技術スタック
- **フロントエンド**: HTML/CSS/JavaScript
- **バックエンド**: Flask（Python）
- **データベース**: SQLite + FTS5（全文検索）
- **コンテナ**: Docker

## 🛠️ 開発者向け情報

### プロジェクト構造
```
instant-search-db/
├── instant_search_db/          # メインアプリケーション
│   ├── __init__.py            # Flaskアプリ設定
│   ├── __main__.py            # モジュール実行用
│   ├── models.py              # データベース操作
│   └── routes.py              # API エンドポイント
├── templates/                 # HTMLテンプレート
│   └── index.html             # メインページ
├── static/                    # CSS/JS
│   └── style.css              # スタイルシート
├── scripts/                   # セットアップスクリプト
│   ├── setup.ps1              # Windows用統合セットアップ
│   ├── setup.sh               # Mac/Linux用統合セットアップ
│   └── (その他のスクリプト)
├── docs/                      # ドキュメント
│   ├── CHANGELOG.md           # 変更履歴
│   ├── DEPLOYMENT.md          # デプロイ手順
│   └── (その他のドキュメント)
├── tests/                     # テストファイル
│   ├── __init__.py
│   └── test_app.py            # アプリケーションテスト
├── .github/                   # GitHub Actions設定
├── .vscode/                   # VSCode設定
├── run_app.py                 # アプリ起動スクリプト
├── requirements.txt           # Python依存関係
├── Dockerfile                 # Docker設定
├── docker-compose.yml         # Docker Compose設定
├── database.db                # サンプルデータベース
├── .gitignore                 # Git除外設定
└── README.md                  # このファイル
```

### API仕様
```
GET /search?q=キーワード
```

**レスポンス例:**
```json
[
  {
    "id": 1,
    "name": "武器 つるはし", 
    "description": "攻 1 買 240 補正 12 売 100..."
  }
]
```

### 起動方法まとめ

| 方法 | コマンド | 推奨度 |
|------|----------|--------|
| Docker | `docker-compose up --build` | ⭐⭐⭐ 最も確実 |
| Python直接 | `python run_app.py` | ⭐⭐ 簡単 |
| 仮想環境 | `python -m instant_search_db` | ⭐ 開発向け |