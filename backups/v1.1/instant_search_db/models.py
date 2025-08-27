import sqlite3
import os
import csv

DB_FILE = "database.db"
CSV_FILE = "data/items.csv"

def load_items_from_csv():
    """CSVファイルからアイテムデータを読み込む"""
    items = []
    
    if not os.path.exists(CSV_FILE):
        print(f"CSVファイル '{CSV_FILE}' が見つかりません。デフォルトデータを使用します。")
        return get_default_items()
    
    try:
        with open(CSV_FILE, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                # カテゴリと名前を結合してフルネームを作成
                full_name = f"{row['category']} {row['name']}"
                items.append((full_name, row['description']))
        
        print(f"CSVから {len(items)} 件のアイテムを読み込みました。")
        return items
        
    except Exception as e:
        print(f"CSVファイルの読み込みエラー: {e}")
        return get_default_items()

def get_default_items():
    """デフォルトのアイテムデータを返す（CSVが利用できない場合）"""
    return [
        ('武器 つるはし', '攻 1 買 240 補正 12 売 100 補正 7テ ○掛 拾食 ×フェイ ○変 ○鍛 ×能力 壁を掘れるが、何度か掘ると壊れる'),
        ('武器 必中の剣', '攻 2 買 10000 補正  900 売  5000 補正  475テ  店掛  ×食  ×フェイ  ○変  ○鍛  ×能力  攻撃が必ず当たる'),
        ('盾 皮甲の盾', '防 2 買 1000 補正 40 売 350 補正 20テ ○掛 －食 ○フェイ ○変 ○鍛 －能力 錆びない。満腹度の減りが1/2になる'),
        ('壺 保存の壺', 'テ ○ 掛 × 食 ○ フェイ ○ 備考 「見る」ことでアイテムを出し入れできる壺の中のアイテムを直接使用できる'),
        ('草・種 薬草', 'テ ○ 掛 ○ 食 ○ フェイ ○ 効果・補足 HPが25回復する。HPが最大の時に飲むとHPの最大値が1上昇。ゴースト系に投げると25ダメージ'),
    ]

def init_db():
    """データベースを初期化し、サンプルデータを投入する"""
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

    # 3. CSVファイルからデータを読み込み
    sample_data = load_items_from_csv()
    
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

def search_items(query_term, category_filter=''):
    """アイテムを検索する"""
    print(f"検索クエリ: '{query_term}', カテゴリフィルタ: '{category_filter}'")
    
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    # まずデータベースの内容を確認
    cursor.execute("SELECT COUNT(*) as count FROM items")
    count = cursor.fetchone()['count']
    print(f"データベース内のアイテム数: {count}")

    # カテゴリフィルタがある場合は排他制御
    if category_filter:
        print(f"カテゴリフィルタ適用: {category_filter}")
        cursor.execute(
            "SELECT * FROM items WHERE name LIKE ?",
            (f"{category_filter}%",)
        )
        results = [dict(row) for row in cursor.fetchall()]
        print(f"カテゴリ検索結果: {len(results)}件")
    else:
        # 通常の検索（LIKE検索を試行）
        search_pattern = f"%{query_term}%"
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

def get_category_counts():
    """各カテゴリのアイテム数を取得する"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    categories = {
        '武器': 0,
        '盾': 0, 
        '矢': 0,
        '腕輪': 0,
        '杖': 0,
        '壺': 0,
        '巻物': 0,
        '草・種': 0,
        'にぎり': 0,
        'その他': 0
    }
    
    for category in categories.keys():
        cursor.execute("SELECT COUNT(*) as count FROM items WHERE name LIKE ?", (f"{category}%",))
        result = cursor.fetchone()
        categories[category] = result[0] if result else 0
    
    conn.close()
    return categories