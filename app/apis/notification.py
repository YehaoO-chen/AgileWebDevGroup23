


from flask import jsonify, request
from flask_login import current_user, login_required
from app import db
from app.models import Notification, User


def init_api_notification(app):
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
