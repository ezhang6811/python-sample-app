"""Users endpoint - healthy endpoint that returns user data."""
from flask import Blueprint, jsonify
import random

users_bp = Blueprint('users', __name__)

SAMPLE_USERS = [
    {'id': 1, 'name': 'Alice', 'email': 'alice@example.com', 'role': 'admin'},
    {'id': 2, 'name': 'Bob', 'email': 'bob@example.com', 'role': 'user'},
    {'id': 3, 'name': 'Charlie', 'email': 'charlie@example.com', 'role': 'user'},
    {'id': 4, 'name': 'Diana', 'email': 'diana@example.com', 'role': 'moderator'},
    {'id': 5, 'name': 'Eve', 'email': 'eve@example.com', 'role': 'user'},
]


@users_bp.route('/api/users', methods=['GET'])
def get_users():
    """Get all users."""
    return jsonify({'users': SAMPLE_USERS, 'count': len(SAMPLE_USERS)})


@users_bp.route('/api/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    """Get a specific user by ID."""
    user = next((u for u in SAMPLE_USERS if u['id'] == user_id), None)
    if user:
        return jsonify(user)
    return jsonify({'error': 'User not found'}), 404


@users_bp.route('/api/users/random', methods=['GET'])
def get_random_user():
    """Get a random user."""
    user = random.choice(SAMPLE_USERS)
    return jsonify(user)
