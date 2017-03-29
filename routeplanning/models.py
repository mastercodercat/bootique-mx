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


class LinePart(models.Model):
    name = models.CharField(max_length=10, blank=False)
    number = models.IntegerField(default=0, null=False, blank=False)

    line = models.ForeignKey(Line, null=True, blank=False)

    def __unicode__(self):
        return self.name


class Flight(models.Model):
    number = models.IntegerField(default=0, null=False, blank=False)
    origin = models.CharField(max_length=10, blank=False)
    destination = models.CharField(max_length=10, blank=False)
    departure_time = models.TimeField(auto_now=True, null=False, blank=False)
    arrival_time = models.TimeField(auto_now=True, null=False, blank=False)
    weekly_availability = models.CharField(default='XXXXXXX', max_length=7, blank=False)

    line = models.ForeignKey(Line, null=True, blank=False)

    def __unicode__(self):
        return str(self.number) + '. ' + self.origin + '-' + self.destination

    def is_available_on_weekday(self, weekday):
        weekday %= 7
        return (self.weekly_availability[weekday:(weekday + 1)] == 'X')

    def is_available_on_weekday_period(self, start, end):
        start %= 7
        end %= 7
        if end < start:     # It's possible that end weekday is smaller than start
            end += 7
        for weekday in range(start, end + 1):
            if self.is_available_on_weekday(weekday):
                return True
        return False

    @property
    def length(self):
        arv_sec = self.arrival_time.hour * 3600 + self.arrival_time.minute * 60 + self.arrival_time.second
        dpt_sec = self.departure_time.hour * 3600 + self.departure_time.minute * 60 + self.departure_time.second
        return (arv_sec - dpt_sec) % 86400


class Assignment(models.Model):
    STATUS_CHOICES = (
        (1, 'Flight'),
        (2, 'Maintenance'),
    )

    flight_number = models.IntegerField(default=0, null=False, blank=False)
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
            end_time__gte=start_time
        ).count()

        return dup_count > 0
