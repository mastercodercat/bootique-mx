from datetime import timedelta, datetime
import json
import dateutil.parser
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, JsonResponse
from django.middleware import csrf

from routeplanning.models import *
from routeplanning.forms import *
from home.helpers import datetime_now_utc, utc, totimestamp


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
        start_time = datetime.fromtimestamp(float(start_tmstmp), tz=utc)
    else:
        start_time = datetime_now_utc()
        start_time.replace(hour=0, minute=0, second=0, microsecond=0)
        start_tmstmp = totimestamp(start_time)

    if start_tmstmp and end_tmstmp:
        end_time = datetime.fromtimestamp(float(end_tmstmp), tz=utc)
        diff_days = int((end_time - start_time).total_seconds() / 3600)
        days = diff_days if days > diff_days else days
        days = 1 if days < 1 else days

    end_time = start_time + timedelta(days=days)
    end_tmstmp = totimestamp(end_time)

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
            big_units.append(totimestamp(start_time + timedelta(days=d)))
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
        'start_tmstmp': start_tmstmp,
        'end_tmstmp': end_tmstmp,
        'csrf_token': csrf.get_token(request),
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
            'title': 'Add Tail',
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
            'title': 'Edit Tail ' + tail.number,
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
            'title': 'Add Line',
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
            'title': 'Edit Line ' + line.name,
        }
        return render(request, 'line.html', context)

@login_required
def flights(request):
    flights = Flight.objects.all()

    context = {
        'flights': flights,
    }
    return render(request, 'flights.html', context)

@login_required
def add_flight(request):
    form = FlightForm(request.POST or None)
    if request.method == 'POST':
        if form.is_valid():
            form.save()
            form = FlightForm()

    context = {
        'form': form,
    }
    return render(request, 'flight.html', context)

@login_required
def api_load_data(request):
    start_time = datetime.fromtimestamp(int(request.GET.get('startdate')), tz=utc)
    end_time = datetime.fromtimestamp(int(request.GET.get('enddate')), tz=utc)
    start_week_day = start_time.weekday()
    end_week_day = end_time.weekday()

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

    assignments_data = []
    assignments = Assignment.objects.select_related('flight', 'tail').all()
    for assignment in assignments:
        if assignment.start_time >= start_time and assignment.end_time <= end_time:
            assignment_data = {
                'flight_number': assignment.flight_number,
                'start_time': assignment.start_time,
                'end_time': assignment.end_time,
                'status': assignment.status,
                'tail': assignment.tail.number,
            }
            assignments_data.append(assignment_data)

    data = {
        'assignments': assignments_data,
        'templates': template_data,
    }
    return JsonResponse(data, safe=False)

@login_required
def api_assign_flight(request):
    result = {
        'success': False,
    }

    try:
        flight_number = request.POST.get('flight_number')
        tail_number = request.POST.get('tail')
        departure_time = dateutil.parser.parse(request.POST.get('departure_time'))
    except:
        result['error'] = 'Invalid parameters'
        return JsonResponse(result, safe=False, status=400)

    try:
        tail = Tail.objects.get(number=tail_number)
        if Assignment.is_duplicated(tail, departure_time):
            result['error'] = 'Duplicated assignment'
            return JsonResponse(result, safe=False)

        flight = Flight.objects.get(number=flight_number)

        assignment = Assignment(
            flight_number=flight.number,
            start_time=departure_time,
            end_time=departure_time + timedelta(seconds=flight.length),
            status=1,
            flight=flight,
            tail=tail
        )
        assignment.save()
    except Exception as e:
        result['error'] = str(e)
        return JsonResponse(result, safe=False, status=500)

    result['success'] = True
    return JsonResponse(result, safe=False)
