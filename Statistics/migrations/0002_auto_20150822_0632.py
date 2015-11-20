# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('Emoticon', '0003_auto_20150822_0632'),
        ('Statistics', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='emoticonupdate',
            name='emoticon_type',
        ),
        migrations.AddField(
            model_name='emoticonupdate',
            name='emoticon',
            field=models.ForeignKey(default=None, to='Emoticon.Emoticon'),
            preserve_default=False,
        ),
    ]
