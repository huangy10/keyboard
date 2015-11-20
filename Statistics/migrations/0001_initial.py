# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('Emoticon', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='EmoticonUpdate',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('update_time', models.DateTimeField(auto_now_add=True, verbose_name=b'\xe6\x9b\xb4\xe6\x96\xb0\xe6\x97\xb6\xe9\x97\xb4')),
                ('emoticon_type', models.ForeignKey(to='Emoticon.EmoticonType')),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ('-update_time',),
                'verbose_name': '\u66f4\u65b0\u8bb0\u5f55',
                'verbose_name_plural': '\u66f4\u65b0\u8bb0\u5f55',
            },
        ),
        migrations.CreateModel(
            name='EmoticonUsage',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('use_time', models.DateTimeField(auto_now_add=True, verbose_name=b'\xe4\xbd\xbf\xe7\x94\xa8\xe6\x97\xb6\xe9\x97\xb4')),
                ('emoticon_used', models.ForeignKey(to='Emoticon.Emoticon')),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ('-use_time',),
                'verbose_name': '\u4f7f\u7528\u8bb0\u5f55',
                'verbose_name_plural': '\u4f7f\u7528\u8bb0\u5f55',
            },
        ),
    ]
