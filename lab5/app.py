from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from models import db, User, Role
import re
import click
from flask.cli import with_appcontext
from flask.cli import AppGroup
from models import db, User, Role, VisitLog  
from functools import wraps

from reports import reports_bp

app = Flask(__name__)
app.config.from_pyfile('config.py')
application = app
app.register_blueprint(reports_bp)

app.config['SECRET_KEY'] = '/RiXnoGXTLXVyfanm2XgKA=='
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

db_cli = AppGroup('db', help='Database management commands')

login_manager = LoginManager(app)
login_manager.login_view = 'login'

# Инициализация БД
with app.app_context():
    db.create_all()

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

def check_rights(required_role):
    def decorator(func):
        @wraps(func)
        def wrapped_function(*args, **kwargs):
            if not current_user.is_authenticated:
                return redirect(url_for('login'))
            if current_user.role.name != required_role:
                flash('У вас недостаточно прав для доступа к данной странице.', 'danger')
                return redirect(url_for('index'))
            return func(*args, **kwargs)
        return wrapped_function
    return decorator


@app.route('/')
def index():
    users = User.query.options(db.joinedload(User.role)).all()
    return render_template('index.html', users=users)



@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        login = request.form['login']
        password = request.form['password']
        user = User.query.filter_by(login=login).first()
        if user and user.check_password(password):
            login_user(user)
            return redirect(url_for('index'))
        flash('Неверный логин или пароль')
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

def validate_user_data(data, is_edit=False):
    errors = {}
    
    if not is_edit:
        # Валидация логина
        login = data.get('login', '').strip()
        if not login:
            errors['login'] = 'Логин обязателен'
        elif len(login) < 5:
            errors['login'] = 'Логин должен быть не короче 5 символов'
        elif not login.isalnum():
            errors['login'] = 'Логин должен содержать только буквы и цифры'
        elif User.query.filter_by(login=login).first():
            errors['login'] = 'Этот логин уже занят'

    if not is_edit:
        # Валидация пароля
        password = data.get('password', '')
        if len(password) < 8:
            errors['password'] = 'Пароль должен быть не короче 8 символов'
        elif len(password) > 128:
            errors['password'] = 'Пароль должен быть не длиннее 128 символов'
        elif not any(c.isupper() for c in password):
            errors['password'] = 'Должна быть хотя бы одна заглавная буква'
        elif not any(c.islower() for c in password):
            errors['password'] = 'Должна быть хотя бы одна строчная буква'
        elif not any(c.isdigit() for c in password):
            errors['password'] = 'Должна быть хотя бы одна цифра'
        elif ' ' in password:
            errors['password'] = 'Пароль не должен содержать пробелов'

    # Валидация имени
    first_name = data.get('first_name', '').strip()
    if not first_name:
        errors['first_name'] = 'Имя обязательно'

    return errors

@app.route('/user/create', methods=['GET', 'POST'])
@login_required
@check_rights('Администратор')
def create_user():
    if not current_user.is_authenticated or current_user.role.name != 'Администратор':
        abort(403)

    roles = Role.query.all()
    
    if request.method == 'POST':
        form_data = request.form
        errors = validate_user_data(form_data)
        
        if errors:
            return render_template('user_form.html',
                                 roles=roles,
                                 form_data=form_data,
                                 errors=errors)

        try:
            new_user = User(
                login=form_data['login'],
                first_name=form_data['first_name'],
                last_name=form_data.get('last_name'),
                middle_name=form_data.get('middle_name'),
                role_id=form_data.get('role_id') or None
            )
            new_user.set_password(form_data['password'])
            
            db.session.add(new_user)
            db.session.commit()
            
            flash('Пользователь успешно создан', 'success')
            return redirect(url_for('index'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Ошибка: {str(e)}', 'danger')
            return render_template('user_form.html',
                                 roles=roles,
                                 form_data=form_data,
                                 errors={'database': str(e)})

    return render_template('user_form.html', roles=roles)

@app.route('/user/<int:id>')
def view_user(id):
    user = User.query.get_or_404(id)
    return render_template('view_user.html', user=user)

@app.route('/user/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit_user(id):
    user = User.query.get_or_404(id)
    if current_user.role.name != 'Администратор' and current_user.id != user.id:
        flash('У вас недостаточно прав для редактирования этого пользователя.', 'danger')
        return redirect(url_for('index'))
    
    roles = Role.query.all() if current_user.role.name == 'Администратор' else []
    
    if request.method == 'POST':
        if current_user.role.name != 'Администратор':
            # Запрет изменения роли для обычных пользователей
            request.form = request.form.copy()
            request.form['role_id'] = user.role_id
        
        # Обновление данных пользователя
        user.login = request.form.get('login', user.login)
        user.first_name = request.form.get('first_name', user.first_name)
        user.last_name = request.form.get('last_name', user.last_name)
        user.middle_name = request.form.get('middle_name', user.middle_name)
        if current_user.role.name == 'Администратор':
            user.role_id = request.form.get('role_id', user.role_id)
        
        db.session.commit()
        flash('Данные пользователя обновлены', 'success')
        return redirect(url_for('view_user', id=user.id))
    
    return render_template('user_form.html', user=user, roles=roles)

@app.route('/user/<int:id>/delete', methods=['POST'])
@login_required
@check_rights('Администратор')
def delete_user(id):
    user = User.query.get_or_404(id)
    db.session.delete(user)
    db.session.commit()
    flash('Пользователь успешно удалён', 'success')
    return redirect(url_for('index'))

def validate_password(password):
    errors = []
    special_chars = {'~','!','?','@','#','$','%','^','&','*','_','-','+',
                    '(',')','[',']','{','}','>','<','/','\\','|','"',"'",'.',',',':',';'}
    
    if len(password) < 8:
        errors.append("Минимум 8 символов")
    if len(password) > 128:
        errors.append("Максимум 128 символов")
    if not any(c.isupper() for c in password):
        errors.append("Хотя бы одна заглавная буква")
    if not any(c.islower() for c in password):
        errors.append("Хотя бы одна строчная буква")
    if not any(c.isdigit() for c in password):
        errors.append("Хотя бы одна цифра")
    if ' ' in password:
        errors.append("Без пробелов")
    if not all(c.isalpha() or c.isdigit() or c in special_chars for c in password):
        errors.append("Недопустимые символы")
    
    return ", ".join(errors) if errors else None

@app.route('/change_password', methods=['GET', 'POST'])
@login_required
def change_password():
    if request.method == 'POST':
        old_password = request.form.get('old_password')
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')
        
        errors = {}
        
        # Проверка старого пароля
        if not current_user.check_password(old_password):
            errors['old_password'] = 'Неверный текущий пароль'
        
        # Валидация нового пароля
        password_error = validate_password(new_password)
        if password_error:
            errors['new_password'] = password_error
        
        # Проверка совпадения паролей
        if new_password != confirm_password:
            errors['confirm_password'] = 'Пароли не совпадают'
        
        if errors:
            for field, message in errors.items():
                flash(message, 'danger')
            return render_template('change_password.html', 
                                 form_data=request.form,
                                 errors=errors)
        
        try:
            current_user.set_password(new_password)
            db.session.commit()
            flash('Пароль успешно изменен', 'success')
            return redirect(url_for('index'))
        
        except Exception as e:
            db.session.rollback()
            flash('Ошибка при изменении пароля', 'danger')
    
    return render_template('change_password.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        login = request.form['login']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        first_name = request.form['first_name']
        last_name = request.form.get('last_name')
        middle_name = request.form.get('middle_name')

        # Валидация данных
        errors = {}
        if not login:
            errors['login'] = 'Логин обязателен'
        elif User.query.filter_by(login=login).first():
            errors['login'] = 'Логин уже занят'
        
        if not password:
            errors['password'] = 'Пароль обязателен'
        elif password != confirm_password:
            errors['confirm_password'] = 'Пароли не совпадают'
        
        if not first_name:
            errors['first_name'] = 'Имя обязательно'
        
                # Валидация пароля
        password_errors = []
        special_chars = {'~','!','?','@','#','$','%','^','&','*','_','-','+',
                        '(',')','[',']','{','}','>','<','/','\\','|','"',"'",'.',',',':',';'}

        has_upper = False
        has_lower = False
        has_digit = False
        valid_chars = True
        has_space = False

        for char in password:
            # Проверка на пробелы
            if char.isspace():
                has_space = True
            
            # Проверка на цифры
            if char.isdigit():
                has_digit = True
            
            # Проверка регистров
            if char.isalpha():
                if char.isupper():
                    has_upper = True
                else:
                    has_lower = True
            
            # Проверка допустимых символов
            if not (char.isalpha() or char.isdigit() or char in special_chars):
                valid_chars = False

        if len(password) < 8:
            password_errors.append("Минимум 8 символов")
        if len(password) > 128:
            password_errors.append("Максимум 128 символов")
        if not has_upper:
            password_errors.append("Нужна хотя бы одна заглавная буква")
        if not has_lower:
            password_errors.append("Нужна хотя бы одна строчная буква")
        if not has_digit:
            password_errors.append("Нужна хотя бы одна цифра")
        if has_space:
            password_errors.append("Нельзя использовать пробелы")
        if not valid_chars:
            password_errors.append("Содержит недопустимые символы")

        if password_errors:
            errors['password'] = ", ".join(password_errors)

        if errors:
            for field, message in errors.items():
                flash(message, 'danger')
            return render_template('register.html', 
                                 form_data=request.form)
        
        try:
            # Создание пользователя
            new_user = User(
                login=login,
                first_name=first_name,
                last_name=last_name,
                middle_name=middle_name,
            )
            new_user.set_password(password)
            
            # Назначение роли "Пользователь" по умолчанию
            default_role = Role.query.filter_by(name='Пользователь').first()
            if default_role:
                new_user.role = default_role
            
            db.session.add(new_user)
            db.session.commit()
            
            flash('Регистрация прошла успешно! Теперь можно войти', 'success')
            return redirect(url_for('login'))
            
        except Exception as e:
            db.session.rollback()
            flash('Ошибка при регистрации', 'danger')
    
    return render_template('register.html')

@db_cli.command('init')
def init_db():
    """Инициализация базы данных"""
    with app.app_context():
        db.create_all()
        
        # Создание ролей
        if not Role.query.first():
            roles = [
                Role(name='Администратор', description='Полный доступ'),
                Role(name='Пользователь', description='Обычный пользователь')
            ]
            db.session.add_all(roles)
            db.session.commit()
            print("Созданы стандартные роли")
        
        # Создание администратора
        if not User.query.filter_by(login='admin').first():
            admin = User(
                login='admin',
                first_name='Админ',
                last_name='Системный'
            )
            admin.set_password('admin123')
            admin.role = Role.query.filter_by(name='Администратор').first()
            db.session.add(admin)
            db.session.commit()
            print("Создан администратор: admin/admin123")

app.cli.add_command(db_cli)

@app.before_request
def log_visit():
    if request.endpoint != 'static' and not request.path.startswith('/static'):
        visit = VisitLog(
            path=request.path,
            user_id=current_user.id if current_user.is_authenticated else None
        )
        db.session.add(visit)
        db.session.commit()


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)