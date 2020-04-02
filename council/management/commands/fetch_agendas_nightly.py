from django.core.management.base import BaseCommand
from council.tasks import fetch_agendas
from council.models import Department

class Command(BaseCommand):
    help = 'Runs fetch agendas command nightly to keep agendas up-to-date'

    def handle(self, *args, **options):
        self.stdout.write("---RUNNING FETCH AGENDAS NIGHTLY TASK---")
        departments = Department.objects.all()
        fetch_agendas.delay(departments[0].id)
        for department in departments:
            self.stdout.write(f'Fetching agendas for {department.agency} - {department.department_name}')
            #fetch_agendas.delay(department.id)
        self.stdout.write("---COMPLETED FETCH AGENDAS NIGHTLY TASK---")