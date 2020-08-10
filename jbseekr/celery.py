from __future__ import absolute_import, unicode_literals
import logging
import os

from django.conf import settings
from celery import Celery

logger = logging.getLogger("Celery")

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'uservice.settings')

app = Celery('apicontext-celery')

app.config_from_object('django.conf:settings', namespace='CELERY')
app.conf.broker_transport_options = {
    'fanout_prefix': True,
    'fanout_patterns': True,
    'visibility_timeout': 43200
}

# Overrides autodiscover_tasks() to find and execute tasks recursively
for app_name in settings.INSTALLED_APPS:
    if app_name.startswith('django'):
        continue
    for root, dirs, files in os.walk(app_name + '/tasks'):
        for file in files:
            if file.startswith('__') or file.endswith('.pyc') or not file.endswith('.py'):
                continue
            file = file[:-3]
            app.autodiscover_tasks([app_name + '.tasks'], related_name=file)
