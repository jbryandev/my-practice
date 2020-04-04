""" Task Module for Celery """
import re
from datetime import datetime, timedelta
from celery import shared_task
from django.shortcuts import get_object_or_404
from django.utils.timezone import get_current_timezone
from council.models import Agenda, Department
from council.modules.PDFConverter import PDFConverter
from council.modules.CouncilRecorder import CouncilRecorder
from council import CrawlerFactory

@shared_task(bind=True)
def convert_to_pdf(self, agenda_id):
    """ Convert agenda to PDF in the background using celery """
    progress_recorder = CouncilRecorder(self)
    progress_recorder.update(0, 4, "Downloading PDF file...")
    agenda = Agenda.objects.get(pk=agenda_id)
    pdf_converter = PDFConverter(agenda.pdf_link)
    request = pdf_converter.request_pdf()
    file = pdf_converter.read_pdf(request)

    progress_recorder.update(1, 4, "Converting PDF into images...")
    images = pdf_converter.get_images(file)

    progress_recorder.update(2, 4, "Extracting text using OCR...")
    pdf_text = ""
    for image in images:
        processed_image = pdf_converter.process_image(image)
        pdf_text += "{}".format(pdf_converter.extract_text(processed_image))
        match = re.search("adjourn", pdf_text, re.IGNORECASE)
        if match:
            # Stop extracting when "adjorn" text is found (aka the end of the agenda)
            break

    agenda.agenda_text = pdf_text
    progress_recorder.update(3, 4, "Extraction complete. Saving PDF text to database...")
    agenda.save()
    return "PDF conversion complete."

@shared_task(bind=True)
def fetch_agendas(self, dept_id):
    """ Fetch new agendas for a given department via celery """
    department = get_object_or_404(Department, pk=dept_id)
    print("Fetching agendas for {} - {}".format(department.agency, department.department_name))
    progress_recorder = CouncilRecorder(self)
    crawler = CrawlerFactory.create_crawler(department, progress_recorder)
    crawler.crawl()
    return "Fetch agendas complete."

@shared_task(bind=True)
def cleanup_old_agendas(self, max_days_old=30):
    """ Delete agendas older than max days old """
    progress_recorder = CouncilRecorder(self)
    progress_recorder.update(0, 15, "Searching for old agendas...")
    print("Cutoff date: {}".format(
        datetime.now(tz=get_current_timezone())-timedelta(days=max_days_old)))
    old_agendas = Agenda.objects.filter(
        agenda_date__lte=datetime.now(tz=get_current_timezone())-timedelta(days=max_days_old)
    )
    print("Found {} that are older than the cutoff date. Preparing to delete...".format(
        len(old_agendas)))
    i = 1
    for agenda in old_agendas:
        print("Deleting agenda {} of {}...".format(i, len(old_agendas)))
        agenda.delete()
        i += 1
    return "Cleanup of old agendas complete."
