"""
This module generates highlights for agendas based on a
set of keyphrases. It uses Acora to search for the keyphrases
and then saves the corresponding start/end string indices of the
highlight to the database.
"""
from datetime import datetime
from django.utils.timezone import get_current_timezone
from .models import Highlight, Keyphrase
from .modules import word_search as wsearch

def hl_exists(agenda, hl_start, hl_end):
    """
    This function takes an agenda and a highlight range and checks that
    it is not already in the database.
    """
    agenda_highlights = Highlight.objects.filter(agenda=agenda)
    for highlight in agenda_highlights:
        return bool(highlight.hl_start == hl_start and \
            highlight.hl_end == hl_end)

def generate_hl(agenda):
    """
    This function takes an agenda and searches it for keyphrase
    matches. If any are found, they are saved as highlights.
    """
    keyphrases = Keyphrase.objects.all()
    for keyphrase in keyphrases:
        matches = wsearch.match_lines(agenda.agenda_text, keyphrase.kp_text)
        for match in matches:
            if not hl_exists(agenda, match.get("start"), match.get("end")):
                new_hl = Highlight(
                    hl_start=match.get("start"),
                    hl_end=match.get("end"),
                    date_added=datetime.now(tz=get_current_timezone()),
                    agenda=agenda,
                    category=keyphrase.category
                )
                new_hl.save()
