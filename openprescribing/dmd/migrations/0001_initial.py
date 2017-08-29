# -*- coding: utf-8 -*-
# Generated by Django 1.9.1 on 2017-06-14 13:07
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='AvailabilityRestriction',
            fields=[
                ('cd', models.IntegerField(primary_key=True, serialize=False)),
                ('desc', models.CharField(max_length=50)),
            ],
            options={
                'db_table': 'dmd_lookup_availability_restriction',
            },
        ),
        migrations.CreateModel(
            name='ControlledDrugCategory',
            fields=[
                ('cd', models.IntegerField(primary_key=True, serialize=False)),
                ('desc', models.CharField(max_length=50)),
            ],
            options={
                'db_table': 'dmd_lookup_control_drug_category',
            },
        ),
        migrations.CreateModel(
            name='DMDProduct',
            fields=[
                ('dmdid', models.BigIntegerField(primary_key=True, serialize=False)),
                ('bnf_code', models.CharField(db_index=True, max_length=15, null=True)),
                ('vpid', models.BigIntegerField(db_index=True, unique=True)),
                ('name', models.CharField(max_length=40)),
                ('full_name', models.TextField(null=True)),
                ('ema', models.CharField(max_length=15, null=True)),
                ('concept_class', models.IntegerField(db_index=True, null=True)),
                ('product_type', models.IntegerField(null=True)),
                ('is_in_nurse_formulary', models.NullBooleanField(db_column='nurse_f')),
                ('is_in_dentist_formulary', models.NullBooleanField(db_column='dent_f')),
                ('product_order_no', models.TextField(db_column='prod_order_no', null=True)),
                ('is_blacklisted', models.NullBooleanField(db_column='sched_1')),
                ('is_schedule_2', models.NullBooleanField(db_column='sched_2')),
                ('can_have_personal_administration_fee', models.NullBooleanField(db_column='padm')),
                ('is_fp10', models.NullBooleanField(db_column='fp10_mda')),
                ('is_borderline_substance', models.NullBooleanField(db_column='acbs')),
                ('has_assorted_flavours', models.NullBooleanField(db_column='assort_flav')),
                ('is_imported', models.NullBooleanField(db_column='flag_imported')),
                ('is_broken_bulk', models.NullBooleanField(db_column='flag_broken_bulk')),
                ('is_non_bioequivalent', models.NullBooleanField(db_column='flag_non_bioequivalence')),
                ('is_special_container', models.NullBooleanField(db_column='flag_special_containers')),
                ('availability_restrictions', models.ForeignKey(db_column='avail_restrictcd', null=True, on_delete=django.db.models.deletion.CASCADE, to='dmd.AvailabilityRestriction')),
                ('controlled_drug_category', models.ForeignKey(db_column='catcd', null=True, on_delete=django.db.models.deletion.CASCADE, to='dmd.ControlledDrugCategory')),
            ],
            options={
                'db_table': 'dmd_product',
            },
        ),
        migrations.CreateModel(
            name='Prescribability',
            fields=[
                ('cd', models.IntegerField(primary_key=True, serialize=False)),
                ('desc', models.CharField(max_length=50)),
            ],
            options={
                'db_table': 'dmd_lookup_virtual_product_pres_status',
            },
        ),
        migrations.CreateModel(
            name='TariffCategory',
            fields=[
                ('cd', models.IntegerField(primary_key=True, serialize=False)),
                ('desc', models.CharField(max_length=50)),
            ],
            options={
                'db_table': 'dmd_lookup_dt_payment_category',
            },
        ),
        migrations.CreateModel(
            name='VMPNonAvailability',
            fields=[
                ('cd', models.IntegerField(primary_key=True, serialize=False)),
                ('desc', models.CharField(max_length=50)),
            ],
            options={
                'db_table': 'dmd_lookup_virtual_product_non_avail',
            },
        ),
        migrations.AddField(
            model_name='dmdproduct',
            name='prescribability',
            field=models.ForeignKey(db_column='pres_statcd', null=True, on_delete=django.db.models.deletion.CASCADE, to='dmd.Prescribability'),
        ),
        migrations.AddField(
            model_name='dmdproduct',
            name='tariff_category',
            field=models.ForeignKey(db_column='tariff_category', null=True, on_delete=django.db.models.deletion.CASCADE, to='dmd.TariffCategory'),
        ),
        migrations.AddField(
            model_name='dmdproduct',
            name='vmp_non_availability',
            field=models.ForeignKey(db_column='non_availcd', null=True, on_delete=django.db.models.deletion.CASCADE, to='dmd.VMPNonAvailability'),
        ),
    ]