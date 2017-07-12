from django.shortcuts import render, redirect
from django.http import Http404

from common.helpers import *


def index_redirect(request):
    if request.user.is_authenticated():
        if can_read_gantt(request.user):
            return redirect('routeplanning:view_gantt')
        # elif can_read_inspection(request.user):
        #     return redirect('home:overview')
        else:
            return render(request, 'no-permissions.html')
    else:
        return redirect('account_login')
