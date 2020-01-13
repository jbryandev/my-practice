""" Task Module for Celery """
from celery import shared_task
from .models import Agenda
from .modules import pdf2text

@shared_task(bind=True)
def convert_agenda_pdf(self, agenda_id):
    """ Celery task to convert PDF into text """
    print("convert_agenda_pdf running")
    agenda = Agenda.objects.get(pk=agenda_id)
    agenda_url = agenda.agenda_url
    #agenda.agenda_text = pdf2text.convert_pdf(self, agenda_url)
    #agenda.save()

    return "PDF conversion via celery task complete!"
