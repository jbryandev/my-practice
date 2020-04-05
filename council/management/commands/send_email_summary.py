from datetime import datetime
from django.utils import timezone
from django.core.management.base import BaseCommand
from council.models import Agenda
from council.modules import mailer

# Command to run: python manage.py send_email_summary
class Command(BaseCommand):
    help = 'Sends an email summary for any agendas added today'

    def handle(self, *args, **options):
        self.stdout.write("---RUNNING EMAIL SUMMARY TASK---")
        today = datetime.now(tz=timezone.get_current_timezone())
        agendas = Agenda.objects.filter(date_added__date=today.date())
        if agendas:
            # Prepare an email
            self.stdout.write(f'Found {len(agendas)} new agendas. Sending summary email...')
            subject = "Council Insights: Agenda Report for {}".format(today.strftime("%m/%d/%y"))
            text_body = "Council Insights: Agenda Report for {}\n\n".format(today.strftime("%m/%d/%y"))
            text_body += "The following agendas were added:\n"
            html_body = "<h4>Council Insights: Agenda Report for {}<h4>\n".format(today.strftime("%m/%d/%y"))
            html_body += "<p>The following agendas were added:</p>\n<ol>\n"

            for agenda in agendas:
                text_body += "{} - {} - {}\n".format(
                    agenda.department.agency,
                    agenda.department,
                    agenda.agenda_date
                )
                html_body += (
                    "<li><a href=\"https://my-practice.herokuapp.com{}\">{} - {} - {}</a></li>\n"
                    .format(
                        agenda.get_absolute_url(),
                        agenda.department.agency,
                        agenda.department,
                        agenda.agenda_date.strftime("%m/%d/%y")
                    )
                )
            html_body += "</ol>"
            mailer.send(subject, text_body, html_body)
        else:
            self.stdout.write("No new agendas found. No summary email will be sent.")
        self.stdout.write("---COMPLETED EMAIL SUMMARY TASK---")
