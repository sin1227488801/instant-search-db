import os
from flask import Flask
from .routes import bp
from .models import init_db

def create_app():
    # 現在のファイルの場所から相対的にパスを設定
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(current_dir)
    
    template_dir = os.path.join(project_root, 'templates')
    static_dir = os.path.join(project_root, 'static')
    
    print(f"Template directory: {template_dir}")
    print(f"Static directory: {static_dir}")
    print(f"Template exists: {os.path.exists(template_dir)}")
    print(f"Index.html exists: {os.path.exists(os.path.join(template_dir, 'index.html'))}")
    
    app = Flask(__name__, 
                template_folder=template_dir,
                static_folder=static_dir)
    app.register_blueprint(bp)
    
    # データベース初期化
    init_db()
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0', port=5000, debug=True)