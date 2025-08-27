#!/usr/bin/env python3
import sqlite3

def check_database():
    try:
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        
        # Check items count
        cursor.execute('SELECT COUNT(*) FROM items')
        count = cursor.fetchone()[0]
        print(f'Items count: {count}')
        
        # Check sample items
        cursor.execute('SELECT name, description FROM items LIMIT 5')
        print('Sample items:')
        for row in cursor.fetchall():
            print(f' - {row[0]}: {row[1][:50]}...')
        
        # Check if FTS table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE '%fts%'")
        fts_tables = cursor.fetchall()
        print(f'FTS tables: {fts_tables}')
        
        # Test search
        cursor.execute("SELECT * FROM items WHERE name LIKE '%武器%' LIMIT 3")
        search_results = cursor.fetchall()
        print(f'Search results for "武器": {len(search_results)} items')
        for row in search_results:
            print(f' - {row[1]}')
        
        conn.close()
        
    except Exception as e:
        print(f'Database error: {e}')

if __name__ == '__main__':
    check_database()