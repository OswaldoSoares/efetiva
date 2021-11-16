with open('/transefetiva/auth/secret_key.txt') as f:
    SECRET_KEY = f.read().strip()

print(SECRET_KEY)

DEBUG = False
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

SECURE_HSTS_SECONDS = 15780000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SECURE_SSL_REDIRECT = True
CSRF_COOKIE_SECURE = True
SESSION_COOKIE_SECURE = True
