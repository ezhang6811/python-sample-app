"""Main Flask application entry point."""
import os
from flask import Flask
from endpoints.users import users_bp
from endpoints.products import products_bp
from endpoints.error import error_bp
from endpoints.slow import slow_bp

app = Flask(__name__)

# Register blueprints
app.register_blueprint(users_bp)
app.register_blueprint(products_bp)
app.register_blueprint(error_bp)
app.register_blueprint(slow_bp)


@app.route('/')
def home():
    """Health check endpoint."""
    return {'status': 'healthy', 'message': 'Python Sample App is running'}


@app.route('/health')
def health():
    """Detailed health check endpoint."""
    return {'status': 'ok', 'service': 'python-sample-app'}


if __name__ == '__main__':
    # Debug mode should only be enabled in development
    # Set FLASK_DEBUG=1 environment variable to enable debug mode
    debug_mode = os.environ.get('FLASK_DEBUG', '0') == '1'
    app.run(host='0.0.0.0', port=8080, debug=debug_mode)

