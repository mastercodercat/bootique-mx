from django.shortcuts import render, redirect
from django.http import Http404

from common.helpers import *


def index_redirect(request):
    if request.user.is_authenticated():
        if can_read_inspection(request.user):
            return redirect('home:overview')
        elif can_read_gantt(request.user):
            return redirect('routeplanning:index')
        else:
            raise Http404('You do not have permission for any page.')
    else:
        return redirect('account_login')
