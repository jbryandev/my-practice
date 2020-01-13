""" Celery Configuration """
import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mypractice.settings')

app = Celery('mypractice')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

# To run celery, use the following command:
# celery -A mypractice worker -l info --without-heartbeat -E -P solo
