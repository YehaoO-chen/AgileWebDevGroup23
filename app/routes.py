import os
from flask import render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from datetime import datetime, timedelta,timezone
from app.models import User, StudyPlan, StudyDuration, Notification
from app import db


def init_routes(app):
    # Home page route
    @app.route('/')
    def index():
        # If the user is already logged in, redirect to the home page
        if not current_user.is_authenticated:
            return render_template('index.html')
        return render_template('base.html', route='mainpage', user=current_user)



    @app.route('/login', methods=['GET', 'POST'])
    def login():
        if current_user.is_authenticated:
            return redirect(url_for('index'))

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
            if user.check_password(password):
                login_user(user)
                flash('Login successful', 'success')
                return redirect(url_for('index'))
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
                # Get form data
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

                flash('Signup successful! Please log in.', 'success')
                return redirect(url_for('login'))
            except Exception as e:
                db.session.rollback()
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
            if not user.check_security_answer(security_answer):  # Use the check_security_answer method
                flash('Incorrect security answer. Please try again.', 'danger')
                return redirect(url_for('reset'))

            # Update the user's password
            try:
                user.password = new_password  # This will automatically hash the password
                db.session.commit()
                flash('Password reset successful! You can now log in with your new password.', 'success')
                return redirect(url_for('login'))
            except Exception as e:
                db.session.rollback()
                flash('An error occurred while resetting your password. Please try again.', 'danger')
                return redirect(url_for('reset'))

        return render_template('reset.html')
    
    # Study plan route (requires login)
    @app.route('/studyplan')
    @login_required
    def study_plan():
        user = current_user
        # Check if the request is an AJAX request (based on header set by JS)
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return render_template('studyplan.html', user=user, is_partial=True) # Pass a flag if needed
        else:
            # If normal request, render with the base template
            return render_template('base.html', route='studyplan', user=user) # Or just render normally


    # Main page route (requires login)
    @app.route('/mainpage')
    @login_required
    def mainpage():
        user = current_user
        # Check if the request is an AJAX request (based on header set by JS)
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return render_template('mainpage.html', user=user, is_partial=True) # Pass a flag if needed
        else:
            # If normal request, render with the base template
            return render_template('base.html', route='mainpage', user=user)

    
    # Dashboard route (requires login)
    @app.route('/dashboard')
    @login_required
    def dashboard():
        user = current_user
        # Check if the request is an AJAX request (based on header set by JS)
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return render_template('dashboard.html', user=user, is_partial=True) # Pass a flag if needed
        else:
            # If normal request, render with the base template
            return render_template('base.html', route='dashboard', user=user)

    
    # Notification route (requires login)
    @app.route('/notification')
    @login_required
    def notification():
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return render_template('notification.html', user=current_user, is_partial=True)
        else:
            return render_template('base.html', route='notification', user=current_user)


    
    #Profile route
    @app.route('/profile')
    @login_required
    def profile():
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return render_template('profile.html')
        else:
            return render_template('base.html', route='profile')
        