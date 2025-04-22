from flask import Flask
from app.extensions import db, login_manager
from flask_migrate import Migrate
import os

# Initialize Flask-Migrate
migrate = Migrate()

def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
    app.config['SECRET_KEY'] = os.environ.get('FLASK_SECRET_KEY', os.urandom(32))

    db_path = os.path.abspath('site.db')
    print(f"Database file should be at: {db_path}")

    # Initialize extensions with app
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    
    # Import models before creating tables
    from app.models import User  # Ensure models are imported

    # Create database tables
    with app.app_context():
        db.create_all()

    # Import and register routes
    from app import routes
    routes.init_routes(app)

    return app
