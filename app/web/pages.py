from pathlib import Path
from flask import Blueprint, redirect, render_template, request, abort
from flask_login import login_user, logout_user, login_required
from app.forms import LoginForm, RegisterForm, RepositoryForm
from app.services import UserService, RepositoryService
from app.utils import get_current_user
from app import Config
import git


blueprint = Blueprint('web', __name__)


@blueprint.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    user_service = UserService()
    if form.validate_on_submit():
        user = user_service.authenticate(email=form.email.data, password=form.password.data)
        if user:
            login_user(user, remember=form.remember_me.data)
            return redirect(f"/{user.username}")
        return render_template('login.html',
                               message="Неправильный логин или пароль",
                               form=form)
    return render_template('login.html', title='Авторизация', form=form)


@blueprint.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    user_service = UserService()
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template('register.html',
                                   title="Регистрация",
                                   form=form,
                                   message="Пароли не совпадают")
        try:
            user = user_service.create_user(email=form.email.data,
                                        username=form.username.data,
                                        password=form.password.data)
        except ValueError as e:
            return render_template('register.html',
                                   title="Регистрация",
                                   form=form,
                                   message=str(e)
                                   )
        return redirect("/")
    return render_template('register.html', title='Регистрация', form=form)


@blueprint.route('/logout')
def logout():
    logout_user()
    return redirect("/get_started")


@blueprint.route('/')
def index():
    return render_template('index.html')

@blueprint.route('/get_started', methods=['GET'])
def get_started():
    return render_template('get_started.html')


@blueprint.route('/<username>')
def user_repos(username):
    user_service = UserService()
    user = user_service.get_user_by_name(username)
    return render_template("user_repos.html", user=user)


@blueprint.route('/new', methods=['GET', 'POST'])
@login_required
def create_repository():
    form = RepositoryForm()
    repo_service = RepositoryService()
    user = get_current_user()
    if form.validate_on_submit():
        try:
            private = False if form.visibility.data == 'public' else True
            repo = repo_service.create_repository(
                owner_id=user.id,
                repo_name=form.name.data,
                private=private
            )
            return redirect(f"/{user.username}")
        except Exception as e:
            return render_template('repository_form.html',
                                   form=form,
                                   message=str(e)
                                   )
    return render_template('repository_form.html', form=form)


@blueprint.route('/<username>/<repo_name>')
@blueprint.route('/<username>/<repo_name>/tree/')
@blueprint.route('/<username>/<repo_name>/tree/<path:filepath>')
def repo_tree(username, repo_name, filepath=''):
    ref = request.args.get('ref', 'HEAD')  # Ветка или коммит
    repo_path = Path(Config.REPOS_BASE_DIR, username, f"{repo_name}.git")

    if not repo_path.exists():
        abort(404, description=f"Репозиторий {repo_name} не найден")

    try:
        git_repo = git.Repo(repo_path)
        try:
            commit = git_repo.commit(ref)
        except (git.BadName, git.BadObject):
            abort(404, description=f"Ветка или коммит {ref} не найден")

        current_tree = commit.tree
        if filepath:
            try:
                for part in filepath.split('/'):
                    if part:
                        current_tree = current_tree / part
            except KeyError:
                abort(404, description=f"Путь {filepath} не найден")

        try:
            tree_items = []
            for item in current_tree:
                tree_items.append({
                    "name": item.name,
                    "type": "tree" if item.type == "tree" else "blob",
                    "size": item.size if item.type == "blob" else None,
                    "path": f"{filepath}/{item.name}".lstrip('/') if filepath else item.name
                })
            return render_template('repo_tree.html',
                                   username=username,
                                   repo_name=repo_name,
                                   current_path=filepath,
                                   ref=ref,
                                   items=tree_items,
                                   is_file=False)

        except (TypeError, IndexError, KeyError):
            blob = current_tree
            if blob.type != "blob":
                abort(404, description="Не файл и не папка")

            file_ext = blob.name.split('.')[-1].lower() if '.' in blob.name else ''

            content = ""
            is_binary = False
            try:
                content = blob.data_stream.read().decode('utf-8')
            except (UnicodeDecodeError, UnicodeError):
                is_binary = True
                content = "Бинарный файл (не может быть отображен)"

            return render_template('repo_tree.html',
                                   username=username,
                                   repo_name=repo_name,
                                   current_path=filepath,
                                   ref=ref,
                                   filename=blob.name,
                                   content=content,
                                   is_binary=is_binary,
                                   file_ext=file_ext,
                                   is_file=True)
    except Exception as e:
        abort(500, description=f"Ошибка при чтении репозитория: {str(e)}")


@blueprint.route('/<username>/<repo_name>/branches')
def repo_branches(username, repo_name):
    repo_path = Path(Config.REPOS_BASE_DIR, username, f"{repo_name}.git")
    if not repo_path.exists():
        abort(404)
    try:
        git_repo = git.Repo(repo_path)
        branches = []
        for branch in git_repo.branches:
            branches.append({
                "name": branch.name,
                "commit": branch.commit.hexsha[:8],
                "message": branch.commit.message.split('\n')[0],
                "date": branch.commit.committed_datetime
            })

        return render_template('repo_branches.html',
                               username=username,
                               repo_name=repo_name,
                               branches=branches,
                               current_ref=git_repo.active_branch.name if git_repo.active_branch else 'master')

    except Exception as e:
        abort(500, description=str(e))
