# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('redirect', '0005_auto_20151120_1709'),
    ]

    operations = [
        migrations.CreateModel(
            name='Statistic',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('referrer', models.CharField(max_length=250, blank=True)),
                ('ip_address', models.IPAddressField(null=True, blank=True)),
                ('accessed', models.DateTimeField(auto_now=True)),
                ('redir', models.ForeignKey(to='redirect.Redirect')),
            ],
        ),
    ]
