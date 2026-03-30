from app import db


class Permission(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    repository_id = db.Column(db.Integer, db.ForeignKey('repository.id'), nullable=False)
    role = db.Column(db.String(20), nullable=False)

    user = db.relationship("User", back_populates="permissions")
    repository = db.relationship("Repository", back_populates="permissions")
