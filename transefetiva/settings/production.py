from transefetiva.settings.settings import *
import os

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '-l-u+z*d%x-8edq9ef+v2uc9*ko#p2z&dij-h@^j71^)0kic5)'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

ALLOWED_HOSTS = ['127.0.0.1']

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'OPTIONS': {
            'read_default_file':  os.path.join(BASE_DIR, 'mysql.cnf'),
        },
    },
}
