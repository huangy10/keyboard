# coding=utf-8
from django.db import models
from django.conf import settings
# Create your models here.


class EmoticonUsage(models.Model):
    """This model provides records for emoticon usage.

    """
    use_time = models.DateTimeField(auto_now_add=True, verbose_name='使用时间')     # When the emoticon is used
    emoticon_used = models.ForeignKey('Emoticon.Emoticon')  # Then emoticon used
    user = models.ForeignKey(settings.AUTH_USER_MODEL)  # The user who use the emoticon

    class Meta:
        verbose_name = u'使用记录'
        verbose_name_plural = u'使用记录'
        ordering = ('-use_time', )


class EmoticonUpdate(models.Model):
    """This model provides record for emoticon updates.

    The emoticons are updated by types as a group.
    """
    update_time = models.DateTimeField(auto_now_add=True, verbose_name='更新时间')
    emoticon_type = models.ForeignKey('Emoticon.EmoticonType')
    user = models.ForeignKey(settings.AUTH_USER_MODEL)

    class Meta:
        verbose_name = u'更新记录'
        verbose_name_plural = u'更新记录'
        ordering = ('-update_time', )