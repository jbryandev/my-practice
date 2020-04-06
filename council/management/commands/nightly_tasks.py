import sys
from datetime import datetime
from django.utils import timezone
from django.core.management.base import BaseCommand
from council.tasks import fetch_agendas, convert_pdf_to_text, \
    generate_highlights, cleanup_old_agendas
from council.models import Department, Agenda, Highlight
from council.modules import mailer

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
        self.cleanup_agendas()
        self.stdout.write("---Step 5: Send Summary Email---")
        self.send_email_summary()
        self.stdout.write("---COMPLETED COUNCIL-INSIGHTS NIGHTLY TASKS---")

    @staticmethod
    def nightly_fetch_agendas():
        departments = Department.objects.all()
        for department in departments:
            try:
                fetch_agendas(department.id)
            except:
                print("EXCEPTION: {}".format(sys.exc_info()[1]))

    @staticmethod
    def nightly_convert_pdf_to_text():
        agendas = Agenda.objects.filter(agenda_text="") | Agenda.objects.filter(agenda_text=None)
        if agendas:
            for agenda in agendas:
                try:
                    convert_pdf_to_text(agenda.id)
                except:
                    print("EXCEPTION: {}".format(sys.exc_info()[1]))
        else:
            print("No agendas need conversion!")

    @staticmethod
    def nightly_generate_highlights():
        today = datetime.now(tz=timezone.get_current_timezone())
        agendas = Agenda.objects.filter(date_added__date=today.date())
        if agendas:
            for agenda in agendas:
                try:
                    generate_highlights(agenda.id)
                except:
                    print("EXCEPTION: {}".format(sys.exc_info()[1]))
        else:
            print("No agendas added today, so highlights won't be created.")

    @staticmethod
    def cleanup_agendas():
        print("Running cleanup process...")
        try:
            cleanup_old_agendas()
            print("Cleanup process complete.")
        except:
            print("ERROR: Could not clean up old agendas.", sys.exc_info()[1])

    @staticmethod
    def send_email_summary():
        try:
            # Send an email summarizing the operations above
            today = datetime.now(tz=timezone.get_current_timezone())
            agendas = Agenda.objects.filter(date_added__date=today.date())
            highlights = Highlight.objects.filter(date_added__date=today.date())
            if agendas or highlights:
                subject = "Council Insights: Agenda Report for {}".format(today.strftime("%m/%d/%y"))
                text_body = "Council Insights: Agenda Report for {}\n\n".format(today.strftime("%m/%d/%y"))
                html_body = "<h4>Council Insights: Agenda Report for {}<h4>\n".format(today.strftime("%m/%d/%y"))

                # Agendas
                if agendas:
                    text_body += "The following agendas were added:\n"
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

                # Highlights
                if highlights:
                    text_body += "The following highlights were added:\n"
                    html_body += "<p>The following highlights were added:</p>\n<ol>\n"
                    for highlight in highlights:
                        text_body += "{} - {} - {}:\n".format(
                            highlight.agenda.department.agency,
                            highlight.agenda.department,
                            highlight.agenda.agenda_date
                        )
                        text_body += highlight.agenda.agenda_text[highlight.start:highlight.end]
                        html_body += (
                            "<li><a href=\"https://my-practice.herokuapp.com{}\">{} - {} - {}</a></li>\n"
                            .format(
                                highlight.agenda.get_absolute_url(),
                                highlight.agenda.department.agency,
                                highlight.agenda.department,
                                highlight.agenda.agenda_date.strftime("%m/%d/%y")
                            )
                        )
                        html_body += "<p>{}</p>\n".format(highlight.agenda.agenda_text[highlight.start:highlight.end])
                    html_body += "</ol>"
                # Send email
                print("New items were added. Sending email summary...")
                mailer.send(subject, text_body, html_body)
                print("Email sent.")
            else:
                print("Nothing new to report. No summary email will be sent.")
        except:
            print("ERROR: Could not send summary email.", sys.exc_info()[1])
