# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('p311', '0002_auto_20150323_1201'),
    ]

    operations = [
        migrations.RenameField(
            model_name='result',
            old_name='result',
            new_name='processed',
        ),
    ]
