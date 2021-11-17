from .settings import *

with open('/efetiva/auth/secret_key.txt') as f:
    SECRET_KEY = f.read().strip()

DEBUG = False
ALLOWED_HOSTS = ['137.184.201.225', 'www.transefetiva.com.br', 'transefetiva.com.br']

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'OPTIONS': {
            'read_default_file': '/efetiva/auth/mysql.cnf',
        },
    },
}

STATIC_URL = '/static/'
STATIC_ROOT = '/efetiva/site/public/static'

MEDIA_URL = '/media/'
MEDIA_ROOT = '/efetiva/site/public/media'

SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_SSL_REDIRECT = False

SECURE_HSTS_SECONDS = 15780000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
