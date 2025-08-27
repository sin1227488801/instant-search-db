# 手動セットアップ手順（PowerShell）

## 🚨 現在の問題
古い仮想環境が残っていて、Pythonのパスが壊れています。

## 🛠️ 解決手順

### 1. 完全クリーンアップ & 自動セットアップ（推奨）
```powershell
# 新しい修復スクリプトを実行
.\fix_and_setup.ps1
```

### 2. 手動での完全リセット
```powershell
# 1. 古い仮想環境を削除
Remove-Item -Recurse -Force venv

# 2. Pythonの確認
python --version
# エラーが出る場合は python3 や py を試す

# 3. 新しい仮想環境を作成
python -m venv venv --clear

# 4. PowerShell実行ポリシーを設定
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# 5. 仮想環境を有効化
.\venv\Scripts\Activate.ps1

# 6. pipをアップグレード
python -m pip install --upgrade pip

# 7. 依存関係をインストール
pip install -r requirements.txt

# 8. アプリケーション起動
python -m instant_search_db
```

### 3. Pythonが見つからない場合のインストール

#### Microsoft Store版（推奨・簡単）
```powershell
# Microsoft StoreでPythonを検索してインストール
start ms-windows-store://search/?query=python
```

#### 公式サイトからダウンロード
1. https://www.python.org/downloads/ にアクセス
2. 最新版をダウンロード
3. インストール時に **「Add Python to PATH」にチェック**
4. PowerShellを再起動
5. `python --version` で確認

### 4. 個別パッケージインストール（requirements.txtが失敗する場合）
```powershell
pip install Flask==3.0.0
pip install Werkzeug==3.0.1  
pip install pytest==7.4.3
```

### 5. 環境テスト
```powershell
# 環境が正しく設定されているかテスト
python quick_test.py
```

### 6. 最終確認
```powershell
# アプリケーション起動
python -m instant_search_db

# ブラウザで確認
# http://127.0.0.1:5000
```

## 🐳 Docker使用（最も確実）
Pythonの環境問題を完全に回避したい場合：
```powershell
# Dockerがインストールされている場合
docker-compose up --build
```

## 📞 サポート
上記手順でも解決しない場合は、以下の情報を確認してください：

```powershell
# システム情報
$PSVersionTable
python --version
pip --version
Get-Command python* | Select-Object Name, Source
```