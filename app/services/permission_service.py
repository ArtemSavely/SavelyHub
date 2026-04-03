from app.repository import PermissionRepository


class PermissionService:
    def __init__(self, permission_repo: PermissionRepository=None):
        self.permission_repo = permission_repo if permission_repo else PermissionRepository()

    def check_permission(self, user_id, repo_id, role):
        permission = self.permission_repo.get_by_user_and_repository(user_id, repo_id)
        if permission.role == role:
            return True
        return False

