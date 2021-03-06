# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2017-07-10 16:36
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('routeplanning', '0031_auto_20170710_0846'),
    ]

    operations = [
        migrations.RenameField(
            model_name='flight',
            old_name='arrival_datetime',
            new_name='scheduled_in_datetime',
        ),
        migrations.RenameField(
            model_name='flight',
            old_name='departure_datetime',
            new_name='scheduled_out_datetime',
        ),
        migrations.AlterField(
            model_name='flight',
            name='scheduled_in_datetime',
            field=models.DateTimeField(default=None, null=True, blank=False),
        ),
        migrations.AlterField(
            model_name='flight',
            name='scheduled_out_datetime',
            field=models.DateTimeField(default=None, null=True, blank=False),
        ),
    ]
