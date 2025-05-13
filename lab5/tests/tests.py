import pytest

import sys
import os
import pytest
from werkzeug.security import check_password_hash

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app, db
from models import User, Role, VisitLog
from flask import url_for

@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['WTF_CSRF_ENABLED'] = False

    with app.test_client() as client:
        with app.app_context():
            db.drop_all()
            db.create_all()

            if not Role.query.first():
                admin_role = Role(name='Администратор')
                user_role = Role(name='Пользователь')
                db.session.add_all([admin_role, user_role])
                db.session.commit()

            admin = User(
                login='admin',
                first_name='Admin',
                role=Role.query.filter_by(name='Администратор').first()
            )
            admin.set_password('admin123')
            
            regular_user = User(
                login='user',
                first_name='User',
                role=Role.query.filter_by(name='Пользователь').first()
            )
            regular_user.set_password('user123')
            
            db.session.add_all([admin, regular_user])
            db.session.commit()
            
        yield client

def test_login(client):
    response = client.post('/login', data={
        'login': 'admin',
        'password': 'admin123'
    }, follow_redirects=True)
    assert 'Admin' in response.data.decode('utf-8')

def test_create_user(client):
    client.post('/login', data={'login': 'admin', 'password': 'admin123'})
    
    response = client.post('/user/create', data={
        'login': 'newuser',
        'password': 'ValidPass123',
        'first_name': 'New',
        'role_id': 2
    }, follow_redirects=True)
    assert response.status_code == 200
    assert 'New' in response.data.decode('utf-8')

def test_admin_access(client):
    client.post('/login', data={'login': 'user', 'password': 'user123'})
    response = client.get('/user/create', follow_redirects=True)
    assert 'недостаточно прав' in response.data.decode('utf-8')

def test_registration(client):
    response = client.post('/register', data={
        'login': 'newuser',
        'password': 'ValidPass123',
        'confirm_password': 'ValidPass123',
        'first_name': 'New'
    }, follow_redirects=True)
    assert 'Теперь можно войти' in response.data.decode('utf-8')