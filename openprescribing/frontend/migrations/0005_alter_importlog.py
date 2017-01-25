# -*- coding: utf-8 -*-
# Generated by Django 1.9.1 on 2016-06-23 10:05
from __future__ import unicode_literals

from django.db import migrations, models
from frontend.models import ImportLog


def seed_log(apps, schema_editor):
    ImportLog.objects.create(
        current_at='2016-03-01',
        filename='dummy-initial-value',
        category='patient_list_size')


class Migration(migrations.Migration):

    dependencies = [
        ('frontend', '0004_importlog'),
    ]

    operations = []