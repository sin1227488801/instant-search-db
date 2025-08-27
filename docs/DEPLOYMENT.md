# デプロイメントガイド

## ローカル開発環境

### 前提条件
- Python 3.9以上
- Git

### セットアップ手順

```bash
# 1. リポジトリのクローン
git clone <repository-url>
cd instant-search-db

# 2. 仮想環境の作成
python -m venv venv

# 3. 仮想環境の有効化
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate

# 4. 依存関係のインストール
pip install -r requirements.txt

# 5. アプリケーションの起動
python -m instant_search_db
```

### アクセス
- URL: http://127.0.0.1:5000
- 検索API: http://127.0.0.1:5000/search?q=キーワード

## Docker環境

### 前提条件
- Docker
- Docker Compose

### 起動手順

```bash
# 1. Docker Composeでビルド・起動
docker-compose up --build

# 2. バックグラウンド実行
docker-compose up -d --build
```

### アクセス
- URL: http://localhost:5000

## テスト実行

```bash
# 単体テスト
pytest tests/ -v

# カバレッジ付きテスト
pytest tests/ --cov=instant_search_db

# 手動テスト
python test_manual.py
```

## 本番環境デプロイ

### 環境変数
```bash
export FLASK_ENV=production
export FLASK_DEBUG=False
```

### 推奨構成
- Webサーバー: Nginx
- WSGIサーバー: Gunicorn
- データベース: SQLite (小規模) / PostgreSQL (大規模)

### Gunicorn起動例
```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 "instant_search_db:create_app()"
```