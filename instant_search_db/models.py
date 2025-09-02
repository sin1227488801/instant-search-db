import sqlite3
import os
import csv
from typing import List, Dict, Any, Optional

from .config_manager import ConfigManager
from .data_manager import DataManager
from .data_models import Item
from .error_handler import ErrorHandler, ErrorContext, graceful_degradation
from .logging_system import get_logging_system, LogCategory, performance_monitor, log_user_action

DB_FILE = "database.db"
CSV_FILE = "data/items.csv"

# Configure logging
logger = get_logging_system().get_logger(LogCategory.DATA_MANAGEMENT)

# Global error handler
error_handler = ErrorHandler(logger)

def get_default_items():
    """デフォルトのアイテムデータを返す（CSVが利用できない場合）"""
    return [
        ('武器 つるはし', '攻 1 買 240 補正 12 売 100 補正 7テ ○掛 拾食 ×フェイ ○変 ○鍛 ×能力 壁を掘れるが、何度か掘ると壊れる'),
        ('武器 必中の剣', '攻 2 買 10000 補正  900 売  5000 補正  475テ  店掛  ×食  ×フェイ  ○変  ○鍛  ×能力  攻撃が必ず当たる'),
        ('盾 皮甲の盾', '防 2 買 1000 補正 40 売 350 補正 20テ ○掛 －食 ○フェイ ○変 ○鍛 －能力 錆びない。満腹度の減りが1/2になる'),
        ('壺 保存の壺', 'テ ○ 掛 × 食 ○ フェイ ○ 備考 「見る」ことでアイテムを出し入れできる壺の中のアイテムを直接使用できる'),
        ('草・種 薬草', 'テ ○ 掛 ○ 食 ○ フェイ ○ 効果・補足 HPが25回復する。HPが最大の時に飲むとHPの最大値が1上昇。ゴースト系に投げると25ダメージ'),
    ]

@performance_monitor("load_items_from_csv", LogCategory.DATA_MANAGEMENT)
@graceful_degradation(get_default_items)
def load_items_from_csv(config_manager: Optional[ConfigManager] = None):
    """CSVファイルからアイテムデータを読み込む（設定ベース）- Enhanced with error handling"""
    if config_manager is None:
        config_manager = ConfigManager()
    
    context = ErrorContext(
        file_path=CSV_FILE,
        function_name="load_items_from_csv"
    )
    
    if not os.path.exists(CSV_FILE):
        error = FileNotFoundError(f"CSV file not found: {CSV_FILE}")
        error_handler.handle_error(error, context, "csv_file_not_found")
        logger.warning(f"CSVファイル '{CSV_FILE}' が見つかりません。デフォルトデータを使用します。")
        return get_default_items()
    
    try:
        # 直接CSVファイルを読み込み（シンプルな方法）
        result_items = []
        
        with open(CSV_FILE, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            
            for row in reader:
                try:
                    category = row.get('category', '').strip()
                    name = row.get('name', '').strip()
                    description = row.get('description', '').strip()
                    
                    if category and name:
                        # データベース用の形式: "カテゴリ名 アイテム名"
                        display_name = f"{category} {name}"
                        result_items.append((display_name, description))
                    
                except Exception as e:
                    logger.warning(f"Failed to process CSV row: {e}")
                    continue
        
        logger.info(f"CSVから {len(result_items)} 件のアイテムを読み込みました。")
        return result_items
        
    except Exception as e:
        error_handler.handle_error(e, context)
        logger.error(f"CSVファイルの読み込みエラー: {e}")
        return get_default_items()

def init_db(config_manager: Optional[ConfigManager] = None):
    """データベースを初期化し、サンプルデータを投入する（設定ベース）"""
    if config_manager is None:
        config_manager = ConfigManager()
    
    # 既存のデータベースを削除して再作成
    if os.path.exists(DB_FILE):
        os.remove(DB_FILE)
        print(f"既存の'{DB_FILE}'を削除しました。")

    print(f"'{DB_FILE}'を新規作成して初期化します。")
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    # 1. 通常テーブルの作成
    cursor.execute("""
    CREATE TABLE items (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        description TEXT NOT NULL
    )
    """)
    
    # 2. FTS5仮想テーブルの作成
    try:
        cursor.execute("""
        CREATE VIRTUAL TABLE items_fts USING fts5(
            name, 
            description,
            content='items',
            content_rowid='id'
        )
        """)
        print("FTS5仮想テーブルを作成しました。")
    except sqlite3.OperationalError as e:
        print(f"FTS5が利用できません: {e}")

    # 3. 設定ベースでCSVファイルからデータを読み込み
    sample_data = load_items_from_csv(config_manager)
    
    cursor.executemany("INSERT INTO items (name, description) VALUES (?, ?)", sample_data)

    # 4. FTSインデックスの構築
    try:
        cursor.execute("INSERT INTO items_fts(items_fts) VALUES('rebuild')")
        print("FTSインデックスを構築しました。")
    except sqlite3.OperationalError:
        print("FTSインデックスの構築をスキップしました。")

    conn.commit()
    conn.close()
    print("データベースの初期化が完了しました。")

def search_items(query_term, category_filter='', config_manager: Optional[ConfigManager] = None):
    """アイテムを検索する（設定ベース）"""
    print(f"検索クエリ: '{query_term}', カテゴリフィルタ: '{category_filter}'")
    
    if config_manager is None:
        config_manager = ConfigManager()
    
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    # まずデータベースの内容を確認
    cursor.execute("SELECT COUNT(*) as count FROM items")
    count = cursor.fetchone()['count']
    print(f"データベース内のアイテム数: {count}")

    # 設定からカテゴリ情報を取得
    try:
        categories_config = config_manager.load_categories()
        category_names = list(categories_config.keys()) if categories_config else []
    except Exception as e:
        print(f"カテゴリ設定の読み込みエラー: {e}")
        category_names = []

    # カテゴリフィルタがある場合
    if category_filter:
        print(f"カテゴリフィルタ適用: {category_filter}")
        
        # 設定されたカテゴリ名を使用してフィルタリング
        if category_filter in category_names:
            # 設定からカテゴリの表示名を取得
            try:
                category_info = categories_config[category_filter]
                if hasattr(category_info, 'display_name'):
                    category_display_name = category_info.display_name
                elif isinstance(category_info, dict):
                    category_display_name = category_info.get('display_name', category_filter)
                else:
                    category_display_name = category_filter
                
                cursor.execute(
                    "SELECT * FROM items WHERE name LIKE ?",
                    (f"{category_display_name}%",)
                )
            except (KeyError, AttributeError):
                # フォールバック: 元のカテゴリ名を使用
                cursor.execute(
                    "SELECT * FROM items WHERE name LIKE ?",
                    (f"{category_filter}%",)
                )
        else:
            # 設定にないカテゴリの場合は元の方法を使用
            cursor.execute(
                "SELECT * FROM items WHERE name LIKE ?",
                (f"{category_filter}%",)
            )
        
        results = [dict(row) for row in cursor.fetchall()]
        print(f"カテゴリ検索結果: {len(results)}件")
    else:
        # 通常の検索（LIKE検索を試行）
        search_pattern = f"%{query_term}%"
        
        # 設定から検索対象フィールドを取得
        try:
            field_config = config_manager.load_field_mappings()
            if isinstance(field_config, dict):
                search_fields = field_config.get('search_fields', ['name', 'description'])
            else:
                search_fields = ['name', 'description']
        except Exception as e:
            print(f"フィールド設定の読み込みエラー: {e}")
            search_fields = ['name', 'description']
        
        # 基本的な検索（name と description）
        cursor.execute(
            "SELECT * FROM items WHERE name LIKE ? OR description LIKE ?",
            (search_pattern, search_pattern)
        )
        results = [dict(row) for row in cursor.fetchall()]
        print(f"LIKE検索を使用: {len(results)}件")
        
        # FTS5が利用可能で結果が少ない場合は試行
        if len(results) == 0:
            try:
                cursor.execute(
                    "SELECT items.* FROM items_fts JOIN items ON items.id = items_fts.rowid WHERE items_fts MATCH ?",
                    (query_term,)
                )
                fts_results = [dict(row) for row in cursor.fetchall()]
                if len(fts_results) > 0:
                    results = fts_results
                    print(f"FTS5検索で追加: {len(fts_results)}件")
            except sqlite3.OperationalError as e:
                print(f"FTS5検索エラー: {e}")

    conn.close()
    return results

def get_category_counts(config_manager: Optional[ConfigManager] = None):
    """各カテゴリのアイテム数を取得する（設定ベース）"""
    if config_manager is None:
        config_manager = ConfigManager()
    
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    # CSVファイルから直接カテゴリを取得（より正確）
    csv_categories = set()
    try:
        if os.path.exists(CSV_FILE):
            with open(CSV_FILE, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    category = row.get('category', '').strip()
                    if category:
                        csv_categories.add(category)
        logger.info(f"CSV categories found: {list(csv_categories)}")
    except Exception as e:
        logger.error(f"Failed to read categories from CSV: {e}")
    
    # データベースからもカテゴリを取得（フォールバック）
    db_categories = set()
    try:
        cursor.execute('''
            SELECT DISTINCT SUBSTR(name, 1, INSTR(name, " ") - 1) as category 
            FROM items 
            WHERE INSTR(name, " ") > 0 
            ORDER BY category
        ''')
        db_categories = set(row[0] for row in cursor.fetchall())
        logger.info(f"Database categories found: {list(db_categories)}")
    except Exception as e:
        logger.error(f"Failed to get categories from database: {e}")
    
    # CSVとデータベースの両方からカテゴリを統合
    all_categories = csv_categories.union(db_categories)
    
    # 設定からカテゴリ情報を取得
    categories_config = {}
    try:
        categories_config = config_manager.load_categories()
        logger.info(f"Loaded {len(categories_config)} categories from config")
    except Exception as e:
        logger.warning(f"カテゴリ設定の読み込みエラー: {e}")
    
    # 各カテゴリのアイテム数をカウント
    category_counts = {}
    
    # 設定にあるカテゴリをチェック
    for category_key, category_info in categories_config.items():
        # CategoryConfigオブジェクトの場合は属性でアクセス
        if hasattr(category_info, 'display_name'):
            display_name = category_info.display_name
        elif isinstance(category_info, dict):
            display_name = category_info.get('display_name', category_key)
        else:
            display_name = category_key
        
        # データベースでカテゴリ名で検索（両方の形式をチェック）
        cursor.execute("SELECT COUNT(*) as count FROM items WHERE name LIKE ?", (f"{display_name}%",))
        result = cursor.fetchone()
        count = result[0] if result else 0
        
        # カウントが0の場合、category_keyでも試す
        if count == 0 and category_key != display_name:
            cursor.execute("SELECT COUNT(*) as count FROM items WHERE name LIKE ?", (f"{category_key}%",))
            result = cursor.fetchone()
            count = result[0] if result else 0
        
        category_counts[category_key] = count
        logger.debug(f"Category '{category_key}' ({display_name}): {count} items")
    
    # 実際のデータにあるが設定にないカテゴリも追加
    for actual_cat in all_categories:
        if actual_cat not in category_counts:
            cursor.execute("SELECT COUNT(*) as count FROM items WHERE name LIKE ?", (f"{actual_cat}%",))
            result = cursor.fetchone()
            count = result[0] if result else 0
            category_counts[actual_cat] = count
            logger.debug(f"Actual category '{actual_cat}': {count} items")
    
    conn.close()
    logger.info(f"Category counts: {category_counts}")
    return category_counts