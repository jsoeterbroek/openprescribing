# -*- coding: utf-8 -*-
# Generated by Django 1.9.1 on 2017-12-13 14:10


from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('dmd', '0007_auto_20171213_1355'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='ncsoconcession',
            name='year_and_month',
        ),
    ]