import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from bs4 import BeautifulSoup

import pytest
from app import create_app, db
from app.models import User, Course, Review, Category

@pytest.fixture
def app():
    app = create_app()
    app.config['TESTING'] = True
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def category(app):
    cat = Category(name='Test Category')
    db.session.add(cat)
    db.session.commit()
    return cat

@pytest.fixture
def user(app):
    u = User(login='testuser', first_name='Test', last_name='User')
    u.set_password('password')
    db.session.add(u)
    db.session.commit()
    return u
from app.models import Image
from datetime import datetime

@pytest.fixture
def image(app):
    img = Image(
        id="img1",
        file_name="background.png",
        mime_type="image/png",
        md5_hash="dummyhash",
        created_at=datetime.utcnow()
    )
    db.session.add(img)
    db.session.commit()
    return img



@pytest.fixture
def course(app, user, category, image):
    c = Course(
        name='Test Course',
        author_id=user.id,
        category_id=category.id,
        short_desc='short',
        full_desc='full',
        background_image_id=image.id
    )
    db.session.add(c)
    db.session.commit()
    return c

@pytest.fixture
def auth_client(client, user):
    response = client.post('/auth/login', data={
        'login': user.login,
        'password': 'password'
    }, follow_redirects=True)
    assert response.status_code == 200
    return client

def test_add_review_success(auth_client, user, course):
    response = auth_client.post(f'/courses/{course.id}/reviews/create', data={
        'rating': '5',
        'text': 'Отличный курс!'
    }, follow_redirects=True)

    assert 'Отзыв успешно добавлен.' in response.data.decode('utf-8')
    review = Review.query.filter_by(course_id=course.id, user_id=user.id).first()
    assert review is not None
    assert review.text == 'Отличный курс!'
    assert review.rating == 5

def test_add_review_empty_text(auth_client, user, course):
    response = auth_client.post(f'/courses/{course.id}/reviews/create', data={
        'rating': '5',
        'text': ''
    }, follow_redirects=True)

    assert 'Текст отзыва не может быть пустым.' in response.data.decode('utf-8')
    review = Review.query.filter_by(course_id=course.id, user_id=user.id).first()
    assert review is None

def test_add_duplicate_review(auth_client, user, course):
    # Сначала добавляем первый отзыв
    auth_client.post(f'/courses/{course.id}/reviews/create', data={
        'rating': '4',
        'text': 'Хороший курс'
    }, follow_redirects=True)

    # Попытка добавить второй отзыв
    response = auth_client.post(f'/courses/{course.id}/reviews/create', data={
        'rating': '3',
        'text': 'Второй отзыв'
    }, follow_redirects=True)

    assert 'Вы уже оставили отзыв на этот курс.' in response.data.decode('utf-8')



def test_reviews_sorting(auth_client, user, course, app):
    with app.app_context():
        user2 = User(login='user2', first_name='Second', last_name='User')
        user2.set_password('password2')
        user3 = User(login='user3', first_name='Third', last_name='User')
        user3.set_password('password3')
        db.session.add_all([user2, user3])
        db.session.commit()

        review1 = Review(course_id=course.id, user_id=user.id, rating=5, text='Отлично')
        review2 = Review(course_id=course.id, user_id=user2.id, rating=3, text='Средне')
        review3 = Review(course_id=course.id, user_id=user3.id, rating=1, text='Плохо')
        db.session.add_all([review1, review2, review3])
        db.session.commit()

    def get_ratings_from_page(html):
        soup = BeautifulSoup(html, 'html.parser')
        ratings = []
        for li in soup.select('ul li'):
            text = li.get_text()
            parts = text.split('рейтинг:')
            if len(parts) > 1:
                rating_str = parts[1].strip().split()[0]  # Берём первое число после "рейтинг:"
                ratings.append(int(rating_str))
        return ratings

    # positive — рейтинг по убыванию
    response = auth_client.get(f'/courses/{course.id}/reviews?sort=positive')
    assert response.status_code == 200
    ratings = get_ratings_from_page(response.data)
    assert ratings == sorted(ratings, reverse=True)

    # negative — рейтинг по возрастанию
    response = auth_client.get(f'/courses/{course.id}/reviews?sort=negative')
    assert response.status_code == 200
    ratings = get_ratings_from_page(response.data)
    assert ratings == sorted(ratings)

    # Повторный отзыв
    response = auth_client.post(f'/courses/{course.id}/reviews/create', data={
        'rating': '4',
        'text': 'Второй отзыв'
    }, follow_redirects=True)

    assert 'Вы уже оставили отзыв на этот курс.' in response.data.decode('utf-8')


def test_reviews_pagination_and_sorting(auth_client, user, course, app):
    with app.app_context():
        # Создаем 12 отзывов с разным рейтингом и текстом
        reviews = []
        for i in range(12):
            r = Review(
                course_id=course.id,
                user_id=user.id,
                rating=(i % 5) + 1,  # рейтинг 1..5
                text=f'Отзыв {i+1}'
            )
            reviews.append(r)
        db.session.add_all(reviews)
        db.session.commit()

    # Запрос страницы 1 с сортировкой positive (рейтинг по убыванию)
    response = auth_client.get(f'/courses/{course.id}/reviews?sort=positive&page=1')
    assert response.status_code == 200
    html = response.data.decode('utf-8')

    # Проверяем, что на странице ровно 5 отзывов (per_page=5)
    assert html.count('<li>') == 5

    # Проверяем, что отзывы идут в правильном порядке по рейтингу (от 5 к 1)
    # Проверим, что самый высокий рейтинг встречается среди первых отзывов
    assert 'рейтинг: 5' in html

    # Запрос страницы 2 с той же сортировкой
    response2 = auth_client.get(f'/courses/{course.id}/reviews?sort=positive&page=2')
    assert response2.status_code == 200
    html2 = response2.data.decode('utf-8')

    # Проверяем, что на странице тоже 5 отзывов
    assert html2.count('<li>') == 5

    # Проверяем, что параметр sort=positive остался (например, в ссылках пагинации)
    # Обычно ссылки пагинации содержат параметры запроса
    assert 'sort=positive' in html2

    # Проверим, что отзывы на странице 2 отличаются от отзывов на странице 1 (например, другой текст)
    assert 'Отзыв 6' in html2 or 'Отзыв 7' in html2
