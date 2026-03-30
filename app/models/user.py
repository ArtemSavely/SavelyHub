from app import db


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True, nullable=False)
    email = db.Column(db.String(64), index=True, unique=True, nullable=False)
    hashed_password = db.Column(db.String(64), nullable=False)

    repositories = db.relationship('Repository', back_populates="owner")
    permissions = db.relationship("Permission", back_populates="user")
