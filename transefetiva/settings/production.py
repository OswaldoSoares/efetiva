from transefetiva.settings.settings import BASE_DIR, INSTALLED_APPS, MIDDLEWARE, ROOT_URLCONF, TEMPLATES, \
    WSGI_APPLICATION, AUTH_PASSWORD_VALIDATORS, LANGUAGE_CODE, TIME_ZONE, USE_I18N, USE_L10N, USE_TZ, br_formats, \
    EMAIL_BACKEND, EMAIL_HOST, EMAIL_HOST_PASSWORD, EMAIL_HOST_USER, EMAIL_PORT, EMAIL_USE_TLS, LOGIN_REDIRECT_URL, \
    LOGIN_URL, LOGOUT_REDIRECT_URL, MEDIA_ROOT, MEDIA_URL, ROLEPERMISSIONS_MODULE, ROLEPERMISSIONS_REGISTER_ADMIN
import os

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '-l-u+z*d%x-8edq9ef+v2uc9*ko#p2z&dij-h@^j71^)0kic5)'

# SECURITY WARNING: don't run with debug turned on in production!
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

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.0/howto/static-files/

STATIC_URL = '/static/'
STATIS_ROOT = '/transefetiva/site/public/static'
