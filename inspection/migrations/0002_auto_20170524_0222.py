# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2017-05-24 09:22
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inspection', '0001_initial'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='Inspection',
            new_name='InspectionTask',
        ),
        migrations.AddField(
            model_name='inspectionprogram',
            name='number',
            field=models.IntegerField(default=0),
            preserve_default=False,
        ),
    ]
