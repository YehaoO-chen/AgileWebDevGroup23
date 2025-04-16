from flask import Flask
from flask_login import LoginManager
from config import DevelopmentConfig

# Initialize login manager
login_manager = LoginManager()
login_manager.login_message = 'Please login first'

def create_app(config_class=DevelopmentConfig):
    # Create Flask app instance
    app = Flask(__name__, 
                static_folder='static',
                template_folder='templates')
    
    # Configure app
    app.config.from_object(config_class)
    
    # Initialize login manager with app
    login_manager.init_app(app)
    
    # Import and register routes
    from app import routes
    routes.init_routes(app)
    
    return app