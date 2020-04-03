""" Task Module for Celery """
from datetime import datetime, timedelta
from celery import shared_task
from celery_progress.backend import ProgressRecorder
from django.shortcuts import get_object_or_404
from django.utils.timezone import get_current_timezone
from council.models import Agenda, Department
from council.modules.backend import PDFConverter, set_progress
from council import CrawlerFactory
from council.modules.backend import CouncilRecorder

@shared_task(bind=True)
def convert_to_pdf(self, agenda_id):
    """ Convert agenda to PDF in the background using celery """
    progress_recorder = ProgressRecorder(self)
    set_progress(progress_recorder, 0, 15, "Attempting to connect...")
    agenda = Agenda.objects.get(pk=agenda_id)
    agenda_url = agenda.agenda_url
    pdf = PDFConverter(agenda_url)
    agenda.agenda_text = pdf.convert_pdf()
    set_progress(progress_recorder, 14, 15, "PDF conversion complete. Saving to database...", 2)
    agenda.save()
    return "PDF conversion complete."

@shared_task(bind=True)
def fetch_agendas(self, dept_id):
    """ Fetch new agendas for a given department via celery """
    department = get_object_or_404(Department, pk=dept_id)
    print("Fetching agendas for {} - {}".format(department.agency, department.department_name))
    progress_recorder = CouncilRecorder(self)
    status = "Connecting to City website..."
    progress_recorder.update(0, 1, status)
    crawler = CrawlerFactory.create_crawler(department, progress_recorder)
    crawler.crawl()
    return "Fetch agendas complete."

@shared_task(bind=True)
def cleanup_old_agendas(self, max_days_old=30):
    """ Delete agendas older than max days old """
    progress_recorder = ProgressRecorder(self)
    set_progress(progress_recorder, 0, 15, "Searching for old agendas...")
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