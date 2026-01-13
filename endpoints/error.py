"""Error endpoint - intentionally fails to demonstrate error handling."""
from flask import Blueprint, jsonify
import random

error_bp = Blueprint('error', __name__)


@error_bp.route('/api/error', methods=['GET'])
def trigger_error():
    """Endpoint that always returns a 500 error."""
    return jsonify({
        'error': 'Internal Server Error',
        'message': 'This endpoint intentionally fails for testing purposes'
    }), 500


@error_bp.route('/api/error/random', methods=['GET'])
def random_error():
    """Endpoint that randomly fails with different error codes."""
    error_types = [
        (400, 'Bad Request', 'Invalid request parameters'),
        (401, 'Unauthorized', 'Authentication required'),
        (403, 'Forbidden', 'Access denied'),
        (404, 'Not Found', 'Resource not found'),
        (500, 'Internal Server Error', 'Something went wrong'),
        (503, 'Service Unavailable', 'Service temporarily unavailable'),
    ]
    
    status_code, error_type, message = random.choice(error_types)
    return jsonify({
        'error': error_type,
        'message': message,
        'code': status_code
    }), status_code


@error_bp.route('/api/error/exception', methods=['GET'])
def trigger_exception():
    """Endpoint that raises an unhandled exception."""
    # This will cause a 500 error with stack trace
    raise Exception('This is an intentional exception for testing purposes')
