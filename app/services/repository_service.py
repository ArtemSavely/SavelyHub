from app.git.git_service import GitService
from app.models import Repository
from app.repository import RepositoryRepository, UserRepository


class RepositoryService:
    def __init__(self, repo_repo: RepositoryRepository=None):
        self.repo_repo = repo_repo if repo_repo else RepositoryRepository()

    def create_repository(self, owner_id, repo_name, private=False):
        existing = self.repo_repo.get_by_name(repo_name)

        if existing:
            return ValueError('Репозиторий с названием {} уже существует'.format(repo_name))

        repository = Repository(
            owner_id = owner_id,
            name = repo_name,
            private = private
        )

        self.repo_repo.save(repository)
        self.repo_repo.commit()

        owner = UserRepository().get_by_id(owner_id)

        git_service = GitService()
        git_service.create_bare_repo(owner=owner.name, repo_name=repo_name)

        return repository

    def get_by_reponame(self, reponame):
        return self.repo_repo.get_by_name(reponame)

    def get_repos_list_for_user(self, user):
        return self.repo_repo.get_all_for_user_id(user.id)