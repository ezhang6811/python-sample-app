"""Products endpoint - healthy endpoint that returns product data."""
from flask import Blueprint, jsonify
import random

products_bp = Blueprint('products', __name__)

SAMPLE_PRODUCTS = [
    {'id': 101, 'name': 'Laptop', 'price': 999.99, 'category': 'Electronics', 'in_stock': True},
    {'id': 102, 'name': 'Mouse', 'price': 29.99, 'category': 'Electronics', 'in_stock': True},
    {'id': 103, 'name': 'Keyboard', 'price': 79.99, 'category': 'Electronics', 'in_stock': True},
    {'id': 104, 'name': 'Monitor', 'price': 299.99, 'category': 'Electronics', 'in_stock': False},
    {'id': 105, 'name': 'Desk Chair', 'price': 199.99, 'category': 'Furniture', 'in_stock': True},
]


@products_bp.route('/api/products', methods=['GET'])
def get_products():
    """Get all products."""
    return jsonify({'products': SAMPLE_PRODUCTS, 'count': len(SAMPLE_PRODUCTS)})


@products_bp.route('/api/products/<int:product_id>', methods=['GET'])
def get_product(product_id):
    """Get a specific product by ID."""
    product = next((p for p in SAMPLE_PRODUCTS if p['id'] == product_id), None)
    if product:
        return jsonify(product)
    return jsonify({'error': 'Product not found'}), 404


@products_bp.route('/api/products/random', methods=['GET'])
def get_random_product():
    """Get a random product."""
    product = random.choice(SAMPLE_PRODUCTS)
    return jsonify(product)
