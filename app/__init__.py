from flask import Flask

from app.config import Config
from app.extensions import login_manager, db
from app.web.pages import blueprint as web_blueprint


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    login_manager.init_app(app)

    app.register_blueprint(web_blueprint)
    return app