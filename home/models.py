from __future__ import unicode_literals

from django.db import models

from django.db import models
from django.contrib.auth.models import User


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

    type = models.ForeignKey('AircraftType', null=True, blank=False)

    class Meta:
        db_table = 'aircraft'

    def __unicode__(self):
        return self.reg


class Airframe(models.Model):
    total_hours = models.IntegerField(default=0, null=True, blank=True)
    reported_hours = models.IntegerField(default=0, null=True, blank=True)
    reported_landings = models.IntegerField(default=0, null=True, blank=True)
    last_inspection_time = models.DateTimeField(blank=True)
    time_between_inspections = models.IntegerField(default=0, null=True, blank=True)

    aircraft = models.OneToOneField('Aircraft', null=True, blank=False)

    class Meta:
        db_table = 'airframe'


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


class Propeller(models.Model):
    last_inspection_time = models.DateTimeField(blank=True)

    aircraft = models.ForeignKey('Aircraft', null=True, blank=False)

    class Meta:
        db_table = 'propeller'
