import json
import os
import logging
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
import jsonschema
from jsonschema import validate, ValidationError

from .error_handler import ErrorHandler, ErrorContext, graceful_degradation
from .logging_system import get_logging_system, LogCategory, performance_monitor, log_configuration_change

# Configure logging
logger = get_logging_system().get_logger(LogCategory.CONFIGURATION)

@dataclass
class CategoryConfig:
    """Configuration for a single category"""
    display_name: str
    icon: str
    emoji_fallback: str
    color: str
    description: str = ""

@dataclass
class FieldMapping:
    """Configuration for field mapping"""
    csv_column: str
    display_name: str
    field_type: str = "string"
    searchable: bool = True
    required: bool = False
    description: str = ""

@dataclass
class UIConfig:
    """UI configuration settings"""
    title: str
    subtitle: str = ""
    theme: Dict[str, str] = None
    layout: Dict[str, Any] = None
    search: Dict[str, Any] = None
    categories: Dict[str, Any] = None

    def __post_init__(self):
        if self.theme is None:
            self.theme = {}
        if self.layout is None:
            self.layout = {}
        if self.search is None:
            self.search = {}
        if self.categories is None:
            self.categories = {}

class ConfigManager:
    """Manages configuration loading, validation, and fallback handling"""
    
    def __init__(self, config_dir: str = "config"):
        self.config_dir = config_dir
        self.schemas_dir = os.path.join(config_dir, "schemas")
        self.examples_dir = os.path.join(config_dir, "examples")
        
        # Cache for loaded configurations
        self._categories_cache: Optional[Dict[str, CategoryConfig]] = None
        self._fields_cache: Optional[Dict[str, Any]] = None
        self._ui_cache: Optional[UIConfig] = None
        
        # Error handler for comprehensive error management
        self.error_handler = ErrorHandler(logger)
        
        # Register recovery callbacks
        self._register_recovery_callbacks()
        
    def _register_recovery_callbacks(self):
        """Register recovery callbacks for error handling"""
        self.error_handler.register_recovery_callback(
            'create_default_config', 
            self._create_default_config_file
        )
        self.error_handler.register_recovery_callback(
            'validate_json_syntax',
            self._validate_json_syntax
        )
    
    def _create_default_config_file(self, error_info):
        """Recovery callback to create default configuration files"""
        try:
            file_path = error_info.context.file_path
            if not file_path:
                return
            
            if 'categories' in file_path:
                default_data = self._get_default_categories()
            elif 'fields' in file_path:
                default_data = self._get_default_fields()
            elif 'ui' in file_path:
                default_data = self._get_default_ui()
            else:
                return
            
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(default_data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Created default configuration file: {file_path}")
            
        except Exception as e:
            logger.error(f"Failed to create default config file: {e}")
    
    def _validate_json_syntax(self, error_info):
        """Recovery callback to validate JSON syntax"""
        try:
            file_path = error_info.context.file_path
            if not file_path or not os.path.exists(file_path):
                return
            
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Try to parse JSON and provide specific error information
            try:
                json.loads(content)
                logger.info(f"JSON syntax validation passed for {file_path}")
            except json.JSONDecodeError as e:
                logger.error(f"JSON syntax error in {file_path} at line {e.lineno}, column {e.colno}: {e.msg}")
                
        except Exception as e:
            logger.error(f"Failed to validate JSON syntax: {e}")

    @performance_monitor("config_load_json_file", LogCategory.CONFIGURATION)
    def _load_json_file(self, file_path: str, fallback_data: Dict[str, Any] = None) -> Dict[str, Any]:
        """Load JSON file with enhanced error handling and fallback"""
        context = ErrorContext(
            file_path=file_path,
            function_name="_load_json_file"
        )
        
        try:
            if not os.path.exists(file_path):
                error = FileNotFoundError(f"Configuration file not found: {file_path}")
                self.error_handler.handle_error(error, context, "config_file_not_found")
                
                if fallback_data:
                    logger.info(f"Using fallback data for {file_path}")
                    return fallback_data
                return {}
                
            with open(file_path, 'r', encoding='utf-8') as file:
                data = json.load(file)
                logger.info(f"Successfully loaded configuration from {file_path}")
                return data
                
        except json.JSONDecodeError as e:
            context.line_number = e.lineno
            context.additional_data = {"column": e.colno, "json_error": e.msg}
            error_info = self.error_handler.handle_error(e, context, "config_invalid_json")
            
            if fallback_data:
                logger.info(f"Using fallback data due to JSON error in {file_path}")
                return fallback_data
            return {}
            
        except PermissionError as e:
            error_info = self.error_handler.handle_error(e, context, "permission_denied")
            if fallback_data:
                return fallback_data
            return {}
            
        except Exception as e:
            error_info = self.error_handler.handle_error(e, context)
            if fallback_data:
                logger.info(f"Using fallback data due to error in {file_path}")
                return fallback_data
            return {}
    
    def _load_schema(self, schema_name: str) -> Optional[Dict[str, Any]]:
        """Load JSON schema for validation"""
        schema_path = os.path.join(self.schemas_dir, f"{schema_name}-schema.json")
        try:
            with open(schema_path, 'r', encoding='utf-8') as file:
                return json.load(file)
        except Exception as e:
            logger.warning(f"Could not load schema {schema_name}: {e}")
            return None
    
    def _validate_config(self, data: Dict[str, Any], schema_name: str) -> bool:
        """Validate configuration data against schema"""
        schema = self._load_schema(schema_name)
        if not schema:
            logger.warning(f"No schema available for {schema_name}, skipping validation")
            return True
            
        try:
            validate(instance=data, schema=schema)
            logger.info(f"Configuration validation passed for {schema_name}")
            return True
        except ValidationError as e:
            logger.error(f"Configuration validation failed for {schema_name}: {e.message}")
            return False
        except Exception as e:
            logger.error(f"Validation error for {schema_name}: {e}")
            return False
    
    def _get_default_categories(self) -> Dict[str, Any]:
        """Get default categories configuration"""
        return {
            "categories": {
                "武器": {
                    "display_name": "武器",
                    "icon": "fas fa-sword",
                    "emoji_fallback": "⚔️",
                    "color": "#e74c3c",
                    "description": "攻撃用の武器類"
                },
                "盾": {
                    "display_name": "盾",
                    "icon": "fas fa-shield-alt",
                    "emoji_fallback": "🛡️",
                    "color": "#3498db",
                    "description": "防御用の盾類"
                },
                "その他": {
                    "display_name": "その他",
                    "icon": "fas fa-question",
                    "emoji_fallback": "❓",
                    "color": "#95a5a6",
                    "description": "その他のアイテム"
                }
            }
        }
    
    def _get_default_fields(self) -> Dict[str, Any]:
        """Get default fields configuration"""
        return {
            "field_mappings": {
                "category": "category",
                "name": "name",
                "description": "description"
            },
            "display_fields": ["name", "description"],
            "search_fields": ["name", "description"],
            "required_fields": ["category", "name"]
        }
    
    def _get_default_ui(self) -> Dict[str, Any]:
        """Get default UI configuration"""
        return {
            "ui": {
                "title": "アイテム検索システム",
                "subtitle": "アイテムを素早く検索できます",
                "theme": {
                    "primary_color": "#3498db",
                    "secondary_color": "#2ecc71",
                    "accent_color": "#e74c3c"
                },
                "layout": {
                    "categories_per_row": 5,
                    "show_category_counts": True,
                    "enable_suggestions": True
                }
            }
        }
    
    @performance_monitor("config_load_categories", LogCategory.CONFIGURATION)
    def load_categories(self, force_reload: bool = False) -> Dict[str, CategoryConfig]:
        """Load categories configuration with enhanced caching and error handling"""
        if self._categories_cache is not None and not force_reload:
            return self._categories_cache
            
        categories_path = os.path.join(self.config_dir, "categories.json")
        fallback_data = self._get_default_categories()
        
        # Track configuration loading
        old_cache = self._categories_cache
        
        try:
            data = self._load_json_file(categories_path, fallback_data)
            
            # Validate configuration
            if not self._validate_config(data, "categories"):
                logger.warning("Using fallback categories due to validation failure")
                data = fallback_data
            
            # Convert to CategoryConfig objects with error handling
            categories = {}
            for key, config in data.get("categories", {}).items():
                try:
                    categories[key] = CategoryConfig(
                        display_name=config["display_name"],
                        icon=config["icon"],
                        emoji_fallback=config["emoji_fallback"],
                        color=config["color"],
                        description=config.get("description", "")
                    )
                except KeyError as e:
                    context = ErrorContext(
                        function_name="load_categories",
                        additional_data={"category_key": key, "config": config}
                    )
                    self.error_handler.handle_error(e, context)
                    continue
                except Exception as e:
                    context = ErrorContext(
                        function_name="load_categories",
                        additional_data={"category_key": key}
                    )
                    self.error_handler.handle_error(e, context)
                    continue
            
            self._categories_cache = categories
            
            # Log configuration change if cache was updated
            if old_cache != categories:
                log_configuration_change(
                    "categories",
                    len(old_cache) if old_cache else 0,
                    len(categories),
                    source="file_reload"
                )
            
            logger.info(f"Loaded {len(categories)} categories")
            return categories
            
        except Exception as e:
            context = ErrorContext(
                function_name="load_categories",
                file_path=categories_path
            )
            self.error_handler.handle_error(e, context)
            
            # Return cached data if available, otherwise fallback
            if self._categories_cache:
                logger.warning("Returning cached categories due to loading error")
                return self._categories_cache
            
            # Create fallback categories
            fallback_categories = {}
            for key, config in fallback_data.get("categories", {}).items():
                try:
                    fallback_categories[key] = CategoryConfig(
                        display_name=config["display_name"],
                        icon=config["icon"],
                        emoji_fallback=config["emoji_fallback"],
                        color=config["color"],
                        description=config.get("description", "")
                    )
                except Exception:
                    continue
            
            self._categories_cache = fallback_categories
            return fallback_categories
    
    def load_field_mappings(self, force_reload: bool = False) -> Dict[str, Any]:
        """Load field mappings configuration with caching"""
        if self._fields_cache is not None and not force_reload:
            return self._fields_cache
            
        fields_path = os.path.join(self.config_dir, "fields.json")
        fallback_data = self._get_default_fields()
        
        data = self._load_json_file(fields_path, fallback_data)
        
        # Validate configuration
        if not self._validate_config(data, "fields"):
            logger.warning("Using fallback fields due to validation failure")
            data = fallback_data
        
        self._fields_cache = data
        logger.info("Loaded field mappings configuration")
        return data
    
    def load_ui_settings(self, force_reload: bool = False) -> UIConfig:
        """Load UI settings configuration with caching"""
        if self._ui_cache is not None and not force_reload:
            return self._ui_cache
            
        ui_path = os.path.join(self.config_dir, "ui.json")
        fallback_data = self._get_default_ui()
        
        data = self._load_json_file(ui_path, fallback_data)
        
        # Validate configuration
        if not self._validate_config(data, "ui"):
            logger.warning("Using fallback UI settings due to validation failure")
            data = fallback_data
        
        # Convert to UIConfig object
        ui_data = data.get("ui", {})
        ui_config = UIConfig(
            title=ui_data.get("title", "アイテム検索システム"),
            subtitle=ui_data.get("subtitle", ""),
            theme=ui_data.get("theme", {}),
            layout=ui_data.get("layout", {}),
            search=ui_data.get("search", {}),
            categories=ui_data.get("categories", {})
        )
        
        self._ui_cache = ui_config
        logger.info("Loaded UI configuration")
        return ui_config
    
    def validate_all_configs(self) -> bool:
        """Validate all configuration files"""
        logger.info("Validating all configuration files...")
        
        all_valid = True
        
        # Validate categories
        try:
            self.load_categories(force_reload=True)
        except Exception as e:
            logger.error(f"Categories validation failed: {e}")
            all_valid = False
        
        # Validate fields
        try:
            self.load_field_mappings(force_reload=True)
        except Exception as e:
            logger.error(f"Fields validation failed: {e}")
            all_valid = False
        
        # Validate UI
        try:
            self.load_ui_settings(force_reload=True)
        except Exception as e:
            logger.error(f"UI validation failed: {e}")
            all_valid = False
        
        if all_valid:
            logger.info("All configurations are valid")
        else:
            logger.warning("Some configurations have validation issues")
        
        return all_valid
    
    def get_example_configs(self) -> List[str]:
        """Get list of available example configurations"""
        if not os.path.exists(self.examples_dir):
            return []
        
        examples = []
        try:
            for filename in os.listdir(self.examples_dir):
                if filename.endswith('.json'):
                    examples.append(filename[:-5])  # Remove .json extension
        except Exception as e:
            logger.error(f"Error listing example configurations: {e}")
        
        return examples
    
    def load_example_config(self, example_name: str) -> Optional[Dict[str, Any]]:
        """Load a specific example configuration"""
        example_path = os.path.join(self.examples_dir, f"{example_name}.json")
        
        if not os.path.exists(example_path):
            logger.error(f"Example configuration not found: {example_name}")
            return None
        
        try:
            with open(example_path, 'r', encoding='utf-8') as file:
                data = json.load(file)
                logger.info(f"Loaded example configuration: {example_name}")
                return data
        except Exception as e:
            logger.error(f"Error loading example configuration {example_name}: {e}")
            return None
    
    def clear_cache(self):
        """Clear all cached configurations"""
        old_categories_count = len(self._categories_cache) if self._categories_cache else 0
        old_fields_count = len(self._fields_cache) if self._fields_cache else 0
        
        self._categories_cache = None
        self._fields_cache = None
        self._ui_cache = None
        
        log_configuration_change(
            "cache_cleared",
            {"categories": old_categories_count, "fields": old_fields_count},
            {"categories": 0, "fields": 0},
            source="manual_clear"
        )
        
        logger.info("Configuration cache cleared")
    
    @graceful_degradation(lambda self: {})
    def get_error_summary(self) -> Dict[str, Any]:
        """Get error summary from the error handler"""
        return self.error_handler.get_error_summary()
    
    def get_recovery_suggestions(self, error_id: str) -> Optional[Dict[str, Any]]:
        """Get recovery suggestions for a specific error"""
        return self.error_handler.get_user_friendly_error(error_id)
    
    @performance_monitor("config_health_check", LogCategory.CONFIGURATION)
    def health_check(self) -> Dict[str, Any]:
        """Perform comprehensive health check of configuration system"""
        health_status = {
            "overall_status": "healthy",
            "timestamp": get_logging_system().performance_metrics[-1].timestamp.isoformat() if get_logging_system().performance_metrics else None,
            "checks": {}
        }
        
        issues = []
        
        # Check configuration directory
        try:
            if not os.path.exists(self.config_dir):
                issues.append("Configuration directory does not exist")
                health_status["checks"]["config_directory"] = {"status": "error", "message": "Directory missing"}
            else:
                health_status["checks"]["config_directory"] = {"status": "ok", "message": "Directory exists"}
        except Exception as e:
            issues.append(f"Cannot access configuration directory: {e}")
            health_status["checks"]["config_directory"] = {"status": "error", "message": str(e)}
        
        # Check each configuration file
        config_files = {
            "categories": "categories.json",
            "fields": "fields.json", 
            "ui": "ui.json"
        }
        
        for config_type, filename in config_files.items():
            try:
                file_path = os.path.join(self.config_dir, filename)
                if os.path.exists(file_path):
                    # Try to load and validate
                    with open(file_path, 'r', encoding='utf-8') as f:
                        json.load(f)
                    health_status["checks"][config_type] = {"status": "ok", "message": "File valid"}
                else:
                    health_status["checks"][config_type] = {"status": "warning", "message": "File missing, using defaults"}
            except json.JSONDecodeError as e:
                issues.append(f"Invalid JSON in {filename}: {e}")
                health_status["checks"][config_type] = {"status": "error", "message": f"Invalid JSON: {e}"}
            except Exception as e:
                issues.append(f"Error checking {filename}: {e}")
                health_status["checks"][config_type] = {"status": "error", "message": str(e)}
        
        # Check schemas directory
        try:
            if os.path.exists(self.schemas_dir):
                schema_count = len([f for f in os.listdir(self.schemas_dir) if f.endswith('.json')])
                health_status["checks"]["schemas"] = {"status": "ok", "message": f"{schema_count} schema files found"}
            else:
                health_status["checks"]["schemas"] = {"status": "warning", "message": "Schemas directory missing"}
        except Exception as e:
            health_status["checks"]["schemas"] = {"status": "error", "message": str(e)}
        
        # Check examples directory
        try:
            if os.path.exists(self.examples_dir):
                example_count = len([f for f in os.listdir(self.examples_dir) if f.endswith('.json')])
                health_status["checks"]["examples"] = {"status": "ok", "message": f"{example_count} example files found"}
            else:
                health_status["checks"]["examples"] = {"status": "warning", "message": "Examples directory missing"}
        except Exception as e:
            health_status["checks"]["examples"] = {"status": "error", "message": str(e)}
        
        # Determine overall status
        if issues:
            if any("error" in check.get("status", "") for check in health_status["checks"].values()):
                health_status["overall_status"] = "unhealthy"
            else:
                health_status["overall_status"] = "degraded"
            health_status["issues"] = issues
        
        return health_status