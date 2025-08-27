"""
DataManager class for handling configurable CSV parsing, data validation, and backup functionality.
"""

import csv
import os
import json
import shutil
import re
from datetime import datetime
from typing import List, Dict, Any, Optional, Tuple
from pathlib import Path
import logging

from .data_models import Item, ValidationResult, DataStats
from .config_manager import ConfigManager
from .error_handler import ErrorHandler, ErrorContext, graceful_degradation
from .logging_system import get_logging_system, LogCategory, performance_monitor, log_user_action

# Configure logging
logger = get_logging_system().get_logger(LogCategory.DATA_MANAGEMENT)


class DataManager:
    """
    Manages data loading, validation, and backup operations with configurable field mappings.
    """
    
    def __init__(self, config_manager: ConfigManager):
        """
        Initialize DataManager with configuration.
        
        Args:
            config_manager: ConfigManager instance for accessing configurations
        """
        self.config_manager = config_manager
        self.backup_dir = Path("backups")
        self.backup_dir.mkdir(exist_ok=True)
        self.validation_schema = None
        
        # Error handler for comprehensive error management
        self.error_handler = ErrorHandler(logger)
        
        # Register recovery callbacks
        self._register_recovery_callbacks()
        
        # Load validation schema with error handling
        self._load_validation_schema()
    
    def _register_recovery_callbacks(self):
        """Register recovery callbacks for error handling"""
        self.error_handler.register_recovery_callback(
            'create_sample_csv',
            self._create_sample_csv_file
        )
        self.error_handler.register_recovery_callback(
            'validate_csv_structure',
            self._validate_csv_structure_callback
        )
        self.error_handler.register_recovery_callback(
            'create_default_schema',
            self._create_default_schema_callback
        )
    
    def _create_sample_csv_file(self, error_info):
        """Recovery callback to create sample CSV file"""
        try:
            file_path = error_info.context.file_path
            if not file_path:
                return
            
            # Create sample CSV data
            sample_data = [
                ["category", "name", "description"],
                ["武器", "つるはし", "攻 1 買 240 補正 12 売 100 補正 7テ ○掛 拾食 ×フェイ ○変 ○鍛 ×能力 壁を掘れるが、何度か掘ると壊れる"],
                ["盾", "皮甲の盾", "防 2 買 1000 補正 40 売 350 補正 20テ ○掛 －食 ○フェイ ○変 ○鍛 －能力 錆びない。満腹度の減りが1/2になる"],
                ["その他", "薬草", "HPが25回復する。HPが最大の時に飲むとHPの最大値が1上昇。"]
            ]
            
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            with open(file_path, 'w', encoding='utf-8', newline='') as f:
                writer = csv.writer(f)
                writer.writerows(sample_data)
            
            logger.info(f"Created sample CSV file: {file_path}")
            
        except Exception as e:
            logger.error(f"Failed to create sample CSV file: {e}")
    
    def _validate_csv_structure_callback(self, error_info):
        """Recovery callback to validate CSV structure"""
        try:
            file_path = error_info.context.file_path
            if not file_path or not os.path.exists(file_path):
                return
            
            validation_result = self.validate_csv_structure(file_path)
            if validation_result.errors:
                logger.error(f"CSV structure validation failed: {validation_result.errors}")
            else:
                logger.info(f"CSV structure validation passed for {file_path}")
                
        except Exception as e:
            logger.error(f"Failed to validate CSV structure: {e}")
    
    def _create_default_schema_callback(self, error_info):
        """Recovery callback to create default validation schema"""
        try:
            self._create_default_validation_schema()
            logger.info("Created default validation schema")
        except Exception as e:
            logger.error(f"Failed to create default validation schema: {e}")

    @performance_monitor("data_load_with_mapping", LogCategory.DATA_MANAGEMENT)
    def load_data_with_mapping(self, csv_path: str, field_mapping: Optional[Dict[str, str]] = None) -> Tuple[List[Item], ValidationResult]:
        """
        Load data from CSV file using configurable field mappings with enhanced error handling.
        
        Args:
            csv_path: Path to the CSV file
            field_mapping: Optional field mapping dictionary. If None, uses config.
            
        Returns:
            Tuple of (items list, validation result)
        """
        validation_result = ValidationResult(is_valid=True)
        items = []
        
        context = ErrorContext(
            file_path=csv_path,
            function_name="load_data_with_mapping"
        )
        
        # Log user action
        log_user_action("load_csv_data", additional_data={"file_path": csv_path})
        
        # Get field mapping from config if not provided
        if field_mapping is None:
            try:
                field_config = self.config_manager.load_field_mappings()
                field_mapping = field_config.get('field_mappings', {})
            except Exception as e:
                error_info = self.error_handler.handle_error(e, context)
                validation_result.add_error(f"Failed to load field mappings: {str(e)}")
                return items, validation_result
        
        # Check if CSV file exists
        if not os.path.exists(csv_path):
            error = FileNotFoundError(f"CSV file not found: {csv_path}")
            self.error_handler.handle_error(error, context, "csv_file_not_found")
            validation_result.add_error(f"CSV file not found: {csv_path}")
            return items, validation_result
        
        try:
            with open(csv_path, 'r', encoding='utf-8') as file:
                # Detect CSV dialect with error handling
                try:
                    sample = file.read(1024)
                    file.seek(0)
                    sniffer = csv.Sniffer()
                    dialect = sniffer.sniff(sample)
                except csv.Error as e:
                    logger.warning(f"Could not detect CSV dialect: {e}. Using default.")
                    dialect = csv.excel
                
                reader = csv.DictReader(file, dialect=dialect)
                
                # Validate CSV headers
                csv_headers = reader.fieldnames or []
                if not csv_headers:
                    error = ValueError("CSV file has no headers")
                    self.error_handler.handle_error(error, context, "csv_invalid_format")
                    validation_result.add_error("CSV file has no headers")
                    return items, validation_result
                
                missing_mappings = []
                for field_name, csv_column in field_mapping.items():
                    if csv_column not in csv_headers:
                        missing_mappings.append(f"Field '{field_name}' maps to missing CSV column '{csv_column}'")
                
                if missing_mappings:
                    for missing in missing_mappings:
                        validation_result.add_warning(missing)
                
                # Process each row with enhanced error handling
                row_number = 1
                for row in reader:
                    row_number += 1
                    
                    try:
                        item = self._create_item_from_row(row, field_mapping, row_number, validation_result)
                        if item:
                            items.append(item)
                    except Exception as e:
                        row_context = ErrorContext(
                            file_path=csv_path,
                            line_number=row_number,
                            function_name="_create_item_from_row",
                            additional_data={"row_data": row}
                        )
                        self.error_handler.handle_error(e, row_context)
                        validation_result.add_error(f"Error processing row {row_number}: {str(e)}")
                
                validation_result.add_warning(f"Loaded {len(items)} items from {csv_path}")
                
                # Log successful data loading
                logger.info(f"Successfully loaded {len(items)} items from {csv_path}")
                
        except PermissionError as e:
            self.error_handler.handle_error(e, context, "permission_denied")
            validation_result.add_error(f"Permission denied accessing CSV file: {csv_path}")
        except UnicodeDecodeError as e:
            context.additional_data = {"encoding_error": str(e)}
            self.error_handler.handle_error(e, context)
            validation_result.add_error(f"Encoding error reading CSV file: {str(e)}")
        except Exception as e:
            self.error_handler.handle_error(e, context)
            validation_result.add_error(f"Failed to read CSV file: {str(e)}")
        
        return items, validation_result
    
    def _create_item_from_row(self, row: Dict[str, str], field_mapping: Dict[str, str], 
                             row_number: int, validation_result: ValidationResult) -> Optional[Item]:
        """
        Create an Item from a CSV row using field mappings.
        
        Args:
            row: CSV row data
            field_mapping: Field mapping configuration
            row_number: Current row number for error reporting
            validation_result: Validation result to add warnings/errors
            
        Returns:
            Item instance or None if creation failed
        """
        try:
            item = Item()
            custom_fields = {}
            
            # Map standard fields
            for field_name, csv_column in field_mapping.items():
                if csv_column in row:
                    value = row[csv_column].strip() if row[csv_column] else ""
                    
                    if field_name == 'category':
                        item.category = value
                    elif field_name == 'name':
                        item.name = value
                    elif field_name == 'description':
                        item.description = value
                    else:
                        # Custom field
                        custom_fields[field_name] = self._convert_field_value(value, field_name)
            
            # Set custom fields
            item.custom_fields = custom_fields
            
            # Validate required fields
            field_config = self.config_manager.load_field_mappings()
            required_fields = field_config.get('required_fields', ['category', 'name'])
            
            for required_field in required_fields:
                if required_field == 'category' and not item.category:
                    validation_result.add_warning(f"Row {row_number}: Missing required field 'category'")
                elif required_field == 'name' and not item.name:
                    validation_result.add_warning(f"Row {row_number}: Missing required field 'name'")
                elif required_field in custom_fields and not custom_fields[required_field]:
                    validation_result.add_warning(f"Row {row_number}: Missing required field '{required_field}'")
            
            return item
            
        except Exception as e:
            validation_result.add_error(f"Row {row_number}: Failed to create item - {str(e)}")
            return None
    
    def _convert_field_value(self, value: str, field_name: str) -> Any:
        """
        Convert field value to appropriate type based on field configuration.
        
        Args:
            value: String value from CSV
            field_name: Name of the field
            
        Returns:
            Converted value
        """
        if not value:
            return None
        
        try:
            field_config = self.config_manager.load_field_mappings()
            field_definitions = field_config.get('field_definitions', {})
            
            if field_name in field_definitions:
                field_type = field_definitions[field_name].get('type', 'string')
                
                if field_type == 'integer':
                    return int(value)
                elif field_type == 'float':
                    return float(value)
                elif field_type == 'boolean':
                    return value.lower() in ('true', '1', 'yes', 'on', '○')
                elif field_type == 'json':
                    return json.loads(value)
        except (ValueError, json.JSONDecodeError, KeyError):
            # If conversion fails, return as string
            pass
        
        return value
    
    def _validate_field_type(self, value: Any, expected_type: str) -> bool:
        """
        Validate that a value matches the expected type.
        
        Args:
            value: Value to validate
            expected_type: Expected type string
            
        Returns:
            True if value matches expected type
        """
        if expected_type == "string":
            return isinstance(value, str)
        elif expected_type == "integer":
            return isinstance(value, int) and not isinstance(value, bool)
        elif expected_type == "float":
            return isinstance(value, (int, float)) and not isinstance(value, bool)
        elif expected_type == "boolean":
            return isinstance(value, bool)
        elif expected_type == "text":
            return isinstance(value, str)
        else:
            # Unknown type, assume valid
            return True
    
    def validate_data(self, items: List[Item], schema: Optional[Dict] = None) -> ValidationResult:
        """
        Validate data based on schema configuration.
        
        Args:
            items: List of items to validate
            schema: Optional validation schema. If None, uses loaded schema or creates default.
            
        Returns:
            ValidationResult with validation details
        """
        # Use comprehensive validation if schema is available
        if schema or self.validation_schema:
            if schema:
                # Temporarily use provided schema
                original_schema = self.validation_schema
                self.validation_schema = schema
                result = self.validate_data_comprehensive(items)
                self.validation_schema = original_schema
                return result
            else:
                return self.validate_data_comprehensive(items)
        
        # Fallback to basic validation
        validation_result = ValidationResult(is_valid=True)
        
        if not items:
            validation_result.add_warning("No items to validate")
            return validation_result
        
        try:
            # Get field configuration for validation
            field_config = self.config_manager.load_field_mappings()
            field_definitions = field_config.get('field_definitions', {})
            required_fields = field_config.get('required_fields', [])
            
            # Validate each item
            for i, item in enumerate(items):
                item_errors = []
                
                # Check required fields
                for required_field in required_fields:
                    value = item.get_field_value(required_field)
                    if not value:
                        item_errors.append(f"Missing required field '{required_field}'")
                
                # Validate field types and constraints
                for field_name, field_def in field_definitions.items():
                    value = item.get_field_value(field_name)
                    
                    if value is not None:
                        # Type validation
                        expected_type = field_def.get('type', 'string')
                        if not self._validate_field_type(value, expected_type):
                            item_errors.append(f"Field '{field_name}' has invalid type (expected {expected_type})")
                        
                        # Length validation for strings
                        if expected_type in ('string', 'text') and isinstance(value, str):
                            max_length = field_def.get('max_length')
                            if max_length and len(value) > max_length:
                                item_errors.append(f"Field '{field_name}' exceeds maximum length ({max_length})")
                        
                        # Range validation for numbers
                        if expected_type in ('integer', 'float') and isinstance(value, (int, float)):
                            min_value = field_def.get('min_value')
                            max_value = field_def.get('max_value')
                            
                            if min_value is not None and value < min_value:
                                item_errors.append(f"Field '{field_name}' below minimum value ({min_value})")
                            if max_value is not None and value > max_value:
                                item_errors.append(f"Field '{field_name}' above maximum value ({max_value})")
                
                # Add item errors to validation result
                if item_errors:
                    for error in item_errors:
                        validation_result.add_error(f"Item {i + 1}: {error}")
            
            if validation_result.is_valid:
                validation_result.add_warning(f"Successfully validated {len(items)} items (basic validation)")
            
        except Exception as e:
            validation_result.add_error(f"Validation failed: {str(e)}")
        
        return validation_result
    
    def create_backup(self, source_path: str) -> str:
        """
        Create a backup of a file or directory.
        
        Args:
            source_path: Path to source file or directory
            
        Returns:
            Path to created backup
            
        Raises:
            FileNotFoundError: If source doesn't exist
        """
        if not os.path.exists(source_path):
            raise FileNotFoundError(f"Source path not found: {source_path}")
        
        # Generate backup name with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        source_name = os.path.basename(source_path)
        backup_name = f"{source_name}_backup_{timestamp}"
        backup_path = self.backup_dir / backup_name
        
        try:
            if os.path.isfile(source_path):
                # Backup file
                shutil.copy2(source_path, backup_path)
                backup_type = "file"
            else:
                # Backup directory
                shutil.copytree(source_path, backup_path)
                backup_type = "directory"
            
            # Create metadata file
            metadata = {
                "source_path": source_path,
                "backup_path": str(backup_path),
                "created_at": datetime.now().isoformat(),
                "backup_type": backup_type
            }
            
            metadata_path = self.backup_dir / f"{backup_name}_metadata.json"
            with open(metadata_path, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, indent=2)
            
            return str(backup_path)
            
        except Exception as e:
            raise IOError(f"Failed to create backup: {str(e)}")
    
    def _load_validation_schema(self) -> None:
        """Load validation schema from configuration files."""
        try:
            # Try to load validation.json first
            validation_path = Path("data/validation.json")
            if validation_path.exists():
                with open(validation_path, 'r', encoding='utf-8') as f:
                    self.validation_schema = json.load(f)
                logger.info("Loaded validation schema from data/validation.json")
            else:
                # Create default validation schema
                self._create_default_validation_schema()
                logger.info("Created default validation schema")
        except Exception as e:
            logger.error(f"Failed to load validation schema: {e}")
            self._create_default_validation_schema()
    
    def _create_default_validation_schema(self) -> None:
        """Create a default validation schema based on field configuration."""
        try:
            field_config = self.config_manager.load_field_mappings()
            categories_config = self.config_manager.load_categories()
            
            # Build validation rules from configuration
            validation_rules = {
                "required_columns": field_config.get('required_fields', ['category', 'name']),
                "field_types": {},
                "data_quality": {
                    "allow_empty_values": False,
                    "trim_whitespace": True,
                    "normalize_case": "none",
                    "duplicate_handling": "warn"
                },
                "custom_validators": []
            }
            
            # Add field type definitions
            field_definitions = field_config.get('field_definitions', {})
            for field_name, field_def in field_definitions.items():
                validation_rules["field_types"][field_name] = {
                    "type": field_def.get('type', 'string'),
                    "required": field_def.get('required', False),
                    "description": field_def.get('description', '')
                }
                
                # Add length constraints for strings
                if field_def.get('type') in ('string', 'text'):
                    if 'max_length' in field_def:
                        validation_rules["field_types"][field_name]["max_length"] = field_def['max_length']
            
            # Add category validation if categories are configured
            if categories_config:
                category_names = list(categories_config.keys())
                if 'category' in validation_rules["field_types"]:
                    validation_rules["field_types"]["category"]["allowed_values"] = category_names
                
                validation_rules["custom_validators"].append({
                    "name": "category_consistency",
                    "field": "category",
                    "rule": "must_exist_in_categories_config",
                    "message": "Category must be defined in categories configuration"
                })
            
            self.validation_schema = {"validation_rules": validation_rules}
            
        except Exception as e:
            logger.error(f"Failed to create default validation schema: {e}")
            # Minimal fallback schema
            self.validation_schema = {
                "validation_rules": {
                    "required_columns": ["category", "name"],
                    "field_types": {
                        "category": {"type": "string", "required": True},
                        "name": {"type": "string", "required": True},
                        "description": {"type": "text", "required": False}
                    },
                    "data_quality": {
                        "allow_empty_values": False,
                        "trim_whitespace": True,
                        "normalize_case": "none",
                        "duplicate_handling": "warn"
                    },
                    "custom_validators": []
                }
            }
    
    def validate_csv_structure(self, csv_path: str) -> ValidationResult:
        """
        Validate CSV file structure before loading data.
        
        Args:
            csv_path: Path to CSV file
            
        Returns:
            ValidationResult with structure validation details
        """
        validation_result = ValidationResult(is_valid=True)
        
        if not os.path.exists(csv_path):
            validation_result.add_error(f"CSV file not found: {csv_path}")
            return validation_result
        
        try:
            with open(csv_path, 'r', encoding='utf-8') as file:
                # Check if file is empty
                file.seek(0, 2)  # Seek to end
                if file.tell() == 0:
                    validation_result.add_error("CSV file is empty")
                    return validation_result
                
                file.seek(0)  # Reset to beginning
                
                # Read first few lines to detect structure
                sample = file.read(1024)
                file.seek(0)
                
                # Detect CSV dialect
                try:
                    sniffer = csv.Sniffer()
                    dialect = sniffer.sniff(sample)
                except csv.Error:
                    validation_result.add_warning("Could not detect CSV dialect, using default")
                    dialect = csv.excel
                
                # Read headers
                reader = csv.DictReader(file, dialect=dialect)
                headers = reader.fieldnames or []
                
                if not headers:
                    validation_result.add_error("CSV file has no headers")
                    return validation_result
                
                # Validate required columns
                if self.validation_schema:
                    required_columns = self.validation_schema.get('validation_rules', {}).get('required_columns', [])
                    field_mappings = self.config_manager.load_field_mappings().get('field_mappings', {})
                    
                    for required_field in required_columns:
                        mapped_column = field_mappings.get(required_field, required_field)
                        if mapped_column not in headers:
                            validation_result.add_error(f"Required column '{mapped_column}' not found in CSV")
                
                # Check for duplicate headers
                if len(headers) != len(set(headers)):
                    duplicates = [h for h in headers if headers.count(h) > 1]
                    validation_result.add_error(f"Duplicate column headers found: {set(duplicates)}")
                
                # Count rows for statistics
                row_count = sum(1 for _ in reader)
                validation_result.add_warning(f"CSV structure validation passed. Found {len(headers)} columns and {row_count} data rows")
                
        except Exception as e:
            validation_result.add_error(f"Failed to validate CSV structure: {str(e)}")
        
        return validation_result
    
    def validate_field_value(self, field_name: str, value: Any, field_rules: Dict[str, Any], 
                           row_number: int = None) -> List[str]:
        """
        Validate a single field value against its rules.
        
        Args:
            field_name: Name of the field
            value: Value to validate
            field_rules: Validation rules for the field
            row_number: Optional row number for error reporting
            
        Returns:
            List of validation error messages
        """
        errors = []
        row_prefix = f"Row {row_number}: " if row_number else ""
        
        # Check if required field is empty
        if field_rules.get('required', False) and (value is None or value == ""):
            errors.append(f"{row_prefix}Required field '{field_name}' is empty")
            return errors
        
        # Skip further validation if value is empty and not required
        if value is None or value == "":
            return errors
        
        # Type validation
        field_type = field_rules.get('type', 'string')
        if not self._validate_field_type(value, field_type):
            errors.append(f"{row_prefix}Field '{field_name}' has invalid type (expected {field_type}, got {type(value).__name__})")
        
        # String/text specific validations
        if field_type in ('string', 'text') and isinstance(value, str):
            # Length validation
            min_length = field_rules.get('min_length')
            max_length = field_rules.get('max_length')
            
            if min_length is not None and len(value) < min_length:
                errors.append(f"{row_prefix}Field '{field_name}' is too short (minimum {min_length} characters)")
            
            if max_length is not None and len(value) > max_length:
                errors.append(f"{row_prefix}Field '{field_name}' is too long (maximum {max_length} characters)")
            
            # Pattern validation
            pattern = field_rules.get('pattern')
            if pattern:
                try:
                    if not re.match(pattern, value):
                        errors.append(f"{row_prefix}Field '{field_name}' does not match required pattern")
                except re.error:
                    errors.append(f"{row_prefix}Invalid regex pattern for field '{field_name}'")
            
            # Allowed values validation
            allowed_values = field_rules.get('allowed_values')
            if allowed_values and value not in allowed_values:
                errors.append(f"{row_prefix}Field '{field_name}' has invalid value. Allowed values: {allowed_values}")
        
        # Numeric validations
        if field_type in ('integer', 'float') and isinstance(value, (int, float)):
            min_value = field_rules.get('min_value')
            max_value = field_rules.get('max_value')
            
            if min_value is not None and value < min_value:
                errors.append(f"{row_prefix}Field '{field_name}' is below minimum value ({min_value})")
            
            if max_value is not None and value > max_value:
                errors.append(f"{row_prefix}Field '{field_name}' is above maximum value ({max_value})")
        
        # Email validation
        if field_type == 'email' and isinstance(value, str):
            email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
            if not re.match(email_pattern, value):
                errors.append(f"{row_prefix}Field '{field_name}' is not a valid email address")
        
        # URL validation
        if field_type == 'url' and isinstance(value, str):
            url_pattern = r'^https?://[^\s/$.?#].[^\s]*$'
            if not re.match(url_pattern, value):
                errors.append(f"{row_prefix}Field '{field_name}' is not a valid URL")
        
        return errors
    
    def validate_data_comprehensive(self, items: List[Item]) -> ValidationResult:
        """
        Comprehensive data validation using loaded schema.
        
        Args:
            items: List of items to validate
            
        Returns:
            ValidationResult with detailed validation information
        """
        validation_result = ValidationResult(is_valid=True)
        
        if not items:
            validation_result.add_warning("No items to validate")
            return validation_result
        
        if not self.validation_schema:
            validation_result.add_warning("No validation schema loaded, performing basic validation")
            return self.validate_data(items)
        
        try:
            validation_rules = self.validation_schema.get('validation_rules', {})
            field_types = validation_rules.get('field_types', {})
            data_quality = validation_rules.get('data_quality', {})
            custom_validators = validation_rules.get('custom_validators', [])
            
            # Track duplicates if needed
            duplicate_check = data_quality.get('duplicate_handling', 'warn') != 'allow'
            seen_items = set() if duplicate_check else None
            
            # Validate each item
            for i, item in enumerate(items, 1):
                # Validate individual fields
                for field_name, field_rules in field_types.items():
                    value = item.get_field_value(field_name)
                    
                    # Apply data quality rules
                    if isinstance(value, str) and data_quality.get('trim_whitespace', True):
                        value = value.strip()
                        item.set_field_value(field_name, value)
                    
                    # Normalize case if specified
                    case_rule = data_quality.get('normalize_case', 'none')
                    if isinstance(value, str) and case_rule != 'none':
                        if case_rule == 'lower':
                            value = value.lower()
                        elif case_rule == 'upper':
                            value = value.upper()
                        elif case_rule == 'title':
                            value = value.title()
                        item.set_field_value(field_name, value)
                    
                    # Validate field
                    field_errors = self.validate_field_value(field_name, value, field_rules, i)
                    for error in field_errors:
                        validation_result.add_error(error)
                
                # Check for duplicates
                if duplicate_check:
                    item_key = (item.category, item.name)
                    if item_key in seen_items:
                        duplicate_action = data_quality.get('duplicate_handling', 'warn')
                        message = f"Item {i}: Duplicate found - Category: '{item.category}', Name: '{item.name}'"
                        
                        if duplicate_action == 'error':
                            validation_result.add_error(message)
                        else:
                            validation_result.add_warning(message)
                    else:
                        seen_items.add(item_key)
                
                # Apply custom validators
                for validator in custom_validators:
                    try:
                        self._apply_custom_validator(item, validator, i, validation_result)
                    except Exception as e:
                        validation_result.add_error(f"Item {i}: Custom validator '{validator.get('name', 'unknown')}' failed: {str(e)}")
            
            # Summary
            if validation_result.is_valid:
                validation_result.add_warning(f"Successfully validated {len(items)} items with comprehensive schema")
            else:
                validation_result.add_warning(f"Validation completed with errors for {len(items)} items")
                
        except Exception as e:
            validation_result.add_error(f"Comprehensive validation failed: {str(e)}")
        
        return validation_result
    
    def _apply_custom_validator(self, item: Item, validator: Dict[str, str], 
                              row_number: int, validation_result: ValidationResult) -> None:
        """
        Apply a custom validator to an item.
        
        Args:
            item: Item to validate
            validator: Custom validator configuration
            row_number: Row number for error reporting
            validation_result: ValidationResult to add errors/warnings
        """
        validator_name = validator.get('name', 'unknown')
        field_name = validator.get('field')
        rule = validator.get('rule')
        message = validator.get('message', f'Custom validation failed for {field_name}')
        
        if not field_name or not rule:
            return
        
        field_value = item.get_field_value(field_name)
        
        try:
            if rule == 'must_exist_in_categories_config':
                # Check if category exists in configuration
                categories_config = self.config_manager.load_categories()
                if field_value and field_value not in categories_config:
                    validation_result.add_error(f"Item {row_number}: {message} (found: '{field_value}')")
            
            elif rule.startswith('regex:'):
                # Regex validation
                pattern = rule[6:]  # Remove 'regex:' prefix
                if field_value and not re.match(pattern, str(field_value)):
                    validation_result.add_error(f"Item {row_number}: {message}")
            
            elif rule.startswith('length_between:'):
                # Length range validation
                range_parts = rule[15:].split(',')  # Remove 'length_between:' prefix
                if len(range_parts) == 2:
                    min_len, max_len = int(range_parts[0]), int(range_parts[1])
                    if field_value and not (min_len <= len(str(field_value)) <= max_len):
                        validation_result.add_error(f"Item {row_number}: {message}")
            
            elif rule == 'not_empty':
                # Non-empty validation
                if not field_value or (isinstance(field_value, str) and not field_value.strip()):
                    validation_result.add_error(f"Item {row_number}: {message}")
            
            else:
                validation_result.add_warning(f"Item {row_number}: Unknown custom validator rule: {rule}")
                
        except Exception as e:
            validation_result.add_error(f"Item {row_number}: Custom validator '{validator_name}' error: {str(e)}")
    
    def generate_validation_report(self, validation_result: ValidationResult, 
                                 output_path: Optional[str] = None) -> str:
        """
        Generate a detailed validation report.
        
        Args:
            validation_result: ValidationResult to generate report from
            output_path: Optional path to save report file
            
        Returns:
            Report content as string
        """
        report_lines = []
        report_lines.append("=" * 60)
        report_lines.append("DATA VALIDATION REPORT")
        report_lines.append("=" * 60)
        report_lines.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report_lines.append("")
        
        # Summary
        report_lines.append("SUMMARY")
        report_lines.append("-" * 20)
        report_lines.append(f"Overall Status: {'PASSED' if validation_result.is_valid else 'FAILED'}")
        report_lines.append(f"Total Errors: {len(validation_result.errors)}")
        report_lines.append(f"Total Warnings: {len(validation_result.warnings)}")
        report_lines.append("")
        
        # Errors
        if validation_result.errors:
            report_lines.append("ERRORS")
            report_lines.append("-" * 20)
            for i, error in enumerate(validation_result.errors, 1):
                report_lines.append(f"{i:3d}. {error}")
            report_lines.append("")
        
        # Warnings
        if validation_result.warnings:
            report_lines.append("WARNINGS")
            report_lines.append("-" * 20)
            for i, warning in enumerate(validation_result.warnings, 1):
                report_lines.append(f"{i:3d}. {warning}")
            report_lines.append("")
        
        # Recommendations
        report_lines.append("RECOMMENDATIONS")
        report_lines.append("-" * 20)
        if validation_result.errors:
            report_lines.append("• Fix all errors before proceeding with data import")
            report_lines.append("• Review field mappings and data types in configuration")
            report_lines.append("• Check CSV file format and encoding")
        else:
            report_lines.append("• Data validation passed successfully")
            if validation_result.warnings:
                report_lines.append("• Review warnings for potential data quality improvements")
        
        report_content = "\n".join(report_lines)
        
        # Save to file if path provided
        if output_path:
            try:
                with open(output_path, 'w', encoding='utf-8') as f:
                    f.write(report_content)
                logger.info(f"Validation report saved to {output_path}")
            except Exception as e:
                logger.error(f"Failed to save validation report: {e}")
        
        return report_content
    
    def setup_backup_directory_structure(self) -> None:
        """
        Create organized backup directory structure with proper naming convention.
        """
        try:
            # Create main backup directory
            self.backup_dir.mkdir(exist_ok=True)
            
            # Create subdirectories for different backup types
            subdirs = ['data', 'config', 'database', 'full_system']
            for subdir in subdirs:
                (self.backup_dir / subdir).mkdir(exist_ok=True)
            
            # Create retention policy file if it doesn't exist
            retention_policy_path = self.backup_dir / "retention_policy.json"
            if not retention_policy_path.exists():
                default_policy = {
                    "retention_rules": {
                        "daily_backups": {
                            "keep_days": 7,
                            "description": "Keep daily backups for 7 days"
                        },
                        "weekly_backups": {
                            "keep_weeks": 4,
                            "description": "Keep weekly backups for 4 weeks"
                        },
                        "monthly_backups": {
                            "keep_months": 12,
                            "description": "Keep monthly backups for 12 months"
                        }
                    },
                    "max_backup_size_mb": 1000,
                    "auto_cleanup_enabled": True
                }
                
                with open(retention_policy_path, 'w', encoding='utf-8') as f:
                    json.dump(default_policy, f, indent=2)
                
                logger.info("Created default backup retention policy")
            
            logger.info("Backup directory structure initialized")
            
        except Exception as e:
            logger.error(f"Failed to setup backup directory structure: {e}")
            raise
    
    def create_automatic_backup(self, source_path: str, backup_type: str = "data", 
                              description: str = None) -> str:
        """
        Create an automatic backup with proper naming and metadata.
        
        Args:
            source_path: Path to source file or directory
            backup_type: Type of backup (data, config, database, full_system)
            description: Optional description for the backup
            
        Returns:
            Path to created backup
        """
        if not os.path.exists(source_path):
            raise FileNotFoundError(f"Source path not found: {source_path}")
        
        # Ensure backup directory structure exists
        self.setup_backup_directory_structure()
        
        # Generate backup name with timestamp and type
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        source_name = os.path.basename(source_path)
        backup_name = f"{backup_type}_{source_name}_{timestamp}"
        
        # Create backup in appropriate subdirectory
        backup_subdir = self.backup_dir / backup_type
        backup_path = backup_subdir / backup_name
        
        try:
            if os.path.isfile(source_path):
                # Backup file
                shutil.copy2(source_path, backup_path)
                backup_file_type = "file"
                backup_size = os.path.getsize(backup_path)
            else:
                # Backup directory
                shutil.copytree(source_path, backup_path)
                backup_file_type = "directory"
                backup_size = self._get_directory_size(backup_path)
            
            # Create comprehensive metadata
            metadata = {
                "backup_id": f"{backup_type}_{timestamp}",
                "source_path": os.path.abspath(source_path),
                "backup_path": str(backup_path),
                "backup_type": backup_type,
                "file_type": backup_file_type,
                "created_at": datetime.now().isoformat(),
                "size_bytes": backup_size,
                "size_mb": round(backup_size / (1024 * 1024), 2),
                "description": description or f"Automatic {backup_type} backup",
                "retention_category": self._determine_retention_category(),
                "checksum": self._calculate_checksum(backup_path) if backup_file_type == "file" else None
            }
            
            # Save metadata
            metadata_path = backup_subdir / f"{backup_name}_metadata.json"
            with open(metadata_path, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, indent=2)
            
            # Update backup index
            self._update_backup_index(metadata)
            
            # Perform cleanup if needed
            if self._should_perform_cleanup():
                self.cleanup_old_backups()
            
            logger.info(f"Created automatic backup: {backup_path} ({metadata['size_mb']} MB)")
            return str(backup_path)
            
        except Exception as e:
            logger.error(f"Failed to create automatic backup: {e}")
            raise IOError(f"Failed to create backup: {str(e)}")
    
    def _get_directory_size(self, directory_path: Path) -> int:
        """Calculate total size of directory in bytes."""
        total_size = 0
        try:
            for dirpath, dirnames, filenames in os.walk(directory_path):
                for filename in filenames:
                    filepath = os.path.join(dirpath, filename)
                    if os.path.exists(filepath):
                        total_size += os.path.getsize(filepath)
        except Exception as e:
            logger.warning(f"Could not calculate directory size: {e}")
        return total_size
    
    def _calculate_checksum(self, file_path: Path) -> str:
        """Calculate MD5 checksum of a file."""
        import hashlib
        try:
            hash_md5 = hashlib.md5()
            with open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_md5.update(chunk)
            return hash_md5.hexdigest()
        except Exception as e:
            logger.warning(f"Could not calculate checksum: {e}")
            return None
    
    def _determine_retention_category(self) -> str:
        """Determine retention category based on current time."""
        now = datetime.now()
        
        # Monthly backup on first day of month
        if now.day == 1:
            return "monthly"
        
        # Weekly backup on Sundays
        if now.weekday() == 6:  # Sunday
            return "weekly"
        
        # Daily backup otherwise
        return "daily"
    
    def _update_backup_index(self, metadata: Dict[str, Any]) -> None:
        """Update the backup index with new backup metadata."""
        index_path = self.backup_dir / "backup_index.json"
        
        try:
            # Load existing index
            if index_path.exists():
                with open(index_path, 'r', encoding='utf-8') as f:
                    index = json.load(f)
            else:
                index = {"backups": [], "last_updated": None}
            
            # Add new backup to index
            index["backups"].append(metadata)
            index["last_updated"] = datetime.now().isoformat()
            
            # Sort by creation date (newest first)
            index["backups"].sort(key=lambda x: x.get("created_at", ""), reverse=True)
            
            # Save updated index
            with open(index_path, 'w', encoding='utf-8') as f:
                json.dump(index, f, indent=2)
                
        except Exception as e:
            logger.warning(f"Could not update backup index: {e}")
    
    def _should_perform_cleanup(self) -> bool:
        """Determine if backup cleanup should be performed."""
        try:
            # Check if cleanup was performed recently
            cleanup_marker = self.backup_dir / ".last_cleanup"
            if cleanup_marker.exists():
                last_cleanup = datetime.fromtimestamp(cleanup_marker.stat().st_mtime)
                if (datetime.now() - last_cleanup).days < 1:
                    return False
            
            # Check total backup size
            total_size = self._get_directory_size(self.backup_dir)
            size_mb = total_size / (1024 * 1024)
            
            # Load retention policy
            retention_policy_path = self.backup_dir / "retention_policy.json"
            if retention_policy_path.exists():
                with open(retention_policy_path, 'r', encoding='utf-8') as f:
                    policy = json.load(f)
                max_size_mb = policy.get("retention_rules", {}).get("max_backup_size_mb", 1000)
                auto_cleanup = policy.get("retention_rules", {}).get("auto_cleanup_enabled", True)
                
                return auto_cleanup and size_mb > max_size_mb
            
            return size_mb > 1000  # Default 1GB limit
            
        except Exception as e:
            logger.warning(f"Could not determine cleanup necessity: {e}")
            return False
    
    def cleanup_old_backups(self) -> Dict[str, int]:
        """
        Clean up old backups based on retention policy.
        
        Returns:
            Dictionary with cleanup statistics
        """
        cleanup_stats = {
            "files_removed": 0,
            "space_freed_mb": 0,
            "errors": 0
        }
        
        try:
            # Load retention policy
            retention_policy_path = self.backup_dir / "retention_policy.json"
            if not retention_policy_path.exists():
                logger.warning("No retention policy found, skipping cleanup")
                return cleanup_stats
            
            with open(retention_policy_path, 'r', encoding='utf-8') as f:
                policy = json.load(f)
            
            retention_rules = policy.get("retention_rules", {})
            
            # Load backup index
            index_path = self.backup_dir / "backup_index.json"
            if not index_path.exists():
                logger.warning("No backup index found, skipping cleanup")
                return cleanup_stats
            
            with open(index_path, 'r', encoding='utf-8') as f:
                index = json.load(f)
            
            backups_to_remove = []
            current_time = datetime.now()
            
            # Apply retention rules
            for backup in index.get("backups", []):
                try:
                    backup_time = datetime.fromisoformat(backup["created_at"])
                    retention_category = backup.get("retention_category", "daily")
                    age_days = (current_time - backup_time).days
                    
                    should_remove = False
                    
                    if retention_category == "daily":
                        keep_days = retention_rules.get("daily_backups", {}).get("keep_days", 7)
                        should_remove = age_days > keep_days
                    elif retention_category == "weekly":
                        keep_weeks = retention_rules.get("weekly_backups", {}).get("keep_weeks", 4)
                        should_remove = age_days > (keep_weeks * 7)
                    elif retention_category == "monthly":
                        keep_months = retention_rules.get("monthly_backups", {}).get("keep_months", 12)
                        should_remove = age_days > (keep_months * 30)
                    
                    if should_remove:
                        backups_to_remove.append(backup)
                        
                except Exception as e:
                    logger.warning(f"Error processing backup for cleanup: {e}")
                    cleanup_stats["errors"] += 1
            
            # Remove old backups
            for backup in backups_to_remove:
                try:
                    backup_path = Path(backup["backup_path"])
                    metadata_path = backup_path.parent / f"{backup_path.name}_metadata.json"
                    
                    # Calculate size before removal
                    size_mb = backup.get("size_mb", 0)
                    
                    # Remove backup file/directory
                    if backup_path.exists():
                        if backup_path.is_file():
                            backup_path.unlink()
                        else:
                            shutil.rmtree(backup_path)
                        cleanup_stats["files_removed"] += 1
                        cleanup_stats["space_freed_mb"] += size_mb
                    
                    # Remove metadata file
                    if metadata_path.exists():
                        metadata_path.unlink()
                    
                    # Remove from index
                    index["backups"].remove(backup)
                    
                    logger.info(f"Removed old backup: {backup_path.name}")
                    
                except Exception as e:
                    logger.error(f"Error removing backup {backup.get('backup_path', 'unknown')}: {e}")
                    cleanup_stats["errors"] += 1
            
            # Update index
            index["last_updated"] = datetime.now().isoformat()
            with open(index_path, 'w', encoding='utf-8') as f:
                json.dump(index, f, indent=2)
            
            # Update cleanup marker
            cleanup_marker = self.backup_dir / ".last_cleanup"
            cleanup_marker.touch()
            
            logger.info(f"Backup cleanup completed: {cleanup_stats['files_removed']} files removed, "
                       f"{cleanup_stats['space_freed_mb']:.2f} MB freed")
            
        except Exception as e:
            logger.error(f"Backup cleanup failed: {e}")
            cleanup_stats["errors"] += 1
        
        return cleanup_stats
    
    def create_pre_update_backup(self, data_path: str, description: str = None) -> str:
        """
        Create a backup before data updates.
        
        Args:
            data_path: Path to data file that will be updated
            description: Optional description for the backup
            
        Returns:
            Path to created backup
        """
        backup_description = description or f"Pre-update backup of {os.path.basename(data_path)}"
        return self.create_automatic_backup(data_path, "data", backup_description)
    
    def get_backup_statistics(self) -> Dict[str, Any]:
        """
        Get comprehensive backup statistics.
        
        Returns:
            Dictionary with backup statistics
        """
        stats = {
            "total_backups": 0,
            "total_size_mb": 0,
            "backup_types": {},
            "retention_categories": {},
            "oldest_backup": None,
            "newest_backup": None,
            "last_cleanup": None
        }
        
        try:
            # Load backup index
            index_path = self.backup_dir / "backup_index.json"
            if not index_path.exists():
                return stats
            
            with open(index_path, 'r', encoding='utf-8') as f:
                index = json.load(f)
            
            backups = index.get("backups", [])
            stats["total_backups"] = len(backups)
            
            for backup in backups:
                # Size statistics
                size_mb = backup.get("size_mb", 0)
                stats["total_size_mb"] += size_mb
                
                # Type statistics
                backup_type = backup.get("backup_type", "unknown")
                stats["backup_types"][backup_type] = stats["backup_types"].get(backup_type, 0) + 1
                
                # Retention category statistics
                retention_category = backup.get("retention_category", "unknown")
                stats["retention_categories"][retention_category] = stats["retention_categories"].get(retention_category, 0) + 1
                
                # Date statistics
                created_at = backup.get("created_at")
                if created_at:
                    if not stats["oldest_backup"] or created_at < stats["oldest_backup"]:
                        stats["oldest_backup"] = created_at
                    if not stats["newest_backup"] or created_at > stats["newest_backup"]:
                        stats["newest_backup"] = created_at
            
            # Last cleanup information
            cleanup_marker = self.backup_dir / ".last_cleanup"
            if cleanup_marker.exists():
                stats["last_cleanup"] = datetime.fromtimestamp(cleanup_marker.stat().st_mtime).isoformat()
            
            # Round total size
            stats["total_size_mb"] = round(stats["total_size_mb"], 2)
            
        except Exception as e:
            logger.error(f"Failed to get backup statistics: {e}")
        
        return stats
    
    def get_data_statistics(self, items: List[Item]) -> DataStats:
        """
        Generate statistics about the loaded data.
        
        Args:
            items: List of items to analyze
            
        Returns:
            DataStats object with statistics
        """
        stats = DataStats()
        stats.total_items = len(items)
        
        # Count categories
        category_counts = {}
        all_custom_fields = set()
        
        for item in items:
            # Count categories
            if item.category:
                category_counts[item.category] = category_counts.get(item.category, 0) + 1
            
            # Collect custom fields
            all_custom_fields.update(item.custom_fields.keys())
        
        stats.categories = category_counts
        stats.fields = ['id', 'category', 'name', 'description']
        stats.custom_fields = list(all_custom_fields)
        
        return stats
    
    def list_backups(self) -> List[Dict[str, Any]]:
        """
        List available backups sorted by creation date (newest first).
        
        Returns:
            List of backup metadata dictionaries
        """
        backups = []
        
        if not self.backup_dir.exists():
            return backups
        
        # Find all metadata files
        for metadata_file in self.backup_dir.glob("*_metadata.json"):
            try:
                with open(metadata_file, 'r', encoding='utf-8') as f:
                    metadata = json.load(f)
                backups.append(metadata)
            except (json.JSONDecodeError, IOError):
                # Skip invalid metadata files
                continue
        
        # Sort by creation date (newest first)
        backups.sort(key=lambda x: x.get('created_at', ''), reverse=True)
        
        return backups
    
    def restore_backup(self, backup_path: str, target_path: str) -> bool:
        """
        Restore a backup to a target location.
        
        Args:
            backup_path: Path to backup file or directory
            target_path: Target path for restoration
            
        Returns:
            True if restoration was successful
        """
        try:
            if not os.path.exists(backup_path):
                return False
            
            # Create target directory if needed
            target_dir = os.path.dirname(target_path)
            if target_dir:
                os.makedirs(target_dir, exist_ok=True)
            
            if os.path.isfile(backup_path):
                # Restore file
                shutil.copy2(backup_path, target_path)
            else:
                # Restore directory
                if os.path.exists(target_path):
                    shutil.rmtree(target_path)
                shutil.copytree(backup_path, target_path)
            
            return True
            
        except Exception:
            return False