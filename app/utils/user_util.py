from app.extensions import db
from app.models import User
from flask_login import current_user


def get_current_user():
    try:
        user = db.session.query(User).filter(User.email == current_user.email).first()
    except Exception:
        return "пользователь не авторизован"
    return user