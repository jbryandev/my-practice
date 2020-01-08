""" Task Module for Celery """
from celery import shared_task
from .models import Agenda
from .modules import pdf2text

@shared_task
def convert_agenda_pdf(agenda_id):
    """ Celery task to convert PDF into text """
    print("convert_agenda_pdf() called with agenda_id: " + str(agenda_id))
    agenda = Agenda.objects.get(pk=agenda_id)
    agenda_url = agenda.agenda_url
    agenda.agenda_text = pdf2text.convert_pdf(agenda_url)
    agenda.save()

    return "PDF conversion via celery task complete!"
