""" Common functions used by the crawlers """
import time
from ..models import Agenda

def agenda_exists(agenda_url):
    """
    This function takes an agenda URL and makes sure that it is not
    already associated with an agenda in the database.
    """
    return bool(Agenda.objects.filter(agenda_url=agenda_url).exists())

def set_progress(progress_recorder, start, end, descr, delay):
    """ This function controls the progress recorder """
    progress_recorder.set_progress(start, end, description=descr)
    time.sleep(delay)
