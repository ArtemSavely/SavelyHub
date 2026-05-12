from app.extensions import db
from app.models import Repository


class RepositoryRepository:
    def get_by_id(self, repo_id):
        return db.session.query(Repository).filter(Repository.id == repo_id).first()

    def get_by_name(self, name):
        return db.session.query(Repository).filter(Repository.name == name).first()

    def get_all_for_user_id(self, user_id):
        return db.session.query(Repository).filter(Repository.owner_id == user_id).all()

    def search_public_repos(self, q):
        return db.session.query(Repository).filter(Repository.private == False,
                                                   Repository.name.like(q)).all()

    def search_private_repos(self, q, user_id):
        return db.session.query(Repository).filter(Repository.private == True,
                                                   Repository.name.like(q),
                                                   Repository.owner_id == user_id).all()

    def save(self, repository):
        db.session.add(repository)
        db.session.flush()

    def delete(self, repository):
        db.session.delete(repository)
        db.session.commit()

    def commit(self):
        db.session.commit()