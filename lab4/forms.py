from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SelectField
from wtforms.validators import DataRequired, Length, ValidationError

class UserForm(FlaskForm):
    login = StringField('Логин', validators=[
        DataRequired(message="Обязательное поле"),
        Length(min=5, max=50)
    ])
    
    password = PasswordField('Пароль', validators=[
        DataRequired(message="Обязательное поле")
    ])
    
    last_name = StringField('Фамилия')
    first_name = StringField('Имя', validators=[
        DataRequired(message="Обязательное поле")
    ])
    middle_name = StringField('Отчество')
    
    role_id = SelectField('Роль', coerce=int)