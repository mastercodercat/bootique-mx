from __future__ import unicode_literals

from django.db import models
from django.db.models import Q, Sum


class Tail(models.Model):
    number = models.CharField(max_length=20, blank=True, unique=True)

    def __unicode__(self):
        return self.number


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

    flight = models.OneToOneField(Flight, null=True, blank=False, on_delete=models.PROTECT)
    tail = models.ForeignKey(Tail, null=True, blank=False, on_delete=models.PROTECT)

    def __unicode__(self):
        if self.status == Assignment.STATUS_FLIGHT:
            return 'Flight ' + str(self.flight_number) + ' Assignment'
        elif self.status == Assignment.STATUS_MAINTENANCE:
            return 'Maintenance'
        elif self.status == Assignment.STATUS_UNSCHEDULED_FLIGHT:
            return 'Unscheduled Flight'
        else:
            return 'Other'

    @classmethod
    def is_duplicated(cls, tail, start_time, end_time, exclude_check_assignment=None):
        query = cls.objects.filter(
            Q(tail=tail) &
            (
                (Q(start_time__lte=start_time) & Q(end_time__gt=start_time)) |
                (Q(start_time__lt=end_time) & Q(end_time__gte=end_time)) |
                (Q(start_time__gte=start_time) & Q(end_time__lte=end_time))
            )
        )
        if exclude_check_assignment:
            query = query.exclude(pk=exclude_check_assignment.id)
        dup_count = query.count()
        if dup_count > 0:
            return True

        return False

    @classmethod
    def is_physically_valid(cls, tail, origin, destination, start_time, end_time, exclude_check_assignment=None):
        query = cls.objects.filter(
                Q(tail=tail) &
                Q(end_time__lte=start_time)
            ) \
            .exclude(status=Assignment.STATUS_MAINTENANCE) \
            .order_by('-start_time') \
            .select_related('flight')
        if exclude_check_assignment:
            query = query.exclude(pk=exclude_check_assignment.id)
        assignment_just_before = query.first()
        if assignment_just_before and assignment_just_before.flight.destination != origin:
            return False

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
            return False

        return True

    @classmethod
    def get_duplicated_assignments(cls, tail, start_time, end_time, exclude_check_assignment=None):
        query = cls.objects.filter(
            Q(tail=tail) &
            (
                (Q(start_time__lte=start_time) & Q(end_time__gt=start_time)) |
                (Q(start_time__lt=end_time) & Q(end_time__gte=end_time)) |
                (Q(start_time__gte=start_time) & Q(end_time__lte=end_time))
            )
        )
        if exclude_check_assignment:
            query = query.exclude(pk=exclude_check_assignment.id)
        return query.all()

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
    flight = models.OneToOneField(Flight, null=True, blank=False, on_delete=models.PROTECT)

    def __unicode__(self):
        return 'Hobbs of ' + self.tail.number + ' on date ' + self.hobbs_time.strftime("%F")

    @classmethod
    def get_hobbs(cls, tail, start_time, end_time):
        return cls.objects.filter(hobbs_time__gte=start_time) \
            .filter(hobbs_time__lt=end_time) \
            .filter(tail=tail) \
            .order_by('hobbs_time') \
            .select_related('flight') \
            .all()

    @classmethod
    def get_projected_actual_value(cls, tail, datetime):
        result = cls.objects.filter(hobbs_time__lt=datetime) \
            .filter(tail=tail) \
            .filter(type=Hobbs.TYPE_ACTUAL) \
            .aggregate(Sum('hobbs'))
        return result['hobbs__sum'] if result and result['hobbs__sum'] else 0

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
