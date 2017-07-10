# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2017-06-06 13:31
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('routeplanning', '0023_auto_20170531_0233'),
    ]

    operations = [
        migrations.CreateModel(
            name='Revision',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField()),
            ],
        ),
        migrations.AddField(
            model_name='assignment',
            name='revision',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, to='routeplanning.Revision'),
        ),
    ]
