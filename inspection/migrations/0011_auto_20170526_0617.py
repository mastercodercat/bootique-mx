# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2017-05-26 13:17
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('inspection', '0010_auto_20170526_0605'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='inspectioncomponenttemplate',
            name='inspection_task',
        ),
        migrations.DeleteModel(
            name='InspectionComponentTemplate',
        ),
    ]
