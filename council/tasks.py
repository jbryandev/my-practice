""" Task Module for Celery """
from datetime import datetime, timedelta
from celery import shared_task
from celery_progress.backend import ProgressRecorder
from django.shortcuts import get_object_or_404
from django.utils.timezone import get_current_timezone
from council.models import Agenda, Department
from council.modules.backend import PDFConverter, set_progress
from council.crawler_router import crawler_router

@shared_task(bind=True)
def convert_to_pdf(self, agenda_id):
    """ Convert agenda to PDF in the background using celery """
    progress_recorder = ProgressRecorder(self)
    set_progress(progress_recorder, 0, 15, "Attempting to connect...")
    agenda = Agenda.objects.get(pk=agenda_id)
    agenda_url = agenda.agenda_url
    pdf = PDFConverter(agenda_url)
    agenda.agenda_text = pdf.convert_pdf(progress_recorder)
    set_progress(progress_recorder, 14, 15, "PDF conversion complete. Saving to database...")
    agenda.save()

    return "PDF conversion complete."

@shared_task(bind=True)
def fetch_agendas(self, dept_id):
    """ Fetch new agendas for a given department via celery """
    progress_recorder = ProgressRecorder(self)
    set_progress(progress_recorder, 0, 15, "Connecting to City website...")
    department = get_object_or_404(Department, pk=dept_id)
    crawler = department.crawler
    crawler.crawl(progress_recorder)

    return "Fetch agendas complete."

@shared_task(bind=True)
def cleanup_old_agendas(self, max_days_old=60):
    """ Delete agendas older than max days old """
    progress_recorder = ProgressRecorder(self)
    set_progress(progress_recorder, 0, 15, "Searching for old agendas...")
    old_agendas = Agenda.objects.filter(date_added__lte=datetime.now(tz=get_current_timezone())-timedelta(days=max_days_old))
    for agenda in old_agendas:
        agenda.delete()
