from flask import Flask, Blueprint
from flask_login import LoginManager

from app.config import Config


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    

    return app