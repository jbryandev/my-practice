""" Task Module for Celery """
from datetime import datetime, timedelta
from celery import shared_task
from django.shortcuts import get_object_or_404
from django.utils.timezone import get_current_timezone
from council.models import Agenda, Department, Keyphrase
from council.modules.CrawlerFactory import CrawlerFactory
from council.modules.PDFConverterFactory import PDFConverterFactory
from council.modules.CouncilRecorder import CouncilRecorder
from council.modules.Highlighter import Highlighter

@shared_task(bind=True)
def fetch_agendas(self, dept_id):
    """ Fetch new agendas for a given department via celery """
    try:
        progress_recorder = CouncilRecorder(self)
        department = get_object_or_404(Department, pk=dept_id)
        crawler_factory = CrawlerFactory(department, progress_recorder)
        crawler = crawler_factory.create_crawler()
        crawler.crawl()
        return "Fetch agendas complete."
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
        converter_factory = PDFConverterFactory(agenda, progress_recorder)
        converter = converter_factory.create_converter()
        # return converter
        converter.convert()
        return "PDF conversion complete."
    except:
        # Pass on exception to be handled by calling function
        # This ensures that celery task does not reach completion
        raise

@shared_task(bind=True)
def generate_highlights(self, agenda_id):
    """ Searches for and generates new highlights for a given agenda """
    try:
        progress_recorder = CouncilRecorder(self)
        agenda = get_object_or_404(Agenda, pk=agenda_id)
        highlighter = Highlighter(agenda, progress_recorder)
        highlighter.highlight()
        return "Highlight process complete."
    except:
        # Pass on exception to be handled by calling function
        # This ensures that celery task does not reach completion
        raise

@shared_task(bind=True)
def cleanup_old_agendas(self, max_days_old=31):
    """ Delete agendas older than max days old """
    try:
        progress_recorder = CouncilRecorder(self)
        progress_recorder.update(0, 15, "Searching for old agendas...")
        cutoff_date = datetime.now(tz=get_current_timezone())-timedelta(days=max_days_old)
        print("Cutoff date: {}".format(cutoff_date.strftime("%m/%d/%y")))
        old_agendas = Agenda.objects.filter(agenda_date__lt=cutoff_date)
        print("Found {} that are older than the cutoff date.".format(
            len(old_agendas)))
        for agenda in old_agendas:
            print("Deleting agenda: {} - {} - {}...".format(
                agenda.department.agency,
                agenda.department,
                agenda
            ))
            agenda.delete()
    except:
        # Pass on exception to be handled by calling function
        # This ensures that celery task does not reach completion
        raise
