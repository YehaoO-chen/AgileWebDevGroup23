from datetime import datetime, timedelta
from flask import jsonify, request
from flask_login import current_user, login_required

from app.models import StudyDuration, StudyPlan
from app import db
from sqlalchemy import func

def init_api_dashboard(app):


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

