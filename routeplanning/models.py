from __future__ import unicode_literals

from django.db import models
from django.db.models import Q


class Tail(models.Model):
    number = models.CharField(max_length=20, blank=True)

    def __unicode__(self):
        return self.number


class Line(models.Model):
    name = models.CharField(max_length=100, blank=True)

    def __unicode__(self):
        return self.name

    @property
    def flights(self):
        line_parts = self.linepart_set.all().values('number')
        flight_numbers = [lp['number'] for lp in line_parts]
        return Flight.objects.filter(number__in=flight_numbers)


class LinePart(models.Model):
    number = models.CharField(default='', max_length=10, null=False, blank=False)

    line = models.ForeignKey(Line, null=True, blank=False)

    def __unicode__(self):
        return self.number


class Flight(models.Model):
    number = models.CharField(db_index=True, max_length=10, default=0, null=False, blank=False)
    origin = models.CharField(max_length=10, blank=False)
    destination = models.CharField(max_length=10, blank=False)
    departure_datetime = models.DateTimeField(null=False, blank=False)
    arrival_datetime = models.DateTimeField(null=False, blank=False)

    # line = models.ForeignKey(Line, null=True, blank=False)

    def __unicode__(self):
        return str(self.number) + '. ' + self.origin + '-' + self.destination

    @property
    def length(self):
        return (self.arrival_datetime - self.departure_datetime).total_seconds()

    def get_assignment(self):
        try:
            return self.assignment
        except:
            return None


class Assignment(models.Model):
    STATUS_CHOICES = (
        (1, 'Flight'),
        (2, 'Maintenance'),
        (3, 'Unscheduled Flight'),
    )

    flight_number = models.CharField(max_length=10, default='', null=False, blank=False)
    start_time = models.DateTimeField(null=False, blank=False)
    end_time = models.DateTimeField(null=False, blank=False)
    status = models.IntegerField(default=1, choices=STATUS_CHOICES)

    flight = models.OneToOneField(Flight, null=True, blank=False, on_delete=models.PROTECT)
    tail = models.ForeignKey(Tail, null=True, blank=False, on_delete=models.PROTECT)

    def __unicode__(self):
        if self.status == 1:
            return 'Flight ' + str(self.flight_number) + ' Assignment'
        elif self.status == 2:
            return 'Maintenance'
        elif self.status == 3:
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
    TYPE_CHOICES = (
        (1, 'Actual'),
        (2, 'Next Due'),
    )

    hobbs_time = models.DateTimeField(null=False, blank=False)
    type = models.IntegerField(default=1, choices=TYPE_CHOICES)
    hobbs = models.FloatField(default=0.0, blank=False)
    tail = models.ForeignKey(Tail, null=True, blank=False, on_delete=models.PROTECT)

    def __unicode__(self):
        return 'Hobbs of ' + self.tail.number + ' on date ' + self.hobbs_time.strftime("%F")

    @classmethod
    def get_hobbs(cls, start_time, end_time):
        return cls.objects.filter(hobbs_time__gte=start_time) \
            .filter(hobbs_time__lt=end_time) \
            .order_by('hobbs_time') \
            .all()

    @classmethod
    def get_last_entered_hobbs(cls, type, datetime):
        return cls.objects.filter(hobbs_time__lt=datetime) \
            .filter(type=type) \
            .order_by('-hobbs_time') \
            .first()
