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


# class Route(models.Model):
#     name = models.CharField(max_length=100, blank=True)

#     def __unicode__(self):
#         return self.name
