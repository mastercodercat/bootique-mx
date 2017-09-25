from datetime import timedelta, datetime
import json
import dateutil.parser
import random
import os
import csv

from django.db.models import Q, ProtectedError, Max
from django.conf import settings

from common.exceptions import APIException
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from common.helpers import *
from common.views.generic import APIView
from common.views.generic import RetrieveDestroyAPIView
from common.views.generic import DataTablePaginatedListView
from routeplanning.models import *
from routeplanning.permissions import GanttReadPermission
from routeplanning.permissions import GanttWritePermission
from routeplanning.serializers import DataTableFlightSerializer
from routeplanning.serializers import HobbsSerializer


class DeleteTailView(RetrieveDestroyAPIView):
    queryset = Tail.objects.all()
    lookup_url_kwarg = 'tail_id'
    delete_error_message = 'Error occurred while deleting tail'
    permission_classes = (IsAuthenticated, GanttWritePermission)


class DeleteLineView(RetrieveDestroyAPIView):
    queryset = Line.objects.all()
    lookup_url_kwarg = 'line_id'
    delete_error_message = 'Error occurred while deleting line'
    permission_classes = (IsAuthenticated, GanttWritePermission)


class FlightListView(DataTablePaginatedListView):
    error_message = 'Error occurred while getting flight page data'
    permission_classes = (IsAuthenticated, GanttReadPermission)
    serializer_class = DataTableFlightSerializer

    def get_queryset(self):
        order_columns = (
            'id', 'number', 'origin', 'destination',
            'scheduled_out_datetime', 'scheduled_off_datetime', 'scheduled_on_datetime', 'scheduled_in_datetime',
            'estimated_out_datetime', 'estimated_off_datetime', 'estimated_on_datetime', 'estimated_in_datetime',
        )
        order_dir = self.request.query_params.get('order[0][dir]')
        order_column_index = int(self.request.query_params.get('order[0][column]', 0))
        search = self.request.query_params.get('search[value]')

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
        return flights

    def get_total_count(self):
        return Flight.objects.count()


class GanttRevisionMixin(object):
    def get_revision(self, revision_id, create_draft=False):
        if revision_id and int(revision_id) > 0:
            try:
                revision = Revision.objects.get(pk=revision_id)
                if create_draft and revision:
                    revision.check_draft_created()
                return revision
            except Revision.DoesNotExist:
                raise APIException('Revision not found', status=400)
        else:
            return None


class LoadDataView(GanttRevisionMixin, APIView):
    permission_classes = (IsAuthenticated, GanttReadPermission)

    def _get(self, *args, **kwargs):
        request = self.request
        start_time = datetime.fromtimestamp(int(request.query_params.get('startdate')), tz=utc)
        end_time = datetime.fromtimestamp(int(request.query_params.get('enddate')), tz=utc)
        assignments_only = request.query_params.get('assignments_only')
        revision_id = request.query_params.get('revision')

        revision = self.get_revision(revision_id)

        if not can_write_gantt(request.user):
            if not revision:    # Current draft gantt
                raise APIException('Not allowed to get draft route plan', status=403)
            else:
                latest_published_datetime_row = Revision.objects.all().aggregate(Max('published_datetime'))
                latest_published_datetime = latest_published_datetime_row['published_datetime__max']
                if revision.published_datetime != latest_published_datetime:
                    raise APIException('Not allowed to get route plans other than current published version', status=403)

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
                assignment_data['flight_id'] = assignment.flight.id
                assignment_data['scheduled_out_datetime'] = assignment.flight.scheduled_out_datetime
                assignment_data['scheduled_in_datetime'] = assignment.flight.scheduled_in_datetime
                assignment_data['scheduled_out_datetime'] = assignment.flight.scheduled_out_datetime
                assignment_data['scheduled_in_datetime'] = assignment.flight.scheduled_in_datetime
                assignment_data['scheduled_off_datetime'] = assignment.flight.scheduled_off_datetime
                assignment_data['scheduled_on_datetime'] = assignment.flight.scheduled_on_datetime
                assignment_data['estimated_out_datetime'] = assignment.flight.estimated_out_datetime
                assignment_data['estimated_in_datetime'] = assignment.flight.estimated_in_datetime
                assignment_data['estimated_off_datetime'] = assignment.flight.estimated_off_datetime
                assignment_data['estimated_on_datetime'] = assignment.flight.estimated_on_datetime
                assignment_data['actual_out_datetime'] = assignment.flight.actual_out_datetime
                assignment_data['actual_in_datetime'] = assignment.flight.actual_in_datetime
                assignment_data['actual_off_datetime'] = assignment.flight.actual_off_datetime
                assignment_data['actual_on_datetime'] = assignment.flight.actual_on_datetime
            assignments_data.append(assignment_data)

        return {
            'assignments': assignments_data,
            'templates': template_data,
            'tails': tails_data,
        }


class AssignFlightView(GanttRevisionMixin, APIView):
    permission_classes = (IsAuthenticated, GanttWritePermission)

    def _post(self, *args, **kwargs):
        request = self.request

        try:
            flight_data = json.loads(request.data.get('flight_data'))
        except:
            raise APIException('Invalid parameters', status=400)

        revision = self.get_revision(request.data.get('revision'), create_draft=True)

        result = {
            'assigned_flights': {},
            'duplication': False,
            'time_conflicts': [],
            'physically_invalid': False,
            'physical_conflicts': [],
        }

        physical_conflicts = []
        time_conflicts = []

        for data in flight_data:
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

            if flight.actual_out_datetime and flight.actual_in_datetime:
                start_time = flight.actual_out_datetime
                end_time = flight.actual_in_datetime
            elif flight.estimated_out_datetime and flight.estimated_in_datetime:
                start_time = flight.estimated_out_datetime
                end_time = flight.estimated_in_datetime
            else:
                start_time = flight.scheduled_out_datetime
                end_time = flight.scheduled_in_datetime

            assignment = Assignment(
                flight_number=flight.number,
                start_time=start_time,
                end_time=end_time,
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

        result['physical_conflicts'] = physical_conflicts
        result['time_conflicts'] = time_conflicts
        return result


class AssignStatusView(GanttRevisionMixin, APIView):
    permission_classes = (IsAuthenticated, GanttWritePermission)

    def _post(self, *args, **kwargs):
        request = self.request

        try:
            tail_number = request.data.get('tail')
            start_time = dateutil.parser.parse(request.data.get('start_time'))
            end_time = dateutil.parser.parse(request.data.get('end_time'))
            status = int(request.data.get('status'))
            origin = request.data.get('origin') or ''     # used for unscheduled flight assignments
            destination = request.data.get('destination') or ''   # used for unscheduled flight assignments
        except:
            raise APIException('Invalid parameters', status=400)

        revision = self.get_revision(request.data.get('revision'), create_draft=True)

        result = {
            'physical_conflicts': [],
            'time_conflicts': [],
        }

        physical_conflicts = []
        time_conflicts = []

        try:
            tail = Tail.objects.get(number=tail_number)
        except Tail.DoesNotExist:
            raise APIException('Tail not found', status=400)

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
            result['time_conflicts'] = time_conflicts
            raise APIException('Duplicated assignment', response=result, status=400)

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
                raise APIException('Physically invalid assignment', response=result, status=400)

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

        result['id'] = assignment.id
        return result


class RemoveAssignmentView(GanttRevisionMixin, APIView):
    permission_classes = (IsAuthenticated, GanttWritePermission)

    def _post(self, *args, **kwargs):
        request = self.request

        try:
            assignment_ids = json.loads(request.data.get('assignment_data'))
        except:
            raise APIException('Invalid parameters', status=400)

        revision_id = request.data.get('revision')
        revision = self.get_revision(revision_id, create_draft=True)

        result = {
            'removed_assignments': [],
        }

        for assignment_id in assignment_ids:
            try:
                assignment = Assignment.objects.get(pk=assignment_id)
                assignment.delete()
                if assignment.status == Assignment.STATUS_UNSCHEDULED_FLIGHT:
                    assignment.flight.delete()
                result['removed_assignments'].append(assignment_id)
            except Assignment.DoesNotExist:
                pass

        return result


class MoveAssignmentView(GanttRevisionMixin, APIView):
    permission_classes = (IsAuthenticated, GanttWritePermission)

    def _post(self, *args, **kwargs):
        request = self.request

        try:
            assignment_data = json.loads(request.data.get('assignment_data'))
        except:
            raise APIException('Invalid parameters', status=400)

        revision_id = request.data.get('revision')
        revision = self.get_revision(revision_id, create_draft=True)

        result = {
            'assignments': {},
            'duplication': False,
            'time_conflicts': [],
            'physically_invalid': False,
            'physical_conflicts': [],
        }

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
                # print(str(e))
                pass

        result['physical_conflicts'] = physical_conflicts
        result['time_conflicts'] = time_conflicts
        return result


class ResizeAssignmentView(GanttRevisionMixin, APIView):
    permission_classes = (IsAuthenticated, GanttWritePermission)

    def _post(self, *args, **kwargs):
        request = self.request

        try:
            assignment_id = request.data.get('assignment_id')
            pos = request.data.get('position')  # start or end
            diff_seconds = round(float(request.data.get('diff_seconds')) / 300.0) * 300.0     # changed time in seconds
        except:
            raise APIException('Invalid parameters', status=400)

        revision_id = request.data.get('revision')
        revision = self.get_revision(revision_id, create_draft=True)

        result = {
            'time_conflicts': [],
        }

        time_conflicts = []

        try:
            assignment = Assignment.objects.get(pk=assignment_id)
        except:
            raise APIException('Invalid assignment ID', status=400)

        start_time = assignment.start_time
        end_time = assignment.end_time
        if pos == 'end':
            end_time = end_time + timedelta(seconds=diff_seconds)
        else:
            start_time = start_time - timedelta(seconds=diff_seconds)

        if start_time >= end_time:
            raise APIException('Start time cannot be later than end time', status=400)

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
            raise APIException('Duplicated assignment', response=result, status=400)

        assignment.start_time = start_time
        assignment.end_time = end_time
        assignment.apply_revision(revision)
        assignment.save()

        if assignment.status == Assignment.STATUS_UNSCHEDULED_FLIGHT:
            assignment.flight.scheduled_out_datetime = start_time
            assignment.flight.scheduled_in_datetime = end_time
            assignment.flight.save()

        result['start_time'] = assignment.start_time.isoformat()
        result['end_time'] = assignment.end_time.isoformat()
        return result


class UploadCSVView(GanttRevisionMixin, APIView):
    permission_classes = (IsAuthenticated, GanttWritePermission)

    def _post(self, *args, **kwargs):
        request = self.request

        filepath = settings.STATIC_ROOT + '/uploads/' + str(totimestamp(datetime_now_utc())) + '_' + str(random.randint(100000, 999999)) + '.csv'
        try:
            file = request.FILES['csvfile']
            destination = open(filepath, 'wb+')
            for chunk in file.chunks():
                destination.write(chunk)
                destination.close()
        except Exception as e:
            raise APIException(str(e), status=500)

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
                    # print(str(e))
                    pass

        try:
            os.remove(filepath)
        except:
            pass

        return {}


class HobbsView(RetrieveDestroyAPIView):
    serializer_class = HobbsSerializer
    lookup_url_kwarg = 'hobbs_id'
    retrieve_error_message = 'Hobbs not found'
    delete_error_message = 'Error occurred while deleting hobbs'
    permission_classes = (IsAuthenticated, GanttWritePermission)

    def get_queryset(self):
        if self.request.method == 'DELETE':
            return Hobbs.objects.filter(type=Hobbs.TYPE_ACTUAL)
        else:
            return Hobbs.objects.all()


class SaveHobbsView(GanttRevisionMixin, APIView):
    permission_classes = (IsAuthenticated, GanttWritePermission)

    def _post(self, *args, **kwargs):
        request = self.request

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
            # print(str(e))
            raise APIException('Invalid parameters', status=400)

        try:
            tail = Tail.objects.get(pk=tail_id)
            if not hobbs:
                hobbs = Hobbs()
                hobbs.type = hobbs_type
            hobbs.hobbs_time = hobbs_datetime
            hobbs.hobbs = hobbs_value
            hobbs.tail = tail
            hobbs.save()
        except Exception as e:      # pragma: no cover
            # print(str(e))
            raise APIException(str(e))

        return {
            'hobbs_id': hobbs.id
        }


class ComingDueListView(GanttRevisionMixin, APIView):
    permission_classes = (IsAuthenticated, GanttReadPermission)

    def _post(self, *args, **kwargs):
        request = self.request

        try:
            tail_id = request.data.get('tail_id')
            start_time = dateutil.parser.parse(request.data.get('start'))
            days = int(request.data.get('days'))
        except:
            raise APIException('Invalid parameters', status=400)

        revision_id = request.data.get('revision')
        revision = self.get_revision(revision_id)

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

        except Exception as e:      # pragma: no cover
            # print(str(e))
            raise APIException('Server error occurred', status=500)

        return {
            'hobbs_list': hobbs_list
        }


class PublishRevisionView(GanttRevisionMixin, APIView):
    permission_classes = (IsAuthenticated, GanttWritePermission)

    def _post(self, *args, **kwargs):
        request = self.request

        revision_id = request.data.get('revision')
        revision = self.get_revision(revision_id)

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
        except Exception as e:      # pragma: no cover
            raise APIException(str(e))

        result = {
            'revision': new_revision.id,
            'revisions': [],
        }
        for revision in Revision.objects.order_by('-published_datetime'):
            result['revisions'].append({
                'id': revision.id,
                'published': totimestamp(revision.published_datetime),
            })

        return result


class ClearRevisionView(GanttRevisionMixin, APIView):
    permission_classes = (IsAuthenticated, GanttWritePermission)

    def _post(self, *args, **kwargs):
        request = self.request

        revision_id = request.data.get('revision')
        revision = self.get_revision(revision_id)

        try:
            Assignment.get_revision_assignments(revision).filter(is_draft=True).delete()

            if revision:
                revision.has_draft = False
                revision.save()
            else:
                # Copy past and current assignments from last revision
                Revision.create_draft()
        except Exception as e:      # pragma: no cover
            raise APIException(str(e))

        return {
            'revision_id': revision_id
        }


class DeleteRevisionView(GanttRevisionMixin, APIView):
    permission_classes = (IsAuthenticated, GanttWritePermission)

    def _post(self, *args, **kwargs):
        request = self.request

        revision_id = request.data.get('revision')
        revision = self.get_revision(revision_id)

        try:
            revision_assignments = Assignment.get_revision_assignments_all(revision)
            revision_assignments.delete()

            if revision:
                revision.delete()
            else:
                # Copy past and current assignments from last revision
                Revision.create_draft()
        except Exception as e:      # pragma: no cover
            raise APIException(str(e))

        result = {
            'revisions': []
        }
        for revision in Revision.objects.order_by('-published_datetime'):
            result['revisions'].append({
                'id': revision.id,
                'published': totimestamp(revision.published_datetime),
            })

        return result
