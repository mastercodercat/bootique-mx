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


@login_required
@gantt_readable_required
def index(request):
    mode = request.GET.get('mode') if request.GET.get('mode') else '4'
    start_tmstmp = request.GET.get('start')
    end_tmstmp = request.GET.get('end')

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

    context = {
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
        'start_param': request.GET.get('start'),
        'end_param': request.GET.get('end'),
        'prev_start_tmstmp': int(start_tmstmp) - table_length_in_secs,
        'next_start_tmstmp': int(start_tmstmp) + table_length_in_secs,
        'csrf_token': csrf.get_token(request),
        'window_at_end': request.GET.get('window_at_end') or 0,
        'revisions': Revision.objects.order_by('-published_datetime'),
    }
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
@api_view(['DELETE'])
def delete_tail(request, tail_id=None):
    result = {
        'success': False,
    }

    try:
        tail = Tail.objects.get(pk=tail_id)
        tail.delete()
        result['success'] = True
    except:
        result['error'] = 'Error occurred while deleting tail'

    return Response(result)

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
@gantt_writable_required
@api_view(['DELETE'])
def delete_line(request, line_id=None):
    result = {
        'success': False,
    }

    try:
        if line_id:
            line = Line.objects.get(pk=line_id)
            line.delete()
            result['success'] = True
        else:
            result['error'] = 'Line id should be specified'
    except:
        result['error'] = 'Error occurred while deleting line'

    return Response(result)

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
@gantt_readable_required
@api_view(['POST'])
def api_flight_get_page(request):
    result = {
        'success': False,
        'draw': 1,
        'recordsTotal': 0,
        'recordsFiltered': 0,
        'data': [],
    }

    order_columns = (
        'id', 'number', 'origin', 'destination',
        'scheduled_out_datetime', 'scheduled_off_datetime', 'scheduled_on_datetime', 'scheduled_in_datetime',
        'estimated_out_datetime', 'estimated_off_datetime', 'estimated_on_datetime', 'estimated_in_datetime',
    )

    try:
        start = int(request.data.get('start'))
        length = int(request.data.get('length'))
        order_dir = request.data.get('order[0][dir]')
        order_column_index = int(request.data.get('order[0][column]'))
        search = request.data.get('search[value]')

        order_column = order_columns[order_column_index]
        if order_dir == 'desc':
            order_column = '-' + order_column

        flights = Flight.objects.all()
        if search:
            flights = flights.filter(
                Q(number__contains=search) |
                Q(origin__icontains=search) |
                Q(destination__icontains=search) |
                Q(scheduled_out_datetime__contains=search) |
                Q(scheduled_in_datetime__contains=search)
            )
        flights = flights.order_by(order_column)
        flights_page = flights[start:(start + length)]
        data = []
        for flight in flights_page:
            flight_edit_link = reverse('routeplanning:edit_flight', kwargs={ 'flight_id': flight.id })
            buttons = '<span style="white-space: nowrap;">'
            buttons += '<a href="' + flight_edit_link + '" class="btn btn-primary btn-xs"><i class="fa fa-fw fa-edit"></i></a> '
            buttons += '<a href="javascript:void();" class="btn-delete-flight btn btn-danger btn-xs"><i class="fa fa-fw fa-trash"></i></a>'
            buttons += '</span>'
            data.append((
                flight.id,
                flight.number,
                flight.origin,
                flight.destination,
                totimestamp(flight.scheduled_out_datetime) if flight.scheduled_out_datetime else '',
                totimestamp(flight.scheduled_off_datetime) if flight.scheduled_off_datetime else '',
                totimestamp(flight.scheduled_on_datetime) if flight.scheduled_on_datetime else '',
                totimestamp(flight.scheduled_in_datetime) if flight.scheduled_in_datetime else '',
                totimestamp(flight.estimated_out_datetime) if flight.estimated_out_datetime else '',
                totimestamp(flight.estimated_off_datetime) if flight.estimated_off_datetime else '',
                totimestamp(flight.estimated_on_datetime) if flight.estimated_on_datetime else '',
                totimestamp(flight.estimated_in_datetime) if flight.estimated_in_datetime else '',
                buttons,
            ))
        result['data'] = data
        result['recordsFiltered'] = flights.count()
        result['recordsTotal'] = Flight.objects.count()

        draw = request.session.get('flights_dt_page_draw', 1)
        draw = draw + 1
        result['draw'] = draw
        request.session['flights_dt_page_draw'] = draw
    except Exception as e:
        result['error'] = str(e)
        return Response(result, status=500)

    result['success'] = True
    return Response(result)

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
            form.save()

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

@login_required
@gantt_readable_required
@api_view(['GET'])
def api_load_data(request):
    start_time = datetime.fromtimestamp(int(request.query_params.get('startdate')), tz=utc)
    end_time = datetime.fromtimestamp(int(request.query_params.get('enddate')), tz=utc)
    assignments_only = request.query_params.get('assignments_only')
    revision_id = request.query_params.get('revision')

    if revision_id and int(revision_id) > 0:
        try:
            revision = Revision.objects.get(pk=revision_id)
        except Revision.DoesNotExist:
            result = {
                'error': 'Revision not found',
            }
            return Response(result, status=400)
    else:
        revision = None

    if not can_write_gantt(request.user):
        if not revision:    # Current draft gantt
            result = {
                'error': 'Not allowed to get draft route plan',
            }
            return Response(result, status=403)
        else:
            ### TODO: This part is not included in test coverage
            latest_published_datetime_row = Revision.objects.all().aggregate(Max('published_datetime'))
            if not latest_published_datetime_row:
                result = {
                    'error': 'No published route plan exists',
                }
                return Response(result, status=403)
            else:
                latest_published_datetime = latest_published_datetime_row['published_datetime__max']
                if revision.published_datetime != latest_published_datetime:
                    result = {
                        'error': 'Not allowed to get route plans other than current published version',
                    }
                    return Response(result, status=403)

    # Date for tails and its last assignment on current revision

    tails_data = []
    tails = Tail.objects.all()
    for tail in tails:
        tail_data = {}
        tail_data['tail'] = {
            'id': tail.id,
            'number': tail.number,
        }
        assignment = tail.get_last_assignment(revision, start_time)
        if assignment:
            tail_data['last_assignment'] = {
                'id': assignment.id,
                'number': assignment.flight_number,
                'start_time': assignment.start_time,
                'end_time': assignment.end_time,
                'status': assignment.status,
                'origin': assignment.flight.origin,
                'destination': assignment.flight.destination,
            }
        else:
            tail_data['last_assignment'] = None
        tails_data.append(tail_data)

    # Data for template flights on Lines

    template_data = []
    if assignments_only != 'true':
        lines = Line.objects.all()
        for line in lines:
            flights = line.flights.filter(
                (Q(scheduled_out_datetime__gte=start_time) & Q(scheduled_out_datetime__lte=end_time)) |
                (Q(scheduled_in_datetime__gte=start_time) & Q(scheduled_in_datetime__lte=end_time)) |
                (Q(scheduled_out_datetime__lte=start_time) & Q(scheduled_in_datetime__gte=end_time))
            )
            for flight in flights:
                flight_data = {
                    'id': flight.id,
                    'number': flight.number,
                    'origin': flight.origin,
                    'destination': flight.destination,
                    'scheduled_out_datetime': flight.scheduled_out_datetime,
                    'scheduled_in_datetime': flight.scheduled_in_datetime,
                    'scheduled_out_datetime': flight.scheduled_out_datetime,
                    'scheduled_in_datetime': flight.scheduled_in_datetime,
                    'scheduled_off_datetime': flight.scheduled_off_datetime,
                    'scheduled_on_datetime': flight.scheduled_on_datetime,
                    'estimated_out_datetime': flight.estimated_out_datetime,
                    'estimated_in_datetime': flight.estimated_in_datetime,
                    'estimated_off_datetime': flight.estimated_off_datetime,
                    'estimated_on_datetime': flight.estimated_on_datetime,
                    'actual_out_datetime': flight.actual_out_datetime,
                    'actual_in_datetime': flight.actual_in_datetime,
                    'actual_off_datetime': flight.actual_off_datetime,
                    'actual_on_datetime': flight.actual_on_datetime,
                    'line_id': line.id,
                }
                template_data.append(flight_data)

    # Data for assignments on Tails

    assignments_data = []
    assignments = Assignment.get_revision_assignments(revision).select_related('flight', 'tail').filter(
        (Q(start_time__gte=start_time) & Q(start_time__lte=end_time)) |
        (Q(end_time__gte=start_time) & Q(end_time__lte=end_time)) |
        (Q(start_time__lte=start_time) & Q(end_time__gte=end_time))
    ).order_by('start_time')

    for assignment in assignments:
        assignment_data = {
            'id': assignment.id,
            'number': assignment.flight_number,
            'start_time': assignment.start_time,
            'end_time': assignment.end_time,
            'status': assignment.status,
            'tail': assignment.tail.number,
            'actual_hobbs': Hobbs.get_projected_value(assignment.tail, assignment.end_time, revision),
            'next_due_hobbs': Hobbs.get_next_due_value(assignment.tail, assignment.end_time),
        }

        if assignment.flight:
            assignment_data['origin'] = assignment.flight.origin
            assignment_data['destination'] = assignment.flight.destination
            assignment_data['scheduled_out_datetime'] = assignment.flight.scheduled_out_datetime
            assignment_data['scheduled_in_datetime'] = assignment.flight.scheduled_in_datetime
            assignment_data['flight_id'] = assignment.flight.id
        assignments_data.append(assignment_data)

    data = {
        'assignments': assignments_data,
        'templates': template_data,
        'tails': tails_data,
    }
    return Response(data)

@login_required
@gantt_writable_required
@api_view(['POST'])
def api_assign_flight(request):
    result = {
        'success': False,
        'assigned_flights': {},
        'duplication': False,
        'time_conflicts': [],
        'physically_invalid': False,
        'physical_conflicts': [],
    }

    try:
        flight_data = json.loads(request.data.get('flight_data'))
        revision_id = request.data.get('revision')
    except:
        result['error'] = 'Invalid parameters'
        return Response(result, status=400)

    if revision_id and int(revision_id) > 0:
        try:
            revision = Revision.objects.get(pk=revision_id)
            if revision:
                revision.check_draft_created()
        except Revision.DoesNotExist:
            result['error'] = 'Revision not found'
            return Response(result, status=400)
    else:
        revision = None

    physical_conflicts = []
    time_conflicts = []

    for data in flight_data:
        try:
            flight_id = data['flight']
            tail_number = data['tail']
            tail = Tail.objects.get(number=tail_number)
            flight = Flight.objects.get(pk=flight_id)

            duplicated_assignment = Assignment.duplication_check(revision, tail, flight.scheduled_out_datetime, flight.scheduled_in_datetime)
            if duplicated_assignment:
                time_conflicts.append({
                    'assignment': {
                        'id': duplicated_assignment.id,
                        'start_time': duplicated_assignment.start_time,
                        'end_time': duplicated_assignment.end_time,
                        'status': duplicated_assignment.status,
                        'flight': {
                            'id': duplicated_assignment.flight.id,
                            'number': duplicated_assignment.flight.number,
                            'origin': duplicated_assignment.flight.origin,
                            'destination': duplicated_assignment.flight.destination,
                        } if duplicated_assignment.flight else None,
                    },
                    'editing_assignment': {
                        'status': Assignment.STATUS_FLIGHT,
                        'flight': {
                            'id': flight.id,
                            'number': flight.number,
                            'origin': flight.origin,
                            'destination': flight.destination,
                        }
                    }
                })
                result['duplication'] = True
                continue

            conflict = Assignment.physical_conflict_check(
                revision,
                tail,
                flight.origin, flight.destination,
                flight.scheduled_out_datetime, flight.scheduled_in_datetime
            )
            if conflict:
                result['physically_invalid'] = True
                physical_conflicts.append({
                    'flight': {
                        'number': conflict['conflict'].flight.number,
                        'origin': conflict['conflict'].flight.origin,
                        'destination': conflict['conflict'].flight.destination,
                    },
                    'assigning_flight': {
                        'number': flight.number,
                        'origin': flight.origin,
                        'destination': flight.destination,
                    },
                    'conflict': conflict['direction'],
                })
                continue

            assignment = Assignment(
                flight_number=flight.number,
                start_time=flight.scheduled_out_datetime,
                end_time=flight.scheduled_in_datetime,
                status=Assignment.STATUS_FLIGHT,
                flight=flight,
                tail=tail
            )
            assignment.apply_revision(revision)
            assignment.save()

            result['assigned_flights'][flight_id] = {
                'assignment_id': assignment.id,
                'actual_hobbs': Hobbs.get_projected_value(tail, assignment.end_time, revision),
                'next_due_hobbs': Hobbs.get_next_due_value(tail, assignment.end_time),
            }
        except Exception as e:
            print(str(e))

    result['physical_conflicts'] = physical_conflicts
    result['time_conflicts'] = time_conflicts
    result['success'] = True
    return Response(result)

@login_required
@gantt_writable_required
@api_view(['POST'])
def api_assign_status(request):
    result = {
        'success': False,
        'physical_conflicts': [],
        'time_conflicts': [],
    }

    try:
        tail_number = request.data.get('tail')
        start_time = dateutil.parser.parse(request.data.get('start_time'))
        end_time = dateutil.parser.parse(request.data.get('end_time'))
        status = int(request.data.get('status'))
        origin = request.data.get('origin') or ''     # used for unscheduled flight assignments
        destination = request.data.get('destination') or ''   # used for unscheduled flight assignments
        revision_id = request.data.get('revision')
    except:
        result['error'] = 'Invalid parameters'
        return Response(result, status=400)

    if revision_id and int(revision_id) > 0:
        try:
            revision = Revision.objects.get(pk=revision_id)
            if revision:
                revision.check_draft_created()
        except Revision.DoesNotExist:
            result['error'] = 'Revision not found'
            return Response(result, status=400)
    else:
        revision = None

    physical_conflicts = []
    time_conflicts = []

    try:
        tail = Tail.objects.get(number=tail_number)

        duplicated_assignment = Assignment.duplication_check(revision, tail, start_time, end_time)
        if duplicated_assignment:
            time_conflicts.append({
                'assignment': {
                    'id': duplicated_assignment.id,
                    'start_time': duplicated_assignment.start_time,
                    'end_time': duplicated_assignment.end_time,
                    'status': duplicated_assignment.status,
                    'flight': {
                        'id': duplicated_assignment.flight.id,
                        'number': duplicated_assignment.flight.number,
                        'origin': duplicated_assignment.flight.origin,
                        'destination': duplicated_assignment.flight.destination,
                    } if duplicated_assignment.flight else None,
                },
                'editing_assignment': {
                    'status': status,
                    'flight': {
                        'number': 0,
                        'origin': origin,
                        'destination': destination,
                    } if origin and destination else None
                }
            })
            result['error'] = 'Duplicated assignment'
            result['time_conflicts'] = time_conflicts
            return Response(result)

        if status == Assignment.STATUS_UNSCHEDULED_FLIGHT:
            conflict = Assignment.physical_conflict_check(revision, tail, origin, destination, start_time, end_time)
            if conflict:
                physical_conflicts.append({
                    'flight': {
                        'number': conflict['conflict'].flight.number,
                        'origin': conflict['conflict'].flight.origin,
                        'destination': conflict['conflict'].flight.destination,
                    },
                    'assigning_flight': {
                        'number': 0,
                        'origin': origin,
                        'destination': destination,
                    },
                    'conflict': conflict['direction'],
                })
                result['physical_conflicts'] = physical_conflicts
                result['error'] = 'Physically invalid assignment'
                return Response(result)

        assignment = Assignment(
            flight_number=0,
            start_time=start_time,
            end_time=end_time,
            status=status,
            flight=None,
            tail=tail
        )
        if status == Assignment.STATUS_UNSCHEDULED_FLIGHT:
            flight = Flight(
                origin=origin,
                destination=destination,
                scheduled_out_datetime=start_time,
                scheduled_in_datetime=end_time,
                type=Flight.TYPE_UNSCHEDULED
            )
            flight.save()

            assignment.flight = flight

        assignment.apply_revision(revision)
        assignment.save()

    except Exception as e:
        result['error'] = str(e)
        return Response(result, status=500)

    result['success'] = True
    result['id'] = assignment.id
    return Response(result)

@login_required
@gantt_writable_required
@api_view(['POST'])
def api_remove_assignment(request):
    result = {
        'success': False,
        'removed_assignments': [],
    }

    try:
        assignment_ids = json.loads(request.data.get('assignment_data'))
        revision_id = request.data.get('revision')
    except:
        result['error'] = 'Invalid parameters'
        return Response(result, status=400)

    if revision_id and int(revision_id) > 0:
        try:
            revision = Revision.objects.get(pk=revision_id)
            if revision:
                revision.check_draft_created()
        except Revision.DoesNotExist:
            result['error'] = 'Revision not found'
            return Response(result, status=400)
    else:
        revision = None

    for assignment_id in assignment_ids:
        try:
            assignment = Assignment.objects.get(pk=assignment_id)
            assignment.delete()
            if assignment.status == Assignment.STATUS_UNSCHEDULED_FLIGHT:
                assignment.flight.delete()

            result['removed_assignments'].append(assignment_id)
        except Exception as e:
            print(str(e))

    result['success'] = True
    return Response(result)

@login_required
@gantt_writable_required
@api_view(['POST'])
def api_move_assignment(request):
    result = {
        'success': False,
        'assignments': {},
        'duplication': False,
        'time_conflicts': [],
        'physically_invalid': False,
        'physical_conflicts': [],
    }

    try:
        assignment_data = json.loads(request.data.get('assignment_data'))
        revision_id = request.data.get('revision')
    except:
        result['error'] = 'Invalid parameters'
        return Response(result, status=400)

    if revision_id and int(revision_id) > 0:
        try:
            revision = Revision.objects.get(pk=revision_id)
            if revision:
                revision.check_draft_created()
        except Revision.DoesNotExist:
            result['error'] = 'Revision not found'
            return Response(result, status=400)
    else:
        revision = None

    physical_conflicts = []
    time_conflicts = []

    for data in assignment_data:
        try:
            assignment_id = data['assignment_id']
            tail_number = data['tail']
            try:
                start_time_str = data['start_time']
                if start_time_str:
                    start_time = dateutil.parser.parse(start_time_str)
                else:
                    start_time = None
            except:
                start_time_str = None
                start_time = None

            assignment = Assignment.objects.select_related('flight').get(pk=assignment_id)
            tail = Tail.objects.get(number=tail_number)

            if not start_time:
                start_time = assignment.start_time
                end_time = assignment.end_time
            else:
                end_time = start_time + (assignment.end_time - assignment.start_time)

            duplicated_assignment = Assignment.duplication_check(revision, tail, start_time, end_time, assignment)
            if duplicated_assignment:
                time_conflicts.append({
                    'assignment': {
                        'id': duplicated_assignment.id,
                        'start_time': duplicated_assignment.start_time,
                        'end_time': duplicated_assignment.end_time,
                        'status': duplicated_assignment.status,
                        'flight': {
                            'id': duplicated_assignment.flight.id,
                            'number': duplicated_assignment.flight.number,
                            'origin': duplicated_assignment.flight.origin,
                            'destination': duplicated_assignment.flight.destination,
                        } if duplicated_assignment.flight else None,
                    },
                    'editing_assignment': {
                        'status': assignment.status,
                        'flight': {
                            'number': assignment.flight.number,
                            'origin': assignment.flight.origin,
                            'destination': assignment.flight.destination,
                        } if assignment.flight else None
                    }
                })
                result['duplication'] = True
                continue

            try:
                if assignment.flight:
                    conflict = Assignment.physical_conflict_check(revision, tail, assignment.flight.origin, assignment.flight.destination, start_time, end_time, assignment)
                    if conflict:
                        physical_conflicts.append({
                            'flight': {
                                'number': conflict['conflict'].flight.number,
                                'origin': conflict['conflict'].flight.origin,
                                'destination': conflict['conflict'].flight.destination,
                            },
                            'assigning_flight': {
                                'number': assignment.flight.number,
                                'origin': assignment.flight.origin,
                                'destination': assignment.flight.destination,
                            },
                            'conflict': conflict['direction'],
                        })
                        result['physically_invalid'] = True
                        continue
            except ObjectDoesNotExist:
                pass

            assignment.tail = tail
            try:
                if start_time_str:
                    if assignment.status == Assignment.STATUS_UNSCHEDULED_FLIGHT:
                        assignment.flight.scheduled_out_datetime = start_time
                        assignment.flight.scheduled_in_datetime = end_time
                        assignment.flight.save()

                    assignment.start_time = start_time
                    assignment.end_time = end_time
                assignment.apply_revision(revision)
                assignment.save()
            except ObjectDoesNotExist:
                pass

            result['assignments'][assignment.id] = {
                'start_time': assignment.start_time.isoformat(),
                'end_time': assignment.end_time.isoformat(),
            }
        except Exception as e:
            print(str(e))

    result['physical_conflicts'] = physical_conflicts
    result['time_conflicts'] = time_conflicts
    result['success'] = True
    return Response(result)

@login_required
@gantt_writable_required
@api_view(['POST'])
def api_resize_assignment(request):
    result = {
        'success': False,
        'time_conflicts': [],
    }

    try:
        assignment_id = request.data.get('assignment_id')
        revision_id = request.data.get('revision')
        pos = request.data.get('position')  # start or end
        diff_seconds = round(float(request.data.get('diff_seconds')) / 300.0) * 300.0     # changed time in seconds
    except:
        result['error'] = 'Invalid parameters'
        return Response(result, status=400)

    if revision_id and int(revision_id) > 0:
        try:
            revision = Revision.objects.get(pk=revision_id)
            if revision:
                revision.check_draft_created()
        except Revision.DoesNotExist:
            result['error'] = 'Revision not found'
            return Response(result, status=400)
    else:
        revision = None

    time_conflicts = []

    try:
        assignment = Assignment.objects.get(pk=assignment_id)

        start_time = assignment.start_time
        end_time = assignment.end_time
        if pos == 'end':
            end_time = end_time + timedelta(seconds=diff_seconds)
        else:
            start_time = start_time - timedelta(seconds=diff_seconds)

        if start_time >= end_time:
            result['error'] = 'Start time cannot be later than end time'
            return Response(result, status=400)

        duplicated_assignment = Assignment.duplication_check(revision, assignment.tail, start_time, end_time, assignment)
        if duplicated_assignment:
            time_conflicts.append({
                'assignment': {
                    'id': duplicated_assignment.id,
                    'start_time': duplicated_assignment.start_time,
                    'end_time': duplicated_assignment.end_time,
                    'status': duplicated_assignment.status,
                    'flight': {
                        'id': duplicated_assignment.flight.id,
                        'number': duplicated_assignment.flight.number,
                        'origin': duplicated_assignment.flight.origin,
                        'destination': duplicated_assignment.flight.destination,
                    } if duplicated_assignment.flight else None,
                },
                'editing_assignment': {
                    'status': assignment.status,
                    'flight': {
                        'number': assignment.flight.number,
                        'origin': assignment.flight.origin,
                        'destination': assignment.flight.destination,
                    } if assignment.flight else None
                }
            })
            result['time_conflicts'] = time_conflicts
            result['error'] = 'Duplicated assignment'
            return Response(result)

        assignment.start_time = start_time
        assignment.end_time = end_time
        assignment.apply_revision(revision)
        assignment.save()

        if assignment.status == Assignment.STATUS_UNSCHEDULED_FLIGHT:
            assignment.flight.scheduled_out_datetime = start_time
            assignment.flight.scheduled_in_datetime = end_time
            assignment.flight.save()

    except Exception as e:
        result['error'] = str(e)
        return Response(result, status=500)

    result['success'] = True
    result['start_time'] = assignment.start_time.isoformat()
    result['end_time'] = assignment.end_time.isoformat()
    return Response(result)

def str_to_datetime(str): # pragma: no cover
    parts = str.split(' ')
    date_parts = parts[0].split('/')
    date = int(date_parts[0])
    month = int(date_parts[1])
    year = int(date_parts[2])
    hour = 0
    minute = 0
    second = 0

    if len(parts) > 1:
        time_parts = parts[1].split(':')
        hour = int(time_parts[0])
        minute = int(time_parts[1])
        second = int(time_parts[2])

    return datetime(year, month, date, hour, minute, second, tzinfo=utc)

@login_required
@gantt_writable_required
@api_view(['POST'])
def api_upload_csv(request): # pragma: no cover
    result = {
        'success': False,
    }

    filepath = settings.STATIC_ROOT + '/uploads/' + str(totimestamp(datetime_now_utc())) + '_' + str(random.randint(100000, 999999)) + '.csv'
    try:
        file = request.FILES['csvfile']
        destination = open(filepath, 'wb+')
        for chunk in file.chunks():
            destination.write(chunk)
            destination.close()
    except Exception as e:
        result['error'] = str(e)
        return Response(result)

    with open(filepath) as csvfile:
        csvreader = csv.reader(csvfile, delimiter=',', quotechar='"')
        now = datetime_now_utc()

        for row in csvreader:
            try:
                flight_number = int(row[1][3:])
                origin = row[2]
                destination = row[3]
                scheduled_out_datetime = str_to_datetime(row[4])
                scheduled_in_datetime = str_to_datetime(row[6])

                # if scheduled_out_datetime < now:
                #     continue

                flight_to_update = None

                closest_past_date = Flight.objects \
                    .filter(number=flight_number, scheduled_out_datetime__lte=scheduled_out_datetime) \
                    .aggregate(closest_past_date=Max('scheduled_out_datetime'))['closest_past_date']
                if closest_past_date and closest_past_date.year == scheduled_out_datetime.year \
                    and closest_past_date.month == scheduled_out_datetime.month \
                    and closest_past_date.day == scheduled_out_datetime.day:
                    flight_to_update = Flight.objects.select_related('assignment').get(
                        number=flight_number,
                        scheduled_out_datetime=closest_past_date
                    )

                if not flight_to_update:
                    closest_next_date = Flight.objects \
                        .filter(number=flight_number, scheduled_out_datetime__gt=scheduled_out_datetime) \
                        .aggregate(closest_next_date=Max('scheduled_out_datetime'))['closest_next_date']
                    if closest_next_date and closest_next_date.year == scheduled_out_datetime.year \
                        and closest_next_date.month == scheduled_out_datetime.month \
                        and closest_next_date.day == scheduled_out_datetime.day:
                        flight_to_update = Flight.objects.select_related('assignment').get(
                            number=flight_number,
                            scheduled_out_datetime=closest_next_date
                        )

                if flight_to_update:
                    flight_to_update.scheduled_out_datetime = scheduled_out_datetime
                    flight_to_update.scheduled_in_datetime = scheduled_in_datetime
                    flight_to_update.save()

                    assignment = flight_to_update.get_assignment()
                    if assignment:
                        dup_assignments = Assignment.get_duplicated_assignments(assignment.tail, scheduled_out_datetime, scheduled_in_datetime, assignment)
                        if dup_assignments.count() > 0:
                            assignment.delete()
                            dup_assignments.delete()
                        else:
                            assignment.start_time = scheduled_out_datetime
                            assignment.end_time = scheduled_in_datetime
                            assignment.save()
                else:
                    flight=Flight(
                        number=flight_number,
                        origin=origin,
                        destination=destination,
                        scheduled_out_datetime=scheduled_out_datetime,
                        scheduled_in_datetime=scheduled_in_datetime
                    )
                    flight.save()

            except Exception as e:
                print(str(e))

    try:
        os.remove(filepath)
    except:
        pass

    result['success'] = True
    return Response(result)

@login_required
@gantt_readable_required
@api_view(['GET'])
def api_get_hobbs(request, hobbs_id=None):
    result = {
        'success': False,
    }

    try:
        hobbs = Hobbs.objects.filter(pk=hobbs_id)
    except:
        return Response(result, status=400)

    result['success'] = True
    result['hobbs'] = serializers.serialize("json", hobbs)
    return Response(result)

@login_required
@gantt_writable_required
@api_view(['POST'])
def api_delete_actual_hobbs(request, hobbs_id=None):
    result = {
        'success': False,
    }

    try:
        Hobbs.objects.filter(pk=hobbs_id).filter(type=Hobbs.TYPE_ACTUAL).delete()
    except:
        return Response(result, status=400)

    result['success'] = True
    return Response(result)

@login_required
@gantt_writable_required
@api_view(['POST'])
def api_save_hobbs(request):
    result = {
        'success': False,
    }

    try:
        tail_id = request.data.get('tail_id')
        hobbs_id = request.data.get('id')
        hobbs_type = int(request.data.get('type'))
        hobbs_value = request.data.get('hobbs')
        hobbs_datetime = dateutil.parser.parse(request.data.get('datetime'))

        if hobbs_id:
            hobbs = Hobbs.objects.get(pk=hobbs_id)
        elif hobbs_type == Hobbs.TYPE_ACTUAL:
            hobbs = Hobbs.objects.filter(hobbs_time=hobbs_datetime).filter(type=Hobbs.TYPE_ACTUAL).first()
        else:
            hobbs = None

        if hobbs and hobbs.hobbs_time != hobbs_datetime:
            hobbs = None    # Create new hobbs item regardless of actual/next due hobbs if date/time is changed

        if hobbs and hobbs.type != hobbs_type:
            raise Exception('Invalid parameters')
    except Exception as e:
        print(str(e))
        result['error'] = 'Invalid parameters'
        return Response(result, status=400)

    try:
        tail = Tail.objects.get(pk=tail_id)
        if not hobbs:
            hobbs = Hobbs()
            hobbs.type = hobbs_type
        hobbs.hobbs_time = hobbs_datetime
        hobbs.hobbs = hobbs_value
        hobbs.tail = tail
        hobbs.save()
    except Exception as e:
        result['error'] = str(e)
        return Response(result, status=500)

    result['success'] = True
    result['hobbs_id'] = hobbs.id
    return Response(result)

@login_required
@gantt_readable_required
@api_view(['POST'])
def api_coming_due_list(request):
    result = {
        'success': False,
    }

    try:
        tail_id = request.data.get('tail_id')
        start_time = dateutil.parser.parse(request.data.get('start'))
        days = int(request.data.get('days'))
        revision_id = request.data.get('revision')
    except:
        result['error'] = 'Invalid parameters'
        return Response(result, status=400)

    if revision_id and int(revision_id) > 0:
        try:
            revision = Revision.objects.get(pk=revision_id)
        except Revision.DoesNotExist:
            result['error'] = 'Revision not found'
            return Response(result, status=400)
    else:
        revision = None

    try:
        tail = Tail.objects.get(pk=tail_id)

        hobbs_list = []

        projected_hobbs_value = Hobbs.get_projected_value(tail, start_time, revision)
        last_actual_hobbs = Hobbs.get_last_actual_hobbs(tail, start_time)
        projected_next_due_hobbs = Hobbs.get_next_due(tail, start_time)
        projected_next_due_hobbs_value = 0
        projected_next_due_hobbs_id = 0
        if projected_next_due_hobbs:
            projected_next_due_hobbs_value = projected_next_due_hobbs.hobbs
            projected_next_due_hobbs_id = projected_next_due_hobbs.id

        end_time = start_time + timedelta(days=days)

        stream = []

        hobbs_set = Hobbs.get_hobbs(tail, start_time, end_time)
        for hobbs in hobbs_set:
            stream.append({
                'datetime': hobbs.hobbs_time,
                'type': 'hobbs',
                'object': hobbs,
            })

        assignments = Assignment.objects.filter(start_time__gte=start_time) \
            .filter(start_time__lt=end_time) \
            .filter(revision=revision) \
            .filter(tail=tail) \
            .select_related('flight') \
            .order_by('start_time')
        for assignment in assignments:
            stream.append({
                'datetime': assignment.start_time,
                'type': 'assignment',
                'object': assignment,
            })

        stream = sorted(stream, key=lambda object: object['datetime'])
        for object in stream:
            if object['type'] == 'hobbs':
                hobbs = object['object']
                if hobbs.type == Hobbs.TYPE_ACTUAL:
                    projected_hobbs_value = hobbs.hobbs
                    last_actual_hobbs = hobbs
                elif hobbs.type == Hobbs.TYPE_NEXT_DUE:
                    projected_next_due_hobbs_value = hobbs.hobbs
                    projected_next_due_hobbs_id = hobbs.id
            elif object['type'] == 'assignment':
                assignment = object['object']
                if not last_actual_hobbs or last_actual_hobbs.hobbs_time < assignment.start_time:
                    projected_hobbs_value += assignment.length / 3600
                hobbs_list.append({
                    'day': assignment.start_time,
                    'projected': projected_hobbs_value,
                    'next_due': projected_next_due_hobbs_value,
                    'next_due_hobbs_id': projected_next_due_hobbs_id,
                    'flight': str(assignment.flight),
                    'start_time_tmstmp': totimestamp(assignment.start_time),
                })

        if len(hobbs_list) == 0:
            hobbs_list.append({
                'day': '',
                'projected': projected_hobbs_value,
                'next_due': projected_next_due_hobbs_value,
                'next_due_hobbs_id': projected_next_due_hobbs_id,
                'flight': '',
            })

    except Exception as e:
        result['error'] = str(e)
        return Response(result, status=500)

    result['success'] = True
    result['hobbs_list'] = hobbs_list
    return Response(result)

@login_required
@gantt_writable_required
@api_view(['POST'])
def api_publish_revision(request):
    result = {
        'success': False,
    }

    revision_id = request.data.get('revision')

    if revision_id and int(revision_id) > 0:
        try:
            revision = Revision.objects.get(pk=revision_id)
        except Revision.DoesNotExist:
            result['error'] = 'Revision not found'
            return Response(result, status=400)
    else:
        revision = None

    try:
        new_revision = Revision(published_datetime=datetime_now_utc(), has_draft=False)
        new_revision.save()

        if not revision or revision.has_draft:
            Assignment.get_revision_assignments(revision).filter(is_draft=True).update(revision=new_revision, is_draft=False)
        else:
            revision_assignments = Assignment.get_revision_assignments(revision).filter(is_draft=False)
            for assignment in revision_assignments:
                assignment.pk = None
                assignment.is_draft = False
                assignment.revision = new_revision
                assignment.save()

        if revision and revision.has_draft:
            revision.has_draft = False
            revision.save()
        elif not revision:
            # Copy past and current assignments from last revision
            Revision.create_draft()
    except Exception as e:
        result['error'] = str(e)
        return Response(result, status=500)

    result['success'] = True
    result['revision'] = new_revision.id
    result['revisions'] = []
    for revision in Revision.objects.order_by('-published_datetime'):
        result['revisions'].append({
            'id': revision.id,
            'published': totimestamp(revision.published_datetime),
        })

    return Response(result)

@login_required
@gantt_writable_required
@api_view(['POST'])
def api_clear_revision(request):
    result = {
        'success': False,
    }

    revision_id = request.data.get('revision')

    if revision_id and int(revision_id) > 0:
        try:
            revision = Revision.objects.get(pk=revision_id)
        except Revision.DoesNotExist:
            result['error'] = 'Revision not found'
            return Response(result, status=400)
    else:
        revision = None

    try:
        Assignment.get_revision_assignments(revision).filter(is_draft=True).delete()

        if revision:
            revision.has_draft = False
            revision.save()
        else:
            # Copy past and current assignments from last revision
            Revision.create_draft()
    except Exception as e:
        result['error'] = str(e)
        return Response(result, status=500)

    result['success'] = True
    return Response(result)

@login_required
@gantt_writable_required
@api_view(['POST'])
def api_delete_revision(request):
    result = {
        'success': False,
    }

    revision_id = request.data.get('revision')

    if revision_id and int(revision_id) > 0:
        try:
            revision = Revision.objects.get(pk=revision_id)
        except Revision.DoesNotExist:
            result['error'] = 'Revision not found'
            return Response(result, status=400)
    else:
        revision = None

    try:
        revision_assignments = Assignment.get_revision_assignments_all(revision)
        revision_assignments.delete()

        if revision:
            revision.delete()
        else:
            # Copy past and current assignments from last revision
            Revision.create_draft()
    except Exception as e:
        result['error'] = str(e)
        return Response(result, status=500)

    result['success'] = True
    result['revisions'] = []
    for revision in Revision.objects.order_by('-published_datetime'):
        result['revisions'].append({
            'id': revision.id,
            'published': totimestamp(revision.published_datetime),
        })
    return Response(result)

