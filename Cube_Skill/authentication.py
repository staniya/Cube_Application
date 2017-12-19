from __builtin__ import unicode
from flask import Flask, request, abort, redirect, Response, url_for
from flask_login import LoginManager, login_required, UserMixin, login_user

import sys
import requests

from Cube_Skill.Cube_Application import launch_cube
from Cube_Skill.ask import alexa
from Cube_Skill.lambda_function import get_cube_launch_intent_handler, get_cube_otp_intent_handler

app = Flask(__name__)

# config
app.config.update(
    DEBUG=True,
    SECRET_KEY=None
)

# flask-login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

@login_manager.user_loader
def load_user(userid):
    return #userid

class User(UserMixin):

    def phoneNumber(self, request):
        resp2, response, phoneNumber = get_cube_launch_intent_handler(request)
        return phoneNumber

    def OTP(self, request):
        resp3, OTP = get_cube_otp_intent_handler(request)
        return OTP

    def __init__(self, phoneNumber, OTP):
        self.phoneNumber = phoneNumber
        self.OTP = OTP

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return unicode(self.phoneNumber)

    def __repr__(self):
        return self.phoneNumber, self.OTP

@app.route('/login', methods=['GET', 'POST'])

def login():
    if request.method == 'POST':


    def __init__(self):




# somewhere to logout
@app.route("/logout")
@login_required
def logout():
    logout_user()
    return Response('<p>Logged out</p>')


# handle login failed
@app.errorhandler(401)
def page_not_found(e):
    return Response('<p>Login failed</p>')


if __name__ == "__main__":
    app.run()

