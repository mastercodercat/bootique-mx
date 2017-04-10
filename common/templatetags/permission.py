from django import template

from common import helpers


register = template.Library()

@register.filter(name='can_read_inspection')
def can_read_inspection(user):
    return helpers.can_read_inspection(user)

@register.filter(name='can_write_inspection')
def can_write_inspection(user):
    return helpers.can_write_inspection(user)

@register.filter(name='can_read_gantt')
def can_read_gantt(user):
    return helpers.can_read_gantt(user)

@register.filter(name='can_write_gantt')
def can_write_gantt(user):
    return helpers.can_write_gantt(user)
