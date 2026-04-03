from app.extensions import db
from app.models import User
from flask_login import current_user


def get_current_user():
    current_user_email = current_user.email
    user = db.session.query(User).filter(User.email == current_user_email).first()
    return user