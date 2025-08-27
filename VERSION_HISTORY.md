# Version History

This document tracks the version history of the instant search database system.

## Version 2.0 (In Development)
- **Status**: In Development
- **Purpose**: Generic database enhancement
- **Key Features**:
  - Configuration-driven system
  - Support for multiple use cases beyond gaming
  - Flexible field mapping
  - UI customization options
  - Example configurations for common scenarios

## Version 1.1 (Current/Backup)
- **Status**: Backed up on 2025-01-24
- **Purpose**: Game-specific instant search database
- **Backup Location**: `backups/v1.1/`
- **Key Features**:
  - Real-time search functionality
  - Game item database with categories (武器, 盾, 壺, etc.)
  - SQLite with FTS5 full-text search
  - Japanese language support
  - Responsive web interface
  - Docker containerization

### v1.1 System Components
- **Backend**: Flask (Python) with SQLite + FTS5
- **Frontend**: HTML/CSS/JavaScript with real-time search
- **Data**: CSV-based item loading with game-specific categories
- **UI**: Category-based navigation with Japanese interface

### v1.1 Restoration Instructions
To restore version 1.1:
1. Copy all files from `backups/v1.1/` to project root
2. Install dependencies: `pip install -r requirements.txt`
3. Run application: `python run_app.py`
4. Access at http://localhost:5000

## Migration Notes
- Version 2.0 maintains backward compatibility with v1.1 data
- Configuration files will be added to support generic use cases
- Original game-specific functionality will be preserved as a default configuration