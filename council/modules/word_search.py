"""
This module uses Acora to search for a given keyphrase
and then returns the full paragraph containing the keyphrase
for any matches found.
"""
from acora import AcoraBuilder

def match_lines(string, *keyphrases):
    """
    This function takes a string and a set of keyphrases to search for.
    It uses Acora to search the string for matches. If matches are found,
    this function returns the start and end position of the whole paragraph
    where the match was found in order to provide context for the match.
    """
    builder = AcoraBuilder('\n\n', *keyphrases)
    acora = builder.build()
    matched_pairs = []
    match_start_end = None
    line_start = 0
    matches = False
    for keys, pos in acora.finditer(string):
        if keys in '\n\n':
            if matches:
                print(string[line_start:pos])
                match_start_end = {"start": line_start, "end": pos}
                matched_pairs.append(match_start_end)
                matches = False
            line_start = pos + 1
        else:
            matches = True
    if matches:
        print(string[line_start:])
        match_start_end = {"start": line_start, "end": len(string)}
        matched_pairs.append(match_start_end)

    return matched_pairs
