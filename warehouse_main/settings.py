import datetime
import os
import sentry_sdk
from celery.schedules import crontab
from sentry_sdk.integrations.django import DjangoIntegration

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get('SECRET_KEY', 'no_secret_key')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.environ.get('DEBUG', False)

ALLOWED_HOSTS = [
    '*'
]

INSTALLED_APPS = [
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'rest_framework',
    'warehouse',
]

ROOT_URLCONF = 'warehouse_main.urls'

WSGI_APPLICATION = 'warehouse_main.wsgi.application'

REST_FRAMEWORK = {
    'DEFAULT_RENDERER_CLASSES': (
        'rest_framework.renderers.JSONRenderer',
        'rest_framework.renderers.BrowsableAPIRenderer'
    ),
    'DEFAULT_PARSER_CLASSES': (
        'rest_framework.parsers.JSONParser',
        'rest_framework.parsers.FormParser'
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'warehouse_main.permissions.AccessPermission',
    ),
    'EXCEPTION_HANDLER': 'warehouse_main.utils.rest_framework_exception_handler'
}

# Internationalization
# https://docs.djangoproject.com/en/2.1/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

# DATABASES
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': os.environ.get('DB_NAME', 'warehouse_db'),
        'USER': os.environ.get('DB_USER', 'warehouse_user'),
        'PASSWORD': os.environ.get('DB_PASSWORD', 'warehouse_pass'),
        'HOST': os.environ.get('DB_HOST', 'localhost'),
        'PORT': os.environ.get('DB_PORT', 5432),
    }
}

# Celery
CELERY_QUEUE = os.environ.get('CELERY_QUEUE', 'warehouse_main')
BROKER_URL = os.environ.get('BROKER_URL', 'amqp://')

# ACCESS TOKEN
ACCESS_TOKEN = os.environ.get('ACCESS_TOKEN', '')

# STATSD
# Важно определять это до первого импорта statsd. Иначе он возьмет настройки по умолчанию.
# https://statsd.readthedocs.io/en/latest/configure.html#in-django
STATSD_HOST = os.environ.get('STATSD_HOST', '127.0.0.1')
STATSD_PORT = os.environ.get('STATSD_PORT', 8125)
STATSD_PREFIX = os.environ.get('STATSD_PREFIX', None)

# Url где находится CSV
GOOGLE_DOCS_DOCUMENT_URL = os.environ.get('GOOGLE_DOCS_DOCUMENT_URL', 
                                          'https://drive.google.com/u/0/uc?id=1jU7X9hScbJZEXcZzz4felythA-MaSAcY'
                                          '&export=download')

# Настройка sentry
SENTRY_SDK_DSN_URL = os.environ.get('SENTRY_SDK_DSN_URL', '')

if SENTRY_SDK_DSN_URL:
    sentry_sdk.init(
        dsn=SENTRY_SDK_DSN_URL,
        integrations=[DjangoIntegration()]
    )

# Это выполнение задач по расписанию, которо запускается процессом CeleryBeat
CELERYBEAT_SCHEDULE = {
    # Раз в сутки
    # 'process_sync_data_from_google_docs': {
    #     'task': 'warehouse.tasks.process_sync_data_from_google_docs',
    #     'schedule': crontab(minute=0, hour=1)
    # },
    'process_sync_data_from_google_docs': {
        'task': 'warehouse.tasks.process_sync_data_from_google_docs',
        'schedule': datetime.timedelta(minutes=1),  # Синхронизация каждую минуту, чтобы быстро получить данные
        'options': {'expires': 55}
    },
}
