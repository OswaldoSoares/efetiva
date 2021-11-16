from .settings import *

with open('/app/auth/secret_key.txt') as f:
    SECRET_KEY = f.read().strip()

DEBUG = False
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
STATIS_ROOT = '/transefetiva/site/public/static'

# SECURE_HSTS_SECONDS = 15780000
# SECURE_HSTS_INCLUDE_SUBDOMAINS = True
# SECURE_HSTS_PRELOAD = True
# SECURE_SSL_REDIRECT = True
# CSRF_COOKIE_SECURE = True
# SESSION_COOKIE_SECURE = True
