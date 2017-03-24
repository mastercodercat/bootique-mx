from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from datetime import timedelta

from home.models import *
from home.forms import *
from home.helpers import is_past_due, is_within_threshold


@login_required
def overview(request):
    aircrafts = Aircraft.objects.all().select_related('airframe')

    past_due_count = 0
    threshold_count = 0
    coming_due_count = 0

    for aircraft in aircrafts:
        if aircraft.next_inspection_due is not None:
            next_due_date = aircraft.next_inspection_due[1]
            if is_past_due(next_due_date):
                past_due_count += 1
            elif is_within_threshold(next_due_date):
                threshold_count += 1
            else:
                coming_due_count += 1

    context = {
        'aircrafts': aircrafts,
        'past_due_count': past_due_count,
        'threshold_count': threshold_count,
        'coming_due_count': coming_due_count,
    }
    return render(request, 'overview.html', context)

@login_required
def aircraft_details(request, reg=''):
    aircraft = get_object_or_404(Aircraft.objects.select_related('airframe'), reg=reg)

    context = {
        'aircraft': aircraft,
    }
    return render(request, 'details.html', context)

@login_required
def aircraft_task_list(request, reg=''):
    aircraft = get_object_or_404(Aircraft.objects.select_related('inspection_program'), reg=reg)

    context = {
        'aircraft': aircraft,
    }
    return render(request, 'task_list.html', context)

@login_required
def aircraft_mels(request, reg=''):
    aircraft = get_object_or_404(Aircraft, reg=reg)

    context = {
        'aircraft': aircraft,
    }
    return render(request, 'mels.html', context)

# maybe temporary
@login_required
def aircraft_assign_program(request, reg=''):
    aircraft = get_object_or_404(Aircraft, reg=reg)
    form = AssignInspectionProgramForm(request.POST or {
        'inspection_program': aircraft.inspection_program
    })
    if request.method == 'POST':
        if form.is_valid():
            inspection_program = form.cleaned_data.get('inspection_program')
            aircraft.inspection_program = inspection_program
            aircraft.save()

    context = {
        'aircraft': aircraft,
        'form': form,
    }
    return render(request, 'assign_inspection_program.html', context)
