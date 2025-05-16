
from datetime import datetime, timedelta
from flask import jsonify, request
from flask_login import current_user, login_required
from app import db
from app.models import StudyDuration


def init_api_studyduration(app):

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


    @app.route('/api/study_time', methods=['POST'])
    @login_required
    def record_study_time():
        print("Received study time data:", request.json)
        try:
            data = request.json
            start_time = datetime.fromisoformat(data['start_time'].replace('Z', '+00:00'))
            end_time = start_time + timedelta(minutes=data['duration'])
            
            study_duration = StudyDuration(
                user_id=current_user.id,
                start_time=start_time,
                end_time=end_time, 
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