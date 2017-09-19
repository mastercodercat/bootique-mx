from datetime import timedelta, datetime
import json
import dateutil.parser
import random
import os
import csv
from django.core import serializers
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseForbidden
from django.middleware import csrf
from django.db.models import Q, ProtectedError, Max
from django.conf import settings
from django.urls import reverse
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.response import Response

from routeplanning.models import *
from routeplanning.forms import *
from common.helpers import *
from common.decorators import *


def gantt_page_context(request, read_only):
    if request.GET.get('mode'):
        mode = request.GET.get('mode')
    elif 'mode' in request.session:
        mode = request.session['mode']
    else:
        mode = '4'

    start_tmstmp = int(request.GET.get('start')) if request.GET.get('start') else 0
    end_tmstmp = int(request.GET.get('end')) if request.GET.get('end') else 0
    if not(start_tmstmp or end_tmstmp):
        start_tmstmp = request.session['start_tmstmp'] \
            if 'start_tmstmp' in request.session \
            else None

    tails = Tail.objects.all()
    lines = Line.objects.order_by('name').all()

    days_options = { '1': 1, '2': 1, '3': 1, '4': 1, '5': 3, '6': 7, }          # Date mark count
    hours_options = { '1': 3, '2': 6, '3': 12, '4': 24, '5': 24, '6': 6, }      # Hours mark count
    units_per_hour_options = { '1': 4, '2': 2, '3': 1, '4': 1, '5': 1, '6': 0.25, }

    days = days_options[mode]

    hours = hours_options[mode]
    units_per_hour = units_per_hour_options[mode]

    if not start_tmstmp:
        if end_tmstmp:
            start_tmstmp = int(end_tmstmp) - 14 * 24 * 3600
        else:
            start_time = datetime_now_utc()
            start_time = start_time.replace(hour=0, minute=0, second=0, microsecond=0)
            start_tmstmp = totimestamp(start_time)

    big_unit_colspan = units_per_hour * hours if units_per_hour > 1 else hours
    big_unit_count = 14 * (24 / hours) if days == 1 else 14
    table_length_in_secs = 14 * 24 * 3600

    return {
        'tails': tails,
        'lines': lines,
        'big_units': big_unit_count,
        'small_units': big_unit_colspan * big_unit_count,
        'days': days,
        'hours': hours,
        'big_unit_colspan': big_unit_colspan,
        'units_per_hour': units_per_hour,
        'mode': mode,
        'start_tmstmp': start_tmstmp,
        'end_tmstmp': end_tmstmp,
        'start_param_exists': 'true' if request.GET.get('start') or 'start_tmstmp' in request.session else 'false',
        'end_param_exists': 'true' if request.GET.get('end') else 'false',
        'prev_start_tmstmp': int(start_tmstmp) - table_length_in_secs,
        'next_start_tmstmp': int(start_tmstmp) + table_length_in_secs,
        'csrf_token': csrf.get_token(request),
        'window_at_end': request.GET.get('window_at_end') or 0,
        'revisions': Revision.objects.order_by('-published_datetime'),
        'read_only': read_only,
    }


def update_session(request, context_data):
    request.session['mode'] = context_data['mode']
    request.session['start_tmstmp'] = context_data['start_tmstmp']


@login_required
@gantt_readable_required
def index(request):
    context = gantt_page_context(request, not can_write_gantt(request.user))
    context['page'] = 'routeplanning:index'
    update_session(request, context)
    return render(request, 'gantt.html', context)


@login_required
@gantt_readable_required
def view_current_published_gantt(request):
    context = gantt_page_context(request, True)
    context['page'] = 'routeplanning:view_current_published_gantt'
    update_session(request, context)
    return render(request, 'gantt.html', context)


@login_required
@gantt_writable_required
def add_tail(request):
    form = TailForm(request.POST or None)
    action_after_save = request.POST.get('action_after_save')

    if request.method == 'POST':
        if form.is_valid():
            tail = form.save()

            if action_after_save == 'save-and-continue':
                return redirect('routeplanning:edit_tail', tail_id=tail.id)
            elif action_after_save == 'save':
                return redirect('routeplanning:index')
            elif action_after_save == 'save-and-add-another':
                form = TailForm()

    tails = Tail.objects.all()
    context = {
        'form': form,
        'title': 'Add Tail',
        'tails': tails,
        'csrf_token': csrf.get_token(request),
    }
    return render(request, 'tail.html', context)


@login_required
@gantt_readable_required
def edit_tail(request, tail_id=None):
    tail = get_object_or_404(Tail, pk=tail_id)

    form = TailForm(request.POST or None, instance=tail)
    action_after_save = request.POST.get('action_after_save')

    if request.method == 'POST':
        if not can_write_gantt(request.user):
            return HttpResponseForbidden()
        if form.is_valid():
            tail = form.save()

            if action_after_save == 'save-and-add-another':
                return redirect('routeplanning:add_tail')
            elif action_after_save == 'save':
                return redirect('routeplanning:index')
            elif action_after_save == 'save-and-add-another':
                form = LineForm()

    tails = Tail.objects.all()
    context = {
        'form': form,
        'title': 'Edit Tail ' + tail.number,
        'tails': tails,
        'csrf_token': csrf.get_token(request),
    }
    return render(request, 'tail.html', context)


@login_required
@gantt_writable_required
def coming_due(request, tail_id=None, revision_id=None):
    tail = Tail.objects.get(pk=tail_id)

    context = {
        'tail': tail,
        'tails': [],
        'revision_id': revision_id if revision_id else 0,
        'csrf_token': csrf.get_token(request),
    }
    return render(request, 'comingdue.html', context)


@login_required
@gantt_writable_required
def add_line(request):
    form = LineForm(request.POST or None)
    action_after_save = request.POST.get('action_after_save')

    if request.method == 'POST':
        if form.is_valid():
            line = Line(name=form.cleaned_data['name'])    
            line.save()

            for i in range(1, 12):
                entered_line_part_number = form.cleaned_data['part' + str(i)]
                if entered_line_part_number:
                    line_part = LinePart(number=entered_line_part_number, line=line)    
                    line_part.save()
                else:
                    break

            if action_after_save == 'save-and-continue':
                return redirect('routeplanning:edit_line', line_id=line.id)
            elif action_after_save == 'save-and-add-another':
                form = LineForm()
            elif action_after_save == 'save':
                return redirect('routeplanning:index')

    lines = Line.objects.all()
    context = {
        'form': form,
        'title': 'Add Line',
        'lines': lines,
        'csrf_token': csrf.get_token(request),
    }
    return render(request, 'line.html', context)


@login_required
@gantt_readable_required
def edit_line(request, line_id=None):
    line = get_object_or_404(Line, pk=line_id)

    initialData = {
        'name': line.name,
    }
    for i, line_part in enumerate(line.linepart_set.all()):
        initialData['part' + str(i)] = line_part.number

    form = LineForm(request.POST or initialData)
    action_after_save = request.POST.get('action_after_save')

    if request.method == 'POST':
        if not can_write_gantt(request.user):
            return HttpResponseForbidden()
        if form.is_valid():
            if line.name != form.cleaned_data['name']:
                line.name = form.cleaned_data['name']
                line.save()

            line.linepart_set.all().delete()

            for i in range(1, 12):
                entered_line_part_number = form.cleaned_data['part' + str(i)]
                if entered_line_part_number:
                    line_part = LinePart(number=entered_line_part_number, line=line)    
                    line_part.save()
                else:
                    break

            if action_after_save == 'save-and-add-another':
                return redirect('routeplanning:add_line')
            elif action_after_save == 'save':
                return redirect('routeplanning:index')
            elif action_after_save == 'save-and-add-another':
                form = LineForm()

    lines = Line.objects.all()
    context = {
        'form': form,
        'title': 'Edit Line ' + line.name,
        'lines': lines,
        'csrf_token': csrf.get_token(request),
    }
    return render(request, 'line.html', context)


@login_required
@gantt_readable_required
def flights(request):
    flights = []

    context = {
        'flights': flights,
        'csrf_token': csrf.get_token(request),
    }
    return render(request, 'flights.html', context)


@login_required
@gantt_writable_required
def add_flight(request):
    form = FlightForm(request.POST or None)
    if request.method == 'POST':
        if form.is_valid():
            flight = form.save()
            return redirect('routeplanning:edit_flight', flight_id=flight.id)

    context = {
        'form': form,
        'title': 'Add Flight',
    }
    return render(request, 'flight.html', context)


@login_required
@gantt_writable_required
def edit_flight(request, flight_id=None):
    flight = get_object_or_404(Flight, pk=flight_id)
    form = FlightForm(request.POST or None, instance=flight)
    if request.method == 'POST':
        if form.is_valid():
            updated_flight = form.save()
            updated_flight.update_assignment_datetimes()

    context = {
        'form': form,
        'title': 'Edit Flight',
    }
    return render(request, 'flight.html', context)


@login_required
@gantt_writable_required
def delete_flights(request):
    if request.method == 'POST':
        ids_string = request.POST.get('flight_ids')
        ids = ids_string.split(',')
        for id in ids:
            try:
                Flight.objects.filter(pk=id).delete()
            except ProtectedError:
                pass
    return redirect('routeplanning:flights')
