import phonenumbers
from django import template

register = template.Library()

@register.filter(name='phonenumber')
def phonenumber(value, country='US'):
   return phonenumbers.parse(value, country)