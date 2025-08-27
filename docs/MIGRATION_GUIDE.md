# Migration Guide: v1.1 to v2.0

This guide helps you migrate from the game-specific instant search database (v1.1) to the generic, configuration-driven system (v2.0).

## Overview

Version 2.0 transforms the system from a game-specific database into a generic, configurable database that can be adapted for various use cases while maintaining all existing functionality.

### Key Changes in v2.0

- **Configuration System**: JSON-based configuration files for categories, fields, and UI
- **Generic Data Model**: Flexible field mapping for different data types
- **Enhanced Error Handling**: Comprehensive error management and logging
- **Multiple Use Cases**: Pre-built configurations for common scenarios
- **Backward Compatibility**: Existing v1.1 data and functionality preserved

## Pre-Migration Checklist

Before starting the migration, ensure you have:

- [ ] **Backup Created**: Your v1.1 system is backed up in `backups/v1.1/`
- [ ] **Data Exported**: Current `data/items.csv` is saved
- [ ] **Custom Changes Documented**: Any customizations you've made are noted
- [ ] **Dependencies Updated**: Python environment meets v2.0 requirements

## Migration Steps

### Step 1: Verify Current System

First, verify your current v1.1 system is working:

```bash
# Test current system
python run_app.py
# Visit http://localhost:5000 to confirm functionality
```

### Step 2: Update Dependencies

Install new dependencies required for v2.0:

```bash
pip install -r requirements.txt
```

New dependencies include:
- `jsonschema` - Configuration validation
- Enhanced logging libraries

### Step 3: Configuration Migration

#### 3.1 Create Configuration Directory

The new system uses configuration files. These should already exist, but verify:

```bash
# Check configuration directory exists
ls -la config/
```

You should see:
- `categories.json` - Category definitions
- `fields.json` - Field mappings
- `ui.json` - UI customization
- `examples/` - Example configurations

#### 3.2 Migrate Your Categories

If you had custom categories in v1.1, update `config/categories.json`:

**Default v1.1 Categories:**
- 武器 (Weapons)
- 盾 (Shields)  
- 壺 (Pots)
- 巻物 (Scrolls)
- 草 (Herbs)
- 杖 (Staves)
- 腕輪 (Bracelets)
- その他 (Others)

**v2.0 Configuration Format:**
```json
{
  "categories": {
    "武器": {
      "display_name": "武器",
      "icon": "fas fa-sword",
      "emoji_fallback": "⚔️",
      "color": "#e74c3c",
      "description": "攻撃用の武器類"
    }
  }
}
```

#### 3.3 Configure Field Mappings

Update `config/fields.json` to match your CSV structure:

```json
{
  "field_mappings": {
    "category": "category",
    "name": "name", 
    "description": "description"
  },
  "display_fields": ["name", "description"],
  "search_fields": ["name", "description"],
  "required_fields": ["category", "name"]
}
```

#### 3.4 Customize UI Settings

Update `config/ui.json` for your preferred interface:

```json
{
  "ui": {
    "title": "ローグライクゲーム アイテム検索",
    "subtitle": "アイテムを素早く検索できます",
    "theme": {
      "primary_color": "#3498db",
      "secondary_color": "#2ecc71", 
      "accent_color": "#e74c3c"
    },
    "layout": {
      "categories_per_row": 5,
      "show_category_counts": true,
      "enable_suggestions": true
    }
  }
}
```

### Step 4: Data Migration

Your existing `data/items.csv` should work without changes. The system will:

1. **Automatically detect** your CSV structure
2. **Map fields** based on configuration
3. **Preserve all data** from v1.1

#### Verify Data Compatibility

```bash
# Check your CSV structure
head -5 data/items.csv
```

Expected format:
```csv
category,name,description
武器,ドラゴンキラー,竜系の敵に特効がある剣
盾,青銅の盾,基本的な防御力を持つ盾
```

### Step 5: Test Migration

Start the v2.0 system and verify functionality:

```bash
# Start v2.0 system
python run_app.py
```

**Verification Checklist:**
- [ ] Application starts without errors
- [ ] All categories display correctly
- [ ] Search functionality works
- [ ] Data appears as expected
- [ ] UI matches your preferences

### Step 6: Configuration Validation

Use the built-in validation tools:

```bash
# Access validation endpoint
curl http://localhost:5000/api/config/validate
```

Or visit the health check endpoint:
```bash
curl http://localhost:5000/api/system/health
```

## Troubleshooting Common Issues

### Issue 1: Configuration Not Loading

**Symptoms:** Default categories appear instead of your custom ones

**Solution:**
1. Check configuration file syntax:
   ```bash
   python -m json.tool config/categories.json
   ```
2. Verify file permissions
3. Check application logs for specific errors

### Issue 2: Data Not Displaying

**Symptoms:** Search returns no results or empty categories

**Solution:**
1. Verify CSV file path and format
2. Check field mappings in `config/fields.json`
3. Ensure database file exists and is readable

### Issue 3: UI Customization Not Applied

**Symptoms:** Interface uses default styling

**Solution:**
1. Validate `config/ui.json` syntax
2. Clear browser cache
3. Check for CSS conflicts

### Issue 4: Performance Issues

**Symptoms:** Slow search or high memory usage

**Solution:**
1. Check database indexes
2. Verify FTS5 is working:
   ```sql
   SELECT * FROM sqlite_master WHERE type='table' AND name LIKE '%fts%';
   ```
3. Monitor system resources

## Advanced Migration Scenarios

### Custom Code Changes

If you modified v1.1 code:

1. **Routes**: Update `instant_search_db/routes.py` to use configuration system
2. **Models**: Modify `instant_search_db/models.py` for custom data handling
3. **Templates**: Update `templates/index.html` for UI changes

### Multiple Environments

For different environments (dev/staging/prod):

1. Create environment-specific configuration files
2. Use environment variables for configuration paths
3. Set up separate data directories

### Large Datasets

For datasets larger than v1.1:

1. Enable database optimization
2. Configure search result limits
3. Implement pagination if needed

## Configuration Templates

### Game Database (v1.1 Compatible)

Use the default configuration or copy from `config/examples/game-database.json`

### Product Catalog

```json
{
  "categories": {
    "electronics": {
      "display_name": "Electronics",
      "icon": "fas fa-laptop",
      "emoji_fallback": "💻",
      "color": "#3498db"
    },
    "books": {
      "display_name": "Books", 
      "icon": "fas fa-book",
      "emoji_fallback": "📚",
      "color": "#e67e22"
    }
  }
}
```

### Document Library

```json
{
  "field_mappings": {
    "category": "document_type",
    "name": "title",
    "description": "summary",
    "author": "author",
    "date": "created_date"
  }
}
```

## Rollback Procedure

If you need to return to v1.1:

### Quick Rollback

```bash
# Stop v2.0 system
# Copy v1.1 backup files
cp -r backups/v1.1/* .
# Start v1.1 system
python run_app.py
```

### Selective Rollback

To keep some v2.0 improvements:

1. **Keep enhanced error handling**: Copy logging and error handling modules
2. **Preserve data**: Keep your updated `data/items.csv`
3. **Maintain Docker setup**: Use v2.0 Docker configuration

## Post-Migration Tasks

After successful migration:

### 1. Update Documentation

- [ ] Update your README.md with new configuration options
- [ ] Document any custom configurations
- [ ] Update deployment procedures

### 2. Team Training

- [ ] Train team members on new configuration system
- [ ] Share troubleshooting procedures
- [ ] Document customization workflows

### 3. Monitoring Setup

- [ ] Set up configuration change monitoring
- [ ] Configure error alerting
- [ ] Implement performance monitoring

### 4. Backup Strategy

- [ ] Update backup procedures for configuration files
- [ ] Test restore procedures
- [ ] Document recovery processes

## Support and Resources

### Configuration Examples

See `config/examples/` for:
- `product-catalog.json` - E-commerce product database
- `document-library.json` - Document management system
- `inventory-system.json` - Inventory tracking

### API Documentation

New v2.0 endpoints:
- `GET /api/config` - Current configuration
- `GET /api/config/validate` - Validate configuration
- `GET /api/config/examples` - Available examples
- `GET /api/system/health` - System health check

### Logging and Debugging

Enhanced logging in v2.0:
- Configuration changes tracked
- Performance metrics collected
- Error details with recovery suggestions

### Getting Help

1. **Check logs**: Look in `logs/` directory for detailed error information
2. **Health check**: Use `/api/system/health` endpoint
3. **Configuration validation**: Use `/api/config/validate` endpoint
4. **Error details**: Check `/api/system/errors` for specific error information

## Migration Checklist

Use this checklist to track your migration progress:

### Pre-Migration
- [ ] v1.1 system backed up
- [ ] Current data exported
- [ ] Dependencies updated
- [ ] Migration guide reviewed

### Configuration
- [ ] Configuration directory verified
- [ ] Categories migrated/configured
- [ ] Field mappings updated
- [ ] UI settings customized

### Testing
- [ ] Application starts successfully
- [ ] Configuration validation passes
- [ ] Data displays correctly
- [ ] Search functionality works
- [ ] UI appears as expected

### Post-Migration
- [ ] Performance verified
- [ ] Team trained
- [ ] Documentation updated
- [ ] Monitoring configured
- [ ] Backup procedures updated

## Conclusion

The migration from v1.1 to v2.0 enhances your system with powerful configuration capabilities while preserving all existing functionality. The new system provides:

- **Flexibility**: Easy adaptation for different use cases
- **Maintainability**: Configuration-driven changes without code modification
- **Reliability**: Enhanced error handling and logging
- **Scalability**: Better performance monitoring and optimization

With proper planning and testing, the migration should be smooth and provide immediate benefits for system customization and maintenance.
## Trou
bleshooting Migration Issues

### Common Error Messages and Solutions

#### "Configuration file not found"

**Error:** `FileNotFoundError: Configuration file not found: config/categories.json`

**Solution:**
1. Ensure configuration directory exists:
   ```bash
   mkdir -p config/examples config/schemas
   ```
2. Copy default configuration:
   ```bash
   cp config/examples/game-database.json config/categories.json
   ```

#### "Invalid JSON in configuration file"

**Error:** `json.JSONDecodeError: Expecting ',' delimiter`

**Solution:**
1. Validate JSON syntax:
   ```bash
   python -m json.tool config/categories.json
   ```
2. Common JSON errors:
   - Missing commas between objects
   - Trailing commas after last element
   - Unescaped quotes in strings
   - Missing closing brackets

#### "Database initialization failed"

**Error:** `sqlite3.OperationalError: no such table: items_fts`

**Solution:**
1. Delete existing database:
   ```bash
   rm database.db
   ```
2. Restart application to recreate database:
   ```bash
   python run_app.py
   ```

#### "Template not found"

**Error:** `jinja2.exceptions.TemplateNotFound: index.html`

**Solution:**
1. Verify template directory structure:
   ```bash
   ls -la templates/
   ```
2. Ensure `templates/index.html` exists
3. Check file permissions

### Performance Issues After Migration

#### Slow Search Performance

**Symptoms:** Search takes longer than v1.1

**Diagnosis:**
```bash
# Check if FTS5 is enabled
sqlite3 database.db "SELECT * FROM sqlite_master WHERE type='table' AND name LIKE '%fts%';"
```

**Solutions:**
1. Rebuild FTS index:
   ```sql
   INSERT INTO items_fts(items_fts) VALUES('rebuild');
   ```
2. Optimize database:
   ```sql
   VACUUM;
   ANALYZE;
   ```

#### High Memory Usage

**Symptoms:** Application uses more memory than v1.1

**Solutions:**
1. Check configuration cache:
   ```bash
   curl http://localhost:5000/api/system/health
   ```
2. Clear configuration cache if needed
3. Reduce logging level in production

### Data Migration Issues

#### Missing Categories

**Symptoms:** Items appear in "その他" category instead of correct category

**Solution:**
1. Check category mapping in CSV:
   ```bash
   cut -d',' -f1 data/items.csv | sort | uniq
   ```
2. Verify categories exist in `config/categories.json`
3. Update field mappings in `config/fields.json`

#### Search Returns No Results

**Symptoms:** Search functionality not working

**Diagnosis Steps:**
1. Check database content:
   ```sql
   SELECT COUNT(*) FROM items;
   SELECT * FROM items LIMIT 5;
   ```
2. Test FTS search:
   ```sql
   SELECT * FROM items_fts WHERE items_fts MATCH 'test';
   ```
3. Check application logs for errors

**Solutions:**
1. Reload data:
   ```bash
   # Delete database and restart
   rm database.db
   python run_app.py
   ```
2. Verify CSV format matches field mappings

### Configuration Issues

#### UI Customization Not Applied

**Symptoms:** Interface looks like default instead of custom styling

**Solution:**
1. Check `config/ui.json` syntax
2. Clear browser cache
3. Verify CSS custom properties are supported
4. Check browser developer tools for CSS errors

#### Icons Not Displaying

**Symptoms:** Category icons show as squares or missing

**Solutions:**
1. Verify Font Awesome is loaded:
   ```html
   <!-- Check in browser developer tools -->
   <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
   ```
2. Use emoji fallbacks:
   ```json
   {
     "icon": "fas fa-sword",
     "emoji_fallback": "⚔️"
   }
   ```
3. Check network connectivity for CDN resources

### Environment-Specific Issues

#### Docker Container Issues

**Error:** Container fails to start after migration

**Solution:**
1. Rebuild Docker image:
   ```bash
   docker-compose down
   docker-compose build --no-cache
   docker-compose up
   ```
2. Check volume mounts for configuration files
3. Verify environment variables

#### Permission Issues

**Error:** `PermissionError: [Errno 13] Permission denied`

**Solution:**
1. Check file permissions:
   ```bash
   ls -la config/
   chmod 644 config/*.json
   ```
2. Ensure application user has read access to configuration files
3. Check directory permissions:
   ```bash
   chmod 755 config/
   ```

### Recovery Procedures

#### Emergency Rollback

If migration fails completely:

```bash
# Stop current system
pkill -f "python run_app.py"

# Quick restore v1.1
cp -r backups/v1.1/* .

# Start v1.1 system
python run_app.py
```

#### Partial Recovery

To keep some v2.0 features while fixing issues:

1. **Keep enhanced logging:**
   ```bash
   # Copy only logging modules from v2.0
   cp instant_search_db/logging_system.py backups/v1.1/instant_search_db/
   cp instant_search_db/error_handler.py backups/v1.1/instant_search_db/
   ```

2. **Preserve data improvements:**
   ```bash
   # Keep updated data file
   cp data/items.csv backups/v1.1/data/
   ```

3. **Maintain configuration structure:**
   ```bash
   # Keep configuration directory for future migration
   cp -r config/ backups/v1.1/
   ```

### Getting Additional Help

#### Log Analysis

Check application logs for detailed error information:

```bash
# View recent logs
tail -f logs/application.log

# Search for specific errors
grep -i "error" logs/application.log | tail -20

# Check configuration-related logs
grep -i "config" logs/application.log | tail -10
```

#### System Health Check

Use built-in diagnostics:

```bash
# Comprehensive health check
curl -s http://localhost:5000/api/system/health | python -m json.tool

# Configuration validation
curl -s http://localhost:5000/api/config/validate | python -m json.tool

# Error summary
curl -s http://localhost:5000/api/system/errors | python -m json.tool
```

#### Debug Mode

Enable debug mode for detailed error information:

```bash
# Set debug environment variable
export FLASK_DEBUG=1
python run_app.py
```

#### Contact Information

For additional support:
1. Check system logs first
2. Use health check endpoints
3. Document specific error messages
4. Include configuration files (remove sensitive data)
5. Provide steps to reproduce the issue

Remember: The v2.0 system is designed to be backward compatible. Most v1.1 functionality should work without modification. If you encounter issues, the fallback mechanisms should allow the system to continue operating with default configurations.