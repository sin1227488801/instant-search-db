"""
Enhanced error handling system for the instant search database application.
Provides comprehensive error handling, user-friendly messages, and recovery suggestions.
"""

import logging
import traceback
import sys
from typing import Dict, Any, Optional, List, Callable
from dataclasses import dataclass
from enum import Enum
import json
from datetime import datetime


class ErrorSeverity(Enum):
    """Error severity levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ErrorCategory(Enum):
    """Error categories for better classification"""
    CONFIGURATION = "configuration"
    DATA_VALIDATION = "data_validation"
    FILE_IO = "file_io"
    DATABASE = "database"
    NETWORK = "network"
    AUTHENTICATION = "authentication"
    VALIDATION = "validation"
    SYSTEM = "system"
    USER_INPUT = "user_input"


@dataclass
class ErrorContext:
    """Context information for errors"""
    user_action: Optional[str] = None
    file_path: Optional[str] = None
    line_number: Optional[int] = None
    function_name: Optional[str] = None
    additional_data: Optional[Dict[str, Any]] = None


@dataclass
class RecoveryAction:
    """Recovery action suggestion"""
    action_type: str
    description: str
    automated: bool = False
    callback: Optional[Callable] = None


@dataclass
class ErrorInfo:
    """Comprehensive error information"""
    error_id: str
    category: ErrorCategory
    severity: ErrorSeverity
    message: str
    user_message: str
    technical_details: str
    context: ErrorContext
    recovery_actions: List[RecoveryAction]
    timestamp: datetime
    resolved: bool = False


class ErrorHandler:
    """
    Enhanced error handler with user-friendly messages and recovery suggestions.
    """
    
    def __init__(self, logger: Optional[logging.Logger] = None):
        """
        Initialize error handler.
        
        Args:
            logger: Optional logger instance. If None, creates a new one.
        """
        self.logger = logger or logging.getLogger(__name__)
        self.error_registry: Dict[str, ErrorInfo] = {}
        self.error_patterns = self._initialize_error_patterns()
        self.recovery_callbacks: Dict[str, Callable] = {}
        
    def _initialize_error_patterns(self) -> Dict[str, Dict[str, Any]]:
        """Initialize common error patterns and their handling strategies"""
        return {
            "config_file_not_found": {
                "category": ErrorCategory.CONFIGURATION,
                "severity": ErrorSeverity.MEDIUM,
                "user_message": "設定ファイルが見つかりません。デフォルト設定を使用します。",
                "recovery_actions": [
                    {
                        "action_type": "create_default_config",
                        "description": "デフォルト設定ファイルを作成する",
                        "automated": True
                    },
                    {
                        "action_type": "check_file_permissions",
                        "description": "ファイルのアクセス権限を確認する",
                        "automated": False
                    }
                ]
            },
            "config_invalid_json": {
                "category": ErrorCategory.CONFIGURATION,
                "severity": ErrorSeverity.HIGH,
                "user_message": "設定ファイルの形式が正しくありません。構文を確認してください。",
                "recovery_actions": [
                    {
                        "action_type": "validate_json_syntax",
                        "description": "JSON構文を検証する",
                        "automated": True
                    },
                    {
                        "action_type": "restore_backup_config",
                        "description": "バックアップから設定を復元する",
                        "automated": False
                    }
                ]
            },
            "csv_file_not_found": {
                "category": ErrorCategory.FILE_IO,
                "severity": ErrorSeverity.MEDIUM,
                "user_message": "データファイルが見つかりません。サンプルデータを使用します。",
                "recovery_actions": [
                    {
                        "action_type": "create_sample_csv",
                        "description": "サンプルCSVファイルを作成する",
                        "automated": True
                    },
                    {
                        "action_type": "check_file_path",
                        "description": "ファイルパスを確認する",
                        "automated": False
                    }
                ]
            },
            "csv_invalid_format": {
                "category": ErrorCategory.DATA_VALIDATION,
                "severity": ErrorSeverity.HIGH,
                "user_message": "CSVファイルの形式が正しくありません。ヘッダーと列の構成を確認してください。",
                "recovery_actions": [
                    {
                        "action_type": "validate_csv_structure",
                        "description": "CSV構造を検証する",
                        "automated": True
                    },
                    {
                        "action_type": "show_csv_template",
                        "description": "正しいCSV形式のテンプレートを表示する",
                        "automated": False
                    }
                ]
            },
            "database_connection_failed": {
                "category": ErrorCategory.DATABASE,
                "severity": ErrorSeverity.CRITICAL,
                "user_message": "データベースに接続できません。システム管理者に連絡してください。",
                "recovery_actions": [
                    {
                        "action_type": "retry_connection",
                        "description": "データベース接続を再試行する",
                        "automated": True
                    },
                    {
                        "action_type": "recreate_database",
                        "description": "データベースを再作成する",
                        "automated": False
                    }
                ]
            },
            "validation_schema_missing": {
                "category": ErrorCategory.VALIDATION,
                "severity": ErrorSeverity.MEDIUM,
                "user_message": "データ検証スキーマが見つかりません。基本的な検証のみ実行します。",
                "recovery_actions": [
                    {
                        "action_type": "create_default_schema",
                        "description": "デフォルト検証スキーマを作成する",
                        "automated": True
                    }
                ]
            },
            "permission_denied": {
                "category": ErrorCategory.SYSTEM,
                "severity": ErrorSeverity.HIGH,
                "user_message": "ファイルまたはディレクトリへのアクセス権限がありません。",
                "recovery_actions": [
                    {
                        "action_type": "check_permissions",
                        "description": "ファイル権限を確認する",
                        "automated": False
                    },
                    {
                        "action_type": "suggest_admin_rights",
                        "description": "管理者権限での実行を提案する",
                        "automated": False
                    }
                ]
            }
        }
    
    def handle_error(self, 
                    exception: Exception, 
                    context: Optional[ErrorContext] = None,
                    error_pattern: Optional[str] = None) -> ErrorInfo:
        """
        Handle an error with comprehensive logging and recovery suggestions.
        
        Args:
            exception: The exception that occurred
            context: Additional context information
            error_pattern: Optional pattern key for predefined error handling
            
        Returns:
            ErrorInfo object with comprehensive error details
        """
        # Generate unique error ID
        error_id = f"ERR_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{id(exception)}"
        
        # Determine error pattern if not provided
        if not error_pattern:
            error_pattern = self._detect_error_pattern(exception)
        
        # Get pattern information
        pattern_info = self.error_patterns.get(error_pattern, {})
        
        # Create error info
        error_info = ErrorInfo(
            error_id=error_id,
            category=pattern_info.get('category', ErrorCategory.SYSTEM),
            severity=pattern_info.get('severity', ErrorSeverity.MEDIUM),
            message=str(exception),
            user_message=pattern_info.get('user_message', "予期しないエラーが発生しました。"),
            technical_details=self._get_technical_details(exception),
            context=context or ErrorContext(),
            recovery_actions=self._create_recovery_actions(pattern_info.get('recovery_actions', [])),
            timestamp=datetime.now()
        )
        
        # Store error in registry
        self.error_registry[error_id] = error_info
        
        # Log error
        self._log_error(error_info)
        
        # Execute automated recovery actions
        self._execute_automated_recovery(error_info)
        
        return error_info
    
    def _detect_error_pattern(self, exception: Exception) -> str:
        """
        Detect error pattern based on exception type and message.
        
        Args:
            exception: The exception to analyze
            
        Returns:
            Error pattern key
        """
        exception_str = str(exception).lower()
        exception_type = type(exception).__name__
        
        # File not found errors
        if isinstance(exception, FileNotFoundError):
            if 'config' in exception_str:
                return "config_file_not_found"
            elif '.csv' in exception_str:
                return "csv_file_not_found"
        
        # JSON decode errors
        elif isinstance(exception, json.JSONDecodeError):
            return "config_invalid_json"
        
        # Permission errors
        elif isinstance(exception, PermissionError):
            return "permission_denied"
        
        # CSV format errors
        elif 'csv' in exception_str and ('format' in exception_str or 'header' in exception_str):
            return "csv_invalid_format"
        
        # Database errors
        elif 'database' in exception_str or 'sqlite' in exception_str:
            return "database_connection_failed"
        
        # Validation errors
        elif 'schema' in exception_str or 'validation' in exception_str:
            return "validation_schema_missing"
        
        # Default pattern
        return "unknown_error"
    
    def _get_technical_details(self, exception: Exception) -> str:
        """
        Get technical details for the exception.
        
        Args:
            exception: The exception to analyze
            
        Returns:
            Technical details string
        """
        details = {
            "exception_type": type(exception).__name__,
            "exception_message": str(exception),
            "traceback": traceback.format_exc()
        }
        
        return json.dumps(details, indent=2, ensure_ascii=False)
    
    def _create_recovery_actions(self, action_configs: List[Dict[str, Any]]) -> List[RecoveryAction]:
        """
        Create recovery action objects from configuration.
        
        Args:
            action_configs: List of action configuration dictionaries
            
        Returns:
            List of RecoveryAction objects
        """
        actions = []
        for config in action_configs:
            action = RecoveryAction(
                action_type=config.get('action_type', 'unknown'),
                description=config.get('description', ''),
                automated=config.get('automated', False),
                callback=self.recovery_callbacks.get(config.get('action_type'))
            )
            actions.append(action)
        
        return actions
    
    def _log_error(self, error_info: ErrorInfo) -> None:
        """
        Log error information with appropriate level.
        
        Args:
            error_info: Error information to log
        """
        log_message = f"[{error_info.error_id}] {error_info.user_message}"
        
        if error_info.severity == ErrorSeverity.CRITICAL:
            self.logger.critical(log_message)
            self.logger.debug(f"Technical details: {error_info.technical_details}")
        elif error_info.severity == ErrorSeverity.HIGH:
            self.logger.error(log_message)
            self.logger.debug(f"Technical details: {error_info.technical_details}")
        elif error_info.severity == ErrorSeverity.MEDIUM:
            self.logger.warning(log_message)
        else:
            self.logger.info(log_message)
    
    def _execute_automated_recovery(self, error_info: ErrorInfo) -> None:
        """
        Execute automated recovery actions.
        
        Args:
            error_info: Error information with recovery actions
        """
        for action in error_info.recovery_actions:
            if action.automated and action.callback:
                try:
                    self.logger.info(f"Executing automated recovery: {action.description}")
                    action.callback(error_info)
                except Exception as e:
                    self.logger.error(f"Automated recovery failed: {e}")
    
    def register_recovery_callback(self, action_type: str, callback: Callable) -> None:
        """
        Register a recovery callback function.
        
        Args:
            action_type: Type of recovery action
            callback: Callback function to execute
        """
        self.recovery_callbacks[action_type] = callback
    
    def get_error_summary(self) -> Dict[str, Any]:
        """
        Get summary of all errors.
        
        Returns:
            Dictionary with error summary statistics
        """
        total_errors = len(self.error_registry)
        resolved_errors = sum(1 for error in self.error_registry.values() if error.resolved)
        
        severity_counts = {}
        category_counts = {}
        
        for error in self.error_registry.values():
            severity_counts[error.severity.value] = severity_counts.get(error.severity.value, 0) + 1
            category_counts[error.category.value] = category_counts.get(error.category.value, 0) + 1
        
        return {
            "total_errors": total_errors,
            "resolved_errors": resolved_errors,
            "unresolved_errors": total_errors - resolved_errors,
            "severity_breakdown": severity_counts,
            "category_breakdown": category_counts,
            "recent_errors": [
                {
                    "error_id": error.error_id,
                    "category": error.category.value,
                    "severity": error.severity.value,
                    "message": error.user_message,
                    "timestamp": error.timestamp.isoformat()
                }
                for error in sorted(self.error_registry.values(), 
                                  key=lambda x: x.timestamp, reverse=True)[:10]
            ]
        }
    
    def mark_error_resolved(self, error_id: str) -> bool:
        """
        Mark an error as resolved.
        
        Args:
            error_id: ID of the error to mark as resolved
            
        Returns:
            True if error was found and marked as resolved
        """
        if error_id in self.error_registry:
            self.error_registry[error_id].resolved = True
            self.logger.info(f"Error {error_id} marked as resolved")
            return True
        return False
    
    def get_user_friendly_error(self, error_id: str) -> Optional[Dict[str, Any]]:
        """
        Get user-friendly error information.
        
        Args:
            error_id: ID of the error
            
        Returns:
            Dictionary with user-friendly error information
        """
        if error_id not in self.error_registry:
            return None
        
        error = self.error_registry[error_id]
        
        return {
            "error_id": error.error_id,
            "message": error.user_message,
            "severity": error.severity.value,
            "category": error.category.value,
            "timestamp": error.timestamp.isoformat(),
            "recovery_suggestions": [
                {
                    "description": action.description,
                    "automated": action.automated
                }
                for action in error.recovery_actions
            ],
            "resolved": error.resolved
        }


# Global error handler instance
_global_error_handler: Optional[ErrorHandler] = None


def get_error_handler() -> ErrorHandler:
    """
    Get the global error handler instance.
    
    Returns:
        Global ErrorHandler instance
    """
    global _global_error_handler
    if _global_error_handler is None:
        _global_error_handler = ErrorHandler()
    return _global_error_handler


def handle_error(exception: Exception, 
                context: Optional[ErrorContext] = None,
                error_pattern: Optional[str] = None) -> ErrorInfo:
    """
    Convenience function to handle errors using the global error handler.
    
    Args:
        exception: The exception that occurred
        context: Additional context information
        error_pattern: Optional pattern key for predefined error handling
        
    Returns:
        ErrorInfo object with comprehensive error details
    """
    return get_error_handler().handle_error(exception, context, error_pattern)


def graceful_degradation(fallback_func: Callable, 
                        error_message: str = "操作に失敗しました。代替処理を実行します。"):
    """
    Decorator for graceful degradation with fallback functionality.
    
    Args:
        fallback_func: Function to call if the decorated function fails
        error_message: Custom error message for logging
        
    Returns:
        Decorator function
    """
    def decorator(func: Callable):
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                error_handler = get_error_handler()
                context = ErrorContext(
                    function_name=func.__name__,
                    additional_data={"args": str(args), "kwargs": str(kwargs)}
                )
                error_info = error_handler.handle_error(e, context)
                
                # Log graceful degradation
                error_handler.logger.warning(f"Graceful degradation: {error_message}")
                
                # Execute fallback
                try:
                    return fallback_func(*args, **kwargs)
                except Exception as fallback_error:
                    error_handler.logger.error(f"Fallback function also failed: {fallback_error}")
                    raise e  # Re-raise original exception
        
        return wrapper
    return decorator