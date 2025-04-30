from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from datetime import datetime
from app.models import User, StudyPlan, StudyDuration, Notification
from app import db

def init_routes(app):
    # Home page route
    @app.route('/')
    def index():
        return render_template('index.html')

    # Dashboard route
    @app.route('/home')
    def home():
        # If the user is authenticated, show the dashboard
        if current_user.is_authenticated:
            return render_template('home.html', username=current_user.username)
        # If not authenticated, redirect to the index page
        return render_template('index.html')

    @app.route('/login', methods=['GET', 'POST'])
    def login():
        # If the user is already logged in, redirect to the home page
        if current_user.is_authenticated:
            return redirect(url_for('home'))

        if request.method == 'POST':
            username = request.form['username']
            password = request.form['password']

            # Query the database for the user
            user = User.query.filter_by(username=username).first()

            # Check if the user exists
            if not user:
                flash('User not found. Please check your username or sign up.', 'danger')
                return redirect(url_for('login'))

            # Validate user credentials
            if user.password == password:
                login_user(user)
                flash('Login successful', 'success')
                return redirect(url_for('home'))
            else:
                flash('Invalid password. Please try again.', 'danger')

        return render_template('login.html')

    # Logout route
    @app.route('/logout')
    @login_required
    def logout():
        logout_user()
        flash('You have been logged out', 'info')
        return redirect(url_for('login'))

    @app.route('/signup', methods=['GET', 'POST'])
    def signup():
        if request.method == 'POST':
            try:
                username = request.form['username']
                password = request.form['password']
                security_answer = request.form['security_answer']

                # Check if the username already exists in the database
                existing_user = User.query.filter_by(username=username).first()
                if existing_user:
                    flash('Username already exists', 'danger')
                    return redirect(url_for('signup'))

                # Create a new user and add it to the database
                new_user = User(username=username, password=password, security_answer=security_answer)
                db.session.add(new_user)
                db.session.commit()
                
                # Verify if the user was successfully added to the database
                check_user = User.query.filter_by(username=username).first()
                if check_user:
                    flash('Signup successful! Please log in.', 'success')
                    return redirect(url_for('login'))
                else:
                    flash('Failed to create user. Please try again.', 'danger')
                    return redirect(url_for('signup'))
                    
            except Exception as e:
                # Rollback the transaction
                db.session.rollback()
                # Output the error message
                flash(f'An error occurred: {str(e)}', 'danger')
                return redirect(url_for('signup'))

        return render_template('signup.html')

    @app.route('/reset', methods=['GET', 'POST'])
    def reset():
        if request.method == 'POST':
            username = request.form['username']
            security_answer = request.form['security_answer']
            new_password = request.form['new_password']

            # Query the database for the user
            user = User.query.filter_by(username=username).first()

            # Check if the user exists
            if not user:
                flash('User not found. Please check your username.', 'danger')
                return redirect(url_for('reset'))

            # Validate the security answer
            if user.security_answer != security_answer:
                flash('Incorrect security answer. Please try again.', 'danger')
                return redirect(url_for('reset'))

            # Update the user's password
            try:
                user.password = new_password
                db.session.commit()
                flash('Password reset successful! You can now log in with your new password.', 'success')
                return redirect(url_for('login'))
            except Exception as e:
                db.session.rollback()
                print(f"Error: {e}")
                flash('An error occurred while resetting your password. Please try again.', 'danger')
                return redirect(url_for('reset'))

        return render_template('reset.html')
    
    # Study plan route (requires login)
    @app.route('/studyplan')
    @login_required
    def studyplan():
        return render_template('studyplan.html')


    # Share route (requires login)

    @app.route('/share')
    @login_required
    def share():
        return render_template('share.html')


    # Main page route (requires login)
    @app.route('/mainpage')
    @login_required
    def mainpage():
        return render_template('mainpage.html', user=current_user)
    
    # Dashboard route (requires login)
    @app.route('/dashboard')
    @login_required
    def dashboard():
        return render_template('dashboard.html')
    
    # Notification route (requires login)
    @app.route('/notification')
    @login_required
    def notification():
        return render_template('notification.html')
