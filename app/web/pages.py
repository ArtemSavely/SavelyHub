from flask import Blueprint, redirect, render_template
from flask_login import login_user


from ..forms.login_form import LoginForm


blueprint = Blueprint('web', __name__)


@blueprint.route('/login', methods=['GET', 'POST'])
def login():
    pass
    # form = LoginForm()
    # if form.validate_on_submit():
    #     user = authenticate(email=form.email.data, password=form.password.data)
    #     if user:
    #         login_user(user, remember=form.remember_me.data)
    #         return redirect("/")
    #     return render_template('login.html',
    #                            message="Неправильный логин или пароль",
    #                            form=form)
    # return render_template('login.html', title='Авторизация', form=form)