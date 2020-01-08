""" Celery Configuration """
import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mypractice.settings')

CELERY_APP = Celery('mypractice')
CELERY_APP.config_from_object('django.conf:settings', namespace='CELERY')
CELERY_APP.autodiscover_tasks()

# To run celery, use the following command:
# celery -A mypractice worker -l info --without-heartbeat -E -P solo
