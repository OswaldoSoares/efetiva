from .settings import *
import os

with open('/transefetiva/auth/secret_key.txt') as f:
    SECRET_KEY = f.read().strip()

print(SECRET_KEY)

DEBUG = True
ALLOWED_HOSTS = ['159.223.191.6']

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'OPTIONS': {
            'read_default_file':  '/transefetiva/auth/mysql.cnf',
        },
    },
}

STATIC_URL = '/static/'
STATIS_ROOT = '/transefetiva/site/public/static'

CSRF_COOKIE_SECURE = True
SESSION_COOKIE_SECURE = True
