#!/usr/bin/env python3
import sqlite3

def check_categories():
    try:
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        
        # Check actual categories in database
        cursor.execute('''
            SELECT DISTINCT SUBSTR(name, 1, INSTR(name, " ") - 1) as category 
            FROM items 
            WHERE INSTR(name, " ") > 0 
            ORDER BY category
        ''')
        categories = cursor.fetchall()
        print('Database categories:')
        for cat in categories:
            print(f' - {cat[0]}')
        
        # Count items per category
        print('\nCategory counts:')
        for cat in categories:
            cursor.execute('SELECT COUNT(*) FROM items WHERE name LIKE ?', (f"{cat[0]}%",))
            count = cursor.fetchone()[0]
            print(f' - {cat[0]}: {count} items')
        
        conn.close()
        
    except Exception as e:
        print(f'Error: {e}')

if __name__ == '__main__':
    check_categories()