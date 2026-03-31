from app.extensions import db
from app.models import Permission


class PermissionRepository:
    def get_by_user_and_repository(self, user_id, repository_id):
        return (db.session.query(Permission).
                filter(Permission.user_id == user_id,
                        Permission.repository_id == repository_id).first())

    def save(self, permission):
        db.session.add(permission)
        db.session.flush()

    def delete(self, permission):
        db.session.delete(permission)
