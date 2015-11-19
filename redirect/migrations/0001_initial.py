# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Redirect',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('source', models.CharField(max_length=500)),
                ('destination', models.CharField(max_length=500)),
                ('is_logged', models.BooleanField(default=True)),
                ('is_active', models.BooleanField(default=True, help_text=b'If False, then the redirect will give a 404 instead.')),
            ],
        ),
    ]
