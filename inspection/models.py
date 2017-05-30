from __future__ import unicode_literals

from django.db import models

from common.helpers import *


class InspectionTask(models.Model):
    TARGET_AIRCRAFT = 1
    TARGET_AIRFRAME = 2
    TARGET_PROPELLER = 3
    TARGET_ENGINE = 4
    TARGET_STRINGS = ('', 'Aircraft', 'Airframe', 'Propeller', 'Engine')
    INSPECTION_TARGET_CHOICES = (
        (TARGET_AIRCRAFT, TARGET_STRINGS[TARGET_AIRCRAFT]),
        (TARGET_AIRFRAME, TARGET_STRINGS[TARGET_AIRFRAME]),
        (TARGET_PROPELLER, TARGET_STRINGS[TARGET_PROPELLER]),
        (TARGET_ENGINE, TARGET_STRINGS[TARGET_ENGINE]),
    )

    number = models.IntegerField(null=False, blank=False)
    name = models.CharField(max_length=100, blank=False)

    target = models.IntegerField(default=1, choices=INSPECTION_TARGET_CHOICES)

    class Meta:
        db_table = 'inspection_task'

    def __unicode__(self):
        return ndigits(self.number, 2) + ' - ' + self.name

    @property
    def target_name(self):
        target_choice_item = None
        for item in InspectionTask.INSPECTION_TARGET_CHOICES:
            if item[0] == self.target:
                target_choice_item = item
                break
        return target_choice_item[1] if target_choice_item else ''


class InspectionProgram(models.Model):
    name = models.CharField(max_length=100, blank=False)

    inspection_tasks = models.ManyToManyField(InspectionTask)

    class Meta:
        db_table = 'inspection_program'

    def __unicode__(self):
        return self.name


class InspectionComponent(models.Model):
    pn = models.CharField(max_length=30, blank=False)
    sn = models.CharField(max_length=30, blank=False)
    name = models.CharField(max_length=100, blank=False)

    inspection_task = models.ForeignKey('InspectionTask', null=True, blank=False)

    class Meta:
        db_table = 'inspection_component'

    def __unicode__(self):
        return self.name

