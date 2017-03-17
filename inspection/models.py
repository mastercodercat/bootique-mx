from __future__ import unicode_literals

from django.db import models

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

    @property
    def target_name(self):
        if self.target is None:
            return ''
        else:
            target_choice_item = None
            for item in Inspection.INSPECTION_TARGET_CHOICES:
                if item[0] == self.target:
                    target_choice_item = item
                    break
            return target_choice_item[1] if target_choice_item else ''


class InspectionProgram(models.Model):
    name = models.CharField(max_length=100, blank=True)

    class Meta:
        db_table = 'inspection_program'

    def __unicode__(self):
        return self.name
