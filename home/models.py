from __future__ import unicode_literals

from django.db import models
from django.contrib.auth.models import User
from datetime import datetime, timedelta

from home.helpers import datetime_now_utc
from inspection.models import *


class UserProfile(models.Model):
    user = models.OneToOneField(User, null=True, blank=True, related_name='userprofile')
    is_admin = models.BooleanField(default=False, blank=True)

    # Todo: Consider cascading deletion of personal_data
    personal_data = models.OneToOneField('PersonalData', null=True, blank=True)

    @property
    def full_name(self):
        return "%s %s" % (self.personal_data.first_name, self.personal_data.last_name)

    class Meta:
        db_table = 'user_profile'

    def __unicode__(self):
        return self.personal_data.first_name + " " + self.personal_data.last_name


class PersonalData(models.Model):
    first_name = models.CharField(max_length=200, blank=True)
    last_name = models.CharField(max_length=200, blank=True)
    email = models.CharField(max_length=500, blank=True)
    onsip = models.IntegerField(default=0, null=True, blank=True)

    # Todo: Add Profile Image

    class Meta:
        db_table = 'personal_data'

    def __unicode__(self):
        return self.first_name + " " + self.last_name


class AircraftType(models.Model):
    type = models.CharField(max_length=50, blank=True)

    class Meta:
        db_table = "aircraft_type"

    def __unicode__(self):
        return self.type


class Aircraft(models.Model):
    reg = models.CharField(max_length=20)
    serial = models.CharField(max_length=20)
    model = models.CharField(max_length=20)
    reported_date = models.DateTimeField(blank=True)

    type = models.ForeignKey(AircraftType, null=True, blank=False)
    inspection_program = models.ForeignKey(InspectionProgram, null=True, blank=False)

    class Meta:
        db_table = 'aircraft'

    def __unicode__(self):
        return self.reg

    @property
    def inspections(self):
        if self.inspection_program is None:
            return []
        else:
            return self.inspection_program.inspection_set.all().prefetch_related('aircraftinspectionrecord_set')

    @property
    def next_inspection_due(self):
        inspections = self.inspections
        _next_inspection_due = None
        _next_inspection_due_date = None
        for inspection in inspections:
            inspection_records = inspection.aircraftinspectionrecord_set.order_by('-inspection_date').all()
            if not inspection_records:
                _next_inspection_due = inspection
                _next_inspection_due_date = datetime_now_utc()
            else:
                last_record = inspection_records[0]
                next_due_date = last_record.inspection_date + (timedelta(days=inspection.interval) if inspection.interval_unit == 'days' else timedelta(hours=inspection.interval))
                if _next_inspection_due_date is None or next_due_date < _next_inspection_due_date:
                    _next_inspection_due_date = next_due_date
                    _next_inspection_due = inspection

        if _next_inspection_due is None:
            return (inspections[0], datetime_now_utc()) if inspections else None
        return (_next_inspection_due, _next_inspection_due_date)


class Airframe(models.Model):
    total_hours = models.IntegerField(default=0)
    reported_hours = models.IntegerField(default=0)
    reported_landings = models.IntegerField(default=0)
    last_inspection_time = models.DateTimeField(null=True, blank=True)

    aircraft = models.OneToOneField(Aircraft, null=True, blank=False)

    class Meta:
        db_table = 'airframe'

    @property
    def time_between_inspections(self):
        return 120

    @property
    def next_inspection_time(self):
        return self.last_inspection_time + timedelta(days=75)


class Engine(models.Model):
    date = models.DateField(blank=True)
    engine_hours = models.IntegerField(default=0, null=True, blank=True)
    engine_cycles = models.IntegerField(default=0, null=True, blank=True)
    last_hot_section_time = models.DateTimeField(blank=True)
    last_overhaul_time = models.DateTimeField(blank=True)
    tbo = models.IntegerField(default=0, null=True, blank=True)

    aircraft = models.ForeignKey(Aircraft, null=True, blank=False)

    class Meta:
        db_table = 'engine'

    @property
    def next_inspection_time(self):
        return self.last_hot_section_time + timedelta(days=90)


class Propeller(models.Model):
    last_inspection_time = models.DateTimeField(blank=True)

    aircraft = models.ForeignKey(Aircraft, null=True, blank=False)

    class Meta:
        db_table = 'propeller'

    @property
    def next_inspection_time(self):
        return self.last_inspection_time + timedelta(days=90)


class AircraftInspectionRecord(models.Model):
    aircraft = models.ForeignKey(Aircraft, null=True, blank=False)
    inspection = models.ForeignKey(Inspection, null=True, blank=False)

    target = models.CharField(max_length=1, choices=Inspection.INSPECTION_TARGET_CHOICES) # redundance field of inspection.target for performance
    inspection_date = models.DateTimeField(blank=True)

    class Meta:
        db_table = 'aircraft_inspection_record'

    def __unicode__(self):
        return self.name
