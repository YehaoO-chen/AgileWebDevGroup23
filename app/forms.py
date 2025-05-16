# app/forms.py

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, SelectField, FileField, TextAreaField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError, Optional
from app.models import User

class LoginForm(FlaskForm):
    """User login form with CSRF protection."""
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Log In')

class RegistrationForm(FlaskForm):
    """User registration form with CSRF protection."""
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=150)])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirm Password', 
                                     validators=[DataRequired(), EqualTo('password')])
    security_question = SelectField('Security Question', choices=[
        ('pet', 'What was your first pet\'s name?'),
        ('school', 'What was the name of your first school?'),
        ('city', 'What city were you born in?'),
        ('mother', 'What is your mother\'s maiden name?')
    ])
    security_answer = PasswordField('Security Answer', validators=[DataRequired()])
    fullname = StringField('Full Name', validators=[Optional(), Length(max=150)])
    major = StringField('Major', validators=[Optional(), Length(max=50)])
    email = StringField('Email', validators=[Optional(), Email(), Length(max=150)])
    phone = StringField('Phone Number', validators=[Optional(), Length(max=20)])
    address = StringField('Address', validators=[Optional(), Length(max=200)])
    student_id = StringField('Student ID', validators=[Optional(), Length(max=20)])
    submit = SubmitField('Register')
    
    # Custom validators to check if username, email, phone or student_id already exists
    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('That username is already taken. Please choose a different one.')
    
    def validate_email(self, email):
        if email.data:
            user = User.query.filter_by(email=email.data).first()
            if user:
                raise ValidationError('That email is already registered. Please use a different one.')
    
    def validate_phone(self, phone):
        if phone.data:
            user = User.query.filter_by(phone=phone.data).first()
            if user:
                raise ValidationError('That phone number is already registered. Please use a different one.')
    
    def validate_student_id(self, student_id):
        if student_id.data:
            user = User.query.filter_by(student_id=student_id.data).first()
            if user:
                raise ValidationError('That student ID is already registered. Please use a different one.')

class PasswordResetForm(FlaskForm):
    """Form for users to reset their password using security question."""
    username = StringField('Username', validators=[DataRequired()])
    security_answer = PasswordField('Security Answer', validators=[DataRequired()])
    password = PasswordField('New Password', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirm New Password', 
                                    validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Reset Password')