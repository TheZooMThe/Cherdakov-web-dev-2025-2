from contextlib import contextmanager
import pytest
from flask import template_rendered, url_for
from datetime import datetime
from unittest.mock import patch
from app import posts_list as original_posts_list

def test_posts_route_status_code(client):
    response = client.get('/posts')
    assert response.status_code == 200

def test_posts_template_used(client):
    with captured_templates(client.application) as templates:
        client.get("/posts")
        assert len(templates) == 1
        assert templates[0][0].name == "posts.html"

def test_posts_context_data(client):
    with captured_templates(client.application) as templates:
        client.get("/posts")
        context = templates[0][1]
        assert context["title"] == "Посты"
        assert isinstance(context["posts"], list)

def test_post_detail_template(client, mocker):
    test_post = {
        "title": "Test Post",
        "text": "Test content",
        "author": "Test Author",
        "date": datetime(2023, 1, 1),
        "image_id": "test.jpg",
        "comments": []
    }

 
    mock_posts = mocker.patch("app.posts_list")
    mock_posts.return_value = [test_post]
    original_posts_list.cache_clear()

    with captured_templates(client.application) as templates:
        response = client.get("/posts/0")  
        assert response.status_code == 200

    assert len(templates) == 1
    template_name = templates[0][0].name
    assert template_name == "post.html", f"Ожидался шаблон post.html, получено {template_name}"

def test_post_detail_content(client):
    test_post = {
        'title': 'Test Post',
        'text': 'Test content',
        'author': 'Test Author',
        'date': datetime(2023, 1, 1),
        'image_id': 'test.jpg',
        'comments': [{
            'author': 'Commenter',
            'text': 'Nice post!',
            'replies': []
        }]
    }
    
    with patch('app.posts_list', return_value=[test_post]):
        response = client.get('/posts/0')
        
        assert 'Test Post' in response.text
        assert 'Test content' in response.text
        assert 'Test Author' in response.text
        assert '01.01.2023' in response.text
        assert 'Commenter' in response.text
        assert 'Nice post!' in response.text

def test_post_image_rendering(client):
    test_post = {
        'title': 'Test Post',
        'text': 'Test content',
        'author': 'Test Author',
        'date': datetime.now(),
        'image_id': 'test_image.jpg',
        'comments': []
    }
    
    with patch('app.posts_list', return_value=[test_post]):
        response = client.get('/posts/0')
        assert 'src="/static/images/test_image.jpg"' in response.text

def test_comment_form_elements(client):
    test_post = {
        'title': 'Test Post',
        'text': 'Test content',
        'author': 'Test Author',
        'date': datetime.now(),
        'image_id': 'test.jpg',
        'comments': []
    }
    
    with patch('app.posts_list', return_value=[test_post]):
        response = client.get('/posts/0')
        assert 'Оставьте комментарий' in response.text
        assert '<textarea' in response.text
        assert 'Отправить' in response.text

def test_nonexistent_post_returns_404(client, mocker):
    mocker.patch("app.posts_list", return_value=[])
    original_posts_list.cache_clear()
    
    response = client.get("/post/999")
    assert response.status_code == 404

def test_post_date_formatting(client):
    test_post = {
        'title': 'Test Post',
        'text': 'Test content',
        'author': 'Test Author',
        'date': datetime(2023, 12, 31, 15, 30),
        'image_id': 'test.jpg',
        'comments': []
    }
    
    with patch('app.posts_list', return_value=[test_post]):
        response = client.get('/posts/0')
        assert '31.12.2023' in response.text
        assert '15:30' not in response.text  

def test_comment_replies_rendering(client):
    test_post = {
        'title': 'Test Post',
        'text': 'Test content',
        'author': 'Test Author',
        'date': datetime.now(),
        'image_id': 'test.jpg',
        'comments': [{
            'author': 'Parent',
            'text': 'Parent comment',
            'replies': [{
                'author': 'Child',
                'text': 'Child comment'
            }]
        }]
    }
    
    with patch('app.posts_list', return_value=[test_post]):
        response = client.get('/posts/0')
        assert 'Parent' in response.text
        assert 'Child' in response.text
        assert 'ms-5' in response.text  

def test_avatar_rendering(client):
    test_post = {
        'title': 'Test Post',
        'text': 'Test content',
        'author': 'Test Author',
        'date': datetime.now(),
        'image_id': 'test.jpg',
        'comments': [{
            'author': 'Commenter',
            'text': 'Test comment',
            'replies': []
        }]
    }
    
    with patch('app.posts_list', return_value=[test_post]):
        response = client.get('/posts/0')
        assert 'src="/static/images/avatar.svg"' in response.text

def test_post_truncation_in_list(client, mocker):
    long_text = "a" * 200
    test_post = {
        "title": "Test Post",
        "text": long_text,
        "author": "Test Author",
        "date": datetime.now(),
        "image_id": "test.jpg",
        "comments": []
    }
    
    mocker.patch("app.posts_list", return_value=[test_post])
    original_posts_list.cache_clear()
    
    response = client.get("/posts")
    assert "a" * 97 + "..." in response.text

def test_post_links_in_list(client):
    test_posts = [
        {'title': f'Post {i}', 'text': '', 'author': '', 
         'date': datetime.now(), 'image_id': '', 'comments': []}
        for i in range(3)
    ]
    
    with patch('app.posts_list', return_value=test_posts):
        response = client.get('/posts')
        for i in range(3):
            assert f'href="/posts/{i}"' in response.text

@contextmanager
def captured_templates(app):
    templates = []
    def record(sender, template, context, **extra):
        templates.append((template, context))
    template_rendered.connect(record, app)
    try:
        yield templates
    finally:
        template_rendered.disconnect(record, app)

def test_post_date_format(client, mocker):
    test_date = datetime(2023, 12, 31, 15, 30)
    test_post = {
        "date": test_date,
        "title": "Test Post",
        "text": "Content",
        "author": "Author",
        "image_id": "test.jpg",
        "comments": []
    }
    
    mocker.patch("app.posts_list", return_value=[test_post])
    original_posts_list.cache_clear()
    
    response = client.get("/posts/0")
    assert test_date.strftime('%d.%m.%Y') in response.text
    assert "15:30" not in response.text 

def test_comment_avatars(client, mocker):
    test_post = {
        "comments": [
            {
                "author": "Commenter",
                "text": "Test comment",
                "replies": [
                    {"author": "Reply Author", "text": "Test reply"}
                ]
            }
        ],
        "title": "Test Post",
        "text": "Content",
        "author": "Author",
        "date": datetime.now(),
        "image_id": "test.jpg"
    }
    
    mocker.patch("app.posts_list", return_value=[test_post])
    original_posts_list.cache_clear()
    
    response = client.get("/posts/0")
    assert 'src="/static/images/avatar.svg"' in response.text
    assert 'alt="Аватар"' in response.text
    assert 'rounded-circle' in response.text  