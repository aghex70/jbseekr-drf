from __future__ import absolute_import, unicode_literals
import logging
import os

from celery import Celery

logger = logging.getLogger("Celery")

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'jbseekr.settings')

app = Celery('jbseekr')

app.config_from_object('django.conf:settings', namespace='CELERY')

app.autodiscover_tasks()
