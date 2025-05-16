import os
from flask import render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from datetime import datetime, timedelta,timezone
from app.models import User, StudyPlan, StudyDuration, Notification
from app import db
from app.forms import LoginForm, RegistrationForm, PasswordResetForm
from flask_wtf.csrf import CSRFProtect

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
        # Redirect if user is already logged in
        if current_user.is_authenticated:
            return redirect(url_for('index'))

        # Create form object to validate CSRF token
        form = LoginForm()
        
        if request.method == 'POST' and form.validate_csrf_token():  # Only validate CSRF token, not other fields
            # Get form data directly from request
            username = request.form.get('username')
            password = request.form.get('password')
            remember_me = 'remember_me' in request.form
            
            # Query the database for the user
            user = User.query.filter_by(username=username).first()
            
            # Check if the user exists
            if not user:
                flash('User not found. Please check your username or sign up.', 'danger')
                return redirect(url_for('login'))
                
            # Validate user credentials
            if user.check_password(password):
                login_user(user, remember=remember_me)
                flash('Login successful', 'success')
                # Redirect to next page if available, otherwise to index
                next_page = request.args.get('next')
                return redirect(next_page) if next_page else redirect(url_for('index'))
            else:
                flash('Invalid password. Please try again.', 'danger')
        
        # Render the login template
        return render_template('login.html', form=form)


    @app.route('/signup', methods=['GET', 'POST'])
    def signup():
        # Create form object to validate CSRF token
        form = RegistrationForm()
        
        if request.method == 'POST' and form.validate_csrf_token():  # Only validate CSRF token, not other fields
            try:
                # Get form data directly from request
                username = request.form.get('username')
                password = request.form.get('password')
                confirm_password = request.form.get('confirm_password')
                security_answer = request.form.get('security_answer')
                
                # Check if passwords match
                if password != confirm_password:
                    flash('Passwords do not match.', 'danger')
                    return redirect(url_for('signup'))
                    
                # Check if username already exists
                existing_user = User.query.filter_by(username=username).first()
                if existing_user:
                    flash('Username already exists', 'danger')
                    return redirect(url_for('signup'))
                
                # Create new user object
                new_user = User(username=username, password=password, security_answer=security_answer)
                
                # Add optional fields if provided
                # Note: In this simplified version we're not collecting these fields,
                # but you can add them if needed in your form
                
                # Save user to database
                db.session.add(new_user)
                db.session.commit()
                
                flash('Signup successful! Please log in.', 'success')
                return redirect(url_for('login'))
            except Exception as e:
                # Rollback transaction in case of error
                db.session.rollback()
                flash(f'An error occurred: {str(e)}', 'danger')
                return redirect(url_for('signup'))
        
        # Render the signup template
        return render_template('signup.html', form=form)


    @app.route('/reset', methods=['GET', 'POST'])
    def reset():
        # Create form object to validate CSRF token
        form = PasswordResetForm()
        
        if request.method == 'POST' and form.validate_csrf_token():  # Only validate CSRF token, not other fields
            # Get form data directly from request
            username = request.form.get('username')
            security_answer = request.form.get('security_answer')
            password = request.form.get('password')
            confirm_password = request.form.get('confirm_password')
            
            # Check if passwords match
            if password != confirm_password:
                flash('Passwords do not match.', 'danger')
                return redirect(url_for('reset'))
            
            # Query for the user
            user = User.query.filter_by(username=username).first()
            if not user:
                flash('User not found. Please check your username.', 'danger')
                return redirect(url_for('reset'))
            
            # Validate security answer
            if not user.check_security_answer(security_answer):
                flash('Incorrect security answer. Please try again.', 'danger')
                return redirect(url_for('reset'))
            
            # Update password
            try:
                user.password = password  # Setter will automatically hash the password
                db.session.commit()
                flash('Password reset successful! You can now log in with your new password.', 'success')
                return redirect(url_for('login'))
            except Exception as e:
                # Rollback transaction in case of error
                db.session.rollback()
                flash('An error occurred while resetting your password. Please try again.', 'danger')
                return redirect(url_for('reset'))
        
        # Render the password reset template
        return render_template('reset.html', form=form)


    # Logout route
    @app.route('/logout')
    @login_required
    def logout():
        # Log out the current user
        logout_user()
        flash('You have been logged out', 'info')
        return redirect(url_for('login'))
    
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
        