from django import template
from django.utils.safestring import mark_safe

from home.helpers import datetime_now_utc

register = template.Library()

@register.filter(name='duestatus')
def duestatus(value):
	delta = value - datetime_now_utc()
	if delta.days < 0:
		result = '<span class="label label-danger">Past Due</span>'
	elif delta.days <= 10:
		result = '<span class="label label-warning">0 - 10 days</span>'
	else:
		result = '<span class="label label-primary">10+ days</span>'
	return mark_safe(result)
