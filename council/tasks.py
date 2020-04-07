""" Task Module for Celery """
from datetime import datetime, timedelta
from celery import shared_task
from django.shortcuts import get_object_or_404
from django.utils.timezone import get_current_timezone
from council.models import Agenda, Department, Keyphrase
from council.modules.PDFConverter import PDFConverter
from council.modules.CouncilRecorder import CouncilRecorder
from council import CrawlerFactory, highlights

@shared_task(bind=True)
def fetch_agendas(self, dept_id):
    """ Fetch new agendas for a given department via celery """
    try:
        progress_recorder = CouncilRecorder(self)
        department = get_object_or_404(Department, pk=dept_id)
        crawler = CrawlerFactory.create_crawler(department, progress_recorder)
        new_agendas = crawler.crawl()
        return "Fetch agendas complete.", {"agendas": new_agendas}
    except:
        # Pass on exception to be handled by calling function
        # This ensures that celery task does not reach completion
        raise

@shared_task(bind=True)
def convert_pdf_to_text(self, agenda_id):
    """ Convert agenda PDF to text in the background using celery """
    try:
        progress_recorder = CouncilRecorder(self)
        agenda = get_object_or_404(Agenda, pk=agenda_id)
        converter = PDFConverter(agenda, progress_recorder)
        converted_agenda = converter.convert_pdf()
        return "PDF conversion complete.", {"agenda": converted_agenda}
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
        cutoff_date = datetime.now(tz=get_current_timezone())-timedelta(days=max_days_old)
        print("Cutoff date: {}".format(cutoff_date.strftime("%m/%d/%y")))
        old_agendas = Agenda.objects.filter(agenda_date__lte=cutoff_date)
        print("Found {} that are older than the cutoff date.".format(
            len(old_agendas)))
        for agenda in old_agendas:
            print("Deleting agenda: {} - {} - {}...".format(
                agenda.department.agency,
                agenda.department,
                agenda
            ))
            agenda.delete()
        return "Cleanup of old agendas complete."
    except:
        # Pass on exception to be handled by calling function
        # This ensures that celery task does not reach completion
        raise
