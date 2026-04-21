from flask_wtf import FlaskForm
from wtforms import SubmitField, StringField, SelectField, TextAreaField
from wtforms.validators import DataRequired


class RepositoryForm(FlaskForm):
    name = StringField('Имя репозитория', validators=[DataRequired()])
    about = TextAreaField('Описание')
    visibility = SelectField('Видимость репозитория',
                             choices=[('public', 'Публичный'), ('private', 'Приватный')])
    submit = SubmitField('Создать')