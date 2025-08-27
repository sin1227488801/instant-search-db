from flask import Blueprint, jsonify, render_template, request, current_app
import logging
from .models import search_items, get_category_counts
from .config_manager import ConfigManager
from .error_handler import ErrorHandler, ErrorContext, graceful_degradation
from .logging_system import get_logging_system, LogCategory, performance_monitor, log_user_action

# Configure logging
logger = get_logging_system().get_logger(LogCategory.SYSTEM)

bp = Blueprint('main', __name__)

# Global error handler for routes
error_handler = ErrorHandler(logger)

@bp.route('/')
@performance_monitor("route_index", LogCategory.USER_INTERACTION)
def index():
    """トップページ（index.html）を返す - Enhanced with comprehensive error handling"""
    
    # Log user action
    log_user_action("access_index_page", additional_data={"user_agent": request.headers.get('User-Agent')})
    
    context = ErrorContext(
        function_name="index",
        user_action="access_index_page"
    )
    
    try:
        # Use configuration manager from app context if available
        config_manager = getattr(current_app, 'config_manager', None)
        config_valid = getattr(current_app, 'config_valid', False)
        
        # Fallback to creating new instance if not available in app context
        if config_manager is None:
            try:
                config_manager = ConfigManager()
                # Validate configuration on page load with error handling
                if not config_manager.validate_all_configs():
                    logger.warning("Configuration validation issues detected")
                    config_valid = False
                else:
                    config_valid = True
            except Exception as e:
                error_handler.handle_error(e, context)
                logger.warning("Configuration validation failed, continuing with available configs")
                config_valid = False
        
        # Load configuration data for template with graceful degradation
        ui_config = None
        categories_config = {}
        field_mappings = {}
        category_counts = {}
        
        try:
            ui_config = config_manager.load_ui_settings()
        except Exception as e:
            error_handler.handle_error(e, context)
            logger.warning("Failed to load UI settings, using defaults")
        
        try:
            categories_config = config_manager.load_categories()
        except Exception as e:
            error_handler.handle_error(e, context)
            logger.warning("Failed to load categories, using defaults")
        
        try:
            field_mappings = config_manager.load_field_mappings()
        except Exception as e:
            error_handler.handle_error(e, context)
            logger.warning("Failed to load field mappings, using defaults")
        
        try:
            # Get category counts with configuration integration
            category_counts = get_category_counts(config_manager)
        except Exception as e:
            error_handler.handle_error(e, context)
            logger.warning("Failed to get category counts, using empty counts")
        
        return render_template('index.html', 
                             category_counts=category_counts,
                             ui_config=ui_config,
                             categories_config=categories_config,
                             field_mappings=field_mappings,
                             config_valid=config_valid)
    
    except Exception as e:
        error_info = error_handler.handle_error(e, context)
        logger.error(f"Critical error in index route: {e}")
        
        # Return error page with user-friendly message
        return render_template('index.html', 
                             category_counts={},
                             ui_config=None,
                             categories_config={},
                             field_mappings={},
                             error_message="設定の読み込みに失敗しました。デフォルト設定を使用します。",
                             error_id=error_info.error_id), 500

@bp.route('/search')
@performance_monitor("route_search", LogCategory.SEARCH)
def search():
    """
    クエリパラメータ 'q' で渡されたキーワードでDBを検索し、
    結果をJSON形式で返すAPIエンドポイント - Enhanced with comprehensive error handling
    カスタムフィールド検索をサポート
    """
    query_term = request.args.get('q', '')
    category_filter = request.args.get('category', '')
    custom_fields = request.args.get('fields', '')
    
    # Log user search action
    log_user_action("search_request", additional_data={
        "query": query_term,
        "category": category_filter,
        "custom_fields": custom_fields,
        "ip_address": request.remote_addr
    })
    
    context = ErrorContext(
        function_name="search",
        user_action="search_request",
        additional_data={
            "query": query_term,
            "category": category_filter,
            "custom_fields": custom_fields
        }
    )
    
    try:
        logger.info(f"Search request: query='{query_term}', category='{category_filter}', fields='{custom_fields}'")
        
        if not query_term:
            logger.info("Empty query, returning empty results")
            return jsonify([])
        
        # Use configuration manager from app context if available
        config_manager = getattr(current_app, 'config_manager', None)
        
        # Fallback to creating new instance if not available in app context
        if config_manager is None:
            try:
                config_manager = ConfigManager()
            except Exception as e:
                error_handler.handle_error(e, context)
                logger.warning("Failed to initialize ConfigManager, using default search")
        
        # Enhanced search with custom field support and error handling
        results = []
        try:
            results = search_items(query_term, category_filter, config_manager)
        except Exception as e:
            error_handler.handle_error(e, context)
            logger.error(f"Search operation failed: {e}")
            return jsonify({
                "error": "検索中にエラーが発生しました",
                "message": "データベースの検索に失敗しました。しばらく後でもう一度お試しください。",
                "technical_details": str(e) if logger.level <= logging.DEBUG else None
            }), 500
        
        # Filter results based on custom fields if specified
        if custom_fields and results:
            try:
                field_list = [f.strip() for f in custom_fields.split(',')]
                filtered_results = []
                
                for result in results:
                    # Check if any of the specified custom fields contain the query
                    for field in field_list:
                        if field in result and query_term.lower() in str(result[field]).lower():
                            filtered_results.append(result)
                            break
                
                results = filtered_results
                logger.info(f"Filtered results by custom fields: {len(results)} items")
                
            except Exception as e:
                error_handler.handle_error(e, context)
                logger.warning(f"Custom field filtering failed: {e}, returning unfiltered results")
        
        logger.info(f"Search completed: {len(results)} results returned")
        return jsonify(results)
        
    except Exception as e:
        error_info = error_handler.handle_error(e, context)
        logger.error(f"Critical error in search endpoint: {e}")
        
        return jsonify({
            "error": "検索中に予期しないエラーが発生しました",
            "message": "システム管理者に連絡してください。",
            "error_id": error_info.error_id,
            "timestamp": error_info.timestamp.isoformat()
        }), 500

@bp.route('/api/config')
def get_current_config():
    """現在の設定を取得するAPIエンドポイント"""
    try:
        # Use configuration manager from app context if available
        config_manager = getattr(current_app, 'config_manager', None)
        if config_manager is None:
            config_manager = ConfigManager()
        
        # Load all configurations
        categories_config = config_manager.load_categories()
        field_mappings = config_manager.load_field_mappings()
        ui_config = config_manager.load_ui_settings()
        
        # Convert CategoryConfig objects to dictionaries
        categories_dict = {}
        for key, category in categories_config.items():
            categories_dict[key] = {
                "display_name": category.display_name,
                "icon": category.icon,
                "emoji_fallback": category.emoji_fallback,
                "color": category.color,
                "description": category.description
            }
        
        # Convert UIConfig to dictionary
        ui_dict = {
            "title": ui_config.title,
            "subtitle": ui_config.subtitle,
            "theme": ui_config.theme,
            "layout": ui_config.layout,
            "search": ui_config.search,
            "categories": ui_config.categories
        }
        
        config_data = {
            "categories": categories_dict,
            "field_mappings": field_mappings,
            "ui": ui_dict,
            "status": "success",
            "timestamp": __import__('datetime').datetime.now().isoformat()
        }
        
        logger.info("Configuration data retrieved successfully")
        return jsonify(config_data)
        
    except Exception as e:
        logger.error(f"Error retrieving configuration: {e}")
        return jsonify({
            "error": "設定の取得に失敗しました",
            "message": str(e),
            "status": "error"
        }), 500

@bp.route('/api/config/validate')
def validate_config():
    """設定ファイルを検証するAPIエンドポイント"""
    try:
        # Use configuration manager from app context if available
        config_manager = getattr(current_app, 'config_manager', None)
        if config_manager is None:
            config_manager = ConfigManager()
        
        # Validate all configurations
        is_valid = config_manager.validate_all_configs()
        
        validation_result = {
            "is_valid": is_valid,
            "status": "success" if is_valid else "warning",
            "message": "すべての設定が有効です" if is_valid else "一部の設定に問題があります",
            "timestamp": __import__('datetime').datetime.now().isoformat()
        }
        
        # Add detailed validation info
        validation_details = {}
        
        try:
            config_manager.load_categories(force_reload=True)
            validation_details["categories"] = {"status": "valid", "message": "カテゴリ設定は有効です"}
        except Exception as e:
            validation_details["categories"] = {"status": "error", "message": f"カテゴリ設定エラー: {str(e)}"}
        
        try:
            config_manager.load_field_mappings(force_reload=True)
            validation_details["fields"] = {"status": "valid", "message": "フィールド設定は有効です"}
        except Exception as e:
            validation_details["fields"] = {"status": "error", "message": f"フィールド設定エラー: {str(e)}"}
        
        try:
            config_manager.load_ui_settings(force_reload=True)
            validation_details["ui"] = {"status": "valid", "message": "UI設定は有効です"}
        except Exception as e:
            validation_details["ui"] = {"status": "error", "message": f"UI設定エラー: {str(e)}"}
        
        validation_result["details"] = validation_details
        
        logger.info(f"Configuration validation completed: {is_valid}")
        return jsonify(validation_result)
        
    except Exception as e:
        logger.error(f"Error validating configuration: {e}")
        return jsonify({
            "error": "設定の検証に失敗しました",
            "message": str(e),
            "status": "error"
        }), 500

@bp.route('/api/config/examples')
def list_example_configs():
    """利用可能なサンプル設定を一覧表示するAPIエンドポイント"""
    try:
        # Use configuration manager from app context if available
        config_manager = getattr(current_app, 'config_manager', None)
        if config_manager is None:
            config_manager = ConfigManager()
        
        # Get list of example configurations
        examples = config_manager.get_example_configs()
        
        # Get detailed information for each example
        example_details = []
        for example_name in examples:
            try:
                example_config = config_manager.load_example_config(example_name)
                if example_config:
                    example_info = {
                        "name": example_name,
                        "title": example_config.get("title", example_name),
                        "description": example_config.get("description", "サンプル設定"),
                        "use_case": example_config.get("use_case", "汎用"),
                        "categories_count": len(example_config.get("categories", {}).get("categories", {})),
                        "has_custom_fields": bool(example_config.get("field_mappings", {}).get("custom_fields")),
                        "available": True
                    }
                else:
                    example_info = {
                        "name": example_name,
                        "title": example_name,
                        "description": "設定の読み込みに失敗しました",
                        "available": False
                    }
                example_details.append(example_info)
            except Exception as e:
                logger.warning(f"Error loading example {example_name}: {e}")
                example_details.append({
                    "name": example_name,
                    "title": example_name,
                    "description": f"エラー: {str(e)}",
                    "available": False
                })
        
        result = {
            "examples": example_details,
            "count": len(example_details),
            "status": "success",
            "timestamp": __import__('datetime').datetime.now().isoformat()
        }
        
        logger.info(f"Listed {len(example_details)} example configurations")
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Error listing example configurations: {e}")
        return jsonify({
            "error": "サンプル設定の一覧取得に失敗しました",
            "message": str(e),
            "status": "error"
        }), 500

@bp.route('/api/config/examples/<example_name>')
def get_example_config(example_name):
    """特定のサンプル設定を取得するAPIエンドポイント"""
    try:
        # Use configuration manager from app context if available
        config_manager = getattr(current_app, 'config_manager', None)
        if config_manager is None:
            config_manager = ConfigManager()
        
        # Load the specific example configuration
        example_config = config_manager.load_example_config(example_name)
        
        if not example_config:
            return jsonify({
                "error": "サンプル設定が見つかりません",
                "message": f"'{example_name}' という名前のサンプル設定は存在しません",
                "status": "not_found"
            }), 404
        
        result = {
            "name": example_name,
            "config": example_config,
            "status": "success",
            "timestamp": __import__('datetime').datetime.now().isoformat()
        }
        
        logger.info(f"Retrieved example configuration: {example_name}")
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Error retrieving example configuration {example_name}: {e}")
        return jsonify({
            "error": "サンプル設定の取得に失敗しました",
            "message": str(e),
            "status": "error"
        }), 500

@bp.route('/api/system/health')
@performance_monitor("route_health_check", LogCategory.SYSTEM)
def system_health():
    """システムヘルスチェックAPIエンドポイント"""
    try:
        # Use configuration manager from app context if available
        config_manager = getattr(current_app, 'config_manager', None)
        if config_manager is None:
            config_manager = ConfigManager()
        
        # Perform comprehensive health check
        health_status = config_manager.health_check()
        
        # Add additional system checks
        health_status["system_checks"] = {}
        
        # Check logging system
        try:
            logging_system = get_logging_system()
            health_status["system_checks"]["logging"] = {
                "status": "ok",
                "message": "Logging system operational"
            }
        except Exception as e:
            health_status["system_checks"]["logging"] = {
                "status": "error",
                "message": f"Logging system error: {e}"
            }
        
        # Check error handler
        try:
            error_summary = error_handler.get_error_summary()
            health_status["system_checks"]["error_handling"] = {
                "status": "ok",
                "message": f"Error handler operational. {error_summary['total_errors']} total errors tracked."
            }
        except Exception as e:
            health_status["system_checks"]["error_handling"] = {
                "status": "error",
                "message": f"Error handler error: {e}"
            }
        
        # Determine HTTP status code based on health
        status_code = 200
        if health_status["overall_status"] == "unhealthy":
            status_code = 503
        elif health_status["overall_status"] == "degraded":
            status_code = 200  # Still operational but with warnings
        
        return jsonify(health_status), status_code
        
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return jsonify({
            "overall_status": "unhealthy",
            "error": "ヘルスチェックに失敗しました",
            "message": str(e),
            "timestamp": __import__('datetime').datetime.now().isoformat()
        }), 503

@bp.route('/api/system/errors')
def system_errors():
    """システムエラー情報APIエンドポイント"""
    try:
        error_summary = error_handler.get_error_summary()
        return jsonify(error_summary)
        
    except Exception as e:
        logger.error(f"Error retrieving system errors: {e}")
        return jsonify({
            "error": "エラー情報の取得に失敗しました",
            "message": str(e)
        }), 500

@bp.route('/api/system/errors/<error_id>')
def get_error_details(error_id):
    """特定のエラーの詳細情報APIエンドポイント"""
    try:
        error_details = error_handler.get_user_friendly_error(error_id)
        
        if not error_details:
            return jsonify({
                "error": "エラーが見つかりません",
                "message": f"ID '{error_id}' のエラーは存在しません"
            }), 404
        
        return jsonify(error_details)
        
    except Exception as e:
        logger.error(f"Error retrieving error details for {error_id}: {e}")
        return jsonify({
            "error": "エラー詳細の取得に失敗しました",
            "message": str(e)
        }), 500

@bp.route('/api/system/performance')
def system_performance():
    """システムパフォーマンス情報APIエンドポイント"""
    try:
        hours = request.args.get('hours', 24, type=int)
        logging_system = get_logging_system()
        performance_summary = logging_system.get_performance_summary(hours)
        
        return jsonify(performance_summary)
        
    except Exception as e:
        logger.error(f"Error retrieving performance data: {e}")
        return jsonify({
            "error": "パフォーマンスデータの取得に失敗しました",
            "message": str(e)
        }), 500

@bp.route('/api/system/logs/config-history')
def config_history():
    """設定変更履歴APIエンドポイント"""
    try:
        hours = request.args.get('hours', 24, type=int)
        config_type = request.args.get('type', None)
        
        logging_system = get_logging_system()
        history = logging_system.get_configuration_history(config_type, hours)
        
        return jsonify({
            "config_history": history,
            "filter": {
                "hours": hours,
                "config_type": config_type
            },
            "count": len(history)
        })
        
    except Exception as e:
        logger.error(f"Error retrieving configuration history: {e}")
        return jsonify({
            "error": "設定変更履歴の取得に失敗しました",
            "message": str(e)
        }), 500