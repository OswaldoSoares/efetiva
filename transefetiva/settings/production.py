from .settings import *

with open('/auth/secret_key.txt') as f:
    SECRET_KEY = f.read().strip()

DEBUG = True
ALLOWED_HOSTS = ['192.81.215.116']

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'OPTIONS': {
            'read_default_file':  '/app/auth/mysql.cnf',
        },
    },
}

STATIC_URL = '/static/'
STATIC_ROOT = '/app/site/public/static'

SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_SSL_REDIRECT = False

SECURE_HSTS_SECONDS = 15780000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
