# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('redirect', '0002_redirect_extra_info'),
    ]

    operations = [
        migrations.CreateModel(
            name='TotalStats',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('accesses', models.BigIntegerField(default=0)),
                ('last_access', models.DateTimeField(auto_now=True)),
                ('redir', models.ForeignKey(to='redirect.Redirect')),
            ],
        ),
    ]
