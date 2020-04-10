from datetime import datetime
from django.utils.timezone import get_current_timezone
from council.models import Highlight, Keyphrase
from council.modules.word_search import match_lines

class Highlighter:

    def __init__(self, agenda, progress_recorder):
        self.agenda = agenda
        self.agenda_text = agenda.agenda_text
        self.progress_recorder = progress_recorder

    def __repr__(self):
        return "{} Agenda Highlighter".format(str(self.agenda))
    
    def highlight(self):
        status = "Generating highlights for {} - {}: {}".format(
            self.agenda.department.agency,
            self.agenda.department,
            self.agenda
        )
        print(status)
        self.progress_recorder.update(0, 4, status)

        if self.agenda_text: # Make sure agenda_text exists
            try:
                self.progress_recorder.update(1, 4, "Loading keyphrases...")
                keyphrases = self.get_keyphrases()
            except:
                print("ERROR: Could not get keyphrases.")
                raise

            try:
                self.progress_recorder.update(2, 4, "Looking for matches...")
                highlights = self.get_highlights(keyphrases)
            except:
                print("ERROR: A problem occurred during the search.")
                raise

            if highlights:
                try:
                    status = "Found {} new highlight(s).".format(len(highlights))
                    print(status)
                    self.progress_recorder.update(3, 4, status)
                except:
                    print("ERROR: Could not save highlights to datbase.")
                    raise
            else:
                status = "Found no new highlights for this agenda."
                print("Found no new matches.")
                self.progress_recorder.update(3, 4, status)

        else:
            status = "Agenda text has not been generated yet. Exiting..."
            self.progress_recorder.update(3, 4, status)

    def highlight_exists(self, start, end):
        agenda_highlights = Highlight.objects.filter(agenda=self.agenda)
        for highlight in agenda_highlights:
            if (highlight.start == start) and (highlight.end == end):
                return True
        return False

    @staticmethod
    def get_keyphrases():
        return Keyphrase.objects.all()

    def get_highlights(self, keyphrases):
        highlights = []
        for keyphrase in keyphrases:
            matches = match_lines(self.agenda_text, keyphrase.phrase)
            if matches:
                for match in matches:
                    if not self.highlight_exists(match.get("start"), match.get("end")):
                        new_highlight = Highlight(
                            start=match.get("start"),
                            end=match.get("end"),
                            date_added=datetime.now(tz=get_current_timezone()),
                            agenda=self.agenda,
                            category=keyphrase.category
                        )
                        new_highlight.save()
                        highlights.append(new_highlight)
        return highlights
