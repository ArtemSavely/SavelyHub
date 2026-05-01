from enum import Enum
from flask import make_response, Blueprint, request, Response
from app.utils import get_current_user
from app.services import PermissionService, UserService, user_service
from .git_service import GitService


class Service(Enum):
    receive = 'git-receive-pack'
    upload = 'git-upload-pack'


def authenticate():
    """Отправляет 401 с заголовком WWW-Authenticate"""
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

    service_type = request.args.get("service")
    if not service_type in ['git-receive-pack', 'git-upload-pack']:
        return make_response("Неверный сервис", 400)

    git_service = GitService()
    data = git_service.inforefs(owner, repo , service_type)
    return make_response(data)

@blueprint.route('/<owner>/<repo>/<service>', methods=['POST'])
def upload(owner, repo, service):
    auth = request.authorization
    if not auth:
        return authenticate()
    data = request.get_data()
    print(data)
    result = GitService.service(owner, repo, service, data)
    return make_response(result)
