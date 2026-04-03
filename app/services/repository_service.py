from app.models import Repository
from app.repository import RepositoryRepository


class RepositoryService:
    def __init__(self, repo_repo: RepositoryRepository=None):
        self.repo_repo = repo_repo if repo_repo else RepositoryRepository()

    def create_repository(self):
        pass

    def get_by_reponame(self, reponame):
        return self.repo_repo.get_by_name(reponame)