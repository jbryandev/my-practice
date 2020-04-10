import re
from django import template
from django.template.defaultfilters import stringfilter
from django.utils.html import strip_tags
from ..models import Highlight, Agenda

register = template.Library()

@register.filter
@stringfilter
def highlight(text, agenda_id):
    agenda = Agenda.objects.get(pk=agenda_id)
    highlights = Highlight.objects.filter(agenda=agenda)
    add_length = 0

    for hl in highlights:
        hl_text = text[hl.start + add_length:hl.end + add_length]
        hl_marked = '<div id="{}" style="background-color: #FFFF00">{}</div>'.format(hl.id, hl_text)
        begin = text[:hl.start + add_length]
        middle = hl_marked
        end = text[hl.end + add_length:]
        text = begin + middle + end
        add_length += len(hl_marked) - len(hl_text)

    return text

@register.filter
@stringfilter
def hl_slice(agenda_text, highlight):
    """
    Returns the agenda text, sliced based on the highlight range.
    """
    try:
        new_text = strip_tags(agenda_text[highlight.start:highlight.end])
        return new_text

    except (ValueError, TypeError):
        return highlight  # Fail silently.

register.filter(highlight)
