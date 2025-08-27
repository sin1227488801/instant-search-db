import pytest
import json
import os
import tempfile
from instant_search_db import create_app
from instant_search_db.models import init_db

@pytest.fixture
def app():
    """テスト用のFlaskアプリケーションを作成"""
    # テスト用の一時データベースファイル
    db_fd, db_path = tempfile.mkstemp()
    
    app = create_app()
    app.config['TESTING'] = True
    
    # テスト用データベースパスを設定
    import instant_search_db.models
    instant_search_db.models.DB_FILE = db_path
    
    with app.app_context():
        init_db()
    
    yield app
    
    # クリーンアップ
    os.close(db_fd)
    os.unlink(db_path)

@pytest.fixture
def client(app):
    """テストクライアントを作成"""
    return app.test_client()

def test_index_page(client):
    """トップページのテスト"""
    response = client.get('/')
    assert response.status_code == 200
    assert b'instant-search-db' in response.data or b'シレン' in response.data

def test_search_empty_query(client):
    """空のクエリでの検索テスト"""
    response = client.get('/search')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data == []

def test_search_with_query(client):
    """キーワード検索のテスト"""
    response = client.get('/search?q=武器')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert isinstance(data, list)
    
    # 結果がある場合の検証
    if data:
        assert 'id' in data[0]
        assert 'name' in data[0]
        assert 'description' in data[0]

def test_search_no_results(client):
    """結果が見つからない検索のテスト"""
    response = client.get('/search?q=存在しないアイテム12345')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data == []

def test_search_special_characters(client):
    """特殊文字を含む検索のテスト（SQLインジェクション対策確認）"""
    response = client.get('/search?q=\'; DROP TABLE items; --')
    assert response.status_code == 200
    # エラーが発生せず、正常にレスポンスが返ることを確認
    data = json.loads(response.data)
    assert isinstance(data, list)