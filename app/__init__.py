from flask import Flask, jsonify, request
from app.extensions import db, login_manager
from flask_migrate import Migrate
import os
from config import get_config
from flask_wtf.csrf import CSRFProtect
from flask_wtf.csrf import validate_csrf, CSRFError

# Initialize Flask-Migrate
migrate = Migrate()

# Initialize CSRF protection
csrf = CSRFProtect()

def create_app(config_class=None):
    app = Flask(__name__)
    
    # Load configuration
    if config_class is None:
        app.config.from_object(get_config())
    else:
        app.config.from_object(config_class)

    db_path = os.path.abspath('site.db')
    print(f"Database file should be at: {db_path}")

    # Initialize extensions with app
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)

    # Initialize CSRF protection with the app
    csrf.init_app(app)
    # Set the login view for unauthorized users
    login_manager.login_view = app.config['LOGIN_VIEW']
    login_manager.login_message = app.config['LOGIN_MESSAGE']
    login_manager.login_message_category = app.config['LOGIN_MESSAGE_CATEGORY']


    @app.before_request
    def csrf_protect():
        if request.path.startswith('/api/'):
            if request.method in ['POST', 'PUT', 'DELETE']:
                token = request.headers.get('X-CSRFToken')
                try:
                    validate_csrf(token)
                except CSRFError:
                    return jsonify({'success': False, 'message': 'CSRF token missing or invalid'}), 400

    # Create database tables
    with app.app_context():
        db.create_all()

    # Import and register routes
    from app import routes
    routes.init_routes(app)
    from app import apis
    apis.init_apis(app)
    
    return app