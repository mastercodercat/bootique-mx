from __future__ import unicode_literals

from django.db import models
from django.db.models import Q, Sum

from common.helpers import *


class Tail(models.Model):
    number = models.CharField(max_length=20, blank=True, unique=True)

    def __unicode__(self):
        return self.number

    def get_last_assignment(self, revision, date):
        assignment = Assignment.objects.filter(tail=self) \
            .filter(revision=revision) \
            .exclude(status=Assignment.STATUS_MAINTENANCE) \
            .filter(end_time__lte=date) \
            .order_by('-end_time') \
            .select_related('flight') \
            .first()
        return assignment


class Line(models.Model):
    name = models.CharField(max_length=100, blank=True, unique=True)

    def __unicode__(self):
        return self.name

    @property
    def flights(self):
        line_parts = self.linepart_set.all().values('number')
        flight_numbers = [lp['number'][0:3] for lp in line_parts]
        return Flight.objects.filter(number__in=set(flight_numbers))


class LinePart(models.Model):
    number = models.CharField(default='', max_length=10, null=False, blank=False)

    line = models.ForeignKey(Line, null=True, blank=False)

    def __unicode__(self):
        return self.number


class Flight(models.Model):
    TYPE_SCHEDULED = 1
    TYPE_UNSCHEDULED = 2

    TYPE_CHOICES = (
        (TYPE_SCHEDULED, 'Scheduled Flight'),
        (TYPE_UNSCHEDULED, 'Unscheduled Flight'),
    )

    number = models.CharField(db_index=True, max_length=10, default=0, null=False, blank=False)
    origin = models.CharField(max_length=10, blank=False)
    destination = models.CharField(max_length=10, blank=False)
    departure_datetime = models.DateTimeField(null=False, blank=False)
    arrival_datetime = models.DateTimeField(null=False, blank=False)
    type = models.IntegerField(default=TYPE_SCHEDULED, choices=TYPE_CHOICES)

    def __unicode__(self):
        if self.type == Flight.TYPE_SCHEDULED:
            return str(self.number) + '. ' + self.origin + '-' + self.destination
        else:
            return 'Unscheduled Flight: ' + self.origin + '-' + self.destination

    @property
    def length(self):
        return (self.arrival_datetime - self.departure_datetime).total_seconds()

    def get_assignment(self):
        try:
            return self.assignment
        except:
            return None


class Revision(models.Model):
    published_datetime = models.DateTimeField(null=False, blank=False)
    has_draft = models.BooleanField(default=False)

    def __unicode__(self):
        model_str = 'Revision at ' + str(self.published_datetime)
        if self.has_draft:
            model_str += ' (edited)'
        return model_str

    @classmethod
    def get_latest_revision(cls):
        revision = Revision.objects.order_by('-published_datetime').first()
        return revision

    @classmethod
    def create_draft(cls):
        latest_revision = Revision.get_latest_revision()
        if latest_revision:
            assignments = Assignment.get_revision_assignments(latest_revision).filter(start_time__lte=datetime_now_utc())
            for assignment in assignments:
                assignment.pk = None
                assignment.is_draft = True
                assignment.revision = None
                assignment.save()

    def check_draft_created(self):
        if not self.has_draft:
            self.has_draft = True
            self.save()
            revision_assignments = Assignment.objects.filter(revision=self)
            # save original objects as draft because front end has already ids for these assignments
            revision_assignments.update(is_draft=True)
            for assignment in revision_assignments:
                # clone object and save as original revision assignment
                assignment.pk = None
                assignment.is_draft = False
                assignment.save()


class Assignment(models.Model):
    STATUS_FLIGHT = 1
    STATUS_MAINTENANCE = 2
    STATUS_UNSCHEDULED_FLIGHT = 3

    STATUS_CHOICES = (
        (STATUS_FLIGHT, 'Flight'),
        (STATUS_MAINTENANCE, 'Maintenance'),
        (STATUS_UNSCHEDULED_FLIGHT, 'Unscheduled Flight'),
    )

    flight_number = models.CharField(max_length=10, default='', null=False, blank=False)
    start_time = models.DateTimeField(null=False, blank=False)
    end_time = models.DateTimeField(null=False, blank=False)
    status = models.IntegerField(default=STATUS_FLIGHT, choices=STATUS_CHOICES)
    is_draft = models.BooleanField(default=False)

    flight = models.ForeignKey(Flight, null=True, blank=False, on_delete=models.PROTECT)
    tail = models.ForeignKey(Tail, null=True, blank=False, on_delete=models.PROTECT)
    revision = models.ForeignKey(Revision, null=True, blank=False, on_delete=models.PROTECT)

    def __unicode__(self):
        if self.status == Assignment.STATUS_FLIGHT:
            return 'Flight ' + str(self.flight_number) + ' Assignment'
        elif self.status == Assignment.STATUS_MAINTENANCE:
            return 'Maintenance'
        elif self.status == Assignment.STATUS_UNSCHEDULED_FLIGHT:
            return 'Unscheduled Flight'
        else:
            return 'Other'

    @property
    def length(self):
        return (self.end_time - self.start_time).total_seconds()

    @classmethod
    def get_revision_assignments(cls, revision):
        if not revision or not revision.has_draft:
            return cls.objects.filter(revision=revision)
        else:
            return cls.objects.filter(revision=revision).filter(is_draft=True)

    @classmethod
    def get_revision_assignments_all(cls, revision):
        return cls.objects.filter(revision=revision)

    @classmethod
    def duplication_check(cls, revision, tail, start_time, end_time, exclude_check_assignment=None):
        query = cls.objects.filter(
            Q(tail=tail) &
            (
                (Q(start_time__lte=start_time) & Q(end_time__gt=start_time)) |
                (Q(start_time__lt=end_time) & Q(end_time__gte=end_time)) |
                (Q(start_time__gte=start_time) & Q(end_time__lte=end_time))
            )
        ).filter(revision=revision)

        if exclude_check_assignment:
            query = query.exclude(pk=exclude_check_assignment.id)

        return query.first()

    @classmethod
    def physical_conflict_check(cls, revision, tail, origin, destination, start_time, end_time, exclude_check_assignment=None):
        query = cls.objects.filter(
                Q(tail=tail) &
                Q(end_time__lte=start_time)
            ) \
            .filter(revision=revision) \
            .exclude(status=Assignment.STATUS_MAINTENANCE) \
            .order_by('-start_time') \
            .select_related('flight')
        if exclude_check_assignment:
            query = query.exclude(pk=exclude_check_assignment.id)
        assignment_just_before = query.first()
        if assignment_just_before and assignment_just_before.flight.destination != origin:
            return {
                'conflict': assignment_just_before,
                'direction': 'destination',     # Origin/direction of conflicted already existing assignment
            }

        query = cls.objects.filter(
                Q(tail=tail) &
                Q(start_time__gte=end_time)
            ) \
            .exclude(status=Assignment.STATUS_MAINTENANCE) \
            .order_by('start_time') \
            .select_related('flight')
        if exclude_check_assignment:
            query = query.exclude(pk=exclude_check_assignment.id)
        assignment_just_after = query.first()
        if assignment_just_after and assignment_just_after.flight.origin != destination:
            return {
                'conflict': assignment_just_after,
                'direction': 'origin',          # Origin/direction of conflicted already existing assignment
            }

        return None

    @classmethod
    def get_duplicated_assignments(cls, revision, tail, start_time, end_time, exclude_check_assignment=None):
        query = cls.objects.filter(
            Q(tail=tail) &
            (
                (Q(start_time__lte=start_time) & Q(end_time__gt=start_time)) |
                (Q(start_time__lt=end_time) & Q(end_time__gte=end_time)) |
                (Q(start_time__gte=start_time) & Q(end_time__lte=end_time))
            )
        ).filter(revision=revision)
        if exclude_check_assignment:
            query = query.exclude(pk=exclude_check_assignment.id)
        return query.all()

    def apply_revision(self, revision):
        if revision and not revision.has_draft:
            self.is_draft = False
        else:
            self.is_draft = True
        self.revision = revision


class Hobbs(models.Model):
    TYPE_ACTUAL = 1
    TYPE_NEXT_DUE = 2

    TYPE_CHOICES = (
        (TYPE_ACTUAL, 'Actual'),
        (TYPE_NEXT_DUE, 'Next Due'),
    )

    hobbs_time = models.DateTimeField(null=False, blank=False)
    type = models.IntegerField(default=TYPE_ACTUAL, choices=TYPE_CHOICES)
    hobbs = models.FloatField(default=0.0, blank=False)

    tail = models.ForeignKey(Tail, null=True, blank=False, on_delete=models.PROTECT)

    def __unicode__(self):
        return 'Hobbs of ' + self.tail.number + ' on date ' + self.hobbs_time.strftime("%F")

    @classmethod
    def get_hobbs(cls, tail, start_time, end_time):
        return cls.objects.filter(hobbs_time__gte=start_time) \
            .filter(hobbs_time__lt=end_time) \
            .filter(tail=tail) \
            .order_by('hobbs_time') \
            .all()

    @classmethod
    def get_last_actual_hobbs(cls, tail, datetime):
        return cls.objects.filter(hobbs_time__lte=datetime) \
            .filter(tail=tail) \
            .filter(type=Hobbs.TYPE_ACTUAL) \
            .order_by('-hobbs_time') \
            .first()

    @classmethod
    def get_projected_value(cls, tail, datetime, revision):
        latest_actual_hobbs = cls.get_last_actual_hobbs(tail, datetime)
        projected_hobbs_value = latest_actual_hobbs.hobbs if latest_actual_hobbs else 0

        if latest_actual_hobbs:
            assignments_after = Assignment.objects.filter(start_time__gt=latest_actual_hobbs.hobbs_time) \
                .filter(start_time__lte=datetime) \
                .filter(tail=tail) \
                .filter(revision=revision) \
                .select_related('flight')
        else:
            assignments_after = Assignment.objects.filter(start_time__lte=datetime) \
                .filter(tail=tail) \
                .filter(revision=revision) \
                .select_related('flight')

        for assignment in assignments_after:
            if assignment.flight:
                projected_hobbs_value += assignment.flight.length / 3600

        return projected_hobbs_value

    @classmethod
    def get_next_due(cls, tail, datetime):
        return cls.objects.filter(hobbs_time__lt=datetime) \
            .filter(tail=tail) \
            .filter(type=Hobbs.TYPE_NEXT_DUE) \
            .order_by('-hobbs_time') \
            .first()

    @classmethod
    def get_next_due_value(cls, tail, datetime):
        next_due_hobbs = cls.objects.filter(hobbs_time__lt=datetime) \
            .filter(tail=tail) \
            .filter(type=Hobbs.TYPE_NEXT_DUE) \
            .order_by('-hobbs_time') \
            .first()
        return next_due_hobbs.hobbs if next_due_hobbs else 0
