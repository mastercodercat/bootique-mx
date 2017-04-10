from django.http import HttpResponseForbidden

from common.helpers import *


def inspection_readable_required(view_func):
    def _wrapped_view_func(request, *args, **kwargs):
        if can_read_inspection(request.user):
            return view_func(request, *args, **kwargs)
        else:
            return HttpResponseForbidden()
    return _wrapped_view_func

def inspection_writable_required(view_func):
    def _wrapped_view_func(request, *args, **kwargs):
        if can_write_inspection(request.user):
            return view_func(request, *args, **kwargs)
        else:
            return HttpResponseForbidden()
    return _wrapped_view_func

def gantt_readable_required(view_func):
    def _wrapped_view_func(request, *args, **kwargs):
        if can_read_gantt(request.user):
            return view_func(request, *args, **kwargs)
        else:
            return HttpResponseForbidden()
    return _wrapped_view_func

def gantt_writable_required(view_func):
    def _wrapped_view_func(request, *args, **kwargs):
        if can_write_gantt(request.user):
            return view_func(request, *args, **kwargs)
        else:
            return HttpResponseForbidden()
    return _wrapped_view_func
