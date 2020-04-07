"""
This module generates highlights for agendas based on a
set of keyphrases.
"""
from datetime import datetime
from django.utils.timezone import get_current_timezone
from council.models import Highlight, Keyphrase
from council.modules.word_search import match_lines

def highlight_exists(agenda, start, end, category):
    """
    This function takes an agenda and a highlight range and category
    and checks that it is not already in the database.
    """
    agenda_highlights = Highlight.objects.filter(agenda=agenda)
    for highlight in agenda_highlights:
        return bool(highlight.start == start and \
            highlight.end == end and highlight.category == category)

def create_highlights(agenda, keyphrases):
    """
    This function takes an agenda and a set of keyphrase objects and searches
    for matches. If any are found, they are saved as highlights.
    """
    highlights = []
    if agenda.agenda_text: # Make sure agenda_text exists
        for keyphrase in keyphrases:
            matches = match_lines(agenda.agenda_text, keyphrase.phrase)
            if matches:
                print("(Keyphrase: {}) Matches found. ({} - {}: {})".format(
                    keyphrase.phrase,
                    agenda.department.agency,
                    agenda.department,
                    agenda
                ))
                for match in matches:
                    if not highlight_exists(agenda, match.get("start"), match.get("end"), keyphrase.category):
                        new_highlight = Highlight(
                            start=match.get("start"),
                            end=match.get("end"),
                            date_added=datetime.now(tz=get_current_timezone()),
                            agenda=agenda,
                            category=keyphrase.category
                        )
                        new_highlight.save()
                        highlights.append(new_highlight)
    return highlights
        