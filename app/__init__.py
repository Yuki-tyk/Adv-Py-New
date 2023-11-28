"""
Set up the 1/ of the app

"""
# Extenal Import
from flask import Flask
from flask_login import LoginManager
from flask_bcrypt import Bcrypt

# Config
app = Flask(__name__)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = "login_page"
login_manager.login_message_category = "info"
app.secret_key = "b'\xe9|r\xd1+q\x8eC\xd8\n,/tlzTdV\x9c\xf3\x96\x7f\xaf\xec'"


# Set up
from app import routes