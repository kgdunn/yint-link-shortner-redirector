# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('redirect', '0003_totalstats'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='totalstats',
            options={'verbose_name_plural': 'Total Stats'},
        ),
        migrations.AddField(
            model_name='redirect',
            name='status_code',
            field=models.SmallIntegerField(default=302),
        ),
    ]
