from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from datetime import timedelta

from home.models import *
from home.forms import *
from common.helpers import *
from common.decorators import *


@login_required
@inspection_readable_required
def overview(request):
    aircrafts = Aircraft.objects.all().select_related('airframe')

    past_due_count = 0
    threshold_count = 0
    coming_due_count = 0

    # for aircraft in aircrafts:
    #     if aircraft.next_inspection_due is not None:
    #         next_due_date = aircraft.next_inspection_due[1]
    #         if is_past_due(next_due_date):
    #             past_due_count += 1
    #         elif is_within_threshold(next_due_date):
    #             threshold_count += 1
    #         else:
    #             coming_due_count += 1

    context = {
        'aircrafts': aircrafts,
        'past_due_count': past_due_count,
        'threshold_count': threshold_count,
        'coming_due_count': coming_due_count,
    }
    return render(request, 'overview.html', context)

@login_required
@inspection_readable_required
def aircraft_details(request, reg=''):
    aircraft = get_object_or_404(Aircraft.objects.select_related('airframe'), reg=reg)

    context = {
        'aircraft': aircraft,
    }
    return render(request, 'details.html', context)

@login_required
@inspection_readable_required
def aircraft_task_list(request, reg=''):
    aircraft = get_object_or_404(Aircraft.objects.select_related('inspection_program'), reg=reg)
    inspection_program = aircraft.inspection_program
    inspection_tasks = inspection_program.inspection_tasks.all() if inspection_program else []

    context = {
        'aircraft': aircraft,
        'inspection_program': inspection_program,
        'inspection_tasks': inspection_tasks,
    }
    return render(request, 'task_list.html', context)

@login_required
@inspection_readable_required
def aircraft_task(request, reg='', task_id=None):
    aircraft = get_object_or_404(Aircraft.objects.select_related('inspection_program'), reg=reg)
    inspection_task = get_object_or_404(InspectionTask, pk=task_id)

    context = {
        'aircraft': aircraft,
        'inspection_task': inspection_task,
    }
    return render(request, 'task.html', context)

@login_required
@inspection_readable_required
def aircraft_mels(request, reg=''):
    aircraft = get_object_or_404(Aircraft, reg=reg)

    context = {
        'aircraft': aircraft,
    }
    return render(request, 'mels.html', context)

# maybe temporary
@login_required
@inspection_readable_required
def aircraft_assign_program(request, reg=''):
    aircraft = get_object_or_404(Aircraft, reg=reg)

    form = AssignInspectionProgramForm(request.POST or {
        'inspection_program': aircraft.inspection_program
    })
    if request.method == 'POST':
        if not can_write_inspection(request.user):
            return HttpResponseForbidden()
        if form.is_valid():
            inspection_program = form.cleaned_data.get('inspection_program')
            aircraft.inspection_program = inspection_program
            aircraft.save()
            return redirect('home:aircraft_detail', reg=aircraft.reg)

    context = {
        'aircraft': aircraft,
        'form': form,
    }
    return render(request, 'assign_inspection_program.html', context)
