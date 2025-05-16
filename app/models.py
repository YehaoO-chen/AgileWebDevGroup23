from flask_login import UserMixin
from datetime import datetime, timezone
from app.extensions import db, login_manager
from werkzeug.security import generate_password_hash, check_password_hash

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False,index=True)
    _password = db.Column('password', db.String(128), nullable=False)
    _security_answer = db.Column('security_answer', db.String(128), nullable=False)
    create_time = db.Column(db.DateTime, default=datetime.now(timezone.utc))
    fullname = db.Column(db.String(150), nullable=True)
    major = db.Column(db.String(50), nullable=True)
    email = db.Column(db.String(150), unique=True, nullable=True)
    phone = db.Column(db.String(20), unique=True, nullable=True)
    address = db.Column(db.String(200), nullable=True)
    student_id = db.Column(db.String(20), unique=True, nullable=True)
    avatar = db.Column(db.String(200), nullable=True, default='')
    
    @property
    def password(self):
        """Prevent direct access to the password."""
        raise AttributeError("Password is not readable.")

    @password.setter
    def password(self, plaintext_password):
        """Hash the password and store it."""
        self._password = generate_password_hash(plaintext_password)

    def check_password(self, plaintext_password):
        """Verify the password."""
        return check_password_hash(self._password, plaintext_password)

    @property
    def security_answer(self):
        """Prevent direct access to the security answer."""
        raise AttributeError("Security answer is not readable.")

    @security_answer.setter
    def security_answer(self, plaintext_answer):
        """Hash the security answer and store it."""
        self._security_answer = generate_password_hash(plaintext_answer)

    def check_security_answer(self, plaintext_answer):
        """Verify the security answer."""
        return check_password_hash(self._security_answer, plaintext_answer)

    def __repr__(self):
        return f'<User {self.username}>'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# StudyPlan model
class StudyPlan(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    content = db.Column(db.String(200), nullable=False)
    create_time = db.Column(db.DateTime, default=datetime.now(timezone.utc), nullable=False)
    complete_time = db.Column(db.DateTime, nullable=True)
    status = db.Column(db.Integer, default=0, nullable=False)  # 0: open, 1: completed, 2: deleted
    
    user = db.relationship('User', backref=db.backref('study_plans', lazy=True))
    
    def __repr__(self):
        return f'<StudyPlan {self.content}>'

# StudyDuration model
class StudyDuration(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    duration = db.Column(db.Float, nullable=False)
    start_time = db.Column(db.DateTime, nullable=False)
    end_time = db.Column(db.DateTime, nullable=True)
    stop_times = db.Column(db.Integer, default=0)
    
    user = db.relationship('User', backref=db.backref('study_durations', lazy=True))
    
    def __repr__(self):
        return f'<StudyDuration {self.duration} minutes>'

# Notification model
class Notification(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    receiver_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    content = db.Column(db.String(200), nullable=False)
    send_time = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    status = db.Column(db.Integer, default=0, nullable=False)  # 0: unread, 1:read  2:deleted
    
    sender = db.relationship('User', foreign_keys=[sender_id], backref=db.backref('sent_notifications', lazy=True))
    receiver = db.relationship('User', foreign_keys=[receiver_id], backref=db.backref('received_notifications', lazy=True))
    
    def __repr__(self):
        return f'<Notification from {self.sender_id} to {self.receiver_id}>'