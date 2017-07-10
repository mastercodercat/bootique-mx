# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2017-07-10 13:25
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('routeplanning', '0029_auto_20170710_0624'),
    ]

    operations = [
        migrations.AddField(
            model_name='assignment',
            name='estimated_in_datetime',
            field=models.DateTimeField(null=True),
        ),
        migrations.AddField(
            model_name='assignment',
            name='estimated_off_datetime',
            field=models.DateTimeField(null=True),
        ),
        migrations.AddField(
            model_name='assignment',
            name='estimated_on_datetime',
            field=models.DateTimeField(null=True),
        ),
        migrations.AddField(
            model_name='assignment',
            name='estimated_out_datetime',
            field=models.DateTimeField(null=True),
        ),
    ]
