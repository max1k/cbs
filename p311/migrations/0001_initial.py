# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='CommonInfo',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, verbose_name='ID', auto_created=True)),
                ('name', models.CharField(max_length=100)),
                ('date', models.DateField(auto_now=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Files',
            fields=[
                ('commoninfo_ptr', models.OneToOneField(parent_link=True, auto_created=True, to='p311.CommonInfo', serialize=False, primary_key=True)),
                ('orgname', models.CharField(max_length=100)),
            ],
            options={
            },
            bases=('p311.commoninfo',),
        ),
        migrations.CreateModel(
            name='Results',
            fields=[
                ('commoninfo_ptr', models.OneToOneField(parent_link=True, auto_created=True, to='p311.CommonInfo', serialize=False, primary_key=True)),
                ('service', models.CharField(max_length=3)),
                ('result', models.BooleanField(default=False)),
                ('description', models.CharField(max_length=250)),
                ('src_file', models.ForeignKey(to='p311.Files')),
            ],
            options={
            },
            bases=('p311.commoninfo',),
        ),
    ]
