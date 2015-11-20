# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('redirect', '0004_auto_20151120_1706'),
    ]

    operations = [
        migrations.AlterField(
            model_name='redirect',
            name='source',
            field=models.CharField(unique=True, max_length=500),
        ),
    ]
