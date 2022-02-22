import os
from decouple import config
from django.conf.locale.pt_BR import formats as br_formats

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',
    # apps de terceiros
    'rolepermissions',
    # meus apps
    'clientes',
    'despesas',
    'faturamentos',
    'minutas',
    'orcamentos',
    'pagamentos',
    'pessoas',
    'usuarios.apps.UsuariosConfig',
    'veiculos',
    'website',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'transefetiva.urls'

WSGI_APPLICATION = 'transefetiva.wsgi.application'

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

LANGUAGE_CODE = 'pt-br'

TIME_ZONE = 'America/Sao_Paulo'

USE_I18N = True

USE_L10N = True

USE_TZ = True

# LOGIN
LOGIN_REDIRECT_URL = 'index_website'
LOGIN_URL = 'login'
LOGOUT_REDIRECT_URL = 'login'

br_formats.DATE_FORMAT = 'd/m/Y'

# Permissões - DJANGO-ROLE-PERMISSIONS
ROLEPERMISSIONS_MODULE = 'transefetiva.roles'
ROLEPERMISSIONS_REGISTER_ADMIN = True
# ROLEPERMISSIONS_REDIRECT_TO_LOGIN = True
