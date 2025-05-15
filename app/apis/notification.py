from flask import jsonify, request
from flask_login import current_user, login_required
from app import db
from app.models import Notification, User
import traceback # For more detailed error logging if needed

    
def init_api_notification(app):
    # Notification API
    @app.route('/api/notification', methods=['POST'])
    @login_required
    def create_notification():
        data = request.get_json()
        if not data or 'receiver_ids' not in data or 'content' not in data:
            return jsonify({'success': False, 'message': 'Missing receiver_ids or content'}), 400

        receiver_ids_input = data['receiver_ids']
        content = data['content']

        if not isinstance(receiver_ids_input, list):
            # If a single ID is passed, treat it as a list with one element
            if isinstance(receiver_ids_input, int):
                receiver_ids_input = [receiver_ids_input]
            else:
                return jsonify({'success': False, 'message': 'receiver_ids must be a list of integers or a single integer.'}), 400
        
        if not receiver_ids_input:
            return jsonify({'success': False, 'message': 'receiver_ids list cannot be empty.'}), 400

        created_notifications_ids = []
        not_found_receivers = []
        successfully_sent_to_count = 0

        for receiver_id in receiver_ids_input:
            if not isinstance(receiver_id, int):
                # Skip non-integer IDs or handle as an error
                # For now, we'll skip and could log this
                print(f"Skipping invalid receiver_id format: {receiver_id}")
                continue

            receiver = User.query.get(receiver_id)
            if not receiver:
                not_found_receivers.append(receiver_id)
                continue
            
            # Prevent users from sending notifications to themselves
            if receiver_id == current_user.id:
                print(f"User {current_user.id} attempted to send a notification to themselves. Skipping.")
                continue

            notification = Notification(
                sender_id=current_user.id,
                receiver_id=receiver_id,
                content=content
                # status defaults to 0 (unread)
                # send_time defaults to datetime.utcnow
            )
            db.session.add(notification)
            successfully_sent_to_count += 1
            # We need to commit to get the ID, or commit in batch later
            # For now, let's commit per notification to get individual IDs if needed,
            # but batch commit is more efficient for many receivers.
            # For simplicity here, we'll commit at the end.

        if successfully_sent_to_count > 0:
            db.session.commit() # Commit all added notifications
            # To get IDs, we'd need to query them back or handle IDs differently if not committing one by one.
            # For now, a general success message is simpler if individual IDs aren't strictly needed in response.
            
            message = f'{successfully_sent_to_count} notification(s) created successfully.'
            if not_found_receivers:
                message += f' Receivers not found for IDs: {not_found_receivers}.'
            return jsonify({'success': True, 'message': message}), 201
        
        else:
            error_message = 'No notifications were sent.'
            if not_found_receivers:
                error_message += f' All specified receiver IDs were not found: {not_found_receivers}.'
            elif not receiver_ids_input: # Should be caught earlier but as a safeguard
                 error_message = 'Receiver IDs list was effectively empty after validation.'
            else: # e.g. all were self-sends
                error_message = 'No valid recipients after filtering (e.g., self-sends or invalid IDs).'

            return jsonify({'success': False, 'message': error_message}), 400

    @app.route('/api/notification/', methods=['GET'])
    @login_required
    def get_active_received_notifications():
        """
        Gets all notifications received by the current user
        that are either unread (status 0) or read (status 1).
        Excludes deleted (status 2) notifications.
        """
        try:
            notifications_list = Notification.query.filter(
                Notification.receiver_id == current_user.id,
                Notification.status.in_([0, 1])  # 0: unread, 1: read
            ).order_by(Notification.send_time.desc()).all()

            result = []
            for n in notifications_list:
                sender = User.query.get(n.sender_id)
                result.append({
                    'id': n.id,
                    'sender_id': n.sender_id,
                    'sender_username': sender.username if sender else "Unknown User",
                    'receiver_id': n.receiver_id, # Current user's ID
                    'content': n.content,
                    'send_time': n.send_time.isoformat() + 'Z', # ISO format with Z for UTC
                    'status': n.status
                })
            return jsonify(result)
        except Exception as e:
            # Log the error for debugging
            print(f"Error in /api/notification/ (get_active_received_notifications): {str(e)}")
            traceback.print_exc()
            return jsonify({'success': False, 'message': 'An error occurred while fetching notifications.'}), 500

    @app.route('/api/notifications/sent', methods=['GET'])
    @login_required
    def get_sent_notifications():
        """
        Gets all notifications sent by the current user.
        Excludes notifications marked as deleted (status 2).
        """
        try:
            notifications = Notification.query.filter(
                Notification.sender_id == current_user.id,
                Notification.status != 2  # Exclude deleted notifications
            ).order_by(
                Notification.send_time.desc()
            ).all()
            
            # print(f"User {current_user.id} has {len(notifications)} non-deleted sent notifications")
            
            result = []
            for notification in notifications:
                receiver = User.query.get(notification.receiver_id)
                receiver_name = receiver.username if receiver else "Unknown User"
                # print(f"Sent Notification ID: {notification.id}, Receiver: {receiver_name}, Content: {notification.content}")
                
                result.append({
                    'id': notification.id,
                    'content': notification.content,
                    'sender_id': notification.sender_id, # Current user's ID
                    'receiver_id': notification.receiver_id,
                    'receiver_username': receiver_name,
                    'send_time': notification.send_time.isoformat() + 'Z', # ISO format with Z for UTC
                    'status': notification.status # This status reflects the receiver's interaction
                })
            
            # print(f"API /api/notifications/sent will return {len(result)} records")
            return jsonify(result)
        except Exception as e:
            print(f"Error in /api/notifications/sent: {str(e)}")
            traceback.print_exc()
            return jsonify({'success': False, 'message': 'An error occurred while fetching sent notifications.'}), 500
        
        
    @app.route('/api/notifications/received', methods=['GET'])
    @login_required
    def get_received_notifications():
        """
        Gets all notifications received by the current user.
        Excludes notifications marked as deleted (status 2).
        """
        try:
            notifications = Notification.query.filter(
                Notification.receiver_id == current_user.id,
                Notification.status != 2  # Exclude deleted notifications
            ).order_by(Notification.send_time.desc()).all()

            result = []
            for notification in notifications:
                sender = User.query.get(notification.sender_id)
                result.append({
                    'id': notification.id,
                    'content': notification.content,
                    'sender_id': sender.id if sender else None,
                    'sender_username': sender.username if sender else "Unknown User",
                    'receiver_id': notification.receiver_id, # Current user's ID
                    'send_time': notification.send_time.isoformat() + 'Z', # ISO format with Z for UTC
                    'status': notification.status
                })
            return jsonify(result)
        except Exception as e:
            print(f"Error in /api/notifications/received: {str(e)}")
            traceback.print_exc()
            return jsonify({'success': False, 'message': 'An error occurred while fetching received notifications.'}), 500

    # You might want an endpoint to mark notifications as read or deleted
    @app.route('/api/notification/<int:notification_id>/status', methods=['PUT'])
    @login_required
    def update_notification_status(notification_id):
        data = request.get_json()
        new_status = data.get('status')

        if new_status is None or new_status not in [0, 1, 2]: # 0: unread, 1: read, 2: deleted
            return jsonify({'success': False, 'message': 'Invalid status provided. Must be 0, 1, or 2.'}), 400

        notification = Notification.query.get(notification_id)

        if not notification:
            return jsonify({'success': False, 'message': 'Notification not found.'}), 404

        # Ensure the current user is the receiver of the notification to change its status
        if notification.receiver_id != current_user.id:
            return jsonify({'success': False, 'message': 'Access denied. You can only update status of notifications you received.'}), 403
        
        # Prevent un-deleting or un-reading if that's not desired, for now, allow any valid transition
        notification.status = new_status
        db.session.commit()
        
        return jsonify({'success': True, 'message': f'Notification {notification_id} status updated to {new_status}.'})
   
    @app.route('/api/notification/<int:notification_id>/data', methods=['GET'])
    @login_required
    def get_notification_shared_data(notification_id):
        notification = Notification.query.get(notification_id)
        if not notification:
            return jsonify({'success': False, 'message': 'Notification not found'}), 404
        if notification.receiver_id != current_user.id and notification.sender_id != current_user.id:
            return jsonify({'success': False, 'message': 'Access denied'}), 403

        content = notification.content
        if "Total Study Time" in content:
            data_type = "Total Study Time"
            value = content.split(":")[1].replace("minutes", "").strip()
        elif "Average Study Time" in content:
            data_type = "Average Study Time"
            value = content.split(":")[1].replace("minutes", "").strip()
        else:
            return jsonify({'success': False, 'message': 'Unrecognized data format'}), 400

        return jsonify({
            'success': True,
            'data_type': data_type,
            'value': value,
            'period': "Shared manually"
        })

