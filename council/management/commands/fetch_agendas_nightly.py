from django.core.management.base import BaseCommand
from council.tasks import fetch_agendas
from council.models import Department

# Command to run: python manage.py fetch_agendas_nightly
class Command(BaseCommand):
    help = 'Runs fetch_agendas() command nightly to keep agendas up-to-date'

    def handle(self, *args, **options):
        self.stdout.write("---RUNNING FETCH AGENDAS NIGHTLY TASK---")
        departments = Department.objects.all()
        for department in departments:
            fetch_agendas(department.id)
        self.stdout.write("---COMPLETED FETCH AGENDAS NIGHTLY TASK---")
