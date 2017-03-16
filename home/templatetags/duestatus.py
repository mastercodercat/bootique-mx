from django import template
from django.utils.safestring import mark_safe

from home.helpers import is_past_due, is_within_threshold, is_coming_due

register = template.Library()

@register.filter(name='duestatus')
def duestatus(value):
	if is_past_due(value):
		result = '<span class="label label-danger">Past Due</span>'
	elif is_within_threshold(value):
		result = '<span class="label label-warning">0 - 10 days</span>'
	else:
		result = '<span class="label label-primary">10+ days</span>'
	return mark_safe(result)
