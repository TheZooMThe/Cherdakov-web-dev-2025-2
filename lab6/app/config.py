import os

SECRET_KEY = '/RiXnoGXTLXVyfanm2XgKA=='

SQLALCHEMY_DATABASE_URI = 'postgresql://postgres:furry@localhost/lab6'

# SQLALCHEMY_DATABASE_URI = 'mysql+mysqlconnector://user:password@std-mysql.ist.mospolytech.ru/db_name'
SQLALCHEMY_TRACK_MODIFICATIONS = False
SQLALCHEMY_ECHO = True

UPLOAD_FOLDER = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), 
    '..',
    'media', 
    'images'
)
