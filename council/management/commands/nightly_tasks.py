from django.core.management.base import BaseCommand
from council.tasks import fetch_agendas, convert_pdf_to_text, \
    generate_highlights, cleanup_old_agendas
from council.models import Department, Agenda

# Command to run: python manage.py nightly_tasks
class Command(BaseCommand):
    help = 'Runs nightly commands to keep agendas up-to-date'

    def handle(self, *args, **options):
        self.stdout.write("---RUNNING COUNCIL-INSIGHTS NIGHTLY TASKS---")
        self.stdout.write("---Step 1: Fetch New Agendas---")
        self.nightly_fetch_agendas()
        self.stdout.write("---Step 2: Convert PDFs to Text---")
        self.nightly_convert_pdf_to_text()
        self.stdout.write("---Step 3: Generate Highlights---")
        self.nightly_generate_highlights()
        self.stdout.write("---Step 4: Clean Out Old Agendas---")
        cleanup_old_agendas()
        self.stdout.write("---COMPLETED COUNCIL-INSIGHTS NIGHTLY TASKS---")

    @staticmethod
    def nightly_fetch_agendas():
        departments = Department.objects.all()
        for department in departments:
            fetch_agendas(department.id)
        pass

    @staticmethod
    def nightly_convert_pdf_to_text():
        agendas = Agenda.objects.filter(agenda_text="") | Agenda.objects.filter(agenda_text=None)
        for agenda in agendas:
            convert_pdf_to_text(agenda.id)
        pass

    @staticmethod
    def nightly_generate_highlights():
        agendas = Agenda.objects.all()
        for agenda in agendas:
            generate_highlights(agenda.id)
