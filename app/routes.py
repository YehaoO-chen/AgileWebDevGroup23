import os
from sqlite3 import IntegrityError
from flask import Flask, jsonify, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from datetime import datetime, timedelta,timezone
from werkzeug.utils import secure_filename
from sqlalchemy import func
from app.models import User, StudyPlan, StudyDuration, Notification
from app import db
from PIL import Image # Import Pillow Image module




ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def init_routes(app):
    # Define the upload folder relative to the app's root path
    # Ensure the UPLOAD_FOLDER exists
    UPLOAD_FOLDER = os.path.join(app.root_path,'static', 'uploads')
    if not os.path.exists(UPLOAD_FOLDER):
        try:
            os.makedirs(UPLOAD_FOLDER) # Create the directory if it doesn't exist
            print(f"Created directory: {UPLOAD_FOLDER}")
        except OSError as e:
            print(f"Error creating directory {UPLOAD_FOLDER}: {e}")
            # Handle the error appropriately, maybe raise it or log critical error

    app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER # Store in app config
    app.config['MAX_IMAGE_SIZE'] = 256 # Define max size for resizing

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


    #Share route (requires login)

    # @app.route('/share')
    # @login_required
    # def share():
    #     data_type = request.form.get('dataType')
    #     users = request.form.getlist('users[]')
    #     return jsonify({
    #         'success': True,
    #         'message': f'successfully {data_type}to {len(users)} user'
    #     })


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
        
        # user = current_user
        # if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        #     # Render only the profile content part
        #     return render_template('profile.html', user=user, is_partial=True)
        # else:
        #     # Render the full page including base
        #     return render_template('profile.html', user=user, is_partial=False)

    
    #=================================================================
    #APIs
    #=================================================================
    @app.route('/api/studyplan', methods=['POST'])
    @login_required
    def create_study_plan():
        data = request.get_json()
        study_plan = StudyPlan(
            user_id=current_user.id,
            title=data['title'],
            description=data['description'],
            start_date=datetime.strptime(data['start_date'], '%Y-%m-%d'),
            end_date=datetime.strptime(data['end_date'], '%Y-%m-%d')
        )
        db.session.add(study_plan)
        db.session.commit()
        return jsonify({'success': True, 'study_plan_id': study_plan.id})
    
    @app.route('/api/studyplan/<int:study_plan_id>', methods=['GET'])
    @login_required
    def get_study_plan(study_plan_id):
        study_plan = StudyPlan.query.get_or_404(study_plan_id)
        return jsonify({
            'id': study_plan.id,
            'title': study_plan.title,
            'description': study_plan.description,
            'start_date': study_plan.start_date.strftime('%Y-%m-%d'),
            'end_date': study_plan.end_date.strftime('%Y-%m-%d')
        })
    
    @app.route('/api/studyplan/<int:study_plan_id>', methods=['PUT'])
    @login_required
    def update_study_plan(study_plan_id):
        data = request.get_json()
        study_plan = StudyPlan.query.get_or_404(study_plan_id)
        study_plan.title = data['title']
        study_plan.description = data['description']
        study_plan.start_date = datetime.strptime(data['start_date'], '%Y-%m-%d')
        study_plan.end_date = datetime.strptime(data['end_date'], '%Y-%m-%d')
        db.session.commit()
        return jsonify({'success': True})
    
    @app.route('/api/studyplan/<int:study_plan_id>', methods=['DELETE'])
    @login_required
    def delete_study_plan(study_plan_id):
        study_plan = StudyPlan.query.get_or_404(study_plan_id)
        db.session.delete(study_plan)
        db.session.commit()
        return jsonify({'success': True})
    
    @app.route('/api/studyplan', methods=['GET'])
    @login_required
    def get_study_plans():
        study_plans = StudyPlan.query.filter_by(user_id=current_user.id).all()
        return jsonify([{
            'id': sp.id,
            'title': sp.title,
            'description': sp.description,
            'start_date': sp.start_date.strftime('%Y-%m-%d'),
            'end_date': sp.end_date.strftime('%Y-%m-%d')
        } for sp in study_plans])
    


    @app.route('/api/studyduration', methods=['POST'])
    @login_required
    def create_study_duration():
        data = request.get_json()
        study_duration = StudyDuration(
            user_id=current_user.id,
            duration=data['duration'],
            start_time=datetime.strptime(data['start_time'], '%Y-%m-%d %H:%M:%S'),
            end_time=datetime.strptime(data['end_time'], '%Y-%m-%d %H:%M:%S'),
            stop_times=data['stop_times']
        )
        db.session.add(study_duration)
        db.session.commit()
        return jsonify({'success': True, 'study_duration_id': study_duration.id})
    
    
    @app.route('/api/studyduration/<int:study_duration_id>', methods=['GET'])
    @login_required
    def get_study_duration(study_duration_id):
        study_duration = StudyDuration.query.get_or_404(study_duration_id)
        return jsonify({
            'id': study_duration.id,
            'duration': study_duration.duration,
            'start_time': study_duration.start_time.strftime('%Y-%m-%d %H:%M:%S'),
            'end_time': study_duration.end_time.strftime('%Y-%m-%d %H:%M:%S'),
            'stop_times': study_duration.stop_times
        })
    
    @app.route('/api/studyduration/<int:study_duration_id>', methods=['PUT'])
    @login_required
    def update_study_duration(study_duration_id):
        data = request.get_json()
        study_duration = StudyDuration.query.get_or_404(study_duration_id)
        study_duration.duration = data['duration']
        study_duration.start_time = datetime.strptime(data['start_time'], '%Y-%m-%d %H:%M:%S')
        study_duration.end_time = datetime.strptime(data['end_time'], '%Y-%m-%d %H:%M:%S')
        study_duration.stop_times = data['stop_times']
        db.session.commit()
        return jsonify({'success': True})
    
    @app.route('/api/studyduration/<int:study_duration_id>', methods=['DELETE'])
    @login_required
    def delete_study_duration(study_duration_id):
        study_duration = StudyDuration.query.get_or_404(study_duration_id)
        db.session.delete(study_duration)
        db.session.commit()
        return jsonify({'success': True})
    
    @app.route('/api/studyduration', methods=['GET'])
    @login_required
    def get_study_durations():
        study_durations = StudyDuration.query.filter_by(user_id=current_user.id).all()
        return jsonify([{
            'id': sd.id,
            'duration': sd.duration,
            'start_time': sd.start_time.strftime('%Y-%m-%d %H:%M:%S'),
            'end_time': sd.end_time.strftime('%Y-%m-%d %H:%M:%S'),
            'stop_times': sd.stop_times
        } for sd in study_durations])


    # Notification API
    @app.route('/api/notification', methods=['POST'])
    @login_required
    def create_notification():
        data = request.get_json()
        notification = Notification(
            sender_id=current_user.id,
            receiver_id=data['receiver_id'],
            content=data['content']
        )
        db.session.add(notification)
        db.session.commit()
        return jsonify({'success': True, 'notification_id': notification.id})
    
    @app.route('/api/notification/', methods=['GET'])
    @login_required
    def get_notification():
        notification = Notification.query.filter_by(receiver_id=current_user.id, status='sent').all()
        return jsonify({
            'id': notification.id,
            'sender_id': notification.sender_id,
            'receiver_id': notification.receiver_id,
            'content': notification.content,
            'send_time': notification.send_time.strftime('%Y-%m-%d %H:%M:%S'),
            'status': notification.status
        })
    


    @app.route('/api/dashboard/duration', methods=['GET'])
    @login_required
    def get_dashboard_data():
        period = request.args.get('period', 'week')
        now = datetime.utcnow()  # ✅  offset-naive 
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        today_end = today_start + timedelta(days=1)

        # offset-naive
        if period == 'day':
            start_date = today_start
        elif period == 'week':
            start_date = today_start - timedelta(days=now.weekday())
        elif period == 'month':
            start_date = today_start.replace(day=1)
        else:
            return jsonify({'error': 'Invalid period specified'}), 400

        
        study_durations = StudyDuration.query.filter(
            StudyDuration.user_id == current_user.id,
            StudyDuration.start_time >= start_date
        ).all()

        total_study_time = sum(sd.duration for sd in study_durations)
        avg_study_time = total_study_time / len(study_durations) if study_durations else 0
        today_study_time = sum(
            sd.duration for sd in study_durations
            if sd.start_time >= today_start and sd.start_time < today_end
        )

        # day
        study_durations_by_day = {}
        for sd in study_durations:
            day = sd.start_time.date().isoformat()
            study_durations_by_day[day] = study_durations_by_day.get(day, 0) + sd.duration

        return jsonify({
            'period': period,
            'total_study_time': total_study_time,
            'avg_study_time': avg_study_time,
            'today_study_time': today_study_time,
            'study_durations_by_day': study_durations_by_day
        })



    @app.route('/api/dashboard/task', methods=['GET'])
    @login_required
    def get_dashboard_task_data():
        try:
            period = request.args.get('period', 'week')
            now = datetime.now()  # ✅ offset-naive
            start_date = None

            if period == 'day':
                start_date = now.replace(hour=0, minute=0, second=0, microsecond=0)
            elif period == 'week':
                start_date = (now - timedelta(days=now.weekday())).replace(hour=0, minute=0, second=0, microsecond=0)
            elif period == 'month':
                start_date = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            elif period == 'quarter':
                current_quarter = (now.month - 1) // 3 + 1
                start_month = (current_quarter - 1) * 3 + 1
                start_date = now.replace(month=start_month, day=1, hour=0, minute=0, second=0, microsecond=0)
            elif period == 'half_year':
                start_month = 1 if now.month <= 6 else 7
                start_date = now.replace(month=start_month, day=1, hour=0, minute=0, second=0, microsecond=0)
            elif period == 'year':
                start_date = now.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
            else:
                return jsonify({'error': 'Invalid period specified'}), 400

            status_counts = db.session.query(
                StudyPlan.status,
                func.count(StudyPlan.id)
            ).filter(
                StudyPlan.user_id == current_user.id,
                StudyPlan.create_time >= start_date 
            ).group_by(StudyPlan.status).all()

            plan_summary = {0: 0, 1: 0, 2: 0}
            for status, count in status_counts:
                if status in plan_summary:
                    plan_summary[status] = count

            return jsonify({
                'period': period,
                'start_date': start_date.strftime('%Y-%m-%d %H:%M:%S'),
                'task_summary': {
                    'open': plan_summary.get(0, 0),
                    'completed': plan_summary.get(1, 0),
                    'deleted': plan_summary.get(2, 0)
                }
            })

        except Exception as e:
            import traceback
            traceback.print_exc()
            return jsonify({'error': 'Server error', 'detail': str(e)}), 500

    
    @app.route('/api/profile', methods=['GET'])
    @login_required
    def get_profile():
        user = current_user
        return jsonify({
            'id': user.id,
            'username': user.username,
            'create_time': user.create_time.strftime('%Y-%m-%d %H:%M:%S'),
            'fullname': user.fullname,
            'major': user.major,
            'email': user.email,
            'phone': user.phone,
            'address': user.address,
            'student_id': user.student_id,
            'avatar': user.avatar
        })


    @app.route('/api/profile', methods=['PUT'])
    @login_required
    def update_profile():
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'error': 'Invalid input data'}), 400

        user = current_user
        errors = {}

        # --- Update fields and perform checks ---

        # Username (check uniqueness if changed)
        new_username = data.get('username')
        if new_username and new_username != user.username:
            existing_user = User.query.filter(User.username == new_username, User.id != user.id).first()
            if existing_user:
                errors['username'] = 'Username already taken.'
            else:
                user.username = new_username

        # Email (check uniqueness if changed)
        new_email = data.get('email')
        if new_email and new_email != user.email:
            existing_user = User.query.filter(User.email == new_email, User.id != user.id).first()
            if existing_user:
                errors['email'] = 'Email already registered.'
            else:
                user.email = new_email
        elif 'email' in data and not new_email: # Allow setting email to null if desired and model allows
             user.email = None


        # Phone (check uniqueness if changed)
        new_phone = data.get('phone')
        if new_phone and new_phone != user.phone:
            existing_user = User.query.filter(User.phone == new_phone, User.id != user.id).first()
            if existing_user:
                errors['phone'] = 'Phone number already registered.'
            else:
                user.phone = new_phone
        elif 'phone' in data and not new_phone: # Allow setting phone to null
            user.phone = None

        # Student ID (check uniqueness if changed)
        new_student_id = data.get('student_id')
        if new_student_id and new_student_id != user.student_id:
            existing_user = User.query.filter(User.student_id == new_student_id, User.id != user.id).first()
            if existing_user:
                errors['student_id'] = 'Student ID already registered.'
            else:
                user.student_id = new_student_id
        elif 'student_id' in data and not new_student_id: # Allow setting student_id to null
            user.student_id = None

        # Update other nullable fields directly if provided
        if 'fullname' in data:
            user.fullname = data.get('fullname')
        if 'major' in data:
            user.major = data.get('major')
        if 'address' in data:
            user.address = data.get('address')

        # --- Commit changes if no errors ---
        if errors:
            return jsonify({'success': False, 'errors': errors}), 400

        try:
            db.session.commit()
            return jsonify({'success': True, 'message': 'Profile updated successfully.'})
        except IntegrityError as e:
            db.session.rollback()
            # This might catch uniqueness errors missed above, though less specific
            return jsonify({'success': False, 'error': 'Database error: Could not update profile. Check unique fields.'}), 500
        except Exception as e:
            db.session.rollback()
            # Log the exception e for debugging
            print(f"Error updating profile: {e}")
            return jsonify({'success': False, 'error': 'An unexpected error occurred.'}), 500


    
    @app.route('/api/upload_avatar', methods=['POST'])
    @login_required
    def upload_avatar():
        # Check if the post request has the file part
        if 'avatar' not in request.files:
            return jsonify({'success': False, 'error': 'No file part in the request'}), 400
        
        file = request.files['avatar']
        
        # If the user does not select a file, the browser submits an empty file without a filename.
        if file.filename == '':
            return jsonify({'success': False, 'error': 'No selected file'}), 400
        
        if file and allowed_file(file.filename):
            # Generate a secure filename and add user-specific prefix to avoid collisions
            original_extension = file.filename.rsplit('.', 1)[1].lower()
            # Using user ID is safer than username for uniqueness and avoiding special chars
            filename = secure_filename(f"user_{current_user.id}_avatar.{original_extension}")
            save_path = os.path.join( app.config['UPLOAD_FOLDER'] , filename)
            
            try:
                # --- Optional: Delete old avatar file before saving new one ---
                if current_user.avatar and current_user.avatar != 'default.jpg':
                    old_avatar_path = os.path.join(app.config['UPLOAD_FOLDER'], current_user.avatar)
                    if os.path.exists(old_avatar_path):
                        try:
                            os.remove(old_avatar_path)
                        except OSError as e:
                            print(f"Error deleting old avatar {old_avatar_path}: {e}") # Log error but continue
               
                # --- End Optional ---

                # --- Image Resizing Logic ---
                max_size = app.config['MAX_IMAGE_SIZE']
                img = Image.open(file.stream) # Open image from the file stream
                width, height = img.size
                resized = False

                if max(width, height) > max_size:
                    ratio = max_size / max(width, height)
                    new_width = int(width * ratio)
                    new_height = int(height * ratio)
                    # Use LANCZOS for high-quality downsampling
                    img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
                    resized = True
                    print(f"Resized image to: {new_width}x{new_height}") # Optional logging

                # Handle image format and transparency for saving
                save_format = original_extension.upper()
                if save_format == 'JPG':
                    save_format = 'JPEG' # Pillow uses 'JPEG'

                # If saving as JPEG and image has alpha channel (transparency), convert to RGB
                if save_format == 'JPEG' and img.mode in ('RGBA', 'P'):
                     img = img.convert('RGB')

                # Save the (potentially resized) image
                img.save(save_path, format=save_format, quality=85, optimize=True) # Adjust quality as needed
                # --- End Image Resizing Logic ---
                
                # Update user avatar field in the database with the new filename
                current_user.avatar = filename
                db.session.commit()
                
                # Construct the URL path for the frontend
                # Assumes 'static' is served at the root URL path '/static'
                avatar_url = url_for('static', filename=f'uploads/{filename}', _external=False) # Use relative URL

                return jsonify({'success': True, 'avatar_url': avatar_url, 'filename': filename})

            except IntegrityError as e:
                 db.session.rollback()
                 return jsonify({'success': False, 'error': 'Database error saving avatar reference.'}), 500
            except Exception as e:
                db.session.rollback() # Rollback DB changes if file save fails after potential DB update attempt
                print(f"Error saving avatar: {e}") # Log the error
                return jsonify({'success': False, 'error': f'Failed to save file: {str(e)}'}), 500
        else:
            return jsonify({'success': False, 'error': 'File type not allowed'}), 400
    
    
    @app.route('/api/users', methods=['GET'])
    @login_required
    def get_users():
        try:
            # Get all users except the current user
            users = User.query.filter(User.id != current_user.id).all()
            print(f"Found {len(users)} users for sharing")
            
            result = [{
                'id': user.id,
                'username': user.username
            } for user in users]
            
            return jsonify(result)
        except Exception as e:
            print(f"Error getting users: {str(e)}")
            return jsonify([]), 500

    @app.route('/api/share', methods=['POST'])
    @login_required
    def share_data():
        try:
            print("Share data API called")
            data = request.get_json()
            
            if not data:
                print("No data received in request")
                return jsonify({
                    'success': False,
                    'message': 'No data received'
                }), 400
                
            data_type = data.get('dataType')
            user_ids = data.get('users', [])
            
            print(f"Received dataType: {data_type}, users: {user_ids}")
            
            if not data_type or not user_ids:
                print("Missing required data")
                return jsonify({
                    'success': False,
                    'message': 'Missing required data'
                }), 400
            
            # Get content based on data type
            shared_content = ""
            if data_type == 'totalTime':
                # Query total study time
                total_time = db.session.query(db.func.sum(StudyDuration.duration))\
                    .filter(StudyDuration.user_id == current_user.id).scalar() or 0
                shared_content = f"{current_user.username} shared their total study time: {total_time} minutes"
            elif data_type == 'averageTime':
                # Query average study time
                result = db.session.query(
                    db.func.avg(StudyDuration.duration).label('avg_duration')
                ).filter(StudyDuration.user_id == current_user.id).first()
                avg_time = round(result.avg_duration) if result and result.avg_duration else 0
                shared_content = f"{current_user.username} shared their average study time: {avg_time} minutes per session"
            
            # Create notifications for each recipient
            notifications_created = 0
            for user_id in user_ids:
                try:
                    user_id = int(user_id)  # Ensure user_id is an integer
                    
                    # Check if user exists
                    user = User.query.get(user_id)
                    if not user:
                        print(f"User with ID {user_id} not found")
                        continue
                    
                    notification = Notification(
                        sender_id=current_user.id,
                        receiver_id=user_id,
                        content=shared_content,
                        status=0  # Unread
                    )
                    db.session.add(notification)
                    notifications_created += 1
                    print(f"Added notification for user_id {user_id}")
                except (ValueError, TypeError) as e:
                    print(f"Invalid user_id: {user_id}, error: {str(e)}")
                    continue
            
            if notifications_created > 0:
                db.session.commit()
                print(f"Successfully created {notifications_created} notifications")
                return jsonify({
                    'success': True,
                    'message': f'Successfully shared {data_type} with {notifications_created} user(s)'
                })
            else:
                db.session.rollback()
                return jsonify({
                    'success': False,
                    'message': 'No valid users to share with'
                }), 400
            
        except Exception as e:
            db.session.rollback()
            print(f"Error sharing data: {str(e)}")
            import traceback
            traceback.print_exc()
            return jsonify({
                'success': False,
                'message': f'An error occurred: {str(e)}'
            }), 500
            
    @app.route('/api/notifications/sent', methods=['GET'])
    @login_required
    def get_sent_notifications():
        try:
            # 获取当前用户发送的通知，按时间倒序排列
            notifications = Notification.query.filter_by(
                sender_id=current_user.id
            ).order_by(
                Notification.send_time.desc()
            ).all()
            
            print(f"用户 {current_user.id} 有 {len(notifications)} 条发送的通知")
            
            # 格式化通知数据
            result = []
            for notification in notifications:
                receiver = User.query.get(notification.receiver_id)
                receiver_name = receiver.username if receiver else "未知用户"
                print(f"通知 ID: {notification.id}, 接收者: {receiver_name}, 内容: {notification.content}")
                
                result.append({
                    'id': notification.id,
                    'content': notification.content,
                    'receiver_id': notification.receiver_id,
                    'receiver_username': receiver_name,
                    'send_time': notification.send_time.isoformat(),
                    'status': notification.status
                })
            
            print(f"API将返回 {len(result)} 条发送通知的记录")
            return jsonify(result)
        except Exception as e:
            print(f"获取发送通知时出错: {str(e)}")
            import traceback
            traceback.print_exc()
            return jsonify([]), 500
        
        
    @app.route('/api/notifications/received', methods=['GET'])
    @login_required
    def get_received_notifications():
        notifications = Notification.query.filter_by(
            receiver_id=current_user.id
        ).order_by(Notification.send_time.desc()).all()

        result = []
        for notification in notifications:
            sender = User.query.get(notification.sender_id)
            result.append({
                'id': notification.id,
                'content': notification.content,
                'sender_id': sender.id if sender else None,
                'sender_username': sender.username if sender else "Unknown",
                'send_time': notification.send_time.isoformat(),
                'status': notification.status
            })

        return jsonify(result)

    @app.route('/api/study_time', methods=['POST'])
    @login_required
    def record_study_time():
        print("Received study time data:", request.json)
        try:
            data = request.json
            
            # 解析开始时间
            start_time = datetime.fromisoformat(data['start_time'].replace('Z', '+00:00'))
            
            # 计算结束时间（开始时间 + 持续时间）
            end_time = start_time + timedelta(minutes=data['duration'])
            
            study_duration = StudyDuration(
                user_id=current_user.id,
                start_time=start_time,
                end_time=end_time,  # 添加结束时间
                duration=data['duration']
            )
            
            print("Created study duration record:", study_duration)
            db.session.add(study_duration)
            db.session.commit()
            print("Successfully saved to database")
            
            return jsonify({'success': True, 'message': 'Study time recorded successfully'})
        except Exception as e:
            print("Error saving study time:", str(e))
            db.session.rollback()
            return jsonify({'success': False, 'message': str(e)}), 500