"""
Browser Error Handler
Provides API endpoint for logging browser errors to file
"""
import json
import logging
import os
from datetime import datetime
from functools import wraps

from flask import Blueprint, jsonify, request

# Create blueprint
browser_error_bp = Blueprint('browser_error', __name__)

# Set up logging
LOG_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'logs')
os.makedirs(LOG_DIR, exist_ok=True)

# Configure browser error logger
browser_logger = logging.getLogger('browser_errors')
browser_logger.setLevel(logging.ERROR)

# Create file handler
log_file = os.path.join(LOG_DIR, 'browser-errors.log')
file_handler = logging.FileHandler(log_file)
file_handler.setLevel(logging.ERROR)

# Create formatter
formatter = logging.Formatter(
    '%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
file_handler.setFormatter(formatter)

# Add handler to logger
browser_logger.addHandler(file_handler)

# Also create a JSON log file for structured data
json_log_file = os.path.join(LOG_DIR, 'browser-errors.json')

def log_browser_error(error_data):
    """Log browser error to both text and JSON files"""
    try:
        # Log to text file
        error_message = f"[{error_data.get('type', 'unknown')}] {error_data.get('message', 'No message')}"
        if error_data.get('source'):
            error_message += f" at {error_data['source']}:{error_data.get('line', 0)}:{error_data.get('column', 0)}"
        if error_data.get('stack'):
            error_message += f"\nStack trace:\n{error_data['stack']}"
        if error_data.get('context'):
            error_message += f"\nContext: {json.dumps(error_data['context'])}"

        browser_logger.error(error_message)

        # Log to JSON file for structured analysis
        with open(json_log_file, 'a') as f:
            json.dump(error_data, f)
            f.write('\n')

        return True
    except Exception as e:
        print(f"Error logging browser error: {e}")
        return False

def cors_enabled(f):
    """Decorator to enable CORS for browser error logging"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        response = f(*args, **kwargs)
        if isinstance(response, tuple):
            response_obj, status_code = response
        else:
            response_obj = response
            status_code = 200

        # Convert dict to proper response
        from flask import make_response
        response = make_response(jsonify(response_obj) if isinstance(response_obj, dict) else response_obj, status_code)

        # Add CORS headers
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Methods'] = 'POST, OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type, X-Requested-With'

        return response
    return decorated_function

@browser_error_bp.route('/api/log-browser-error', methods=['POST', 'OPTIONS'])
@cors_enabled
def log_browser_error_endpoint():
    """API endpoint to receive and log browser errors"""
    if request.method == 'OPTIONS':
        # Handle preflight request
        return {'status': 'ok'}, 200

    try:
        error_data = request.get_json()

        if not error_data:
            return {'error': 'No data provided'}, 400

        # Handle batch of errors
        if error_data.get('type') == 'error-batch':
            errors = error_data.get('errors', [])
            for error in errors:
                log_browser_error(error)

            return {
                'status': 'success',
                'message': f'Logged {len(errors)} errors',
                'timestamp': datetime.now().isoformat()
            }, 200
        else:
            # Single error
            success = log_browser_error(error_data)

            if success:
                return {
                    'status': 'success',
                    'message': 'Error logged',
                    'timestamp': datetime.now().isoformat()
                }, 200
            else:
                return {
                    'status': 'error',
                    'message': 'Failed to log error'
                }, 500

    except Exception as e:
        print(f"Error in browser error endpoint: {e}")
        return {
            'status': 'error',
            'message': str(e)
        }, 500

@browser_error_bp.route('/api/browser-errors', methods=['GET'])
def get_browser_errors():
    """API endpoint to retrieve recent browser errors"""
    try:
        errors = []

        # Read last 100 errors from JSON file
        if os.path.exists(json_log_file):
            with open(json_log_file, 'r') as f:
                lines = f.readlines()
                for line in lines[-100:]:  # Get last 100 errors
                    try:
                        errors.append(json.loads(line))
                    except:
                        pass

        return jsonify({
            'status': 'success',
            'errors': errors,
            'count': len(errors),
            'log_file': log_file
        })

    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@browser_error_bp.route('/api/clear-browser-errors', methods=['POST'])
def clear_browser_errors():
    """API endpoint to clear browser error logs"""
    try:
        # Clear both log files
        if os.path.exists(log_file):
            open(log_file, 'w').close()
        if os.path.exists(json_log_file):
            open(json_log_file, 'w').close()

        return jsonify({
            'status': 'success',
            'message': 'Browser error logs cleared'
        })

    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

# Export blueprint
__all__ = ['browser_error_bp']
