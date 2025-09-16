"""
Comprehensive Logging Configuration
Provides structured logging with rotation, multiple handlers, and proper formatting
"""

import json
import logging
import logging.config
import os
from datetime import datetime
from logging.handlers import RotatingFileHandler


def setup_logging(app=None, log_level='INFO'):
    """
    Configure comprehensive logging for the application

    Args:
        app: Flask application instance (optional)
        log_level: Default logging level
    """

    # Create logs directory if it doesn't exist
    log_dir = 'logs'
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    # Logging configuration dictionary
    LOGGING_CONFIG = {
        'version': 1,
        'disable_existing_loggers': False,

        'formatters': {
            'default': {
                'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                'datefmt': '%Y-%m-%d %H:%M:%S'
            },
            'detailed': {
                'format': '%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(funcName)s() - %(message)s',
                'datefmt': '%Y-%m-%d %H:%M:%S'
            },
            'json': {
                'format': '%(message)s',
                'class': 'logging_config.JSONFormatter'
            }
        },

        'handlers': {
            'console': {
                'class': 'logging.StreamHandler',
                'level': 'INFO',
                'formatter': 'default',
                'stream': 'ext://sys.stdout'
            },
            'file_app': {
                'class': 'logging.handlers.RotatingFileHandler',
                'level': 'INFO',
                'formatter': 'detailed',
                'filename': f'{log_dir}/app.log',
                'maxBytes': 10485760,  # 10MB
                'backupCount': 5,
                'encoding': 'utf8'
            },
            'file_error': {
                'class': 'logging.handlers.RotatingFileHandler',
                'level': 'ERROR',
                'formatter': 'detailed',
                'filename': f'{log_dir}/error.log',
                'maxBytes': 10485760,  # 10MB
                'backupCount': 5,
                'encoding': 'utf8'
            },
            'file_access': {
                'class': 'logging.handlers.TimedRotatingFileHandler',
                'level': 'INFO',
                'formatter': 'default',
                'filename': f'{log_dir}/access.log',
                'when': 'midnight',
                'interval': 1,
                'backupCount': 30,
                'encoding': 'utf8'
            },
            'file_security': {
                'class': 'logging.handlers.RotatingFileHandler',
                'level': 'WARNING',
                'formatter': 'detailed',
                'filename': f'{log_dir}/security.log',
                'maxBytes': 10485760,  # 10MB
                'backupCount': 10,
                'encoding': 'utf8'
            },
            'file_database': {
                'class': 'logging.handlers.RotatingFileHandler',
                'level': 'DEBUG',
                'formatter': 'detailed',
                'filename': f'{log_dir}/database.log',
                'maxBytes': 10485760,  # 10MB
                'backupCount': 3,
                'encoding': 'utf8'
            }
        },

        'loggers': {
            # Application logger
            'app': {
                'level': log_level,
                'handlers': ['console', 'file_app', 'file_error'],
                'propagate': False
            },
            # Database logger
            'sqlalchemy': {
                'level': 'WARNING',
                'handlers': ['file_database'],
                'propagate': False
            },
            'sqlalchemy.engine': {
                'level': 'WARNING',
                'handlers': ['file_database'],
                'propagate': False
            },
            # Security logger
            'security': {
                'level': 'INFO',
                'handlers': ['file_security', 'console'],
                'propagate': False
            },
            # Access logger
            'werkzeug': {
                'level': 'INFO',
                'handlers': ['file_access'],
                'propagate': False
            },
            # Auth logger
            'auth': {
                'level': 'INFO',
                'handlers': ['file_security', 'file_app'],
                'propagate': False
            }
        },

        'root': {
            'level': log_level,
            'handlers': ['console', 'file_app']
        }
    }

    # Apply configuration
    logging.config.dictConfig(LOGGING_CONFIG)

    # If Flask app provided, configure Flask logging
    if app:
        app.logger.setLevel(getattr(logging, log_level))

        # Add Flask-specific handlers
        if not app.debug:
            file_handler = RotatingFileHandler(
                f'{log_dir}/flask.log',
                maxBytes=10485760,
                backupCount=10
            )
            file_handler.setFormatter(logging.Formatter(
                '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
            ))
            file_handler.setLevel(logging.INFO)
            app.logger.addHandler(file_handler)

            app.logger.info('Flask application startup')

class JSONFormatter(logging.Formatter):
    """
    Custom JSON formatter for structured logging
    """

    def format(self, record):
        log_obj = {
            'timestamp': datetime.utcnow().isoformat(),
            'level': record.levelname,
            'logger': record.name,
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno,
            'message': record.getMessage()
        }

        # Add exception info if present
        if record.exc_info:
            log_obj['exception'] = self.formatException(record.exc_info)

        # Add extra fields
        for key, value in record.__dict__.items():
            if key not in ['name', 'msg', 'args', 'created', 'filename', 'funcName',
                          'levelname', 'levelno', 'lineno', 'module', 'msecs',
                          'message', 'pathname', 'process', 'processName', 'relativeCreated',
                          'thread', 'threadName', 'exc_info', 'exc_text', 'stack_info']:
                log_obj[key] = value

        return json.dumps(log_obj)

def log_request(request, response=None, duration=None):
    """
    Log HTTP request details
    """
    logger = logging.getLogger('access')

    log_data = {
        'method': request.method,
        'path': request.path,
        'ip': request.remote_addr,
        'user_agent': request.user_agent.string,
        'referrer': request.referrer
    }

    if response:
        log_data['status_code'] = response.status_code

    if duration:
        log_data['duration_ms'] = round(duration * 1000, 2)

    logger.info(f"Request: {json.dumps(log_data)}")

def log_security_event(event_type, user_id=None, details=None):
    """
    Log security-related events
    """
    logger = logging.getLogger('security')

    log_data = {
        'event_type': event_type,
        'timestamp': datetime.utcnow().isoformat()
    }

    if user_id:
        log_data['user_id'] = user_id

    if details:
        log_data['details'] = details

    logger.warning(f"Security Event: {json.dumps(log_data)}")

def log_database_operation(operation, table, duration=None, rows_affected=None):
    """
    Log database operations
    """
    logger = logging.getLogger('sqlalchemy')

    log_data = {
        'operation': operation,
        'table': table
    }

    if duration:
        log_data['duration_ms'] = round(duration * 1000, 2)

    if rows_affected is not None:
        log_data['rows_affected'] = rows_affected

    logger.debug(f"Database Operation: {json.dumps(log_data)}")

def get_logger(name):
    """
    Get a logger instance with the given name
    """
    return logging.getLogger(name)

# Request logging middleware
def add_request_logging(app):
    """
    Add request/response logging middleware to Flask app
    """
    import time

    from flask import g, request

    @app.before_request
    def before_request():
        g.start_time = time.time()

    @app.after_request
    def after_request(response):
        if hasattr(g, 'start_time'):
            duration = time.time() - g.start_time
            log_request(request, response, duration)
        return response

    return app
