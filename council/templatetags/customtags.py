from django import template
from django.template.defaultfilters import stringfilter
from ..models import Highlight, Agenda

register = template.Library()

@register.filter
@stringfilter
def highlight(value, agenda_id):
    agenda = Agenda.objects.get(pk=agenda_id)
    highlights = Highlight.objects.filter(agenda=agenda)
    for hl in highlights:
        begin = value[:hl.hl_start] + '<mark>'
        middle = value[hl.hl_start:hl.hl_end]
        end = '</mark>' + value[hl.hl_end:]
        value = begin + middle + end
    return value

register.filter(highlight)