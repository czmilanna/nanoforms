'''
Django settings for nanoforms project.

Generated by 'django-admin startproject' using Django 3.1.

For more information on this file, see
https://docs.djangoproject.com/en/3.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.0/ref/settings/
'''
import os
import pathlib
from pathlib import Path

SELF_URL = os.environ.get('SELF_URL', 'http://localhost:8000')

BASE_DIR = Path(__file__).resolve(strict=True).parent.parent
BASE_STORAGE_DIR = os.environ.get('BASE_STORAGE_DIR', '/srv/nanoporedev/')
KRAKEN_DB_DIR = os.path.join(BASE_STORAGE_DIR, 'minikraken2_v2_8GB_201904_UPDATE/')
BASE_UPLOAD_DIR = os.environ.get('BASE_UPLOAD_DIR', os.path.join(BASE_STORAGE_DIR, 'upload/'))
WDL_DIR = BASE_DIR.joinpath('wdl')

pathlib.Path(BASE_UPLOAD_DIR).mkdir(parents=True, exist_ok=True)

CROMWELL_EXECUTION_DIR = os.environ.get('CROMWELL_EXECUTION_DIR',
                                        os.path.join(BASE_STORAGE_DIR, 'cromwell-executions/'))
CROMWELL_URL = os.environ.get('CROMWELL_URL', 'http://127.0.0.1:7338')

# # Static files (CSS, JavaScript, Images)
# # https://docs.djangoproject.com/en/3.0/howto/static-files/
STATIC_URL = '/static/'
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, "static")
]

SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY', '!@0u)0e(5e$2x)*qi11a_x$s!&=yn+b&-iapq3nj=3jx=*zmaa')
ALLOWED_HOSTS = ['*']

CRISPY_TEMPLATE_PACK = 'bootstrap4'

if os.environ.get('PYCHARM_HOSTED'):
    DEBUG = True

if os.environ.get('EMAIL_HOST'):
    EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
    EMAIL_HOST = os.environ.get('EMAIL_HOST')
    EMAIL_PORT = int(os.environ.get('EMAIL_PORT'))
    EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER')
    DEFAULT_FROM_EMAIL = os.environ.get('EMAIL_FROM', EMAIL_HOST_USER)
    EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD')

else:
    EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# Application definition

INSTALLED_APPS = [
    'nanoforms_app.apps.NanoporeAppConfig',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django_registration',
    'crispy_forms',
    'active_link'
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'threadlocals.middleware.ThreadLocalMiddleware'
]

ROOT_URLCONF = 'nanoforms.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
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

WSGI_APPLICATION = 'nanoforms.wsgi.application'

# Database
# https://docs.djangoproject.com/en/3.0/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': os.environ['POSTGRES_USER'],
        'USER': os.environ['POSTGRES_USER'],
        'PASSWORD': os.environ['POSTGRES_PASSWORD'],
        'HOST': os.environ['POSTGRES_HOST'],
        'PORT': os.environ['POSTGRES_PORT']
    } if os.environ.get('POSTGRES_HOST') else {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_STORAGE_DIR, 'db.sqlite3')
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

ACCOUNT_ACTIVATION_DAYS = 7

# Internationalization
# https://docs.djangoproject.com/en/3.0/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True
