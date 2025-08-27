# instant-search-db

汎用リアルタイム検索データベースシステム v2.0

> **v2.0の新機能**: 設定ファイルによる完全カスタマイズ対応！ゲーム、商品カタログ、ドキュメント管理など、あらゆる用途に対応可能な汎用システムに進化しました。

## 🌟 システム概要

このシステムは、**設定ファイルだけでカスタマイズ可能**な汎用データベース検索システムです。コードを変更することなく、様々な用途に対応できます。

### ✨ 主な特徴

- **🔧 設定ベース**: JSONファイルでカテゴリ、フィールド、UIを完全カスタマイズ
- **⚡ 高速検索**: SQLite FTS5による高性能全文検索
- **🎨 柔軟なUI**: テーマ、レイアウト、アイコンを自由に設定
- **📊 多様な用途**: ゲーム、商品、文書、在庫など幅広い用途に対応
- **🌐 多言語対応**: 日本語、英語をはじめとする多言語サポート
- **🐳 簡単デプロイ**: Docker対応で環境構築が簡単

### 🎯 対応用途

| 用途 | 説明 | 設定例 |
|------|------|--------|
| **ゲームアイテム** | RPG/ローグライクゲームのアイテム管理 | `game-database.json` |
| **商品カタログ** | ECサイトや商品データベース | `product-catalog.json` |
| **ドキュメント管理** | 企業の文書管理システム | `document-library.json` |
| **在庫管理** | 倉庫や製造業の在庫追跡 | `inventory-system.json` |
| **その他** | カスタム設定で任意の用途に対応 | 独自設定ファイル |

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

### デフォルト（ゲーム）設定での確認
- 検索ボックスに「武器」と入力 → 武器カテゴリのアイテムが表示
- 「つるはし」と入力 → つるはし系のアイテムが表示  
- 「壺」と入力 → 壺カテゴリのアイテムが表示

### 設定システムの確認
- **設定API**: http://localhost:5000/api/config で現在の設定を確認
- **ヘルスチェック**: http://localhost:5000/api/system/health でシステム状態を確認
- **設定検証**: http://localhost:5000/api/config/validate で設定ファイルの妥当性を確認

### 他の用途での試用

#### 🛍️ 商品カタログとして使用
```bash
# 商品カタログ設定に切り替え
cp config/examples/product-catalog.json config/categories.json
cp config/examples/product-catalog-sample.csv data/items.csv
docker-compose restart
# → 電子機器、衣類、本などの商品カテゴリで検索可能
```

#### 📚 ドキュメント管理として使用
```bash
# ドキュメント管理設定に切り替え
cp config/examples/document-library.json config/categories.json
cp config/examples/document-library-sample.csv data/items.csv
docker-compose restart
# → ポリシー、マニュアル、レポートなどの文書カテゴリで検索可能
```

#### 📦 在庫管理として使用
```bash
# 在庫管理設定に切り替え
cp config/examples/inventory-system.json config/categories.json
cp config/examples/inventory-system-sample.csv data/items.csv
docker-compose restart
# → 原材料、完成品、工具などの在庫カテゴリで検索可能
```

### 🔧 カスタム設定の作成

独自の用途に合わせて設定をカスタマイズ：

```bash
# 1. 設定ファイルをコピーして編集
cp config/examples/game-database.json config/my-custom-config.json

# 2. 設定を個別ファイルに分割
# categories.json, fields.json, ui.json を編集

# 3. データファイルを準備
# data/items.csv を用途に合わせて作成

# 4. システム再起動
docker-compose restart
```

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

## 📖 システムアーキテクチャ

汎用的なデータベース検索システムとして設計されており、設定ファイルの変更だけで様々な用途に対応できます。

### 🏗️ アーキテクチャ概要

```
┌─────────────────────────────────────────────────────────────┐
│                    設定レイヤー                              │
├─────────────────────────────────────────────────────────────┤
│  config/                                                    │
│  ├── categories.json    # カテゴリ定義とアイコン            │
│  ├── fields.json        # データフィールドマッピング        │
│  ├── ui.json            # UI設定とテーマ                    │
│  └── examples/          # 用途別設定例                      │
└─────────────────────────────────────────────────────────────┘
┌─────────────────────────────────────────────────────────────┐
│                  アプリケーションレイヤー                    │
├─────────────────────────────────────────────────────────────┤
│  instant_search_db/                                         │
│  ├── config_manager.py  # 設定管理とバリデーション          │
│  ├── models.py          # データモデルと検索エンジン        │
│  ├── routes.py          # API エンドポイント               │
│  ├── error_handler.py   # エラーハンドリング               │
│  └── logging_system.py  # ログとパフォーマンス監視          │
└─────────────────────────────────────────────────────────────┘
┌─────────────────────────────────────────────────────────────┐
│                      データレイヤー                          │
├─────────────────────────────────────────────────────────────┤
│  data/                                                      │
│  ├── items.csv          # メインデータファイル              │
│  ├── schema.json        # データ検証スキーマ                │
│  └── backups/           # 自動バックアップ                  │
└─────────────────────────────────────────────────────────────┘
```

### 🔧 主な機能

#### コア機能
- **リアルタイム検索**: 入力と同時に検索結果を表示
- **全文検索**: SQLite FTS5による高性能検索
- **カテゴリフィルタ**: 設定可能なカテゴリによる絞り込み
- **レスポンシブUI**: モバイル・デスクトップ対応

#### v2.0の新機能
- **設定ベースカスタマイズ**: コード変更なしでの完全カスタマイズ
- **多用途対応**: ゲーム、商品、文書、在庫など幅広い用途
- **エラーハンドリング**: 包括的なエラー管理と復旧機能
- **パフォーマンス監視**: 詳細なログとメトリクス収集
- **設定検証**: 自動的な設定ファイル検証とフォールバック

### 🛠️ 技術スタック

| レイヤー | 技術 | 説明 |
|----------|------|------|
| **フロントエンド** | HTML/CSS/JavaScript | レスポンシブWebUI |
| **バックエンド** | Flask (Python) | 軽量Webフレームワーク |
| **データベース** | SQLite + FTS5 | 高性能全文検索 |
| **設定管理** | JSON + JSONSchema | 構造化設定とバリデーション |
| **コンテナ** | Docker + Docker Compose | 簡単デプロイメント |
| **監視** | カスタムログシステム | パフォーマンス監視 |

## 🛠️ 開発者向け情報

### 📁 プロジェクト構造
```
instant-search-db/
├── 📁 config/                     # 🆕 設定ファイル（v2.0の核心）
│   ├── categories.json            # カテゴリ定義とアイコン設定
│   ├── fields.json                # データフィールドマッピング
│   ├── ui.json                    # UI設定とテーマ
│   ├── 📁 examples/               # 用途別設定例
│   │   ├── game-database.json     # ゲーム用設定（v1.1互換）
│   │   ├── product-catalog.json   # 商品カタログ用設定
│   │   ├── document-library.json  # 文書管理用設定
│   │   └── inventory-system.json  # 在庫管理用設定
│   └── 📁 schemas/                # 設定検証用スキーマ
├── 📁 instant_search_db/          # メインアプリケーション
│   ├── __init__.py                # Flaskアプリ設定（設定システム統合）
│   ├── __main__.py                # モジュール実行用
│   ├── models.py                  # データベース操作
│   ├── routes.py                  # API エンドポイント
│   ├── config_manager.py          # 🆕 設定管理システム
│   ├── error_handler.py           # 🆕 エラーハンドリング
│   ├── logging_system.py          # 🆕 ログとパフォーマンス監視
│   └── data_manager.py            # 🆕 データ管理とバリデーション
├── 📁 data/                       # データファイル
│   ├── items.csv                  # メインデータファイル
│   ├── schema.json                # 🆕 データ検証スキーマ
│   └── 📁 backups/                # 🆕 自動バックアップ
├── 📁 templates/                  # HTMLテンプレート
│   └── index.html                 # メインページ（設定対応）
├── 📁 static/                     # CSS/JS
│   └── style.css                  # スタイルシート（テーマ対応）
├── 📁 docs/                       # ドキュメント
│   ├── CHANGELOG.md               # 変更履歴
│   ├── DEPLOYMENT.md              # デプロイ手順
│   ├── MIGRATION_GUIDE.md         # 🆕 v1.1→v2.0移行ガイド
│   └── REQUIREMENTS_CHECK.md      # 要件チェック
├── 📁 scripts/                    # セットアップスクリプト
│   ├── setup.ps1                  # Windows用統合セットアップ
│   ├── setup.sh                   # Mac/Linux用統合セットアップ
│   └── (その他のスクリプト)
├── 📁 tests/                      # テストファイル
│   ├── test_app.py                # アプリケーションテスト
│   ├── test_config_manager.py     # 🆕 設定システムテスト
│   ├── test_data_manager.py       # 🆕 データ管理テスト
│   └── test_integration_examples.py # 🆕 設定例統合テスト
├── 📁 backups/                    # システムバックアップ
│   └── 📁 v1.1/                   # v1.1システムバックアップ
├── run_app.py                     # アプリ起動スクリプト（設定統合）
├── requirements.txt               # Python依存関係
├── Dockerfile                     # Docker設定
├── docker-compose.yml             # Docker Compose設定
├── database.db                    # データベースファイル
└── README.md                      # このファイル

🆕 = v2.0で新規追加
```

### 🔌 API仕様

#### 検索API
```http
GET /search?q=キーワード&category=カテゴリ&fields=フィールド名
```

**パラメータ:**
- `q`: 検索キーワード（必須）
- `category`: カテゴリフィルタ（オプション）
- `fields`: 検索対象フィールド（オプション、カンマ区切り）

**レスポンス例:**
```json
[
  {
    "id": 1,
    "name": "ドラゴンキラー",
    "description": "竜系の敵に特効がある剣",
    "category": "武器",
    "custom_fields": {
      "price": "1200",
      "rarity": "レア"
    }
  }
]
```

#### 設定管理API（v2.0新機能）

**現在の設定取得**
```http
GET /api/config
```

**設定検証**
```http
GET /api/config/validate
```

**利用可能な設定例一覧**
```http
GET /api/config/examples
```

**特定の設定例取得**
```http
GET /api/config/examples/{example_name}
```

#### システム監視API（v2.0新機能）

**ヘルスチェック**
```http
GET /api/system/health
```

**エラー情報**
```http
GET /api/system/errors
```

**パフォーマンス情報**
```http
GET /api/system/performance?hours=24
```

**設定変更履歴**
```http
GET /api/system/logs/config-history?hours=24&type=categories
```

### 起動方法まとめ

| 方法 | コマンド | 推奨度 |
|------|----------|--------|
| Docker | `docker-compose up --build` | ⭐⭐⭐ 最も確実 |
| Python直接 | `python run_app.py` | ⭐⭐ 簡単 |
| 仮想環境 | `python -m instant_search_db` | ⭐ 開発向け |

---

## 🎛️ 設定システム完全ガイド

v2.0の最大の特徴は、**コードを変更せずに設定ファイルだけで完全にカスタマイズできる**ことです。

### 🚀 5分でカスタマイズ

#### ステップ1: 用途を決める
```bash
# 利用可能な設定例を確認
ls config/examples/
# → game-database.json, product-catalog.json, document-library.json, inventory-system.json
```

#### ステップ2: 設定をコピー
```bash
# 例：商品カタログ用に設定
cp config/examples/product-catalog.json my-config.json

# 設定を個別ファイルに分割（手動またはスクリプト使用）
# → categories.json, fields.json, ui.json
```

#### ステップ3: データを準備
```bash
# サンプルデータをコピー
cp config/examples/product-catalog-sample.csv data/items.csv

# または独自のCSVファイルを作成
```

#### ステップ4: システム再起動
```bash
docker-compose restart
# → 新しい設定でシステムが起動
```

### 📋 設定ファイル詳細

#### 1. カテゴリ設定 (`config/categories.json`)

```json
{
  "categories": {
    "electronics": {
      "display_name": "電子機器",
      "icon": "fas fa-laptop",
      "emoji_fallback": "💻",
      "color": "#3498db",
      "description": "電子機器とガジェット"
    },
    "books": {
      "display_name": "書籍",
      "icon": "fas fa-book",
      "emoji_fallback": "📚",
      "color": "#e67e22",
      "description": "書籍と雑誌"
    }
  }
}
```

**設定項目説明:**
- `display_name`: UI上での表示名
- `icon`: Font Awesomeアイコンクラス
- `emoji_fallback`: アイコンが表示できない場合の絵文字
- `color`: カテゴリの色（16進数カラーコード）
- `description`: カテゴリの説明（ツールチップ等で使用）

#### 2. フィールド設定 (`config/fields.json`)

```json
{
  "field_mappings": {
    "category": "product_category",
    "name": "product_name",
    "description": "description",
    "price": "price",
    "brand": "brand"
  },
  "display_fields": ["name", "brand", "price", "description"],
  "search_fields": ["name", "brand", "description"],
  "required_fields": ["category", "name"]
}
```

**設定項目説明:**
- `field_mappings`: CSVの列名とシステム内部フィールドのマッピング
- `display_fields`: 検索結果に表示するフィールド
- `search_fields`: 検索対象とするフィールド
- `required_fields`: 必須フィールド（データ検証で使用）

#### 3. UI設定 (`config/ui.json`)

```json
{
  "ui": {
    "title": "商品検索システム",
    "subtitle": "商品を素早く検索できます",
    "theme": {
      "primary_color": "#2c3e50",
      "secondary_color": "#3498db",
      "accent_color": "#e74c3c"
    },
    "layout": {
      "categories_per_row": 4,
      "show_category_counts": true,
      "enable_suggestions": true
    },
    "search": {
      "placeholder": "商品名、ブランドで検索...",
      "debounce_ms": 300,
      "min_query_length": 1
    }
  }
}
```

**設定項目説明:**
- `title/subtitle`: アプリケーションのタイトルとサブタイトル
- `theme`: カラーテーマ設定
- `layout`: レイアウト設定（カテゴリ表示数など）
- `search`: 検索機能の設定

### 🎨 テーマカスタマイズ

#### カラーテーマの変更

```json
{
  "theme": {
    "primary_color": "#2c3e50",    // メインカラー（ヘッダー等）
    "secondary_color": "#3498db",  // セカンダリカラー（ボタン等）
    "accent_color": "#e74c3c",     // アクセントカラー（強調表示）
    "background_color": "#f8f9fa", // 背景色
    "text_color": "#2c3e50",       // テキスト色
    "border_color": "#dee2e6"      // ボーダー色
  }
}
```

#### レイアウトの調整

```json
{
  "layout": {
    "categories_per_row": 5,        // 1行あたりのカテゴリ数
    "show_category_counts": true,   // カテゴリ別件数表示
    "compact_mode": false,          // コンパクト表示モード
    "enable_suggestions": true,     // 検索候補表示
    "max_results": 100             // 最大検索結果数
  }
}
```

### 🔄 設定の動的変更

#### 設定変更の反映方法

1. **ファイル編集後の再起動**
   ```bash
   # Docker使用の場合
   docker-compose restart
   
   # Python直接実行の場合
   # Ctrl+C で停止後、再度起動
   python run_app.py
   ```

2. **設定検証**
   ```bash
   # 設定ファイルの妥当性をチェック
   curl http://localhost:5000/api/config/validate
   
   # システム全体のヘルスチェック
   curl http://localhost:5000/api/system/health
   ```

#### 設定のバックアップと復元

```bash
# 現在の設定をバックアップ
cp -r config config_backup_$(date +%Y%m%d)

# 設定を復元
cp -r config_backup_20240315/* config/

# システム再起動
docker-compose restart
```

### 🛠️ カスタム設定の作成

#### 新しい用途向け設定の作成手順

1. **ベース設定の選択**
   ```bash
   # 最も近い用途の設定をコピー
   cp config/examples/product-catalog.json config/my-custom.json
   ```

2. **カテゴリの定義**
   ```json
   {
     "categories": {
       "my_category_1": {
         "display_name": "カスタムカテゴリ1",
         "icon": "fas fa-custom-icon",
         "emoji_fallback": "🔧",
         "color": "#custom-color"
       }
     }
   }
   ```

3. **フィールドマッピングの設定**
   ```json
   {
     "field_mappings": {
       "category": "my_csv_category_column",
       "name": "my_csv_name_column",
       "description": "my_csv_description_column"
     }
   }
   ```

4. **UIのカスタマイズ**
   ```json
   {
     "ui": {
       "title": "マイカスタムシステム",
       "theme": {
         "primary_color": "#my-brand-color"
       }
     }
   }
   ```

5. **データファイルの準備**
   ```csv
   my_csv_category_column,my_csv_name_column,my_csv_description_column
   category1,Item 1,Description of item 1
   category2,Item 2,Description of item 2
   ```

### ⚠️ 設定時の注意点

#### よくある設定ミス

1. **JSON形式エラー**
   ```bash
   # JSON形式をチェック
   python -m json.tool config/categories.json
   ```

2. **フィールドマッピングの不一致**
   ```bash
   # CSVヘッダーと設定の確認
   head -1 data/items.csv
   cat config/fields.json | jq '.field_mappings'
   ```

3. **カラーコードの形式エラー**
   ```json
   // 正しい形式
   "color": "#3498db"
   
   // 間違った形式
   "color": "blue"        // ❌
   "color": "3498db"      // ❌
   "color": "#blue"       // ❌
   ```

#### 設定のベストプラクティス

1. **段階的な変更**: 一度に全ての設定を変更せず、段階的に変更
2. **バックアップの作成**: 設定変更前に必ずバックアップを作成
3. **検証の実行**: 変更後は必ず設定検証APIを実行
4. **テストデータの使用**: 本番データで試す前にテストデータで確認

---

## 🔄 v1.1からv2.0への移行

既存のv1.1システムをお使いの方向けの移行ガイドです。

### 📋 移行前チェックリスト

- [ ] **現在のシステムが正常動作している**
- [ ] **データのバックアップが完了している** (`backups/v1.1/`に保存済み)
- [ ] **カスタマイズ内容を把握している**
- [ ] **移行後のテスト計画がある**

### 🚀 簡単移行（推奨）

v2.0は**完全に後方互換**です。既存のデータとカスタマイズを保持したまま移行できます。

```bash
# 1. 現在のシステムを停止
docker-compose down

# 2. v2.0システムを起動
docker-compose up --build

# 3. 動作確認
# → 既存のデータがそのまま表示されることを確認
```

### 🎯 設定システムの活用

移行後は設定ファイルでカスタマイズが可能になります：

#### 既存のゲーム設定を維持
```bash
# v1.1互換の設定を使用（デフォルト）
cp config/examples/game-database.json config/categories.json
# → 武器、盾、壺などのカテゴリがそのまま使用可能
```

#### 新しい用途に拡張
```bash
# 商品カタログに変更
cp config/examples/product-catalog.json config/categories.json
cp config/examples/product-catalog-sample.csv data/items.csv

# ドキュメント管理に変更
cp config/examples/document-library.json config/categories.json
cp config/examples/document-library-sample.csv data/items.csv
```

### 🔧 カスタマイズの移行

v1.1でコードを直接変更していた場合の移行方法：

#### カテゴリのカスタマイズ
```javascript
// v1.1: コード内で直接変更
const categories = ['武器', '盾', '壺'];

// v2.0: 設定ファイルで変更
// config/categories.json
{
  "categories": {
    "武器": {"display_name": "武器", "icon": "fas fa-sword", ...},
    "盾": {"display_name": "盾", "icon": "fas fa-shield-alt", ...}
  }
}
```

#### UIのカスタマイズ
```css
/* v1.1: CSSファイルを直接編集 */
.header { background-color: #3498db; }

/* v2.0: 設定ファイルで変更 */
// config/ui.json
{
  "ui": {
    "theme": {
      "primary_color": "#3498db"
    }
  }
}
```

### 📊 移行後の新機能

v2.0で利用可能になる新機能：

#### 1. 設定管理API
```bash
# 現在の設定を確認
curl http://localhost:5000/api/config

# 設定の妥当性をチェック
curl http://localhost:5000/api/config/validate
```

#### 2. システム監視
```bash
# システムの健康状態をチェック
curl http://localhost:5000/api/system/health

# パフォーマンス情報を取得
curl http://localhost:5000/api/system/performance
```

#### 3. エラーハンドリング
- 設定ファイルエラーの自動検出と修復提案
- 詳細なエラーログとトラブルシューティング情報
- グレースフルデグラデーション（設定エラー時のフォールバック）

### 🆘 トラブルシューティング

#### 移行後に問題が発生した場合

1. **v1.1への緊急復旧**
   ```bash
   # v1.1システムを復元
   cp -r backups/v1.1/* .
   docker-compose up --build
   ```

2. **設定の問題診断**
   ```bash
   # 設定ファイルの検証
   python -m json.tool config/categories.json
   
   # システムヘルスチェック
   curl http://localhost:5000/api/system/health
   ```

3. **ログの確認**
   ```bash
   # アプリケーションログを確認
   docker-compose logs app
   
   # 設定関連のログを抽出
   docker-compose logs app | grep -i config
   ```

### 📖 詳細な移行ガイド

より詳細な移行手順については、[移行ガイド](docs/MIGRATION_GUIDE.md)を参照してください。

---

## 📚 システム管理者向け操作マニュアル

このシステムは汎用的なデータベース検索システムとして設計されており、設定ファイルを変更することで様々な用途に対応できます。

### 🔧 設定システムの概要

システムは以下の3つの主要な設定ファイルで動作をカスタマイズできます：

- **`config/categories.json`** - カテゴリの定義とアイコン設定
- **`config/fields.json`** - データフィールドのマッピングと表示設定
- **`config/ui.json`** - UI要素とテーマの設定

### 📂 設定ファイルの構造

```
config/
├── categories.json     # カテゴリ設定
├── fields.json         # フィールドマッピング
├── ui.json            # UI設定
├── schemas/           # バリデーション用スキーマ
└── examples/          # 使用例設定
    ├── product-catalog.json
    ├── document-library.json
    └── inventory-system.json
```

### 🎯 カテゴリのカスタマイズ

#### 基本的なカテゴリ設定

`config/categories.json` を編集してカテゴリを変更できます：

```json
{
  "categories": {
    "category_key": {
      "display_name": "表示名",
      "icon": "fas fa-icon-name",
      "emoji_fallback": "🔧",
      "color": "#3498db",
      "description": "カテゴリの説明"
    }
  }
}
```

#### ステップバイステップ カテゴリ変更例

**例：商品カタログ用にカテゴリを変更する場合**

1. **設定ファイルをバックアップ**
   ```bash
   cp config/categories.json config/categories.json.backup
   ```

2. **新しいカテゴリを定義**
   ```json
   {
     "categories": {
       "electronics": {
         "display_name": "電子機器",
         "icon": "fas fa-laptop",
         "emoji_fallback": "💻",
         "color": "#3498db",
         "description": "電子機器とガジェット"
       },
       "clothing": {
         "display_name": "衣類",
         "icon": "fas fa-tshirt", 
         "emoji_fallback": "👕",
         "color": "#e74c3c",
         "description": "アパレルとファッション"
       }
     }
   }
   ```

3. **アプリケーションを再起動**
   ```bash
   # Docker使用の場合
   docker-compose restart
   
   # Python直接実行の場合
   # Ctrl+C で停止後、再度 python run_app.py
   ```

### 🗂️ データフィールドのカスタマイズ

#### フィールドマッピングの設定

`config/fields.json` でCSVファイルの列とシステムフィールドをマッピングします：

```json
{
  "field_mappings": {
    "category": "csv_category_column",
    "name": "csv_name_column",
    "description": "csv_description_column",
    "custom_field": "csv_custom_column"
  },
  "display_fields": ["name", "description", "custom_field"],
  "search_fields": ["name", "description"],
  "required_fields": ["category", "name"]
}
```

#### ステップバイステップ フィールド設定例

**例：商品データベース用のフィールド設定**

1. **CSVファイルの構造を確認**
   ```csv
   product_category,product_name,description,price,brand,sku
   electronics,Laptop Computer,High-performance laptop,999.99,TechBrand,SKU001
   ```

2. **フィールドマッピングを設定**
   ```json
   {
     "field_mappings": {
       "category": "product_category",
       "name": "product_name", 
       "description": "description",
       "price": "price",
       "brand": "brand",
       "sku": "sku"
     },
     "display_fields": ["name", "brand", "price", "description"],
     "search_fields": ["name", "brand", "description", "sku"],
     "required_fields": ["category", "name", "price"]
   }
   ```

3. **フィールド定義を追加**
   ```json
   {
     "field_definitions": {
       "price": {
         "display_name": "価格",
         "type": "currency",
         "searchable": false,
         "required": true,
         "description": "商品価格（USD）"
       },
       "brand": {
         "display_name": "ブランド",
         "type": "string", 
         "searchable": true,
         "required": false,
         "description": "商品ブランドまたはメーカー"
       }
     }
   }
   ```

### 🎨 UIのカスタマイズ

#### テーマとレイアウトの設定

`config/ui.json` でUIの外観と動作を設定します：

```json
{
  "ui": {
    "title": "アプリケーションタイトル",
    "subtitle": "サブタイトル",
    "theme": {
      "primary_color": "#3498db",
      "secondary_color": "#2ecc71", 
      "accent_color": "#e74c3c"
    },
    "layout": {
      "categories_per_row": 5,
      "show_category_counts": true,
      "enable_suggestions": true
    }
  }
}
```

#### ステップバイステップ UI設定例

**例：企業向けドキュメントライブラリのUI設定**

1. **ブランディングを設定**
   ```json
   {
     "ui": {
       "title": "企業ドキュメントライブラリ",
       "subtitle": "社内文書を素早く検索",
       "theme": {
         "primary_color": "#2c3e50",
         "secondary_color": "#3498db",
         "accent_color": "#e74c3c"
       }
     }
   }
   ```

2. **レイアウトを調整**
   ```json
   {
     "layout": {
       "categories_per_row": 4,
       "show_category_counts": true,
       "compact_mode": false
     },
     "search": {
       "placeholder_text": "文書タイトル、作成者、内容で検索...",
       "min_search_length": 2,
       "max_results": 100
     }
   }
   ```

### 📋 事前設定済み例の使用

システムには3つの事前設定済み例が含まれています：

#### 1. 商品カタログ (`config/examples/product-catalog.json`)
- **用途**: ECサイトや商品データベース
- **カテゴリ**: 電子機器、衣類、本、スポーツ用品など
- **フィールド**: 商品名、ブランド、価格、SKU、在庫数など

#### 2. ドキュメントライブラリ (`config/examples/document-library.json`)
- **用途**: 企業の文書管理システム
- **カテゴリ**: ポリシー、マニュアル、レポート、プレゼンテーションなど
- **フィールド**: タイトル、作成者、作成日、ファイル形式など

#### 3. 在庫管理システム (`config/examples/inventory-system.json`)
- **用途**: 倉庫や製造業の在庫管理
- **カテゴリ**: 原材料、完成品、工具、安全装備など
- **フィールド**: 数量、保管場所、ステータス、単価など

#### 例の適用方法

1. **例の設定をコピー**
   ```bash
   # 商品カタログの例を使用
   cp config/examples/product-catalog.json config/active-config.json
   ```

2. **設定を個別ファイルに分割**
   ```bash
   # 手動で categories.json, fields.json, ui.json に分割
   # または提供されているスクリプトを使用
   ```

3. **サンプルデータを配置**
   ```bash
   cp config/examples/product-catalog-sample.csv data/items.csv
   ```

### 🔄 設定変更の適用

設定を変更した後は、以下の方法でシステムに反映させます：

#### Docker使用の場合
```bash
# コンテナを再起動
docker-compose restart

# または完全に再ビルド
docker-compose down
docker-compose up --build
```

#### Python直接実行の場合
```bash
# アプリケーションを停止（Ctrl+C）
# 再度起動
python run_app.py
```

### ⚠️ 設定変更時の注意点

1. **バックアップの作成**
   ```bash
   # 設定変更前に必ずバックアップを作成
   cp -r config config_backup_$(date +%Y%m%d)
   ```

2. **JSON形式の検証**
   ```bash
   # JSONファイルの形式をチェック
   python -m json.tool config/categories.json
   ```

3. **段階的な変更**
   - 一度に全ての設定を変更せず、段階的に変更
   - 各変更後に動作確認を実施

4. **データとの整合性**
   - フィールドマッピング変更時は、CSVファイルの列名と一致させる
   - カテゴリ変更時は、データ内のカテゴリ値も更新する

### 🔍 設定のトラブルシューティング

#### よくある問題と解決方法

**問題1: カテゴリが表示されない**
```bash
# 解決方法
1. categories.json の JSON形式を確認
2. カテゴリキーがデータのカテゴリ値と一致するか確認
3. アプリケーションログでエラーを確認
```

**問題2: 検索結果が表示されない**
```bash
# 解決方法  
1. fields.json のフィールドマッピングを確認
2. CSVファイルの列名とマッピングが一致するか確認
3. required_fields が適切に設定されているか確認
```

**問題3: UIが正しく表示されない**
```bash
# 解決方法
1. ui.json の JSON形式を確認
2. カラーコードが正しい形式（#RRGGBB）か確認
3. ブラウザのキャッシュをクリア
```

### 📞 サポートとリソース

- **設定例**: `config/examples/` ディレクトリを参照
- **スキーマ**: `config/schemas/` でバリデーションルールを確認
- **ログ**: アプリケーション起動時のコンソール出力を確認
- **テスト**: 設定変更後は必ず動作テストを実施

---

## 📊 データ管理ガイドライン

### 📝 CSVファイル形式要件

システムは標準的なCSV形式のデータファイルを使用します。以下の要件を満たす必要があります：

#### 基本要件

1. **ファイル形式**: UTF-8エンコーディングのCSVファイル
2. **ヘッダー行**: 1行目に列名を含める（必須）
3. **区切り文字**: カンマ（,）を使用
4. **引用符**: テキストにカンマや改行が含まれる場合はダブルクォート（"）で囲む
5. **ファイル名**: `data/items.csv` として配置

#### 必須列

設定ファイル（`config/fields.json`）の `required_fields` で指定された列は必須です：

```csv
category,name,description
武器,つるはし,攻撃力1の基本的な武器
盾,青銅の盾,防御力2の軽量な盾
```

#### データ形式の例

**基本的なゲームアイテムデータ**
```csv
category,name,description
武器,つるはし,攻 1 買 240 補正 12 売 100
盾,青銅の盾,防 2 買 800 補正 8 売 320
壺,保存の壺[5],アイテムを5個まで保存できる壺
```

**商品カタログデータ**
```csv
product_category,product_name,description,price,brand,sku,stock_quantity
electronics,Laptop Computer,High-performance laptop for business,999.99,TechBrand,SKU001,25
clothing,Cotton T-Shirt,Comfortable cotton t-shirt,19.99,FashionCorp,SKU002,100
books,Programming Guide,Complete guide to web development,49.99,TechBooks,SKU003,15
```

**ドキュメントライブラリデータ**
```csv
document_type,title,description,author,created_date,file_format,department
policies,Employee Handbook,Complete guide for new employees,HR Team,2024-01-15,PDF,Human Resources
manuals,API Documentation,Technical documentation for REST API,Dev Team,2024-02-20,HTML,Engineering
reports,Q1 Sales Report,Quarterly sales analysis and projections,Sales Team,2024-03-31,XLSX,Sales
```

### 🔄 データの一括操作

#### データの追加・更新

1. **新しいデータの追加**
   ```bash
   # 既存のCSVファイルをバックアップ
   cp data/items.csv data/items_backup_$(date +%Y%m%d).csv
   
   # 新しいデータを追加（エディタで編集）
   nano data/items.csv
   
   # アプリケーションを再起動してデータを反映
   docker-compose restart
   ```

2. **大量データのインポート**
   ```bash
   # 新しいCSVファイルを準備
   # data/new_items.csv
   
   # 既存データと結合
   cat data/items.csv data/new_items.csv > data/combined.csv
   
   # 重複を除去（必要に応じて）
   sort data/combined.csv | uniq > data/items.csv
   ```

3. **データの検証**
   ```bash
   # CSVファイルの形式をチェック
   head -5 data/items.csv
   
   # 列数の確認
   awk -F',' '{print NF}' data/items.csv | sort | uniq -c
   
   # 必須フィールドの確認
   cut -d',' -f1,2 data/items.csv | grep -v '^,'
   ```

#### データのエクスポート

1. **現在のデータをエクスポート**
   ```bash
   # データベースからCSVを生成（カスタムスクリプトが必要）
   python scripts/export_data.py > data/exported_items.csv
   ```

2. **フィルタリングされたデータのエクスポート**
   ```bash
   # 特定のカテゴリのみをエクスポート
   grep "^武器," data/items.csv > data/weapons_only.csv
   
   # ヘッダーを追加
   head -1 data/items.csv > data/weapons_with_header.csv
   grep "^武器," data/items.csv >> data/weapons_with_header.csv
   ```

### 🔍 データ品質管理

#### データ検証のベストプラクティス

1. **必須フィールドの確認**
   ```bash
   # 空の必須フィールドをチェック
   awk -F',' '$1=="" || $2=="" {print "Line " NR ": " $0}' data/items.csv
   ```

2. **データ型の検証**
   ```bash
   # 数値フィールドの検証（価格など）
   awk -F',' '$4 !~ /^[0-9]+\.?[0-9]*$/ && NR>1 {print "Invalid price at line " NR ": " $4}' data/items.csv
   ```

3. **カテゴリの整合性確認**
   ```bash
   # 定義されていないカテゴリをチェック
   cut -d',' -f1 data/items.csv | sort | uniq | grep -v -f <(jq -r '.categories | keys[]' config/categories.json)
   ```

#### データクリーニング

1. **重複データの除去**
   ```bash
   # 完全に同じ行を除去
   sort data/items.csv | uniq > data/items_cleaned.csv
   
   # 名前が同じアイテムを除去（ヘッダーを保持）
   head -1 data/items.csv > data/items_unique.csv
   tail -n +2 data/items.csv | sort -t',' -k2,2 | uniq -t',' -f1 >> data/items_unique.csv
   ```

2. **データの正規化**
   ```bash
   # カテゴリ名の統一（例：「武器」と「weapon」を統一）
   sed 's/weapon/武器/g' data/items.csv > data/items_normalized.csv
   
   # 余分な空白の除去
   sed 's/[[:space:]]*,[[:space:]]*/,/g' data/items.csv > data/items_trimmed.csv
   ```

### 🛠️ データトラブルシューティング

#### よくあるデータ問題と解決方法

**問題1: データが表示されない**

**症状**: アプリケーションは起動するが、検索結果が表示されない

**原因と解決方法**:
```bash
# 1. CSVファイルの存在確認
ls -la data/items.csv

# 2. ファイルの内容確認
head -5 data/items.csv

# 3. エンコーディング確認
file data/items.csv

# 4. 列名の確認
head -1 data/items.csv

# 解決方法
# - ファイルが存在しない場合: サンプルデータをコピー
cp config/examples/product-catalog-sample.csv data/items.csv

# - エンコーディングが正しくない場合: UTF-8に変換
iconv -f SHIFT_JIS -t UTF-8 data/items.csv > data/items_utf8.csv
mv data/items_utf8.csv data/items.csv
```

**問題2: 一部のデータが検索できない**

**症状**: 特定のアイテムが検索結果に表示されない

**原因と解決方法**:
```bash
# 1. フィールドマッピングの確認
cat config/fields.json | jq '.field_mappings'

# 2. データの形式確認
grep "検索できないアイテム名" data/items.csv

# 3. 特殊文字の確認
hexdump -C data/items.csv | grep "検索できないアイテム名"

# 解決方法
# - フィールドマッピングが正しくない場合: config/fields.json を修正
# - 特殊文字が含まれている場合: データをクリーニング
```

**問題3: カテゴリが正しく表示されない**

**症状**: アイテムが「その他」カテゴリに分類される

**原因と解決方法**:
```bash
# 1. カテゴリ定義の確認
cat config/categories.json | jq '.categories | keys'

# 2. データ内のカテゴリ値確認
cut -d',' -f1 data/items.csv | sort | uniq

# 3. 不一致の確認
comm -23 <(cut -d',' -f1 data/items.csv | sort | uniq) <(jq -r '.categories | keys[]' config/categories.json | sort)

# 解決方法
# - カテゴリ定義を追加: config/categories.json に新しいカテゴリを追加
# - データを修正: CSVファイル内のカテゴリ名を既存の定義に合わせる
```

### 📋 データメンテナンスのベストプラクティス

#### 定期的なメンテナンス

1. **週次データチェック**
   ```bash
   #!/bin/bash
   # weekly_data_check.sh
   
   echo "=== データ品質チェック $(date) ==="
   
   # ファイルサイズ確認
   echo "ファイルサイズ: $(du -h data/items.csv)"
   
   # 行数確認
   echo "データ行数: $(wc -l < data/items.csv)"
   
   # 重複チェック
   echo "重複行数: $(sort data/items.csv | uniq -d | wc -l)"
   
   # 空フィールドチェック
   echo "空フィールドのある行: $(awk -F',' '$1=="" || $2=="" {count++} END {print count+0}' data/items.csv)"
   ```

2. **月次バックアップ**
   ```bash
   #!/bin/bash
   # monthly_backup.sh
   
   BACKUP_DIR="backups/$(date +%Y-%m)"
   mkdir -p $BACKUP_DIR
   
   # データファイルのバックアップ
   cp data/items.csv $BACKUP_DIR/items_$(date +%Y%m%d).csv
   
   # 設定ファイルのバックアップ
   cp -r config $BACKUP_DIR/
   
   # 圧縮
   tar -czf $BACKUP_DIR.tar.gz $BACKUP_DIR
   
   echo "バックアップ完了: $BACKUP_DIR.tar.gz"
   ```

#### データ移行手順

**既存システムからの移行**

1. **データ形式の分析**
   ```bash
   # 既存データの構造を確認
   head -10 old_system_data.csv
   
   # 列数と列名を確認
   head -1 old_system_data.csv | tr ',' '\n' | nl
   ```

2. **マッピングテーブルの作成**
   ```bash
   # mapping.txt を作成
   old_column_name -> new_column_name
   item_type -> category
   item_name -> name
   item_desc -> description
   ```

3. **データ変換スクリプトの実行**
   ```bash
   # convert_data.py を使用してデータを変換
   python scripts/convert_data.py old_system_data.csv mapping.txt > data/items.csv
   ```

4. **変換結果の検証**
   ```bash
   # 変換後のデータを確認
   head -5 data/items.csv
   
   # データ数の確認
   echo "変換前: $(wc -l < old_system_data.csv) 行"
   echo "変換後: $(wc -l < data/items.csv) 行"
   ```

### 🔒 データセキュリティとバックアップ

#### バックアップ戦略

1. **自動バックアップの設定**
   ```bash
   # crontab -e で以下を追加
   # 毎日午前2時にバックアップ
   0 2 * * * /path/to/backup_script.sh
   
   # 毎週日曜日に週次チェック
   0 3 * * 0 /path/to/weekly_data_check.sh
   ```

2. **バックアップの復元**
   ```bash
   # 特定の日付のバックアップから復元
   cp backups/2024-03/items_20240315.csv data/items.csv
   
   # 設定ファイルも復元
   cp -r backups/2024-03/config/* config/
   
   # アプリケーション再起動
   docker-compose restart
   ```

#### データ保護

1. **アクセス権限の設定**
   ```bash
   # データファイルの権限を制限
   chmod 644 data/items.csv
   
   # 設定ファイルの権限を制限
   chmod 644 config/*.json
   
   # バックアップディレクトリの権限
   chmod 700 backups/
   ```

2. **機密データの取り扱い**
   ```bash
   # 機密情報を含む列の暗号化（必要に応じて）
   # または機密情報を別ファイルで管理
   
   # 本番環境では環境変数で機密情報を管理
   export DB_PASSWORD="your_secure_password"
   ```

---

## 🚀 デプロイメントとスケーリングガイド

### 🌍 環境別デプロイメント

#### 開発環境

**特徴**: 設定変更の即座反映、デバッグ機能有効

```bash
# 開発環境用の起動
export FLASK_ENV=development
export FLASK_DEBUG=1

# ホットリロード有効でPython直接実行
python run_app.py

# または開発用Dockerコンテナ
docker-compose -f docker-compose.dev.yml up
```

**開発環境用設定**:
```yaml
# docker-compose.dev.yml
version: '3.8'
services:
  app:
    build: .
    ports:
      - "5000:5000"
    volumes:
      - .:/app
      - ./data:/app/data
      - ./config:/app/config
    environment:
      - FLASK_ENV=development
      - FLASK_DEBUG=1
    command: python run_app.py
```

#### ステージング環境

**特徴**: 本番環境に近い設定、テストデータ使用

```bash
# ステージング環境用の設定
export FLASK_ENV=staging
export DATABASE_URL=sqlite:///staging.db

# ステージング用Dockerコンテナ
docker-compose -f docker-compose.staging.yml up -d
```

**ステージング環境用設定**:
```yaml
# docker-compose.staging.yml
version: '3.8'
services:
  app:
    build: .
    ports:
      - "8080:5000"
    volumes:
      - ./data:/app/data:ro
      - ./config:/app/config:ro
    environment:
      - FLASK_ENV=staging
      - DATABASE_URL=sqlite:///staging.db
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:5000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
```

#### 本番環境

**特徴**: 高可用性、セキュリティ強化、監視機能

```bash
# 本番環境用の設定
export FLASK_ENV=production
export DATABASE_URL=postgresql://user:pass@db:5432/proddb
export SECRET_KEY=your_production_secret_key

# 本番用Dockerコンテナ（複数インスタンス）
docker-compose -f docker-compose.prod.yml up -d --scale app=3
```

**本番環境用設定**:
```yaml
# docker-compose.prod.yml
version: '3.8'
services:
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/nginx/ssl
    depends_on:
      - app
    restart: always

  app:
    build: .
    expose:
      - "5000"
    volumes:
      - ./data:/app/data:ro
      - ./config:/app/config:ro
      - ./logs:/app/logs
    environment:
      - FLASK_ENV=production
      - DATABASE_URL=${DATABASE_URL}
      - SECRET_KEY=${SECRET_KEY}
    restart: always
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:5000/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  db:
    image: postgres:13
    environment:
      - POSTGRES_DB=proddb
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=${DB_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    restart: always

volumes:
  postgres_data:
```

### ⚡ パフォーマンス最適化

#### データベース最適化

1. **SQLiteの最適化**
   ```python
   # instant_search_db/models.py での最適化設定
   
   # インデックスの作成
   CREATE INDEX idx_category ON items(category);
   CREATE INDEX idx_name ON items(name);
   CREATE INDEX idx_search ON items_fts(name, description);
   
   # SQLite設定の最適化
   PRAGMA journal_mode = WAL;
   PRAGMA synchronous = NORMAL;
   PRAGMA cache_size = 10000;
   PRAGMA temp_store = MEMORY;
   ```

2. **PostgreSQL移行（大規模データ用）**
   ```python
   # requirements.txt に追加
   psycopg2-binary==2.9.5
   
   # 環境変数設定
   export DATABASE_URL=postgresql://user:pass@localhost:5432/searchdb
   
   # マイグレーションスクリプト
   python scripts/migrate_to_postgresql.py
   ```

#### アプリケーション最適化

1. **キャッシュの実装**
   ```python
   # Flask-Cachingの追加
   pip install Flask-Caching
   
   # instant_search_db/__init__.py
   from flask_caching import Cache
   
   cache = Cache()
   cache.init_app(app, config={'CACHE_TYPE': 'simple'})
   
   # routes.py でキャッシュ使用
   @cache.cached(timeout=300)
   def get_categories():
       return load_categories()
   ```

2. **静的ファイルの最適化**
   ```bash
   # CSS/JSの圧縮
   npm install -g uglifycss uglify-js
   
   uglifycss static/style.css > static/style.min.css
   uglifyjs static/script.js > static/script.min.js
   
   # Gzip圧縮の有効化（Nginx設定）
   gzip on;
   gzip_types text/css application/javascript application/json;
   ```

#### 検索パフォーマンスの向上

1. **全文検索の最適化**
   ```sql
   -- FTS5の設定最適化
   CREATE VIRTUAL TABLE items_fts USING fts5(
       name, description, category,
       content='items',
       tokenize='porter unicode61'
   );
   
   -- 検索結果のランキング改善
   SELECT *, rank FROM items_fts 
   WHERE items_fts MATCH ? 
   ORDER BY rank 
   LIMIT 50;
   ```

2. **検索結果のページネーション**
   ```python
   # routes.py での実装
   @app.route('/search')
   def search():
       page = request.args.get('page', 1, type=int)
       per_page = 20
       offset = (page - 1) * per_page
       
       results = search_items(query, limit=per_page, offset=offset)
       return jsonify(results)
   ```

### 📈 スケーリング戦略

#### 水平スケーリング

1. **ロードバランサーの設定**
   ```nginx
   # nginx.conf
   upstream app_servers {
       server app1:5000;
       server app2:5000;
       server app3:5000;
   }
   
   server {
       listen 80;
       location / {
           proxy_pass http://app_servers;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
       }
   }
   ```

2. **Docker Swarmでのスケーリング**
   ```bash
   # Swarmクラスターの初期化
   docker swarm init
   
   # サービスのデプロイ
   docker stack deploy -c docker-compose.prod.yml searchapp
   
   # スケールアップ
   docker service scale searchapp_app=5
   ```

3. **Kubernetesでのデプロイ**
   ```yaml
   # k8s-deployment.yml
   apiVersion: apps/v1
   kind: Deployment
   metadata:
     name: search-app
   spec:
     replicas: 3
     selector:
       matchLabels:
         app: search-app
     template:
       metadata:
         labels:
           app: search-app
       spec:
         containers:
         - name: app
           image: search-app:latest
           ports:
           - containerPort: 5000
           resources:
             requests:
               memory: "256Mi"
               cpu: "250m"
             limits:
               memory: "512Mi"
               cpu: "500m"
   ```

#### 垂直スケーリング

1. **リソース使用量の監視**
   ```bash
   # システムリソースの監視
   docker stats
   
   # アプリケーションメトリクスの収集
   pip install prometheus-flask-exporter
   ```

2. **メモリとCPUの最適化**
   ```python
   # Gunicornでのワーカー数調整
   # gunicorn_config.py
   workers = 4  # CPU数 × 2
   worker_class = "gevent"
   worker_connections = 1000
   max_requests = 1000
   max_requests_jitter = 100
   ```

### 🔧 インフラストラクチャ管理

#### Docker最適化

1. **マルチステージビルド**
   ```dockerfile
   # Dockerfile.prod
   FROM python:3.9-slim as builder
   WORKDIR /app
   COPY requirements.txt .
   RUN pip install --no-cache-dir -r requirements.txt
   
   FROM python:3.9-slim
   WORKDIR /app
   COPY --from=builder /usr/local/lib/python3.9/site-packages /usr/local/lib/python3.9/site-packages
   COPY . .
   EXPOSE 5000
   CMD ["gunicorn", "--config", "gunicorn_config.py", "run_app:app"]
   ```

2. **ヘルスチェックの実装**
   ```python
   # instant_search_db/routes.py
   @app.route('/health')
   def health_check():
       try:
           # データベース接続確認
           db_status = check_database_connection()
           # 設定ファイル確認
           config_status = check_configuration()
           
           if db_status and config_status:
               return jsonify({'status': 'healthy'}), 200
           else:
               return jsonify({'status': 'unhealthy'}), 503
       except Exception as e:
           return jsonify({'status': 'error', 'message': str(e)}), 503
   ```

#### 監視とログ

1. **ログ管理**
   ```python
   # logging_config.py
   import logging
   from logging.handlers import RotatingFileHandler
   
   def setup_logging(app):
       if not app.debug:
           file_handler = RotatingFileHandler(
               'logs/app.log', maxBytes=10240000, backupCount=10
           )
           file_handler.setFormatter(logging.Formatter(
               '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
           ))
           file_handler.setLevel(logging.INFO)
           app.logger.addHandler(file_handler)
           app.logger.setLevel(logging.INFO)
   ```

2. **メトリクス収集**
   ```python
   # prometheus_metrics.py
   from prometheus_flask_exporter import PrometheusMetrics
   
   def init_metrics(app):
       metrics = PrometheusMetrics(app)
       
       # カスタムメトリクス
       search_counter = metrics.counter(
           'search_requests_total', 'Total search requests'
       )
       
       search_duration = metrics.histogram(
           'search_duration_seconds', 'Search request duration'
       )
   ```

### 🔐 セキュリティ強化

#### HTTPS設定

1. **SSL証明書の設定**
   ```bash
   # Let's Encryptを使用
   sudo apt install certbot python3-certbot-nginx
   sudo certbot --nginx -d yourdomain.com
   
   # 自動更新の設定
   sudo crontab -e
   0 12 * * * /usr/bin/certbot renew --quiet
   ```

2. **Nginx SSL設定**
   ```nginx
   server {
       listen 443 ssl http2;
       server_name yourdomain.com;
       
       ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
       ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;
       
       ssl_protocols TLSv1.2 TLSv1.3;
       ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512;
       ssl_prefer_server_ciphers off;
       
       location / {
           proxy_pass http://app_servers;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
           proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
           proxy_set_header X-Forwarded-Proto $scheme;
       }
   }
   ```

#### アクセス制御

1. **基本認証の実装**
   ```python
   # Flask-HTTPAuthを使用
   from flask_httpauth import HTTPBasicAuth
   
   auth = HTTPBasicAuth()
   
   @auth.verify_password
   def verify_password(username, password):
       # 環境変数から認証情報を取得
       return username == os.environ.get('ADMIN_USER') and \
              password == os.environ.get('ADMIN_PASS')
   
   @app.route('/admin')
   @auth.login_required
   def admin():
       return render_template('admin.html')
   ```

2. **レート制限**
   ```python
   # Flask-Limiterを使用
   from flask_limiter import Limiter
   from flask_limiter.util import get_remote_address
   
   limiter = Limiter(
       app,
       key_func=get_remote_address,
       default_limits=["200 per day", "50 per hour"]
   )
   
   @app.route('/search')
   @limiter.limit("10 per minute")
   def search():
       # 検索処理
       pass
   ```

### 📊 バックアップとリストア手順

#### 自動バックアップシステム

1. **データベースバックアップ**
   ```bash
   #!/bin/bash
   # backup_database.sh
   
   BACKUP_DIR="/backups/$(date +%Y-%m)"
   mkdir -p $BACKUP_DIR
   
   # SQLiteバックアップ
   sqlite3 database.db ".backup $BACKUP_DIR/database_$(date +%Y%m%d_%H%M%S).db"
   
   # PostgreSQLバックアップ
   pg_dump $DATABASE_URL > $BACKUP_DIR/database_$(date +%Y%m%d_%H%M%S).sql
   
   # 設定ファイルバックアップ
   tar -czf $BACKUP_DIR/config_$(date +%Y%m%d_%H%M%S).tar.gz config/
   
   # 古いバックアップの削除（30日以上）
   find /backups -name "*.db" -mtime +30 -delete
   find /backups -name "*.sql" -mtime +30 -delete
   find /backups -name "*.tar.gz" -mtime +30 -delete
   ```

2. **クラウドバックアップ**
   ```bash
   # AWS S3へのバックアップ
   aws s3 sync /backups s3://your-backup-bucket/search-app-backups/
   
   # Google Cloud Storageへのバックアップ
   gsutil -m rsync -r /backups gs://your-backup-bucket/search-app-backups/
   ```

#### リストア手順

1. **データベースリストア**
   ```bash
   # SQLiteリストア
   cp /backups/2024-03/database_20240315_120000.db database.db
   
   # PostgreSQLリストア
   psql $DATABASE_URL < /backups/2024-03/database_20240315_120000.sql
   ```

2. **設定ファイルリストア**
   ```bash
   # 現在の設定をバックアップ
   mv config config_backup_$(date +%Y%m%d_%H%M%S)
   
   # バックアップから復元
   tar -xzf /backups/2024-03/config_20240315_120000.tar.gz
   
   # アプリケーション再起動
   docker-compose restart
   ```

### 🔍 トラブルシューティング

#### パフォーマンス問題

1. **レスポンス時間の改善**
   ```bash
   # アプリケーションプロファイリング
   pip install flask-profiler
   
   # SQLクエリの分析
   EXPLAIN QUERY PLAN SELECT * FROM items_fts WHERE items_fts MATCH 'search_term';
   ```

2. **メモリ使用量の最適化**
   ```bash
   # メモリ使用量の監視
   docker stats --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}"
   
   # メモリリークの検出
   pip install memory-profiler
   python -m memory_profiler run_app.py
   ```

#### 可用性の向上

1. **ヘルスチェックとフェイルオーバー**
   ```bash
   # ヘルスチェックスクリプト
   #!/bin/bash
   if ! curl -f http://localhost:5000/health; then
       echo "Application unhealthy, restarting..."
       docker-compose restart app
   fi
   ```

2. **ゼロダウンタイムデプロイ**
   ```bash
   # Blue-Greenデプロイメント
   docker-compose -f docker-compose.blue.yml up -d
   # ヘルスチェック後
   docker-compose -f docker-compose.green.yml down
   ```
