from app.models import User
from werkzeug.security import generate_password_hash, check_password_hash
from app.repository import UserRepository


class UserService:
    def __init__(self, user_repo: UserRepository=None):
        self.user_repo = user_repo if user_repo else UserRepository()

    def create_user(self, email, password, username):
        if self.user_repo.get_by_email(email):
            raise ValueError("Пользователь с этой почтой уже существует")
        if self.user_repo.get_by_username(username):
            raise ValueError("Пользователь с таким именем уже существует")
        user = User(email=email,
                    username=username,
                    password=generate_password_hash(password))
        user = self.user_repo.save(user)
        self.user_repo.commit()
        return user

    def authenticate(self, email, password):
        user = self.user_repo.get_by_email(email)
        if user and check_password_hash(user.hashed_password, password):
            return user
        return None
