from django import template
from django.utils.safestring import mark_safe

from common.helpers import *

register = template.Library()

@register.filter(name='ndigits')
def ndigits_filter(value, digits = 1):
    return ndigits(value, digits)
