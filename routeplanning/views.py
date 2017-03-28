from datetime import timedelta, datetime
import json
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, JsonResponse

from routeplanning.models import *
from routeplanning.forms import *
from home.helpers import datetime_now_utc


@login_required
def index(request):
    mode = request.GET.get('mode') if request.GET.get('mode') else '1'
    start_tmstmp = request.GET.get('start')
    end_tmstmp = request.GET.get('end')

    tails = Tail.objects.all()
    lines = Line.objects.all()

    days_options = { '1': 1, '2': 1, '3': 1, '4': 1, '5': 3, '6': 7, }
    hours_options = { '1': 3, '2': 6, '3': 12, '4': 24, '5': 24, '6': 24, }
    units_per_hour_options = { '1': 4, '2': 2, '3': 1, '4': 1, '5': 1, '6': 1, }

    days = days_options[mode]
    hours = hours_options[mode]
    units_per_hour = units_per_hour_options[mode]

    if start_tmstmp:
        start_time = datetime.fromtimestamp(float(start_tmstmp))
    else:
        start_time = datetime_now_utc()
        start_time.replace(hour=0, minute=0, second=0, microsecond=0)
        start_tmstmp = int((start_time.replace(tzinfo=None) - datetime(1970, 1, 1)).total_seconds())

    if start_tmstmp and end_tmstmp:
        end_time = datetime.fromtimestamp(float(end_tmstmp))
        diff_days = int((end_time - start_time).total_seconds() / 3600)
        days = diff_days if days > diff_days else days
        days = 1 if days < 1 else days

    end_time = start_time + timedelta(days=days)
    end_tmstmp = int((end_time.replace(tzinfo=None) - datetime(1970, 1, 1)).total_seconds())

    if units_per_hour > 1:
        big_units = list()
        small_units = list()
        for d in range(0, hours):
            big_units.append(str(d))
            for h in range(0, units_per_hour):
                small_units.append(str(d) + ':' + str(60 / units_per_hour * h))
    else:
        big_units = list()
        small_units = list()
        for d in range(0, days):
            big_units.append(start_time + timedelta(days=d))
            for h in range(0, hours):
                small_units.append(h)

    context = {
        'tails': tails,
        'lines': lines,
        'big_units': big_units,
        'small_units': small_units,
        'days': days,
        'hours': hours,
        'big_unit_colspan': units_per_hour if units_per_hour > 1 else hours,
        'days': days,
        'units_per_hour': units_per_hour,
        'mode': mode,
        'start_time': start_time,
        'end_time': end_time,
        'start_tmstmp': start_tmstmp,
        'end_tmstmp': end_tmstmp,
    }
    return render(request, 'index_rp.html', context)

@login_required
def add_tail(request):
    form = TailForm(request.POST or None)

    if request.method == 'POST':
        if form.is_valid():
            tail = form.save()

    action_after_save = request.POST.get('action_after_save')

    if action_after_save == 'save-and-continue':
        return redirect('routeplanning:edit_tail', tail_id=tail.id)
    elif action_after_save == 'save-and-add-another':
        form = TailForm()

    if action_after_save == 'save':
        return redirect('routeplanning:index')
    else:
        context = {
            'form': form,
        }
        return render(request, 'tail.html', context)

@login_required
def edit_tail(request, tail_id=None):
    tail = get_object_or_404(Tail, pk=tail_id)

    form = TailForm(request.POST or None, instance=tail)
    if request.method == 'POST':
        if form.is_valid():
            tail = form.save()

    action_after_save = request.POST.get('action_after_save')

    if action_after_save == 'save-and-add-another':
        return redirect('routeplanning:add_tail')
    elif action_after_save == 'save':
        return redirect('routeplanning:index')
    else:
        context = {
            'form': form,
        }
        return render(request, 'tail.html', context)

@login_required
def add_line(request):
    form = LineForm(request.POST or None)
    if request.method == 'POST':
        if form.is_valid():
            line = Line(name=form.cleaned_data['name'])    
            line.save()

            for i in range(1, 12):
                entered_line_part_name = form.cleaned_data['part' + str(i)]
                if entered_line_part_name:
                    line_part = LinePart(name=entered_line_part_name, number=i, line=line)    
                    line_part.save()
                else:
                    break

    action_after_save = request.POST.get('action_after_save')

    if action_after_save == 'save-and-continue':
        return redirect('routeplanning:edit_line', line_id=line.id)
    elif action_after_save == 'save-and-add-another':
        form = LineForm()

    if action_after_save == 'save':
        return redirect('routeplanning:index')
    else:
        context = {
            'form': form,
        }
        return render(request, 'line.html', context)

@login_required
def edit_line(request, line_id=None):
    line = get_object_or_404(Line, pk=line_id)

    initialData = {
        'name': line.name,
    }
    for line_part in line.linepart_set.all():
        initialData['part' + str(line_part.number)] = line_part.name

    form = LineForm(request.POST or initialData)
    if request.method == 'POST':
        if form.is_valid():
            if line.name != form.cleaned_data['name']:
                line.name = form.cleaned_data['name']
                line.save()

            for i in range(1, 12):
                entered_line_part_name = form.cleaned_data['part' + str(i)]
                if entered_line_part_name:
                    try:
                        line_part = line.linepart_set.get(number=i)
                        if line_part.name != entered_line_part_name:
                            line_part.name = entered_line_part_name
                            line_part.save()
                    except:
                        line_part = LinePart(name=entered_line_part_name, number=i, line=line)    
                        line_part.save()
                else:
                    break

    action_after_save = request.POST.get('action_after_save')

    if action_after_save == 'save-and-add-another':
        return redirect('routeplanning:add_line')
    elif action_after_save == 'save':
        return redirect('routeplanning:index')
    else:
        context = {
            'form': form,
        }
        return render(request, 'line.html', context)

@login_required
def api_load_data(request):
    start_date = datetime.fromtimestamp(int(request.GET.get('startdate')))
    end_date = datetime.fromtimestamp(int(request.GET.get('enddate')))
    start_week_day = start_date.weekday()
    end_week_day = end_date.weekday()

    template_data = []
    flights = Flight.objects.all().select_related('line')
    for flight in flights:
        if flight.is_available_on_weekday_period(start_week_day, end_week_day):
            flight_data = {
                'number': flight.number,
                'origin': flight.origin,
                'destination': flight.destination,
                'departure_time': flight.departure_time,
                'arrival_time': flight.arrival_time,
                'weekly_availability': flight.weekly_availability,
                'line_id': flight.line.id,
            }
            template_data.append(flight_data)

    data = {
        'assignments': [],
        'templates': template_data,
    }
    return JsonResponse(data, safe=False)
