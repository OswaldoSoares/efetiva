"""
Django settings for transefetiva project.

Generated by 'django-admin startproject' using Django 3.0.3.

For more information on this file, see
https://docs.djangoproject.com/en/3.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.0/ref/settings/
"""

import os
from django.conf.locale.pt_BR import formats as br_formats
import django_heroku

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '-l-u+z*d%x-8edq9ef+v2uc9*ko#p2z&dij-h@^j71^)0kic5)'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['*']


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # apps de terceiros
    'rolepermissions',
    # meus apps
    'clientes',
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

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            'templates'
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'transefetiva.wsgi.application'


# Database
# https://docs.djangoproject.com/en/3.0/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'USER': 'root',
        'PASSWORD': 'S1c9c1p0',
        'SERVER': 'localhost',
        'PORT': '3306',
        'NAME': 'transefetiva',
        'options': {
            'init_command': 'SET foreing_key_checks = 0',
        }
    }
}


# Password validation
# https://docs.djangoproject.com/en/3.0/ref/settings/#auth-password-validators

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


# Internationalization
# https://docs.djangoproject.com/en/3.0/topics/i18n/

LANGUAGE_CODE = 'pt-br'

TIME_ZONE = 'America/Sao_Paulo'

USE_I18N = True

USE_L10N = True

USE_TZ = True

# USE_THOUSAND_SEPARATOR = True


# Configuração de E-Mails
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_USE_TLS = True
EMAIL_HOST = 'smtp.terra.com.br'
EMAIL_PORT = 587
EMAIL_HOST_USER = 'financeiro.efetiva@terra.com.br'
EMAIL_HOST_PASSWORD = 'mau159753'

# LOGIN
LOGIN_REDIRECT_URL = 'index_website'
LOGIN_URL = 'login'
LOGOUT_REDIRECT_URL = 'login'

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.0/howto/static-files/

STATIC_URL = '/static/'


MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

br_formats.DATE_FORMAT = 'd/m/Y'

django_heroku.settings(locals())

# Permissões - DJANGO-ROLE-PERMISSIONS
ROLEPERMISSIONS_MODULE = 'transefetiva.roles'
ROLEPERMISSIONS_REGISTER_ADMIN = True
# ROLEPERMISSIONS_REDIRECT_TO_LOGIN = True
