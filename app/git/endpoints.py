from enum import Enum
from pathlib import Path

from flask import make_response, Blueprint, request, Response
from app.services import PermissionService, UserService, user_service
from .git_service import GitService
from .. import Config


class Service(Enum):
    receive = 'git-receive-pack'
    upload = 'git-upload-pack'


def authenticate():
    return Response(
        'Unauthorized',
        401,
        {'WWW-Authenticate': 'Basic realm="Git Server"'}
    )


blueprint = Blueprint("git", __name__)


@blueprint.route('/<owner>/<repo>/info/refs', methods=['GET'])
def info_refs(owner, repo):
    auth = request.authorization
    if not auth:
        return authenticate()
    user_service = UserService()
    permission_service = PermissionService()
    user = user_service.get_user_by_email(auth.username)

    if not repo or not permission_service.check_permission(user.id, repo, "write"):
        return make_response("Доступ к репозиторию запрещен", 403)

    service = request.args.get("service")
    if not service in ['git-receive-pack', 'git-upload-pack']:
        return make_response("Неверный сервис", 400)

    path = Path(Config.REPOS_BASE_DIR, owner, repo)
    repo = GitService(path) if path.exists() else GitService.init(path)
    data = repo.inforefs(service)
    media = f'application/x-{service}-advertisement'
    return Response(data, mimetype=media)

@blueprint.route('/<owner>/<repo>/<service>', methods=['POST'])
def upload(owner, repo, service):
    auth = request.authorization
    if not auth:
        return authenticate()
    auth = request.authorization
    if not auth:
        return authenticate()

    path = Path(Config.REPOS_BASE_DIR, owner, repo)
    repo = GitService(path)
    data = request.get_data()
    data = repo.service(service, data)

    media = f'application/x-{service}-result'
    return Response(data, mimetype=media)
