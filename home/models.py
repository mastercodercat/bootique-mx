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
