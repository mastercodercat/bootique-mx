from __future__ import unicode_literals

from django.db import models

from common.helpers import *


class InspectionTask(models.Model):
    number = models.IntegerField(null=False, blank=False)
    name = models.CharField(max_length=100, blank=True)
    INSPECTION_TARGET_CHOICES = (
        (1, 'Aircraft'),
        (2, 'Airframe'),
        (3, 'Propeller'),
        (4, 'Engine'),
    )
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
    name = models.CharField(max_length=100, blank=True)

    inspection_tasks = models.ManyToManyField(InspectionTask)

    class Meta:
        db_table = 'inspection_program'

    def __unicode__(self):
        return self.name


class InspectionComponent(models.Model):
    pn = models.CharField(max_length=30, blank=True)
    sn = models.CharField(max_length=30, blank=True)
    name = models.CharField(max_length=100, blank=True)

    inspection_task = models.ForeignKey('InspectionTask', null=True, blank=False)

    class Meta:
        db_table = 'inspection_component'

    def __unicode__(self):
        return self.name

