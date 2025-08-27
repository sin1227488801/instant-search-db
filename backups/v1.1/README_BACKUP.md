# System Backup v1.1

This directory contains a complete backup of the instant search database system version 1.1, created before implementing the generic database enhancement.

## Backup Information
- **Version**: v1.1
- **Backup Date**: 2025-01-24
- **Purpose**: Pre-enhancement backup before implementing generic database system
- **Original System**: Game-specific instant search database

## Contents
This backup includes all files from the original system:

### Core Application Files
- `instant_search_db/` - Main application package
  - `__init__.py` - Package initialization
  - `__main__.py` - Main entry point
  - `models.py` - Data models and database operations
  - `routes.py` - Flask routes and API endpoints

### Data Files
- `data/` - Data directory
  - `items.csv` - Main data file with game items
  - `items.csv更新用.txt` - Update instructions file
- `database.db` - SQLite database file

### Frontend Files
- `templates/` - HTML templates
  - `index.html` - Main application template
- `static/` - Static assets
  - `style.css` - Application styles

### Configuration Files
- `requirements.txt` - Python dependencies
- `run_app.py` - Application runner
- `docker-compose.yml` - Docker composition
- `Dockerfile` - Docker container definition
- `.gitignore` - Git ignore rules

### Documentation
- `README.md` - Original project documentation
- `docs/` - Additional documentation files

### Scripts
- `scripts/` - Setup and utility scripts

### Tests
- `tests/` - Test files

## Restoration Instructions
To restore this version:
1. Copy all files from this backup directory to the project root
2. Install dependencies: `pip install -r requirements.txt`
3. Run the application: `python run_app.py`

## Notes
- This backup was created automatically as part of the generic database enhancement implementation
- All original functionality should be preserved in this backup
- The database.db file contains the original SQLite database with FTS5 search capabilities