# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2017-03-29 13:47
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('routeplanning', '0007_auto_20170329_1347'),
    ]

    operations = [
        migrations.AlterField(
            model_name='assignment',
            name='tail',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='routeplanning.Tail'),
        ),
    ]
