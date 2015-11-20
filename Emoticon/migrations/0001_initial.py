# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.core.validators
import Emoticon.models


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Emoticon',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('is_active', models.BooleanField(default=True, editable=False)),
                ('is_published', models.BooleanField(default=False, editable=False)),
                ('icon', models.ImageField(upload_to=Emoticon.models.emoticon_path_finder, verbose_name=b'\xe8\xa1\xa8\xe6\x83\x85')),
                ('description', models.CharField(max_length=255, verbose_name=b'\xe8\xa1\xa8\xe6\x83\x85\xe6\x8f\x8f\xe8\xbf\xb0')),
                ('code', models.CharField(max_length=100, verbose_name=b'\xe7\xbc\x96\xe5\x8f\xb7')),
                ('version_no', models.IntegerField(default=0, verbose_name=b'\xe7\x89\x88\xe6\x9c\xac\xe5\x8f\xb7')),
                ('order_weight', models.IntegerField(default=0, verbose_name=b'\xe6\x8e\x92\xe5\xba\x8f\xe6\x9d\x83\xe9\x87\x8d')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'ordering': ('-order_weight',),
                'verbose_name': '\u8868\u60c5',
                'verbose_name_plural': '\u8868\u60c5',
            },
        ),
        migrations.CreateModel(
            name='EmoticonType',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=128, verbose_name=b'\xe7\xb1\xbb\xe5\x9e\x8b\xe5\x90\x8d\xe7\xa7\xb0')),
                ('version_no', models.IntegerField(default=0, verbose_name=b'\xe7\x89\x88\xe6\x9c\xac\xe5\x8f\xb7')),
                ('version_no_expired', models.BooleanField(default=False, editable=False)),
                ('is_active', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('time_mark_start_hour', models.IntegerField(default=0, validators=[django.core.validators.MaxValueValidator(24), django.core.validators.MinValueValidator(0)])),
                ('time_mark_start_min', models.IntegerField(default=0, validators=[django.core.validators.MaxValueValidator(60), django.core.validators.MinValueValidator(0)])),
                ('time_mark_end_hour', models.IntegerField(default=0, validators=[django.core.validators.MaxValueValidator(24), django.core.validators.MinValueValidator(0)])),
                ('time_mark_end_min', models.IntegerField(default=0, validators=[django.core.validators.MaxValueValidator(60), django.core.validators.MinValueValidator(0)])),
            ],
            options={
                'verbose_name': '\u8868\u60c5\u7c7b\u578b',
                'verbose_name_plural': '\u8868\u60c5\u7c7b\u578b',
            },
        ),
        migrations.AddField(
            model_name='emoticon',
            name='e_type',
            field=models.ForeignKey(verbose_name=b'\xe8\xa1\xa8\xe6\x83\x85\xe7\xb1\xbb\xe5\x9e\x8b', to='Emoticon.EmoticonType'),
        ),
    ]
