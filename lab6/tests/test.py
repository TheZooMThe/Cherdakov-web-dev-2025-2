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

@pytest.fixture
def course(app, user, category):
    c = Course(
        name='Test Course',
        author_id=user.id,
        category_id=category.id,
        short_desc='short',
        full_desc='full',
        background_image_id="img1"
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
    # Создаем еще двух пользователей, чтобы сделать разные отзывы
    with app.app_context():
        user2 = User(login='user2', first_name='Second', last_name='User')
        user2.set_password('password2')
        user3 = User(login='user3', first_name='Third', last_name='User')
        user3.set_password('password3')
        db.session.add_all([user2, user3])
        db.session.commit()

        # Добавляем отзывы разных пользователей
        review1 = Review(course_id=course.id, user_id=user.id, rating=5, text='Отлично')
        review2 = Review(course_id=course.id, user_id=user2.id, rating=3, text='Средне')
        review3 = Review(course_id=course.id, user_id=user3.id, rating=1, text='Плохо')
        db.session.add_all([review1, review2, review3])
        db.session.commit()

    # Запрос с сортировкой positive
    response = auth_client.get(f'/courses/{course.id}/reviews?sort=positive')
    assert response.status_code == 200
    assert 'Отлично' in response.data.decode('utf-8')

    # Запрос с сортировкой negative
    response = auth_client.get(f'/courses/{course.id}/reviews?sort=negative')
    assert response.status_code == 200
    assert 'Плохо' in response.data.decode('utf-8')
