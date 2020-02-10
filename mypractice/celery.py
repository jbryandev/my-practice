""" Celery Configuration """
import os
from celery import Celery
from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mypractice.settings')

app = Celery('mypractice')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

# To run celery worker, use the following command:
# celery -A mypractice worker -l info --without-heartbeat -E -P solo

# To run celery beat, use the following command:
# celery -A mypractice beat -l info

@app.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):

    # Calls test('hello') every 10 seconds.
    sender.add_periodic_task(10.0, test.s('hello'), name='add every 10')

    # Calls test('world') every 30 seconds
    sender.add_periodic_task(30.0, test.s('world'), expires=10)

    # Executes every Monday morning at 7:30 a.m.
    sender.add_periodic_task(
        crontab(hour=7, minute=30, day_of_week=1),
        test.s('Happy Mondays!'),
    )

@app.task
def test(arg):
    print(arg)
