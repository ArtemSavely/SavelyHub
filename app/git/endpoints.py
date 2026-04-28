from enum import Enum
from flask import make_response, Blueprint, request
from app.utils import get_current_user
from app.services import PermissionService
from .git_service import GitService


class Service(Enum):
    receive = 'git-receive-pack'
    upload = 'git-upload-pack'


blueprint = Blueprint("git", __name__)


@blueprint.route('/<owner>/<repo>/info/refs', methods=['GET'])
def info_refs(owner, repo):
    user = get_current_user()
    permission_service = PermissionService()

    # if not repo or not permission_service.check_permission(user, repo, "read"):
    #     return make_response("Доступ к репозиторию запрещен", 403)

    service_type = request.args.get("service")
    if service_type in [Service.upload, Service.receive]:
        return make_response("Неверный сервис", 400)

    git_service = GitService()
    data = git_service.inforefs(owner, repo , service_type)
    return make_response(data)

@blueprint.route('/<owner>/<repo>/<service>', methods=['POST'])
def upload(owner, repo, service):
    data = request.get_data()
    print(data)
    result = GitService.service(owner, repo, service, data)
    return make_response(result)
