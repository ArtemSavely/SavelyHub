from flask import Blueprint, redirect, render_template
from flask_login import login_user, logout_user, login_required
from app.forms import LoginForm, RegisterForm, RepositoryForm
from app.services import UserService, RepositoryService
from app.utils import get_current_user


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
    #print(username)
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
            print(user.username)
            private = False if form.visibility.data == 'public' else True
            repo = repo_service.create_repository(
                owner_id=user.id,
                repo_name=form.name.data,
                private=private
            )
        except Exception as e:
            return render_template('repository_form.html',
                                   form=form,
                                   message=str(e)
                                   )
    return render_template('user_repos.html', user=user)
