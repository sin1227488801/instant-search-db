# Changelog

## [1.0.0] - 2025-08-24

### Added
- プロジェクトを `gemini-test` から `instant-search-db` にリネーム
- SQLite FTS5による高速全文検索機能
- LIKE検索へのフォールバック機能
- モジュール化されたプロジェクト構造 (instant_search_db/)
- Docker対応 (Dockerfile, docker-compose.yml)
- 基本テストスイート (pytest)
- GitHub Actions CI/CD
- セキュリティ強化 (SQLインジェクション対策)
- レスポンシブデザイン
- リアルタイム検索 (デバウンス300ms)

### Changed
- プロジェクト名: gemini-test → instant-search-db
- アプリケーション構造: 単一ファイル → モジュール化
- 検索エンジン: LIKE検索 → FTS5 + フォールバック

### Security
- SQLインジェクション対策の実装確認
- プレースホルダを使用したパラメータ化クエリ