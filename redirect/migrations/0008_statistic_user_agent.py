# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('redirect', '0007_auto_20151120_2110'),
    ]

    operations = [
        migrations.AddField(
            model_name='statistic',
            name='user_agent',
            field=models.CharField(max_length=250, blank=True),
        ),
    ]
