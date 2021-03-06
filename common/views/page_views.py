from django.shortcuts import render, redirect

from common.helpers import *


def index_redirect(request):
    if request.user.is_authenticated():
        if can_read_gantt(request.user):
            return redirect('routeplanning:view_current_published_gantt')
        # elif can_read_inspection(request.user):
        #     return redirect('home:overview')
        else:
            return render(request, 'home-empty.html')
    else:
        return redirect('account_login')