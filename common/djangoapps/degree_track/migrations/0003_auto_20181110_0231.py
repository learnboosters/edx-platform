# -*- coding: utf-8 -*-
# Generated by Django 1.11.15 on 2018-11-10 07:31
from __future__ import unicode_literals

from django.db import migrations, models
import opaque_keys.edx.django.models


class Migration(migrations.Migration):

    dependencies = [
        ('degree_track', '0002_auto_20181110_0120'),
    ]

    operations = [
        migrations.CreateModel(
            name='Degree',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('course_id', opaque_keys.edx.django.models.CourseKeyField(db_index=True, max_length=255)),
                ('name', models.CharField(max_length=255, verbose_name='Course Name')),
            ],
            options={
                'ordering': ('name',),
                'verbose_name': 'Degree Course',
                'verbose_name_plural': 'Degree Courses',
            },
        ),
        migrations.AlterField(
            model_name='degreetrack',
            name='courses',
            field=models.ManyToManyField(to='degree_track.Degree'),
        ),
    ]
