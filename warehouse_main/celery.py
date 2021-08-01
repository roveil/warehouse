import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'warehouse_main.settings')

from django.conf import settings

app = Celery('tasks', backend='amqp')

app.config_from_object('django.conf:settings')
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)