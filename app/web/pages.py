from pathlib import Path
from flask import Blueprint, redirect, render_template, request, abort, url_for
from flask_login import login_user, logout_user, login_required, current_user
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
    return redirect("/")


@blueprint.route('/')
def index():
    return render_template('index.html')


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
        except (git.BadName, git.BadObject) as e:
            if 'did not resolve to an object' in str(e):
                return render_template('repo_empty.html',
                                       username=username,
                                       repo_name=repo_name,
                                       is_empty=True)
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
            sidebar_items = []

            def get_last_commit(path):
                """Получает последний коммит для указанного пути"""
                try:
                    # git log -1 --format="%H|%ci|%s" -- path
                    log_output = git_repo.git.log('-1', '--format=%H|%ci|%s', '--', path)
                    if log_output:
                        parts = log_output.strip().split('|')
                        return {
                            'hash': parts[0][:8],
                            'date': parts[1] if len(parts) > 1 else '',
                            'message': parts[2][:50] + '...' if len(parts) > 2 and len(parts[2]) > 50 else (
                                parts[2] if len(parts) > 2 else '')
                        }
                except:
                    pass
                return None

            def walk_tree(tree, prefix='', depth=0):
                for item in sorted(tree, key=lambda x: (x.type != 'tree', x.name.lower())):
                    item_path = f"{prefix}/{item.name}" if prefix else item.name
                    sidebar_items.append({
                        'name': item.name,
                        'path': item_path,
                        'type': item.type,
                        'depth': depth
                    })
                    if item.type == 'tree':
                        walk_tree(item, item_path, depth + 1)

            walk_tree(commit.tree)
            tree_items = []
            for item in current_tree:
                item_path = f"{filepath}/{item.name}".lstrip('/') if filepath else item.name
                last_commit = get_last_commit(item_path)
                tree_items.append({
                    "name": item.name,
                    "type": "tree" if item.type == "tree" else "blob",
                    "size": item.size if item.type == "blob" else None,
                    "path": f"{filepath}/{item.name}".lstrip('/') if filepath else item.name,
                    "last_commit": last_commit
                })
            return render_template('repo_tree.html',
                                   username=username,
                                   repo_name=repo_name,
                                   current_path=filepath,
                                   ref=ref,
                                   items=tree_items,
                                   sidebar_items=sidebar_items,
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

            sidebar_items = []

            def walk_tree(tree, prefix='', depth=0):
                for item in sorted(tree, key=lambda x: (x.type != 'tree', x.name.lower())):
                    item_path = f"{prefix}/{item.name}" if prefix else item.name
                    sidebar_items.append({
                        'name': item.name,
                        'path': item_path,
                        'type': item.type,
                        'depth': depth
                    })
                    if item.type == 'tree':
                        walk_tree(item, item_path, depth + 1)

            walk_tree(commit.tree)

            return render_template('repo_tree.html',
                                   username=username,
                                   repo_name=repo_name,
                                   current_path=filepath,
                                   sidebar_items=sidebar_items,
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


@blueprint.route('/search')
def search_repos():
    query = request.args.get('q', '').strip()
    if not query:
        return redirect(url_for('web.index'))
    repo_service = RepositoryService()
    public_repos = repo_service.search_public_repos(query)
    if current_user.is_authenticated:
        private_repos = repo_service.search_private_repos(query, current_user.id)
    else:
        private_repos = []
    repos = private_repos + public_repos
    repos.sort(key=lambda repo: repo.name)

    return render_template('search_results.html', query=query, repos=repos)
