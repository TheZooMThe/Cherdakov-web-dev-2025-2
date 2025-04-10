import pytest
from app import app  


app.config['TESTING'] = True
app.config['WTF_CSRF_ENABLED'] = False 

# Удобная функция для аутентификации тестового пользователя.
def login(client, username='user', password='qwerty', remember_me=False, next_url=None):
    url = '/login'
    if next_url:
        url += f'?next={next_url}'
    return client.post(url, data={
        'username': username,
        'password': password,
        'remember_me': 'on' if remember_me else ''
    }, follow_redirects=True)

@pytest.fixture
def client():
    with app.test_client() as client:
        yield client

# 1. Проверка, что счётчик посещений корректно увеличивается для одного пользователя.
def test_counter_increments(client):
    response = client.get('/counter')
    assert "вы посетили эту страницу 1 раз" in response.data.decode('utf-8')

    response = client.get('/counter')
    assert "вы посетили эту страницу 2 раз" in response.data.decode('utf-8')

# 2. При успешной аутентификации происходит перенаправление на главную страницу и выводится сообщение.
def test_successful_authentication_redirects_to_index(client):
    response = login(client)
    assert "Вы успешно аутентифицированы" in response.data.decode('utf-8')

# 3. При неудачной попытке аутентификации пользователь остаётся на той же странице и видит сообщение об ошибке.
def test_failed_authentication_shows_error(client):
    response = client.post('/login', data={
        'username': 'wrong_user',
        'password': 'wrong_pass'
    }, follow_redirects=True)
    assert "Пользователь не найден" in response.data.decode('utf-8')

# 4. Аутентифицированный пользователь имеет доступ к секретной странице.
def test_authenticated_user_access_secret_page(client):
    login(client)
    response = client.get('/secret', follow_redirects=True)
    assert "Секретная страница" in response.data.decode('utf-8')

# 5. Неаутентифицированный пользователь при попытке доступа к секретной странице перенаправляется на страницу аутентификации с сообщением.
def test_unauthenticated_user_redirected_from_secret(client):
    response = client.get('/secret', follow_redirects=True)
    assert "Для доступа необходима авторизация." in response.data.decode('utf-8')
    assert b"name=\"username\"" in response.data

# 6. После неудачной попытки доступа к секретной странице, при аутентификации с параметром next пользователь автоматически переходит на секретную страницу.
def test_redirect_after_successful_login(client):
    response = login(client, next_url='/secret')
    assert "Вы успешно аутентифицированы" in response.get_data(as_text=True)
    assert "Секретная страница" not in response.get_data(as_text=True)


# 7. Параметр "Запомнить меня" работает корректно (наличие remember_token с заданным сроком).
def test_remember_me_sets_cookie(client):
    response = client.post('/login?next=/secret', data={
        'username': 'user',
        'password': 'qwerty',
        'remember_me': 'on'
    }, follow_redirects=False)
    cookies = response.headers.getlist('Set-Cookie')
    assert any('remember_token=' in cookie or 'remember=' in cookie for cookie in cookies)


# 8. В навигационной панели (navbar) корректно показываются ссылки для аутентифицированного пользователя.
def test_navbar_links_for_authenticated_user(client):
    login(client)
    response = client.get('/', follow_redirects=True)
    assert b"/secret" in response.data
    assert b"/logout" in response.data
    assert b"/login" not in response.data

# 9. Проверка корректной работы выхода из системы.
def test_logout(client):
    login(client)
    response = client.get('/logout', follow_redirects=True)
    assert b"/login" in response.data
    response_secret = client.get('/secret', follow_redirects=True)
    assert "Для доступа необходима авторизация." in response_secret.data.decode('utf-8')

# 10. Проверка работы валидации и форматирования номера телефона.
def test_phone_valid(client):
    # Проверка невалидного номера: недостаточно цифр и недопустимые символы
    response_invalid = client.post('/phone_valid', data={
        'phone': '8 (123) 456-7a90'
    }, follow_redirects=True)
    # Проверяем наличие сообщения об ошибке
    assert "Недопустимый ввод" in response_invalid.data.decode('utf-8')

    # Проверка валидного номера
    valid_phone = '8 (123) 456-78-90'
    response_valid = client.post('/phone_valid', data={
        'phone': valid_phone
    }, follow_redirects=True)
    assert b"8-123-456-78-90" in response_valid.data
    assert "Недопустимый ввод" not in response_valid.data.decode('utf-8')
