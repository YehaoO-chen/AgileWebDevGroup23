from flask_login import UserMixin
from datetime import datetime, timezone
from app.extensions import db, login_manager
from werkzeug.security import generate_password_hash, check_password_hash

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    security_answer = db.Column(db.String(255), nullable=False)
    create_time = db.Column(db.DateTime, default=datetime.utcnow)

    def set_password(self, password):
        # hash the password and store it
        self.password = generate_password_hash(password)

    def check_password(self, password):
        # check the hashed password against the provided password
        return check_password_hash(self.password, password)

    def set_security_answer(self, answer):
        # hash the security answer and store it
        self.security_answer = generate_password_hash(answer)

    def check_security_answer(self, answer):
        # check the hashed security answer against the provided answer
        return check_password_hash(self.security_answer, answer)

    def __repr__(self):
        return f'<User id={self.id}, username={self.username}>'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# studyplan model
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

# study duration model
class StudyDuration(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    duration = db.Column(db.Float, nullable=False)
    start_time = db.Column(db.DateTime, nullable=False)
    end_time = db.Column(db.DateTime, nullable=False)
    stop_times = db.Column(db.Integer, default=0)
    
    user = db.relationship('User', backref=db.backref('study_durations', lazy=True))
    
    def __repr__(self):
        return f'<StudyDuration {self.duration} minutes>'

# notification model
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