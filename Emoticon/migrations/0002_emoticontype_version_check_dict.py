# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import jsonfield.fields


class Migration(migrations.Migration):

    dependencies = [
        ('Emoticon', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='emoticontype',
            name='version_check_dict',
            field=jsonfield.fields.JSONField(default='{}'),
            preserve_default=False,
        ),
    ]
