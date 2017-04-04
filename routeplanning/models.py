from __future__ import unicode_literals

from django.db import models


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
        return self.name


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


class Assignment(models.Model):
    STATUS_CHOICES = (
        (1, 'Flight'),
        (2, 'Maintenance'),
    )

    flight_number = models.CharField(max_length=10, default='', null=False, blank=False)
    start_time = models.DateTimeField(null=False, blank=False)
    end_time = models.DateTimeField(null=False, blank=False)
    status = models.IntegerField(default=1, choices=STATUS_CHOICES)

    flight = models.ForeignKey(Flight, null=True, blank=False)
    tail = models.ForeignKey(Tail, null=True, blank=False)

    def __unicode__(self):
        if self.status == 1:
            return 'Flight ' + str(self.flight_number) + ' Assignment'
        elif self.status == 2:
            return 'Maintenance'
        else:
            return 'Other'

    @classmethod
    def is_duplicated(cls, tail, start_time):
        dup_count = cls.objects.filter(
            tail=tail,
            start_time__lte=start_time,
            end_time__gt=start_time
        ).count()

        return dup_count > 0
