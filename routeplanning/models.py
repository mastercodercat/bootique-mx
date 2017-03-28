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


class FlightAssignment(models.Model):
    flight_number = models.IntegerField(default=0, null=False, blank=False)
    departure_datetime = models.DateTimeField(null=False, blank=False)

    flight = models.ForeignKey(Flight, null=True, blank=False)
    tail = models.ForeignKey(Tail, null=True, blank=False)

    def __unicode__(self):
        return str(flight_number) + ' Assignment'
