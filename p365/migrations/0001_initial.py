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
                ('id', models.AutoField(primary_key=True, auto_created=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('mod_date', models.DateField(auto_now=True)),
                ('doc_date', models.DateField(null=True)),
                ('prefix', models.CharField(max_length=6, null=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='File',
            fields=[
                ('commoninfo_ptr', models.OneToOneField(serialize=False, auto_created=True, primary_key=True, parent_link=True, to='p365.CommonInfo')),
                ('orgname', models.CharField(max_length=100)),
            ],
            options={
            },
            bases=('p365.commoninfo',),
        ),
        migrations.CreateModel(
            name='Result',
            fields=[
                ('commoninfo_ptr', models.OneToOneField(serialize=False, auto_created=True, primary_key=True, parent_link=True, to='p365.CommonInfo')),
                ('processed', models.BooleanField(default=False)),
                ('description', models.CharField(max_length=250, null=True)),
            ],
            options={
            },
            bases=('p365.commoninfo',),
        ),
        migrations.CreateModel(
            name='Sent',
            fields=[
                ('commoninfo_ptr', models.OneToOneField(serialize=False, auto_created=True, primary_key=True, parent_link=True, to='p365.CommonInfo')),
                ('in_file', models.ForeignKey(to='p365.File')),
            ],
            options={
            },
            bases=('p365.commoninfo',),
        ),
        migrations.AddField(
            model_name='result',
            name='out_file',
            field=models.ForeignKey(to='p365.Sent'),
            preserve_default=True,
        ),
    ]
