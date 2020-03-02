"""
Django settings for prolife project.
"""

import datetime as dt
import environ
import sentry_sdk
import logging
from sentry_sdk.integrations.django import DjangoIntegration
from sentry_sdk.integrations.logging import LoggingIntegration


root = environ.Path(__file__) - 2
env = environ.Env(
    DEBUG=(bool, False),
)

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = env('SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = env('DEBUG')

ALLOWED_HOSTS = ['*']


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'django_extensions',

    'prolife.core',

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

ROOT_URLCONF = 'prolife.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [root('prolife/templates')],
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

WSGI_APPLICATION = 'prolife.wsgi.application'


# Database

DATABASES = {
    'default': env.db(),
}

# Password validation

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

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)

STATIC_URL = env('STATIC_URL', default='/static/')

STATIC_ROOT = env('STATIC_ROOT', default=root('static'))

MEDIA_URL = env('MEDIA_URL', default='/media/')

MEDIA_ROOT = env('MEDIA_ROOT', default=root('media'))

# redirect HTTP to HTTPS
if env.bool('HTTPS_REDIRECT', default=False) and not DEBUG:
    SECURE_SSL_REDIRECT = True
    SECURE_REDIRECT_EXEMPT = []
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
else:
    SECURE_SSL_REDIRECT = False

# trust the given (by default "X-Scheme") header that comes from our proxy (nginx),
# and any time its value is "https",
# then the request is guaranteed to be secure (i.e., it originally came in via HTTPS).
HTTPS_PROXY_HEADER = 'X_SCHEME'
if HTTPS_PROXY_HEADER and not DEBUG:
    SECURE_PROXY_SSL_HEADER = (f'HTTP_{HTTPS_PROXY_HEADER}', 'https')
else:
    SECURE_PROXY_SSL_HEADER = None



# --- Celery

CELERY_BROKER_URL = env('CELERY_BROKER_URL', default='')

# Store task results in Redis
CELERY_RESULT_BACKEND = env('CELERY_BROKER_URL', default='')

# Task result life time until they will be deleted
CELERY_RESULT_EXPIRES = int(dt.timedelta(days=1).total_seconds())

# Needed for worker monitoring
CELERY_SEND_EVENTS = True

CELERY_BEAT_SCHEDULE = {}

# default to json serialization only
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'


if env('SENTRY_DSN', default=''):
    sentry_logging = LoggingIntegration(
        level=logging.INFO,  # Capture info and above as breadcrumbs
        event_level=logging.ERROR     # Send error events from log messages
    )

    sentry_sdk.init(
        dsn=env('SENTRY_DSN', default=''),
        integrations=[DjangoIntegration(), sentry_logging]
    )

EMAIL_USE_SSL = False
EMAIL_USE_TLS = True
EMAIL_HOST = env('EMAIL_HOST', default='')
EMAIL_PORT = env('EMAIL_PORT', default=587)
EMAIL_HOST_USER = env('EMAIL_HOST_USER', default='')
EMAIL_HOST_PASSWORD = env('EMAIL_HOST_PASSWORD', default='')
DEFAULT_FROM_EMAIL = env('DEFAULT_FROM_EMAIL', default='Monster@prolifedistribution.co.uk')

ORDER_CREATED_TO_EMAILS = env.list('ORDER_CREATED_TO_EMAILS', default=[])
ORDER_CREATED_CC_EMAILS = env.list('ORDER_CREATED_CC_EMAILS', default=[])

BASE_URL = env('BASE_URL', default='')

STATICFILES_DIRS = [
    root('prolife/static'),
]
