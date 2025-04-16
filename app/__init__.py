from flask import Flask

def create_app():
    # Create a Flask application instance
    app = Flask(__name__)

    # Configure the app (e.g., secret key, database URI, etc.)
    app.config['SECRET_KEY'] = 'your_secret_key'

    # Import and register routes
    from .routes import init_routes
    init_routes(app)

    return app