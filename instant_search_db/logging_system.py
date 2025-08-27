"""
Comprehensive logging system for the instant search database application.
Provides structured logging, performance monitoring, and debug capabilities.
"""

import logging
import logging.handlers
import os
import json
import time
import functools
from typing import Dict, Any, Optional, List, Callable
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from enum import Enum
import threading
from pathlib import Path


class LogLevel(Enum):
    """Custom log levels for application-specific logging"""
    PERFORMANCE = 25
    CONFIGURATION = 26
    DATA_VALIDATION = 27
    USER_ACTION = 28


class LogCategory(Enum):
    """Log categories for better organization"""
    SYSTEM = "system"
    CONFIGURATION = "configuration"
    DATA_MANAGEMENT = "data_management"
    SEARCH = "search"
    VALIDATION = "validation"
    PERFORMANCE = "performance"
    USER_INTERACTION = "user_interaction"
    ERROR_HANDLING = "error_handling"
    SECURITY = "security"


@dataclass
class PerformanceMetric:
    """Performance metric data structure"""
    operation: str
    duration: float
    timestamp: datetime
    category: LogCategory
    additional_data: Optional[Dict[str, Any]] = None
    success: bool = True


@dataclass
class ConfigurationChange:
    """Configuration change tracking"""
    config_type: str
    old_value: Any
    new_value: Any
    timestamp: datetime
    user: Optional[str] = None
    source: Optional[str] = None


class StructuredFormatter(logging.Formatter):
    """Custom formatter for structured logging"""
    
    def format(self, record):
        # Create structured log entry
        log_entry = {
            "timestamp": datetime.fromtimestamp(record.created).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno
        }
        
        # Add extra fields if present
        if hasattr(record, 'category'):
            log_entry['category'] = record.category
        if hasattr(record, 'user_id'):
            log_entry['user_id'] = record.user_id
        if hasattr(record, 'operation'):
            log_entry['operation'] = record.operation
        if hasattr(record, 'duration'):
            log_entry['duration'] = record.duration
        if hasattr(record, 'additional_data'):
            log_entry['additional_data'] = record.additional_data
        
        # Add exception info if present
        if record.exc_info:
            log_entry['exception'] = self.formatException(record.exc_info)
        
        return json.dumps(log_entry, ensure_ascii=False, default=str)


class LoggingSystem:
    """
    Comprehensive logging system with structured logging, performance monitoring,
    and configuration change tracking.
    """
    
    def __init__(self, 
                 log_dir: str = "logs",
                 app_name: str = "instant_search_db",
                 max_log_size: int = 10 * 1024 * 1024,  # 10MB
                 backup_count: int = 5):
        """
        Initialize logging system.
        
        Args:
            log_dir: Directory for log files
            app_name: Application name for log files
            max_log_size: Maximum size of each log file in bytes
            backup_count: Number of backup log files to keep
        """
        self.log_dir = Path(log_dir)
        self.app_name = app_name
        self.max_log_size = max_log_size
        self.backup_count = backup_count
        
        # Create log directory
        self.log_dir.mkdir(exist_ok=True)
        
        # Performance metrics storage
        self.performance_metrics: List[PerformanceMetric] = []
        self.metrics_lock = threading.Lock()
        
        # Configuration change tracking
        self.config_changes: List[ConfigurationChange] = []
        self.config_lock = threading.Lock()
        
        # Initialize loggers
        self.loggers: Dict[str, logging.Logger] = {}
        self._setup_loggers()
        
        # Add custom log levels
        self._add_custom_log_levels()
    
    def _add_custom_log_levels(self):
        """Add custom log levels to logging module"""
        for level in LogLevel:
            logging.addLevelName(level.value, level.name)
    
    def _setup_loggers(self):
        """Setup different loggers for different purposes"""
        
        # Main application logger
        self.loggers['main'] = self._create_logger(
            'main',
            f"{self.app_name}.log",
            logging.INFO
        )
        
        # Error logger
        self.loggers['error'] = self._create_logger(
            'error',
            f"{self.app_name}_errors.log",
            logging.ERROR
        )
        
        # Performance logger
        self.loggers['performance'] = self._create_logger(
            'performance',
            f"{self.app_name}_performance.log",
            LogLevel.PERFORMANCE.value
        )
        
        # Configuration logger
        self.loggers['config'] = self._create_logger(
            'config',
            f"{self.app_name}_config.log",
            LogLevel.CONFIGURATION.value
        )
        
        # Data validation logger
        self.loggers['validation'] = self._create_logger(
            'validation',
            f"{self.app_name}_validation.log",
            LogLevel.DATA_VALIDATION.value
        )
        
        # User action logger
        self.loggers['user'] = self._create_logger(
            'user',
            f"{self.app_name}_user_actions.log",
            LogLevel.USER_ACTION.value
        )
        
        # Debug logger (only in development)
        self.loggers['debug'] = self._create_logger(
            'debug',
            f"{self.app_name}_debug.log",
            logging.DEBUG
        )
    
    def _create_logger(self, name: str, filename: str, level: int) -> logging.Logger:
        """
        Create a logger with file and console handlers.
        
        Args:
            name: Logger name
            filename: Log file name
            level: Logging level
            
        Returns:
            Configured logger instance
        """
        logger = logging.getLogger(f"{self.app_name}.{name}")
        logger.setLevel(level)
        
        # Prevent duplicate handlers
        if logger.handlers:
            return logger
        
        # File handler with rotation
        file_handler = logging.handlers.RotatingFileHandler(
            self.log_dir / filename,
            maxBytes=self.max_log_size,
            backupCount=self.backup_count,
            encoding='utf-8'
        )
        file_handler.setLevel(level)
        file_handler.setFormatter(StructuredFormatter())
        
        # Console handler for errors and warnings
        if level <= logging.WARNING:
            console_handler = logging.StreamHandler()
            console_handler.setLevel(logging.WARNING)
            console_handler.setFormatter(
                logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            )
            logger.addHandler(console_handler)
        
        logger.addHandler(file_handler)
        return logger
    
    def get_logger(self, category: LogCategory = LogCategory.SYSTEM) -> logging.Logger:
        """
        Get logger for specific category.
        
        Args:
            category: Log category
            
        Returns:
            Logger instance
        """
        category_mapping = {
            LogCategory.SYSTEM: 'main',
            LogCategory.CONFIGURATION: 'config',
            LogCategory.DATA_MANAGEMENT: 'main',
            LogCategory.SEARCH: 'main',
            LogCategory.VALIDATION: 'validation',
            LogCategory.PERFORMANCE: 'performance',
            LogCategory.USER_INTERACTION: 'user',
            LogCategory.ERROR_HANDLING: 'error',
            LogCategory.SECURITY: 'main'
        }
        
        logger_name = category_mapping.get(category, 'main')
        return self.loggers[logger_name]
    
    def log_performance(self, 
                       operation: str,
                       duration: float,
                       category: LogCategory = LogCategory.PERFORMANCE,
                       additional_data: Optional[Dict[str, Any]] = None,
                       success: bool = True):
        """
        Log performance metrics.
        
        Args:
            operation: Name of the operation
            duration: Duration in seconds
            category: Log category
            additional_data: Additional data to log
            success: Whether the operation was successful
        """
        metric = PerformanceMetric(
            operation=operation,
            duration=duration,
            timestamp=datetime.now(),
            category=category,
            additional_data=additional_data,
            success=success
        )
        
        with self.metrics_lock:
            self.performance_metrics.append(metric)
            
            # Keep only recent metrics (last 1000)
            if len(self.performance_metrics) > 1000:
                self.performance_metrics = self.performance_metrics[-1000:]
        
        # Log to performance logger
        logger = self.get_logger(LogCategory.PERFORMANCE)
        logger.log(
            LogLevel.PERFORMANCE.value,
            f"Performance: {operation}",
            extra={
                'category': category.value,
                'operation': operation,
                'duration': duration,
                'success': success,
                'additional_data': additional_data
            }
        )
    
    def log_configuration_change(self,
                                config_type: str,
                                old_value: Any,
                                new_value: Any,
                                user: Optional[str] = None,
                                source: Optional[str] = None):
        """
        Log configuration changes.
        
        Args:
            config_type: Type of configuration changed
            old_value: Previous value
            new_value: New value
            user: User who made the change
            source: Source of the change (file, API, etc.)
        """
        change = ConfigurationChange(
            config_type=config_type,
            old_value=old_value,
            new_value=new_value,
            timestamp=datetime.now(),
            user=user,
            source=source
        )
        
        with self.config_lock:
            self.config_changes.append(change)
            
            # Keep only recent changes (last 500)
            if len(self.config_changes) > 500:
                self.config_changes = self.config_changes[-500:]
        
        # Log to configuration logger
        logger = self.get_logger(LogCategory.CONFIGURATION)
        logger.log(
            LogLevel.CONFIGURATION.value,
            f"Configuration changed: {config_type}",
            extra={
                'category': LogCategory.CONFIGURATION.value,
                'config_type': config_type,
                'old_value': str(old_value),
                'new_value': str(new_value),
                'user': user,
                'source': source
            }
        )
    
    def log_user_action(self,
                       action: str,
                       user_id: Optional[str] = None,
                       additional_data: Optional[Dict[str, Any]] = None):
        """
        Log user actions.
        
        Args:
            action: Description of the action
            user_id: User identifier
            additional_data: Additional data about the action
        """
        logger = self.get_logger(LogCategory.USER_INTERACTION)
        logger.log(
            LogLevel.USER_ACTION.value,
            f"User action: {action}",
            extra={
                'category': LogCategory.USER_INTERACTION.value,
                'user_id': user_id,
                'action': action,
                'additional_data': additional_data
            }
        )
    
    def log_data_validation(self,
                           validation_type: str,
                           result: bool,
                           details: Optional[Dict[str, Any]] = None):
        """
        Log data validation results.
        
        Args:
            validation_type: Type of validation performed
            result: Validation result (True/False)
            details: Additional validation details
        """
        logger = self.get_logger(LogCategory.VALIDATION)
        logger.log(
            LogLevel.DATA_VALIDATION.value,
            f"Data validation: {validation_type} - {'PASSED' if result else 'FAILED'}",
            extra={
                'category': LogCategory.VALIDATION.value,
                'validation_type': validation_type,
                'result': result,
                'additional_data': details
            }
        )
    
    def get_performance_summary(self, 
                               hours: int = 24) -> Dict[str, Any]:
        """
        Get performance summary for the specified time period.
        
        Args:
            hours: Number of hours to look back
            
        Returns:
            Performance summary dictionary
        """
        cutoff_time = datetime.now() - timedelta(hours=hours)
        
        with self.metrics_lock:
            recent_metrics = [
                m for m in self.performance_metrics 
                if m.timestamp >= cutoff_time
            ]
        
        if not recent_metrics:
            return {"message": "No performance data available"}
        
        # Calculate statistics
        total_operations = len(recent_metrics)
        successful_operations = sum(1 for m in recent_metrics if m.success)
        failed_operations = total_operations - successful_operations
        
        # Group by operation
        operation_stats = {}
        for metric in recent_metrics:
            if metric.operation not in operation_stats:
                operation_stats[metric.operation] = {
                    'count': 0,
                    'total_duration': 0,
                    'min_duration': float('inf'),
                    'max_duration': 0,
                    'success_count': 0
                }
            
            stats = operation_stats[metric.operation]
            stats['count'] += 1
            stats['total_duration'] += metric.duration
            stats['min_duration'] = min(stats['min_duration'], metric.duration)
            stats['max_duration'] = max(stats['max_duration'], metric.duration)
            if metric.success:
                stats['success_count'] += 1
        
        # Calculate averages
        for operation, stats in operation_stats.items():
            stats['avg_duration'] = stats['total_duration'] / stats['count']
            stats['success_rate'] = stats['success_count'] / stats['count']
        
        return {
            "time_period_hours": hours,
            "total_operations": total_operations,
            "successful_operations": successful_operations,
            "failed_operations": failed_operations,
            "success_rate": successful_operations / total_operations if total_operations > 0 else 0,
            "operation_statistics": operation_stats,
            "summary_generated_at": datetime.now().isoformat()
        }
    
    def get_configuration_history(self, 
                                 config_type: Optional[str] = None,
                                 hours: int = 24) -> List[Dict[str, Any]]:
        """
        Get configuration change history.
        
        Args:
            config_type: Filter by configuration type
            hours: Number of hours to look back
            
        Returns:
            List of configuration changes
        """
        cutoff_time = datetime.now() - timedelta(hours=hours)
        
        with self.config_lock:
            changes = [
                asdict(change) for change in self.config_changes
                if change.timestamp >= cutoff_time and
                (config_type is None or change.config_type == config_type)
            ]
        
        # Convert datetime objects to ISO strings
        for change in changes:
            change['timestamp'] = change['timestamp'].isoformat()
        
        return changes
    
    def cleanup_old_logs(self, days: int = 30):
        """
        Clean up log files older than specified days.
        
        Args:
            days: Number of days to keep logs
        """
        cutoff_time = datetime.now() - timedelta(days=days)
        
        for log_file in self.log_dir.glob("*.log*"):
            try:
                if log_file.stat().st_mtime < cutoff_time.timestamp():
                    log_file.unlink()
                    self.get_logger().info(f"Deleted old log file: {log_file}")
            except Exception as e:
                self.get_logger().error(f"Failed to delete log file {log_file}: {e}")


def performance_monitor(operation_name: Optional[str] = None,
                       category: LogCategory = LogCategory.PERFORMANCE,
                       log_args: bool = False):
    """
    Decorator for automatic performance monitoring.
    
    Args:
        operation_name: Custom operation name (defaults to function name)
        category: Log category
        log_args: Whether to log function arguments
        
    Returns:
        Decorator function
    """
    def decorator(func: Callable):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            op_name = operation_name or f"{func.__module__}.{func.__name__}"
            success = True
            additional_data = {}
            
            if log_args:
                additional_data['args_count'] = len(args)
                additional_data['kwargs_keys'] = list(kwargs.keys())
            
            try:
                result = func(*args, **kwargs)
                return result
            except Exception as e:
                success = False
                additional_data['error'] = str(e)
                raise
            finally:
                duration = time.time() - start_time
                logging_system = get_logging_system()
                logging_system.log_performance(
                    operation=op_name,
                    duration=duration,
                    category=category,
                    additional_data=additional_data,
                    success=success
                )
        
        return wrapper
    return decorator


def log_user_action(action: str, 
                   user_id: Optional[str] = None,
                   additional_data: Optional[Dict[str, Any]] = None):
    """
    Convenience function to log user actions.
    
    Args:
        action: Description of the action
        user_id: User identifier
        additional_data: Additional data about the action
    """
    logging_system = get_logging_system()
    logging_system.log_user_action(action, user_id, additional_data)


def log_configuration_change(config_type: str,
                            old_value: Any,
                            new_value: Any,
                            user: Optional[str] = None,
                            source: Optional[str] = None):
    """
    Convenience function to log configuration changes.
    
    Args:
        config_type: Type of configuration changed
        old_value: Previous value
        new_value: New value
        user: User who made the change
        source: Source of the change
    """
    logging_system = get_logging_system()
    logging_system.log_configuration_change(config_type, old_value, new_value, user, source)


# Global logging system instance
_global_logging_system: Optional[LoggingSystem] = None


def get_logging_system() -> LoggingSystem:
    """
    Get the global logging system instance.
    
    Returns:
        Global LoggingSystem instance
    """
    global _global_logging_system
    if _global_logging_system is None:
        _global_logging_system = LoggingSystem()
    return _global_logging_system


def initialize_logging(log_dir: str = "logs",
                      app_name: str = "instant_search_db",
                      max_log_size: int = 10 * 1024 * 1024,
                      backup_count: int = 5) -> LoggingSystem:
    """
    Initialize the global logging system.
    
    Args:
        log_dir: Directory for log files
        app_name: Application name for log files
        max_log_size: Maximum size of each log file in bytes
        backup_count: Number of backup log files to keep
        
    Returns:
        Initialized LoggingSystem instance
    """
    global _global_logging_system
    _global_logging_system = LoggingSystem(log_dir, app_name, max_log_size, backup_count)
    return _global_logging_system