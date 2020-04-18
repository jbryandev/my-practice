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
def hl_slice(agenda_text, hl):
    """
    Returns the highlighted portion of the agenda text.
    """
    try:
        hl_text = strip_tags(agenda_text[hl.start:hl.end])
        return hl_text
    except (ValueError, TypeError):
        return hl  # Fail silently.

@register.filter
def order_by(queryset, args):
    args = [x.strip() for x in args.split(',')]
    return queryset.order_by(*args)

register.filter(highlight)
register.filter(order_by)
