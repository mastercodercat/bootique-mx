# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2017-05-03 19:15
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('routeplanning', '0016_auto_20170428_1236'),
    ]

    operations = [
        migrations.CreateModel(
            name='Hobbs',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('hobbs_time', models.DateTimeField()),
                ('type', models.IntegerField(choices=[(1, 'Actual'), (2, 'Next Due')], default=1)),
                ('name', models.CharField(blank=True, max_length=30)),
                ('tail', models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, to='routeplanning.Tail')),
            ],
        ),
    ]
