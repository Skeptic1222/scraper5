"""
Database Error Handler Module
Provides comprehensive error handling for SQL Server database operations
"""

import functools
import logging

import pyodbc
from flask import jsonify
from sqlalchemy.exc import (
    DatabaseError,
    DataError,
    DisconnectionError,
    IntegrityError,
    InvalidRequestError,
    OperationalError,
    TimeoutError as SQLTimeoutError,
)

logger = logging.getLogger(__name__)

class DatabaseError(Exception):
    """Base exception for database errors"""
    pass

class ConnectionError(DatabaseError):
    """Database connection error"""
    pass

class QueryTimeoutError(DatabaseError):
    """Query timeout error"""
    pass

def handle_db_error(func):
    """
    Decorator to handle database errors gracefully
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except IntegrityError as e:
            logger.error(f"Database integrity error in {func.__name__}: {str(e)}")
            if 'api' in func.__module__:
                return jsonify({'error': 'Data conflict occurred', 'details': 'Duplicate or invalid data'}), 409
            raise DatabaseError("Data integrity violation")

        except OperationalError as e:
            logger.error(f"Database operational error in {func.__name__}: {str(e)}")
            if 'Cannot open database' in str(e) or 'Login failed' in str(e):
                if 'api' in func.__module__:
                    return jsonify({'error': 'Database connection failed'}), 503
                raise ConnectionError("Unable to connect to database")
            elif 'timeout' in str(e).lower():
                if 'api' in func.__module__:
                    return jsonify({'error': 'Database query timeout'}), 504
                raise QueryTimeoutError("Query execution timeout")
            else:
                if 'api' in func.__module__:
                    return jsonify({'error': 'Database operation failed'}), 500
                raise DatabaseError("Database operation failed")

        except DataError as e:
            logger.error(f"Data error in {func.__name__}: {str(e)}")
            if 'api' in func.__module__:
                return jsonify({'error': 'Invalid data format'}), 400
            raise DatabaseError("Invalid data format")

        except InvalidRequestError as e:
            logger.error(f"Invalid request error in {func.__name__}: {str(e)}")
            if 'api' in func.__module__:
                return jsonify({'error': 'Invalid database request'}), 400
            raise DatabaseError("Invalid database request")

        except DisconnectionError as e:
            logger.error(f"Database disconnection in {func.__name__}: {str(e)}")
            if 'api' in func.__module__:
                return jsonify({'error': 'Database connection lost'}), 503
            raise ConnectionError("Database connection lost")

        except SQLTimeoutError as e:
            logger.error(f"SQL timeout in {func.__name__}: {str(e)}")
            if 'api' in func.__module__:
                return jsonify({'error': 'Operation timeout'}), 504
            raise QueryTimeoutError("Operation timeout")

        except pyodbc.Error as e:
            logger.error(f"PyODBC error in {func.__name__}: {str(e)}")
            error_code = e.args[0] if e.args else 'Unknown'

            # Handle specific SQL Server error codes
            if error_code == '08001':  # Unable to connect
                if 'api' in func.__module__:
                    return jsonify({'error': 'Cannot reach database server'}), 503
                raise ConnectionError("Cannot reach database server")
            elif error_code == '28000':  # Invalid authorization
                if 'api' in func.__module__:
                    return jsonify({'error': 'Database authentication failed'}), 401
                raise ConnectionError("Database authentication failed")
            elif error_code == 'HYT00':  # Timeout expired
                if 'api' in func.__module__:
                    return jsonify({'error': 'Query timeout'}), 504
                raise QueryTimeoutError("Query timeout")
            else:
                if 'api' in func.__module__:
                    return jsonify({'error': 'Database error occurred'}), 500
                raise DatabaseError(f"Database error: {error_code}")

        except Exception as e:
            logger.error(f"Unexpected error in {func.__name__}: {str(e)}", exc_info=True)
            if 'api' in func.__module__:
                return jsonify({'error': 'An unexpected error occurred'}), 500
            raise

    return wrapper

def with_retry(max_attempts=3, delay=1):
    """
    Decorator to retry database operations on transient failures
    """
    import time

    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None

            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except (OperationalError, DisconnectionError, pyodbc.Error) as e:
                    last_exception = e
                    if attempt < max_attempts - 1:
                        logger.warning(f"Retry {attempt + 1}/{max_attempts} for {func.__name__}: {str(e)}")
                        time.sleep(delay * (attempt + 1))  # Exponential backoff
                    else:
                        logger.error(f"Max retries exceeded for {func.__name__}: {str(e)}")
                except Exception as e:
                    # Don't retry for non-transient errors
                    raise

            raise last_exception

        return wrapper
    return decorator

def validate_connection(db):
    """
    Validate database connection is alive
    """
    try:
        # Execute a simple query to test connection
        db.session.execute('SELECT 1')
        return True
    except Exception as e:
        logger.error(f"Database connection validation failed: {str(e)}")
        return False

def get_connection_info(db):
    """
    Get current database connection information
    """
    try:
        engine = db.get_engine()
        pool_status = {
            'size': engine.pool.size(),
            'checked_in': engine.pool.checkedin(),
            'overflow': engine.pool.overflow(),
            'total': engine.pool.size() + engine.pool.overflow()
        }
        return pool_status
    except Exception as e:
        logger.error(f"Failed to get connection info: {str(e)}")
        return None
