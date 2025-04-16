from flask_login import UserMixin
from app import login_manager

# Create a simple User class
class User(UserMixin):
    def __init__(self, id, username, password):
        self.id = id
        self.username = username
        self.password = password

# Create a simple in-memory user database
users = {
    '1': User('1', 'aaa', 'aaaaaaaa'),
    '2': User('2', 'b', 'b')
}

@login_manager.user_loader
def load_user(user_id):
    return users.get(user_id)
