from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from datetime import timedelta

from home.models import *


@login_required
def index(request):
    return render(request, 'test.html')

@login_required
def overview(request):
    aircrafts = Aircraft.objects.all().select_related('airframe')

    context = {
        'aircrafts': aircrafts,
        'past_due_count': Airframe.past_due_count,
        'threshold_count': Airframe.threshold_count,
        'not_due_count': Airframe.not_due_count,
    }
    return render(request, 'overview.html', context)

@login_required
def aircraft_details(request, reg=''):
    aircraft = get_object_or_404(Aircraft.objects.select_related('airframe'), reg=reg)

    context = {
        'aircraft': aircraft,
    }
    return render(request, 'aircraft_details.html', context)
