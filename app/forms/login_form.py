from flask_wtf import FlaskForm
from wtforms import PasswordField, BooleanField, SubmitField, EmailField
from wtforms.fields.simple import StringField
from wtforms.validators import DataRequired


class LoginForm(FlaskForm):
    email = EmailField('Почта', validators=[DataRequired()])
    username = StringField("Имя пользователя", validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    remember_me = BooleanField('Запомнить меня')
    submit = SubmitField('Войти')