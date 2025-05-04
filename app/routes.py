from flask import Flask, jsonify, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from datetime import datetime, timedelta

from sqlalchemy import func
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
    def study_plan():
        return render_template('studyplan.html')


    #Share route (requires login)

    @app.route('/share')
    @login_required
    def share():
        data_type = request.form.get('dataType')
        users = request.form.getlist('users[]')
    
    # 这里添加处理分享逻辑
    # 例如保存到数据库或发送通知
    
    # 返回成功响应
        return jsonify({
            'success': True,
            'message': f'成功分享{data_type}给{len(users)}位用户'
        })


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
    
    #Profile route
    @app.route('/profile')
    @login_required
    def profile():
        user = current_user
        return render_template('profile.html', user=user)
    
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
        period = request.args.get('period', 'week') # get period ，default 'week'
        # cal start date
        now = datetime.now(datetime.timezone.utc)
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

        study_durations = StudyDuration.query.filter(
            StudyDuration.user_id == current_user.id,
            StudyDuration.start_time >= start_date
        ).all()
        #cal total study time in minutes
        total_study_time = sum(sd.duration for sd in study_durations)

        #cal avg study time in minutes
        if len(study_durations) > 0:
            avg_study_time = total_study_time / len(study_durations)
        else:
            avg_study_time = 0
        
        #cal today study time in minutes
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        today_end = now.replace(hour=23, minute=59, second=59, microsecond=999999)
        today_study_time = sum(sd.duration for sd in study_durations if sd.start_time >= today_start and sd.end_time <= today_end)

        #cal each day study time in minutes during period
        study_durations_by_day = {}
        for sd in study_durations:
            day = sd.start_time.date()
            if day not in study_durations_by_day:
                study_durations_by_day[day] = 0
            study_durations_by_day[day] += sd.duration
 
        # study_plans = StudyPlan.query.filter_by(user_id=current_user.id).all()

        return jsonify({
            'period': period,
            'start_date': start_date.strftime('%Y-%m-%d %H:%M:%S'),
            'end_date': now.strftime('%Y-%m-%d %H:%M:%S'),
            'total_study_time': total_study_time,
            'avg_study_time': avg_study_time,
            'today_study_time': today_study_time,
            'study_durations_by_day': study_durations_by_day
        })
    
    @app.route('/api/dashboard/task', methods=['GET'])
    @login_required
    def get_dashboard_task_data(): # Renamed function
        period = request.args.get('period', 'week') # get period, default 'week'

        # Calculate start date based on period (same logic as above)
        now = datetime.now(datetime.timezone.utc) # Use timezone-aware datetime
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

        # Query StudyPlan counts grouped by status within the period
        # Filter based on create_time >= start_date
        status_counts = db.session.query(
                StudyPlan.status,
                func.count(StudyPlan.id)
            ).filter(
                StudyPlan.user_id == current_user.id,
                StudyPlan.create_time >= start_date # Filter plans created within the period
            ).group_by(
                StudyPlan.status
            ).all()

        # Format the results into a dictionary {status_code: count}
        # Initialize with 0 counts for all statuses
        plan_summary = {0: 0, 1: 0, 2: 0}
        for status, count in status_counts:
            if status in plan_summary: # Ensure status is valid (0, 1, or 2)
                plan_summary[status] = count

        return jsonify({
            'period': period,
            'start_date': start_date.isoformat(), # Optionally return the calculated start date
            'task_summary': {
                'open': plan_summary.get(0, 0),
                'completed': plan_summary.get(1, 0),
                'deleted': plan_summary.get(2, 0)
            }
        })
    
    @app.route('/api/profile', methods=['GET'])
    @login_required
    def get_profile():
        user = current_user
        return jsonify({
            'id': user.id,
            'username': user.username,
            'create_time': user.create_time.strftime('%Y-%m-%d %H:%M:%S')
        })


    @app.route('/api/profile', methods=['PUT'])
    @login_required
    def update_profile():
        data = request.get_json()
        user = current_user
        user.username = data['username']
        user.password = data['password']
        db.session.commit()
        return jsonify({'success': True})
    



    # UPLOAD_FOLDER = 'static/uploads'
    
    # @app.route('/upload_avatar', methods=['POST'])
    # @login_required
    # def upload_avatar():
    #     if 'avatar' in request.files:
    #         file = request.files['avatar']
    #         filename = secure_filename(file.filename)
    #         save_path = os.path.join(UPLOAD_FOLDER, filename)
    #         file.save(save_path)
    #         avatar_url = url_for('static', filename=f'uploads/{filename}')
    #         return jsonify({'success': True, 'avatar_url': avatar_url})
    #     return jsonify({'success': False})
