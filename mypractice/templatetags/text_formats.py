""" Template tags for various text formatting """
from django import template
register = template.Library()

@register.filter()
def currency(value):
    """ Converts specified value to currency """
    return '${:,}'.format(value)

@register.filter()
def phone(value):
    """ Display 10-digit number as phone number"""
    return '({}) {}-{}'.format(value[0:3], value[3:6], value[6:])
