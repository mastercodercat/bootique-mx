# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2017-03-27 09:34
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('routeplanning', '0003_flight'),
    ]

    operations = [
        migrations.AddField(
            model_name='flight',
            name='weekly_availability',
            field=models.CharField(default='XXXXXXX', max_length=7),
        ),
    ]
