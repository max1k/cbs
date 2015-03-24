# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('p311', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Result',
            fields=[
                ('commoninfo_ptr', models.OneToOneField(auto_created=True, serialize=False, parent_link=True, to='p311.CommonInfo', primary_key=True)),
                ('service', models.CharField(max_length=3)),
                ('result', models.BooleanField(default=False)),
                ('description', models.CharField(max_length=250)),
            ],
            options={
            },
            bases=('p311.commoninfo',),
        ),
        migrations.RenameModel(
            old_name='Files',
            new_name='File',
        ),
        migrations.RemoveField(
            model_name='results',
            name='commoninfo_ptr',
        ),
        migrations.RemoveField(
            model_name='results',
            name='src_file',
        ),
        migrations.DeleteModel(
            name='Results',
        ),
        migrations.AddField(
            model_name='result',
            name='src_file',
            field=models.ForeignKey(to='p311.File'),
            preserve_default=True,
        ),
    ]
