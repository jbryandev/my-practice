import os
from datetime import datetime
from django.utils import timezone
from django.core.management.base import BaseCommand
from council.tasks import fetch_agendas
from council.models import Department, Agenda
from council.modules import mailer

# Command to run: python manage.py fetch_agendas_nightly
class Command(BaseCommand):
    help = 'Runs fetch agendas command nightly to keep agendas up-to-date'

    def handle(self, *args, **options):
        self.stdout.write("---RUNNING FETCH AGENDAS NIGHTLY TASK---")
        departments = Department.objects.all()
        starting_agenda_count = Agenda.objects.count()
        for department in departments:
            fetch_agendas(department.id)
        self.stdout.write("Fetch agendas complete.")
        ending_agenda_count = Agenda.objects.count()
        if ending_agenda_count > starting_agenda_count:
            # Found new agendas
            new_count = ending_agenda_count - starting_agenda_count
            self.stdout.write(f'Found {new_count} new agendas. Sending email summary...')
            self.send_email(new_count)
        else:
            self.stdout.write(f'No new agendas were found.')
        self.stdout.write("---COMPLETED FETCH AGENDAS NIGHTLY TASK---")

    @staticmethod
    def send_email(new_count):
        print("Preparing email...")
        today = datetime.now(tz=timezone.get_current_timezone())
        agendas = Agenda.objects.filter(date_added__date=today.date())
        subject = "Council Insights: Agenda Report for {}".format(today.strftime("%m/%d/%y"))
        text_body = "Found {} new agendas.\n\nAgenda Summary:\n".format(new_count)
        html_body = "<p>Found {} new agendas.</p>\n".format(new_count)
        html_body += (
            "<p>Agenda Summary:</p>\n"
            "<ol>\n"
        )
        for agenda in agendas:
            text_body += "{} - {}: {}\n".format(
                agenda.department.agency,
                agenda.department,
                agenda.agenda_date
            )
            html_body += (
                "<li><a href=\"https://my-practice.herokuapp.com{}\">{} - {}: {}</a></li>\n"
                .format(
                    agenda.get_absolute_url(),
                    agenda.department.agency,
                    agenda.department,
                    agenda.agenda_date.strftime("%m/%d/%y")
                )
            )
        html_body += "</ol>"

        mailer.send(subject, text_body, html_body)
