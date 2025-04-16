import random
from functools import lru_cache
from flask import Flask, render_template
from faker import Faker
from flask import abort
from flask import request, redirect, url_for, flash
from flask import make_response, render_template, session
from flask_login import LoginManager, UserMixin, login_user, logout_user, current_user,login_required

fake = Faker()

login_manager = LoginManager()


app = Flask(__name__)
application = app

login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Для доступа необходима авторизация.'
login_manager.login_message_category = 'warning'

app.config.from_pyfile('config.py')

images_ids = ['7d4e9175-95ea-4c5f-8be5-92a6b708bb3c',
              '2d2ab7df-cdbc-48a8-a936-35bba702def5',
              '6e12f3de-d5fd-4ebb-855b-8cbc485278b7',
              'afc2cfe7-5cac-4b80-9b9a-d5c65ef0c728',
              'cab5b7f2-774e-4884-a200-0c0180fa777f']

def generate_comments(replies=True):
    comments = []
    for _ in range(random.randint(1, 3)):
        comment = { 'author': fake.name(), 'text': fake.text() }
        if replies:
            comment['replies'] = generate_comments(replies=False)
        comments.append(comment)
    return comments

def generate_post(i):
    return {
        'title': 'Заголовок поста',
        'text': fake.paragraph(nb_sentences=100),
        'author': fake.name(),
        'date': fake.date_time_between(start_date='-2y', end_date='now'),
        'image_id': f'{images_ids[i]}.jpg',
        'comments': generate_comments()
    }
def validate_phone(phone):
    allowed_symbols = {' ', '(', ')', '-', '.','+'}
    digits = []
    
    for char in phone:
        if char.isdigit():
            digits.append(char)
        elif char in allowed_symbols:
            continue  
        else:
            return "Недопустимый ввод. В номере телефона встречаются недопустимые символы."
    
    if len(digits) != 11 and len(digits) != 10:
        return f"Недопустимый ввод. Неверное количество цифр. Найдено {len(digits)}."
    
    return None

def fix_phone_format(phone):
    clear_phone=[]
    x=0
    for i in phone:
        if i.isdigit():
            clear_phone.append(i)
    phone_format="8-XXX-XXX-XX-XX"
    if len(clear_phone)==11:
        x=1
    else:
        x=0
    for i in range(x,len(clear_phone)):
        phone_format=phone_format.replace('X',clear_phone[i],1)
    return phone_format
        
@lru_cache
def posts_list():
    return sorted([generate_post(i) for i in range(5)], key=lambda p: p['date'], reverse=True)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/posts')
def posts():
    return render_template('posts.html', title='Посты', posts=posts_list())

@app.route('/posts/<int:index>')
def post(index):
    posts = posts_list()
    if index < 0 or index >= len(posts):
        abort(404)
    p = posts[index]
    return render_template('post.html', title=p['title'], post=p, avatar='avatar.svg')

@app.route('/about')
def about():
    return render_template('about.html', title='Об авторе')

@app.route('/phone_valid', methods=['GET','POST'])
def phone_valid():
    error = None
    fix_phone = None
    if request.method == 'POST':
        phone = request.form.get('phone')
        error=validate_phone(phone)
        fix_phone=fix_phone_format(phone)
    return render_template('phone_valid.html', title='Телефон', error=error,fix_phone=fix_phone)

@app.route('/args')
def args():
    return render_template('args.html', title='Параметры Url')

@app.route('/headers')
def headers():
    return render_template('headers.html', title='Заголовки')

@app.route('/cookies')
def cookies():
    if request.cookies.get("Cats"):
        # удаляем куку
        response = make_response(render_template('cookies.html', title='Печенье'))
        response.set_cookie("Cats", "", expires=0)
    else:
        # устанавливаем куку
        response = make_response(render_template('cookies.html', title='Печенье'))
        response.set_cookie("Cats", "meow")
    return response


@app.route('/form', methods=['GET','POST'])
def form():
    return render_template('form.html', title='Форма')

@app.route('/counter')
def counter():
    if session.get('counter'):
        session['counter']+=1
    else:
        session['counter']=1
    return render_template('counter.html')

def get_users():
    return[
        {
            'id': '1',
            'login': 'user',
            'password': 'qwerty'
        }
    ]

class User(UserMixin):
    def __init__(self, user_id, login):
        self.id = user_id
        self.login =login

@login_manager.user_loader
def load_user(user_id):
    for user in get_users():
        if user_id == user['id']:
            return User(user['id'], user['login'])
    return None

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method== 'POST':
        login = request.form.get('username')
        password = request.form.get('password')
        remember_me = request.form.get('remember_me') == 'on'
        if login and password:
            for user in get_users():
                if user['login'] == login and user['password'] == password:
                    user = User(user['id'], user['login'])
                    login_user(user, remember=remember_me)
                    flash('Вы успешно аутентифицированы', 'success')
                    return redirect(url_for('index'))
            return render_template('auth.html', error='Пользователь не найден, проверьте корректность введённых данных.')
    return render_template('auth.html')

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/secret')
@login_required
def secret():
    return render_template('secret.html')

if __name__== '_main_':
    app.run()

