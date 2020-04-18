import re
"""
from council.modules.word_search import match_lines
from council.models import Agenda
agenda = Agenda.objects.get(id=127)
words = "Consideration", "CEC, Inc."
match_lines(agenda.agenda_text, words)
"""
def match_lines(string, *search_words):
    """
    This function takes a string and a set of keyphrases to search for.
    If matches are found, this function returns the start and end of the
    paragraph containing the match.
    """
    matches = []
    for i in range(0, len(search_words)):
        for match in re.finditer(search_words[i], string, re.IGNORECASE):
            start_line_break = re.search("".join(reversed("\">")), string[match.start()::-1])
            end_line_break = re.search("</div>", string[match.end():])
            if start_line_break and end_line_break:
                start_para = match.start() - start_line_break.start() + 1
                end_para = match.end() + end_line_break.start()
                matches.append({"start": start_para, "end": end_para})
            else:
                matches.append({"start": match.start(), "end": match.end()})
    return matches
