"""Slow endpoint - intentionally has high latency to demonstrate performance issues."""
from flask import Blueprint, jsonify, request
import time
import random

slow_bp = Blueprint('slow', __name__)


@slow_bp.route('/api/slow', methods=['GET'])
def slow_endpoint():
    """Endpoint with fixed 3-second delay."""
    time.sleep(3)
    return jsonify({
        'message': 'This response was delayed by 3 seconds',
        'delay': 3
    })


@slow_bp.route('/api/slow/random', methods=['GET'])
def random_delay():
    """Endpoint with random delay between 1-5 seconds."""
    delay = random.uniform(1, 5)
    time.sleep(delay)
    return jsonify({
        'message': f'This response was delayed by {delay:.2f} seconds',
        'delay': round(delay, 2)
    })


@slow_bp.route('/api/slow/custom', methods=['GET'])
def custom_delay():
    """Endpoint with custom delay specified in query parameter."""
    try:
        delay = float(request.args.get('delay', 2))
        # Cap the delay at 10 seconds to prevent abuse
        delay = min(delay, 10)
        time.sleep(delay)
        return jsonify({
            'message': f'This response was delayed by {delay:.2f} seconds',
            'delay': round(delay, 2)
        })
    except ValueError:
        return jsonify({
            'error': 'Invalid delay parameter',
            'message': 'Delay must be a number'
        }), 400
