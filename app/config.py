import secrets


class Config:
    SECRET_KEY = secrets.token_urlsafe(32)