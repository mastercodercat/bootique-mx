from django import template
from django.utils.safestring import mark_safe

register = template.Library()

@register.filter(name='ndigits')
def ndigits(value, digits = 1):
    s = str(value)
    while len(s) < digits:
        s = '0' + s
    return s
