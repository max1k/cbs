# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('p311', '0003_auto_20150323_1217'),
    ]

    operations = [
        migrations.RenameField(
            model_name='commoninfo',
            old_name='date',
            new_name='mod_date',
        ),
        migrations.AddField(
            model_name='commoninfo',
            name='doc_date',
            field=models.DateField(null=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='result',
            name='description',
            field=models.CharField(null=True, max_length=250),
            preserve_default=True,
        ),
    ]
