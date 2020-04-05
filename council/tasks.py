""" Task Module for Celery """
import re, sys
from datetime import datetime, timedelta
from celery import shared_task
from django.shortcuts import get_object_or_404
from django.utils.timezone import get_current_timezone
from council.models import Agenda, Department, Keyphrase
from council.modules.PDFConverter import PDFConverter
from council.modules.CouncilRecorder import CouncilRecorder
from council import CrawlerFactory, highlights

@shared_task(bind=True)
def convert_pdf_to_text(self, agenda_id):
    """ Convert agenda PDF to text in the background using celery """
    try:
        agenda = Agenda.objects.get(pk=agenda_id)
        progress_recorder = CouncilRecorder(self)
        status = "Converting {} - {}: {} PDF to text...".format(
            agenda.department.agency,
            agenda.department,
            agenda
        )
        progress_recorder.update(0, 5, status)
        progress_recorder.update(1, 5, "Downloading PDF file...")
        pdf_converter = PDFConverter(agenda.pdf_link)
        request = pdf_converter.request_pdf()
        file = pdf_converter.read_pdf(request)

        progress_recorder.update(2, 5, "Converting PDF into images...")
        images = pdf_converter.get_images(file)

        progress_recorder.update(3, 5, "Extracting text using OCR...")
        pdf_text = ""
        for image in images:
            processed_image = pdf_converter.process_image(image)
            pdf_text += "{}".format(pdf_converter.extract_text(processed_image))
            match = re.search("adjourn", pdf_text, re.IGNORECASE)
            if match:
                # Stop extracting when "adjorn" text is found (aka the end of the agenda)
                break

        agenda.agenda_text = pdf_text
        progress_recorder.update(4, 5, "Extraction complete. Saving PDF text to database...")
        agenda.save()
        return "PDF conversion complete."
    except:
        # Pass on exception to be handled by calling function
        # This ensures that celery task does not reach completion
        raise

@shared_task(bind=True)
def fetch_agendas(self, dept_id):
    """ Fetch new agendas for a given department via celery """
    try:
        progress_recorder = CouncilRecorder(self)
        department = get_object_or_404(Department, pk=dept_id)
        print("Fetching agendas for {} - {}".format(department.agency, department.department_name))
        crawler = CrawlerFactory.create_crawler(department, progress_recorder)
        new_agendas = crawler.crawl()
        return "Fetch agendas complete.", {"agendas": new_agendas}
    except:
        # Pass on exception to be handled by calling function
        # This ensures that celery task does not reach completion
        raise

@shared_task(bind=True)
def generate_highlights(self, agenda_id):
    """ Searches for and generates new highlights for a given agenda """
    try:
        agenda = get_object_or_404(Agenda, pk=agenda_id)
        progress_recorder = CouncilRecorder(self)
        status = "Generating highlights for {} - {}: {}".format(
            agenda.department.agency, agenda.department, agenda
        )
        progress_recorder.update(1, 4, status)
        keyphrases = Keyphrase.objects.all()
        status = "Searching agenda for keyphrases..."
        progress_recorder.update(2, 4, status)
        if agenda.agenda_text:
            new_highlights = highlights.create_highlights(agenda, keyphrases)
        else:
            new_highlights = []
            status = "Agenda text has not been generated yet. Exiting..."
            progress_recorder.update(3, 4, status)
        return "Generating highlights complete.", {"highlights": new_highlights}
    except:
        # Pass on exception to be handled by calling function
        # This ensures that celery task does not reach completion
        raise

@shared_task(bind=True)
def cleanup_old_agendas(self, max_days_old=30):
    """ Delete agendas older than max days old """
    try:
        progress_recorder = CouncilRecorder(self)
        progress_recorder.update(0, 15, "Searching for old agendas...")
        print("Cutoff date: {}".format(
            datetime.now(tz=get_current_timezone())-timedelta(days=max_days_old)))
        old_agendas = Agenda.objects.filter(
            agenda_date__lte=datetime.now(tz=get_current_timezone())-timedelta(days=max_days_old)
        )
        print("Found {} that are older than the cutoff date.".format(
            len(old_agendas)))
        i = 1
        for agenda in old_agendas:
            print("Deleting agenda {} of {}...".format(i, len(old_agendas)))
            agenda.delete()
            i += 1
        return "Cleanup of old agendas complete."
    except:
        # Pass on exception to be handled by calling function
        # This ensures that celery task does not reach completion
        raise
