from flask import Blueprint, jsonify, render_template, request
from .models import search_items, get_category_counts

bp = Blueprint('main', __name__)

@bp.route('/')
def index():
    """トップページ（index.html）を返す"""
    category_counts = get_category_counts()
    return render_template('index.html', category_counts=category_counts)

@bp.route('/search')
def search():
    """
    クエリパラメータ 'q' で渡されたキーワードでDBを検索し、
    結果をJSON形式で返すAPIエンドポイント
    """
    query_term = request.args.get('q', '')
    category_filter = request.args.get('category', '')
    print(f"Flask検索エンドポイント: クエリ='{query_term}', カテゴリ='{category_filter}'")
    
    if not query_term:
        print("クエリが空のため空の結果を返します")
        return jsonify([])
    
    results = search_items(query_term, category_filter)
    print(f"Flask検索エンドポイント: {len(results)}件の結果を返します")
    return jsonify(results)