""" Celery Configuration """
import os
from celery import Celery
from celery.schedules import crontab
from django.core.mail import send_mail

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
    """ Function that establishes periodic tasks to be run by celery """

    # Run fetch_agendas() for all departments every day at midnight
    """
    sender.add_periodic_task(
        crontab(hour=0, minute=0),
        fetch_agendas.s(),
        name='Fetch Agendas Crontab',
    )
    """

@app.task
def fetch_agendas():
    """ Function to run fetch_agendas() on regular intervals as a crontab """
    from council.tasks import fetch_agendas as fetch
    from council.models import Department
    for department in Department.objects.all():
        fetch.delay(department.id)
        print("Beat Scheduled Task: Running fetch_agendas(" + str(department.id) + ")")

    subject = "Council Insights: Crontab Run"
    body = "The fetch_agendas() crontab was called successfully at midnight."
    send_mail(
        subject,
        body,
        'council-insights@my-practice.herokuapp.com',
        ['james.bryan@kimley-horn.com']
    )
