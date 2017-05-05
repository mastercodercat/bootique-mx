from django import template

from common.helpers import *


register = template.Library()

@register.filter(name='timestamp')
def timestamp(date):
    return totimestamp(date)
