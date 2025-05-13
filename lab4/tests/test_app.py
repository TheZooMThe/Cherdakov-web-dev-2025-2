import sys
import os
import pytest
from werkzeug.security import check_password_hash

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app, db
from models import User, Role

@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['WTF_CSRF_ENABLED'] = False

    with app.test_client() as client:
        with app.app_context():
            # Очищаем базу перед каждым тестом
            db.drop_all()
            db.create_all()
            
            # Создаем роли только если они не существуют
            admin_role = Role.query.filter_by(name='Администратор').first()
            if not admin_role:
                admin_role = Role(name='Администратор', description='Полный доступ')
                db.session.add(admin_role)
            
            user_role = Role.query.filter_by(name='Пользователь').first()
            if not user_role:
                user_role = Role(name='Пользователь', description='Обычный пользователь')
                db.session.add(user_role)
            
            # Создаем администратора
            admin = User.query.filter_by(login='admin').first()
            if not admin:
                admin = User(
                    login='admin',
                    first_name='Admin',
                    role=admin_role
                )
                admin.set_password('admin123')
                db.session.add(admin)
            
            db.session.commit()
        
        yield client
        
        # Очищаем сессию после теста
        with app.app_context():
            db.session.remove()

def test_login_failure(client):
    response = client.post('/login', data={
        'login': 'admin',
        'password': 'wrong'
    }, follow_redirects=True)
    assert 'Неверный логин или пароль'.encode('utf-8') in response.data

def test_create_user_validation(client):
    # Логинимся как админ
    client.post('/login', data={
        'login': 'admin',
        'password': 'admin123'
    }, follow_redirects=True)
    
    response = client.post('/user/create', data={
        'login': 'adm',
        'password': 'invalid',
        'first_name': ''
    }, follow_redirects=True)
    
    assert 'Логин должен быть не короче 5 символов'.encode('utf-8') in response.data
    assert 'Пароль должен быть не короче 8 символов'.encode('utf-8') in response.data
    assert 'Имя обязательно'.encode('utf-8') in response.data

def test_change_password(client):
    # Логинимся как админ
    client.post('/login', data={
        'login': 'admin',
        'password': 'admin123'
    }, follow_redirects=True)
    
    response = client.post('/change_password', data={
        'old_password': 'admin123',
        'new_password': 'NewPass123!',
        'confirm_password': 'NewPass123!'
    }, follow_redirects=True)
    
    assert 'Пароль успешно изменен'.encode('utf-8') in response.data
    user = User.query.filter_by(login='admin').first()
    assert check_password_hash(user.password_hash, 'NewPass123!') is True