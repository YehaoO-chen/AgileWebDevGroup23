from datetime import datetime, timezone
from flask import jsonify, request
from flask_login import current_user, login_required
from app import db
from app.models import StudyPlan

def init_api_studyplan(app):
    @app.route('/api/studyplan', methods=['POST'])
    @login_required
    def create_study_plan():
        data = request.get_json()
        if not data or 'content' not in data:
            return jsonify({'success': False, 'message': 'Missing content in request'}), 400

        study_plan = StudyPlan(
            user_id=current_user.id,
            content=data['content'],
            # create_time is set by default in model
            # complete_time is initially null
            # status is set by default in model (0: open)
        )
        db.session.add(study_plan)
        db.session.commit()
        return jsonify({
            'success': True,
            'message': 'Study plan created successfully.',
            'study_plan': {
                'id': study_plan.id,
                'user_id': study_plan.user_id,
                'content': study_plan.content,
                'create_time': study_plan.create_time.isoformat() + 'Z', # ISO format with Z for UTC
                'complete_time': study_plan.complete_time.isoformat() + 'Z' if study_plan.complete_time else None,
                'status': study_plan.status
            }
        }), 201

    @app.route('/api/studyplan/<int:study_plan_id>', methods=['GET'])
    @login_required
    def get_study_plan(study_plan_id):
        study_plan = StudyPlan.query.filter_by(id=study_plan_id, user_id=current_user.id).first()
        if not study_plan:
            return jsonify({'success': False, 'message': 'Study plan not found or access denied'}), 404
        
        return jsonify({
            'success': True,
            'study_plan': {
                'id': study_plan.id,
                'user_id': study_plan.user_id,
                'content': study_plan.content,
                'create_time': study_plan.create_time.isoformat() + 'Z',
                'complete_time': study_plan.complete_time.isoformat() + 'Z' if study_plan.complete_time else None,
                'status': study_plan.status
            }
        })

    @app.route('/api/studyplan/<int:study_plan_id>', methods=['PUT'])
    @login_required
    def update_study_plan(study_plan_id):
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'message': 'No data provided for update'}), 400

        study_plan = StudyPlan.query.filter_by(id=study_plan_id, user_id=current_user.id).first()
        if not study_plan:
            return jsonify({'success': False, 'message': 'Study plan not found or access denied'}), 404

        if 'content' in data:
            study_plan.content = data['content']
        
        if 'status' in data:
            try:
                status = int(data['status'])
                if status in [0, 1, 2]: # 0: open, 1: completed, 2: deleted
                    study_plan.status = status
                    if status == 1 and not study_plan.complete_time: # Mark as completed
                        study_plan.complete_time = datetime.now(timezone.utc)
                    elif status != 1: # If not completed, clear complete_time
                        study_plan.complete_time = None
                else:
                    return jsonify({'success': False, 'message': 'Invalid status value'}), 400
            except ValueError:
                return jsonify({'success': False, 'message': 'Status must be an integer'}), 400

        # Allow explicitly setting complete_time if provided and valid
        if 'complete_time' in data:
            if data['complete_time'] is None:
                study_plan.complete_time = None
            else:
                try:
                    # Expecting ISO format string like "YYYY-MM-DDTHH:MM:SSZ" or "YYYY-MM-DDTHH:MM:SS.ffffffZ"
                    # Or allow just date "YYYY-MM-DD" and set time to midnight UTC
                    dt_str = data['complete_time']
                    if 'T' not in dt_str: # If only date is provided
                        dt_str += "T00:00:00Z"
                    if dt_str.endswith('Z'):
                         study_plan.complete_time = datetime.fromisoformat(dt_str.replace('Z', '+00:00'))
                    else: # Assuming local time if no Z, convert to UTC (less ideal)
                         study_plan.complete_time = datetime.fromisoformat(dt_str).astimezone(timezone.utc)

                except ValueError:
                    return jsonify({'success': False, 'message': 'Invalid complete_time format. Use ISO format (YYYY-MM-DDTHH:MM:SSZ).'}), 400
        
        db.session.commit()
        return jsonify({
            'success': True,
            'message': 'Study plan updated successfully.',
            'study_plan': {
                'id': study_plan.id,
                'user_id': study_plan.user_id,
                'content': study_plan.content,
                'create_time': study_plan.create_time.isoformat() + 'Z',
                'complete_time': study_plan.complete_time.isoformat() + 'Z' if study_plan.complete_time else None,
                'status': study_plan.status
            }
        })

    @app.route('/api/studyplan/<int:study_plan_id>', methods=['DELETE'])
    @login_required
    def delete_study_plan(study_plan_id):
        study_plan = StudyPlan.query.filter_by(id=study_plan_id, user_id=current_user.id).first()
        if not study_plan:
            return jsonify({'success': False, 'message': 'Study plan not found or access denied'}), 404
        
        # Option 1: Hard delete
        # db.session.delete(study_plan)
        
        # Option 2: Soft delete (mark as deleted)
        study_plan.status = 2 # 2: deleted
        study_plan.complete_time = datetime.now(timezone.utc) # Optionally mark completion time on deletion

        db.session.commit()
        return jsonify({'success': True, 'message': 'Study plan deleted successfully.'})

    @app.route('/api/studyplan', methods=['GET'])
    @login_required
    def get_study_plans():
        # Optionally filter by status, e.g., to exclude deleted plans by default
        status_filter = request.args.get('status')
        query = StudyPlan.query.filter_by(user_id=current_user.id)

        if status_filter is not None:
            try:
                status_val = int(status_filter)
                if status_val in [0, 1, 2]:
                    query = query.filter_by(status=status_val)
                else:
                    # Silently ignore invalid status filter or return error
                    pass # Or: return jsonify({'success': False, 'message': 'Invalid status filter value'}), 400
            except ValueError:
                 # Silently ignore invalid status filter or return error
                pass # Or: return jsonify({'success': False, 'message': 'Status filter must be an integer'}), 400
        else:
            # Default: Exclude deleted plans if no status filter is provided
            query = query.filter(StudyPlan.status != 2)


        study_plans = query.order_by(StudyPlan.create_time.desc()).all()
        
        return jsonify({
            'success': True,
            'study_plans': [{
                'id': sp.id,
                'user_id': sp.user_id,
                'content': sp.content,
                'create_time': sp.create_time.isoformat() + 'Z',
                'complete_time': sp.complete_time.isoformat() + 'Z' if sp.complete_time else None,
                'status': sp.status
            } for sp in study_plans]
        })