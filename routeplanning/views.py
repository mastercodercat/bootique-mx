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
    tails = Tail.objects.all()
    lines = Line.objects.all()

    days = 3
    hours = 24
    units_per_hour = 1

    start_time = datetime_now_utc() - timedelta(days=5)
    start_time.replace(hour=0, minute=0, second=0, microsecond=0)

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
            }
            template_data.append(flight_data)

    data = {
        'assignments': [],
        'templates': template_data,
    }
    return JsonResponse(data, safe=False)
