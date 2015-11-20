# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('Emoticon', '0002_emoticontype_version_check_dict'),
    ]

    operations = [
        migrations.AddField(
            model_name='emoticontype',
            name='order_weight',
            field=models.IntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='emoticontype',
            name='updated_at',
            field=models.DateTimeField(auto_now=True, verbose_name=b'\xe4\xb8\x8a\xe6\xac\xa1\xe4\xbf\xae\xe6\x94\xb9\xe6\x97\xb6\xe9\x97\xb4'),
        ),
        migrations.AlterField(
            model_name='emoticontype',
            name='version_no_expired',
            field=models.BooleanField(default=False, verbose_name=b'\xe6\x98\xaf\xe5\x90\xa6\xe6\x9c\x89\xe6\x9c\xaa\xe8\xa2\xab\xe5\xba\x94\xe7\x94\xa8\xe7\x9a\x84\xe6\x9b\xb4\xe6\x94\xb9', editable=False),
        ),
    ]
