from flask import current_app
from flask_login import login_manager, UserMixin


class User(UserMixin):
    def __init__(self):
        super()
        self.id = 'nsf'

    @staticmethod
    def check_password(password):
        pswd = current_app.config['SHARED_PSWD']
        return pswd == password

