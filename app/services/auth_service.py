from app.data import db_session
from app.data.models.users import User


def authenticate(email, password):
    db_sess = db_session.create_session()
    user = db_sess.query(User).filter(User.email == email).first()
    if user and user.check_password(password):
        return user
    return None