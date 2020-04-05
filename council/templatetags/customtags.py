import re
from django import template
from django.template.defaultfilters import stringfilter
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
        hl_marked = '<mark>' + hl_text + '</mark>'
        begin = text[:hl.start + add_length]
        middle = hl_marked
        end = text[hl.end + add_length:]
        text = begin + middle + end
        add_length += len(hl_marked) - len(hl_text)

    return text

register.filter(highlight)
