from app.models import Permission
from app.repository import PermissionRepository
from app.repository import RepositoryRepository


class PermissionService:
    def __init__(self, permission_repo: PermissionRepository=None):
        self.permission_repo = permission_repo if permission_repo else PermissionRepository()

    def create_permission(self, user_id, repo_id, role):
        existing = self.permission_repo.get_by_user_and_repository(user_id, repo_id)
        if existing:
            existing.role = role
            self.permission_repo.save(existing)
        else:
            permission = Permission(
            user_id=user_id,
            repository_id=repo_id,
            role=role)
            self.permission_repo.save(permission)
        self.permission_repo.commit()
        return self.permission_repo.get_by_user_and_repository(user_id, repo_id)

    def check_permission(self, user_id, repo, role):
        repo_repo = RepositoryRepository()
        repo_name = repo[:-4]
        repo = repo_repo.get_by_name(repo_name)
        if not repo.private and role == 'read':
            return True
        try:
            permission = self.permission_repo.get_by_user_and_repository(user_id, repo.id)
            if permission.role == role:
                return True
        except AttributeError:
            return "Вы не авторизованы для проверки прав"
        return False

