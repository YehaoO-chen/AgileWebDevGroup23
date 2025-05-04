from flask_login import UserMixin
from datetime import datetime, timezone
from app.extensions import db, login_manager

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False,index=True)
    password = db.Column(db.String(150), nullable=False)
    security_answer = db.Column(db.String(150), nullable=False)
    create_time = db.Column(db.DateTime, default=datetime.now(timezone.utc))
    fullname = db.Column(db.String(150), nullable=True)
    major = db.Column(db.String(50), nullable=True)
    email = db.Column(db.String(150), unique=True, nullable=True)
    phone = db.Column(db.String(20), unique=True, nullable=True)
    address = db.Column(db.String(200), nullable=True)
    student_id = db.Column(db.String(20), unique=True, nullable=True)
    def __repr__(self):
        return f'<User {self.username}>'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# 添加到现有的models.py文件中

# 学习计划模型
class StudyPlan(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.String(200), nullable=False)
    create_time = db.Column(db.DateTime, default=datetime.now(timezone.utc), nullable=False)
    complete_time = db.Column(db.DateTime, nullable=True)
    status = db.Column(db.Integer, default=0, nullable=False)  # 0: open, 1: completed, 2: deleted
    
    user = db.relationship('User', backref=db.backref('study_plans', lazy=True))
    
    def __repr__(self):
        return f'<StudyPlan {self.title}>'

# 学习时长记录模型
class StudyDuration(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    duration = db.Column(db.Float, nullable=False)  # 以分钟为单位
    start_time = db.Column(db.DateTime, nullable=False)
    end_time = db.Column(db.DateTime, nullable=False)
    stop_times = db.Column(db.Integer, default=0)
    
    user = db.relationship('User', backref=db.backref('study_durations', lazy=True))
    
    def __repr__(self):
        return f'<StudyDuration {self.duration} minutes>'

# 添加到models.py，作为分享功能的依赖

# 通知模型（简化版，仅用于支持分享功能）
class Notification(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    receiver_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    content = db.Column(db.String(200), nullable=False)
    send_time = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    status = db.Column(db.Integer, default=0, nullable=False)  # 0: unread, 1: deleted 2:read
    
    sender = db.relationship('User', foreign_keys=[sender_id], backref=db.backref('sent_notifications', lazy=True))
    receiver = db.relationship('User', foreign_keys=[receiver_id], backref=db.backref('received_notifications', lazy=True))
    
    def __repr__(self):
        return f'<Notification from {self.sender_id} to {self.receiver_id}>'