# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('redirect', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='redirect',
            name='extra_info',
            field=models.CharField(max_length=200, blank=True),
        ),
    ]
