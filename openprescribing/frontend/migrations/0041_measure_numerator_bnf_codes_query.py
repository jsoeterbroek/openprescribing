# -*- coding: utf-8 -*-
# Generated by Django 1.11.18 on 2019-01-19 22:23
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('frontend', '0040_merge_20190119_2222'),
    ]

    operations = [
        migrations.AddField(
            model_name='measure',
            name='numerator_bnf_codes_query',
            field=models.CharField(max_length=10000, null=True),
        ),
    ]