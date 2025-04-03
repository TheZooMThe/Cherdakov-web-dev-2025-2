import pytest
from app import app, validate_phone, fix_phone_format

@pytest.fixture
def client():
    with app.test_client() as client:
        yield client

# 1. Проверка отображения параметров URL
def test_args_page_parameters_displayed(client):
    response = client.get('/args?param1=value1&param2=value2')
    html = response.get_data(as_text=True)
    assert 'param1' in html and 'value1' in html
    assert 'param2' in html and 'value2' in html

# 2. Проверка отображения заголовков запроса
def test_headers_page_headers_displayed(client):
    response = client.get('/headers', headers={'Custom-Header': 'TestValue'})
    html = response.get_data(as_text=True)
    assert 'Custom-Header' in html and 'TestValue' in html

# 3. Проверка отображения куки
def test_cookies_page_cookies_displayed(client):
    client.set_cookie('mycookie', 'cookievalue')
    response = client.get('/cookies')
    html = response.get_data(as_text=True)
    assert 'mycookie' in html and 'cookievalue' in html

# 4. Проверка отображения формы (GET-запрос)
def test_form_page_get(client):
    response = client.get('/form')
    html = response.get_data(as_text=True)
    # Форма должна присутствовать, а таблица с данными – отсутствовать, т.к. форма не отправлена.
    assert '<form' in html
    assert '<table' not in html

# 5. Проверка передачи данных формы (POST-запрос)
def test_form_page_post(client):
    data = {'theme': 'Test Theme', 'text': 'Test Text'}
    response = client.post('/form', data=data)
    html = response.get_data(as_text=True)
    assert 'Test Theme' in html
    assert 'Test Text' in html
    # Таблица с отправленными данными должна быть видна
    assert '<table' in html

# 6. Проверка валидации номера: недопустимые символы
def test_phone_valid_invalid_symbol(client):
    data = {'phone': '12345a78901'}  # содержит букву "a"
    response = client.post('/phone_valid', data=data)
    html = response.get_data(as_text=True)
    assert "Недопустимый ввод. В номере телефона встречаются недопустимые символы." in html

# 7. Проверка валидации номера: неверное количество цифр (меньше 11)
def test_phone_valid_wrong_digit_count(client):
    data = {'phone': '1234567890'}  # 10 цифр
    response = client.post('/phone_valid', data=data)
    html = response.get_data(as_text=True)
    assert "Неверное количество цифр" in html

# 8. Проверка корректного ввода номера: валидный номер с форматированием
def test_phone_valid_correct_number(client):
    phone_input = '8 912-345-67-89'
    data = {'phone': phone_input}
    response = client.post('/phone_valid', data=data)
    html = response.get_data(as_text=True)
    # Ошибки отсутствуют, поэтому не должно быть класса is-invalid
    assert "is-invalid" not in html
    # Ожидаемый отформатированный номер
    assert '8-912-345-67-89' in html

# 9. Проверка наличия класса Bootstrap is-invalid при ошибке валидации
def test_phone_valid_bootstrap_class_on_error(client):
    data = {'phone': '1234'}  # недостаточное количество цифр
    response = client.post('/phone_valid', data=data)
    html = response.get_data(as_text=True)
    assert 'is-invalid' in html

# 10. Тестирование функции fix_phone_format напрямую
def test_fix_phone_format_function():
    input_phone = '89123456789'
    formatted = fix_phone_format(input_phone)
    assert formatted == '8-912-345-67-89'

# 11. Тестирование функции validate_phone: недопустимые символы
def test_validate_phone_invalid_symbols():
    error = validate_phone('12345a78901')
    expected = "Недопустимый ввод. В номере телефона встречаются недопустимые символы."
    assert error == expected

# 12. Тестирование функции validate_phone: неверное количество цифр
def test_validate_phone_wrong_digit_count():
    error = validate_phone('1234567890')  # 10 цифр
    assert "Неверное количество цифр" in error

# 13. Тестирование функции validate_phone: корректный номер
def test_validate_phone_valid():
    error = validate_phone('89123456789')
    assert error is None

# 14. Проверка страницы phone_valid с использованием разрешённых символов (пробелы, скобки, тире, точка, +)
def test_phone_valid_allowed_characters(client):
    phone_input = '+8 (912) 345.67-89'
    data = {'phone': phone_input}
    response = client.post('/phone_valid', data=data)
    html = response.get_data(as_text=True)
    # В случае корректного ввода не должно быть ошибки и класс is-invalid отсутствует
    assert "is-invalid" not in html
    # Ожидаемый формат номера (извлечены все цифры)
    expected = '8-912-345-67-89'
    assert expected in html

# 15. Проверка GET-запроса для страницы валидации номера: форма отображается без ошибок
def test_phone_valid_get_request(client):
    response = client.get('/phone_valid')
    html = response.get_data(as_text=True)
    # Отсутствует сообщение об ошибке (div с invalid-feedback)
    assert 'invalid-feedback' not in html
    # Поле ввода должно быть пустым
    assert 'value=""' in html
