import pytest

import sys
import os
import pytest
from werkzeug.security import check_password_hash

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app, db
from models import User, Role, VisitLog
from flask import url_for
import io
import csv


@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['WTF_CSRF_ENABLED'] = False
    with app.test_client() as client:
        with app.app_context():
            db.drop_all()
            db.create_all()

            # Setup roles
            admin_role = Role(name='Администратор', description='Полный доступ')
            user_role = Role(name='Пользователь', description='Обычный пользователь')
            db.session.add_all([admin_role, user_role])
            db.session.commit()

            # Create admin
            admin = User(login='admin', first_name='Админ', last_name='Тестовый', role_id=admin_role.id)
            admin.set_password('admin123')
            db.session.add(admin)

            # Create regular users
            for i in range(25):
                user = User(login=f'user{i}', first_name='User', role_id=user_role.id)
                user.set_password('passwordA1')
                db.session.add(user)
            db.session.commit()

        yield client


def test_login(client):
    response = client.post('/login', data={
        'login': 'admin',
        'password': 'admin123'
    }, follow_redirects=True)
    assert 'Админ' in response.data.decode('utf-8')

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


def test_registration(client):
    response = client.post('/register', data={
        'login': 'newuser',
        'password': 'ValidPass123',
        'confirm_password': 'ValidPass123',
        'first_name': 'New'
    }, follow_redirects=True)
    assert 'Теперь можно войти' in response.data.decode('utf-8')

def test_visit_log_created(client):
    client.post('/login', data={'login': 'admin', 'password': 'admin123'})
    client.get('/')
    
    with app.app_context():
        visit = VisitLog.query.filter_by(path='/').first()
        assert visit is not None
        assert visit.user_id is not None

def test_visit_log_pagination(client):
    client.post('/login', data={'login': 'admin', 'password': 'admin123'})

    # Имитация 25 посещений
    with client.application.app_context():
        user = User.query.filter_by(login='admin').first()
        for _ in range(15):
            db.session.add(VisitLog(path='/dummy', user_id=user.id))
        db.session.commit()

    # Проверка первой страницы
    response = client.get('/reports/visits?page=1')
    assert response.status_code == 200
    assert b'<nav' in response.data or b'pagination' in response.data
    assert response.data.count(b'<tr') >= 10  # 10 записей на странице

    # Проверка второй страницы
    response = client.get('/reports/visits?page=2')
    assert response.status_code == 200
    assert response.data.count(b'<tr') == 5  # Оставшиеся записи


def test_pages_report(client):
    client.post('/login', data={'login': 'admin', 'password': 'admin123'})
    with client.application.app_context():
        user = User.query.filter_by(login='admin').first()
        db.session.add_all([
            VisitLog(path='/page1', user_id=user.id),
            VisitLog(path='/page1', user_id=user.id),
            VisitLog(path='/page2', user_id=user.id),
        ])
        db.session.commit()

    response = client.get('/reports/pages')
    assert response.status_code == 200
    assert b'/page1' in response.data
    assert b'/page2' in response.data

def test_users_report(client):
    client.post('/login', data={'login': 'admin', 'password': 'admin123'})
    with client.application.app_context():
        admin = User.query.filter_by(login='admin').first()
        db.session.add_all([
            VisitLog(path='/a', user_id=admin.id),
            VisitLog(path='/b', user_id=admin.id)
        ])
        db.session.commit()

    response = client.get('/reports/users')
    assert response.status_code == 200
    assert 'Админ' in response.data.decode('utf-8')



def test_export_csv_pages(client):
    client.post('/login', data={'login': 'admin', 'password': 'admin123'})
    with client.application.app_context():
        admin = User.query.filter_by(login='admin').first()
        db.session.add_all([
            VisitLog(path='/home', user_id=admin.id),
            VisitLog(path='/home', user_id=admin.id),
            VisitLog(path='/about', user_id=admin.id)
        ])
        db.session.commit()

    response = client.get('/reports/export/pages')
    content = response.data.decode('utf-8')
    assert response.status_code == 200
    assert 'Страница,Количество посещений' in content
    assert '/home,2' in content
    assert '/about,1' in content
    assert response.headers['Content-type'] == 'text/csv'


def test_export_csv_users(client):
    client.post('/login', data={'login': 'admin', 'password': 'admin123'})
    with client.application.app_context():
        admin = User.query.filter_by(login='admin').first()
        db.session.add_all([
            VisitLog(path='/home', user_id=admin.id),
            VisitLog(path='/about', user_id=admin.id),
        ])
        db.session.commit()

    response = client.get('/reports/export/users')
    content = response.data.decode('utf-8')
    assert response.status_code == 200
    assert 'Пользователь,Количество посещений' in content
    assert 'Админ' in content or 'Системный' in content
    assert response.headers['Content-Disposition'].endswith('users_report.csv')

def test_export_invalid_report_type(client):
    response = client.get('/reports/export/invalid')
    assert response.status_code == 400
    assert b'Invalid report type' in response.data
