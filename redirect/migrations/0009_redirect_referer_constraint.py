# -*- coding: utf-8 -*-
# Generated by Django 1.9.2 on 2017-03-28 09:04
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('redirect', '0008_statistic_user_agent'),
    ]

    operations = [
        migrations.AddField(
            model_name='redirect',
            name='referer_constraint',
            field=models.CharField(blank=True, max_length=200),
        ),
    ]
