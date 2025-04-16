from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user, UserMixin
from flask_login import LoginManager
from datetime import datetime
from app.models import User, users

def init_routes(app):
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'login'

    @login_manager.user_loader
    def load_user(user_id):
        return users.get(user_id)

    @app.route('/')
    def index():
        return render_template('index.html')


    @app.route('/home')
    def home():
        # If user is authenticated, show dashboard
        if current_user.is_authenticated:
            return render_template('home.html', username=current_user.username)
        # If not authenticated, show welcome message
        return render_template('home.html')

    @app.route('/login', methods=['GET', 'POST'])
    def login():
        # If user is already logged in, redirect to home page
        if current_user.is_authenticated:
            return redirect(url_for('home'))
            
        if request.method == 'POST':
            username = request.form['username']
            password = request.form['password']

            # Convert username to uppercase for comparison
            username_upper = username.upper()

            # Validate user credentials
            for user in users.values():
                if user.username.upper() == username_upper and user.password == password:
                    login_user(user)
                    flash('Login successful')
                    return redirect(url_for('home'))

            flash('Invalid username or password')
        return render_template('login.html')
    
    @app.route('/logout')
    @login_required
    def logout():
        logout_user()
        flash('You have been logged out')
        return redirect(url_for('login'))

    @app.route('/visualization')
    @login_required
    def visualization():
        return render_template('visualization.html')