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

CORS_REPLACE_HTTPS_REFERER      = False
HOST_SCHEME                     = "http://"
SECURE_PROXY_SSL_HEADER         = None
SECURE_SSL_REDIRECT             = False
SESSION_COOKIE_SECURE           = False
CSRF_COOKIE_SECURE              = False
SECURE_HSTS_SECONDS             = None
SECURE_HSTS_INCLUDE_SUBDOMAINS  = False
SECURE_FRAME_DENY               = False
SECURE_CONTENT_TYPE_NOSNIFF = False
SECURE_BROWSER_XSS_FILTER = False
X_FRAME_OPTIONS = 'DENY'
