# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('p365', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='result',
            name='description',
            field=models.CharField(null=True, max_length=400),
            preserve_default=True,
        ),
    ]
