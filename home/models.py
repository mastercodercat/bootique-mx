from __future__ import unicode_literals

from django.db import models
from django.contrib.auth.models import User
from datetime import datetime, timedelta

from home.helpers import datetime_now_utc


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

    type = models.ForeignKey('AircraftType', null=True, blank=False)
    inspection_program = models.ForeignKey('InspectionProgram', null=True, blank=False)

    class Meta:
        db_table = 'aircraft'

    def __unicode__(self):
        return self.reg


class Airframe(models.Model):
    total_hours = models.IntegerField(default=0)
    reported_hours = models.IntegerField(default=0)
    reported_landings = models.IntegerField(default=0)
    last_inspection_time = models.DateTimeField(null=True, blank=True)

    aircraft = models.OneToOneField('Aircraft', null=True, blank=False)

    class Meta:
        db_table = 'airframe'

    @property
    def time_between_inspections(self):
        return 120

    @property
    def next_inspection_time(self):
        return self.last_inspection_time + timedelta(days=75)

    @classmethod
    def past_due_count(cls):
        dt_now = datetime_now_utc()
        return Airframe.objects.filter(last_inspection_time__lte=dt_now-timedelta(days=75)).count()

    @classmethod
    def threshold_count(cls):
        dt_now = datetime_now_utc()
        return Airframe.objects.filter(
            last_inspection_time__gte=dt_now-timedelta(days=75), 
            last_inspection_time__lte=dt_now-timedelta(days=65)
        ).count()

    @classmethod
    def coming_due_count(cls):
        dt_now = datetime_now_utc()
        return Airframe.objects.filter(last_inspection_time__gte=dt_now-timedelta(days=75-10)).count()


class Engine(models.Model):
    date = models.DateField(blank=True)
    engine_hours = models.IntegerField(default=0, null=True, blank=True)
    engine_cycles = models.IntegerField(default=0, null=True, blank=True)
    last_hot_section_time = models.DateTimeField(blank=True)
    last_overhaul_time = models.DateTimeField(blank=True)
    tbo = models.IntegerField(default=0, null=True, blank=True)

    aircraft = models.ForeignKey('Aircraft', null=True, blank=False)

    class Meta:
        db_table = 'engine'

    @property
    def next_inspection_time(self):
        return self.last_hot_section_time + timedelta(days=90)


class Propeller(models.Model):
    last_inspection_time = models.DateTimeField(blank=True)

    aircraft = models.ForeignKey('Aircraft', null=True, blank=False)

    class Meta:
        db_table = 'propeller'

    @property
    def next_inspection_time(self):
        return self.last_inspection_time + timedelta(days=90)


class Inspection(models.Model):
    name = models.CharField(max_length=100, blank=True)
    INSPECTION_TARGET_CHOICES = (
        (1, 'Aircraft'),
        (2, 'Airframe'),
        (3, 'Engine'),
        (4, 'Propeller'),
    )
    target = models.IntegerField(default=1, choices=INSPECTION_TARGET_CHOICES)
    interval = models.IntegerField(default=0)
    interval_unit = models.CharField(max_length=10, default='hours')

    inspection_program = models.ForeignKey('InspectionProgram', null=True, blank=False)

    class Meta:
        db_table = 'inspection'

    def __unicode__(self):
        return self.name


class InspectionProgram(models.Model):
    name = models.CharField(max_length=100, blank=True)

    class Meta:
        db_table = 'inspection_program'

    def __unicode__(self):
        return self.name


class AircraftInspectionRecord(models.Model):
    aircraft = models.ForeignKey('Aircraft', null=True, blank=False)
    inspection = models.ForeignKey('Inspection', null=True, blank=False)

    target = models.CharField(max_length=1, choices=Inspection.INSPECTION_TARGET_CHOICES) # redundance field of inspection.target for performance
    inspection_date = models.DateTimeField(blank=True)

    class Meta:
        db_table = 'aircraft_inspection_record'

    def __unicode__(self):
        return self.name
