# coding=utf-8
from django.db import models
from django.dispatch import receiver
from django.db.models.signals import post_save
from django.conf import settings
# Create your models here.


class UserProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, related_name='profile')
    #
    created_at = models.DateTimeField(auto_now_add=True, editable=True)
    # 用户的设备类型
    device_type = models.CharField(max_length=64, default='')


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def auto_create_profile(sender, instance, created, **kwargs):
    if created:
        # If the user is first created, then create a profile for him/her
        UserProfile.objects.create(user=instance)
    else:
        # Always save the profile after saving the user instance.
        instance.profile.save()