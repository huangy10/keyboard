# coding=utf-8
import uuid

from django.db import models
from django.utils import timezone
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db.models import Q
from django.core.exceptions import ObjectDoesNotExist

# Create your models here.


class EmoticonType(models.Model):
    # Name of this type
    name = models.CharField(max_length=128, verbose_name='类型名称')
    # Version number of the type. 'no' means No. here
    version_no = models.IntegerField(default=0, verbose_name='版本号')
    # If any new emoticon of this type is created, or if any emoticon of this type is modified,
    # this attributes will be set to True.
    version_no_expired = models.BooleanField(default=False, editable=False)
    # Inactive type is treated as been deleted
    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    updated_at = models.DateTimeField(auto_now=True)

    time_mark_start_hour = models.IntegerField(default=0, validators=[MaxValueValidator(24), MinValueValidator(0)])
    time_mark_start_min = models.IntegerField(default=0, validators=[MaxValueValidator(60), MinValueValidator(0)])
    time_mark_end_hour = models.IntegerField(default=0, validators=[MaxValueValidator(24), MinValueValidator(0)])
    time_mark_end_min = models.IntegerField(default=0, validators=[MaxValueValidator(60), MinValueValidator(0)])

    def synchronize(self):
        """ Apply the modification of this type.
        Actually, it just set all the active emoticons to be published
        """
        return Emoticon.objects.all().update(is_published=True)

    class Meta:
        verbose_name = '表情类型'
        verbose_name_plural = '表情类型'


def emoticon_path_finder(instance, filename):
    ext = filename.split('.')[-1]
    filename = ("%s.%s" % (uuid.uuid4(), ext)).replace("-", "")
    time = timezone.now()
    return "icons/%s/%s/%s/%s" % (time.year, time.month, time.day, filename)


class EmoticonManager(object, models.Manager):

    def available_emoticons(self, e_type):
        """ Get the available emoticons to be displayed
         :param e_type given type
        """
        return self.filter(is_published=True).order_by('-version_no', 'code').distinct('code')

    def create(self, code, **kwargs):
        # Get the proper version number
        version_no = Emoticon.objects.filter(code=code, including_inactive=True).count()
        kwargs['version_no'] = version_no
        # create!
        obj = super(EmoticonManager, self).create(**kwargs)
        if obj is not None:
            # Update the status of e_type
            obj.e_type.version_no_expired = True    # As mentioned above, set this attribute of the e_type to True
            obj.e_type.save()
        return obj

    def filter(self, including_inactive=False, **kwargs):
        """ Exclude the inactive emoticons automatically
         :param including_inactive  If you want to fetch the inactive emoticons, set this to True
        """
        if not including_inactive:
            kwargs['is_active'] = True
        return super(EmoticonManager, self).filter(**kwargs)

    def all(self, including_inactive=False):
        """ Exclude the inactive emoticons automatically
         :param including_inactive  If you want to fetch the inactive emoticons, set this to True
        """
        if including_inactive:
            return super(EmoticonManager, self).all()
        else:
            return self.filter()

    def get(self, including_inactive=False, **kwargs):
        """ Exclude the inactive emoticons automatically
         :param including_inactive  If you want to fetch the inactive emoticons, set this to True
        """
        if not including_inactive:
            kwargs['is_active'] = True
        return super(EmoticonManager, self).get(**kwargs)

    def get_or_create(self, **kwargs):
        assert True, 'Do not use get_or_create function for Emoticon'
        return None, False


class Emoticon(models.Model):
    # Set this attribute to False to del an Emoticon. Do not del it manually using delete function, or the
    # related statistical data will also be deleted at the same time.
    is_active = models.BooleanField(default=True, editable=False)
    # Attribute of draft system. Automatically set to False at creation. After synchronized by the e_type,
    # The most recently active emoticons will be published.
    is_published = models.BooleanField(default=False, editable=False)
    # The content of the emoticon, .JPG, .PNG, .GIF are all supported here.
    # Other formats are not guaranteed to be supported here.
    icon = models.ImageField(upload_to=emoticon_path_finder,
                             verbose_name='表情')
    # Short description About the emoticon
    description = models.CharField(max_length=255, verbose_name='表情描述')
    # Code for this emoticon. Note that the emoticons with the same code will be regarded as the same one.
    # The emoticons with the same code will be set to be inactive automatically, which means those emoticons
    # will not be sent to the user.
    code = models.CharField(max_length=100, verbose_name='编号')
    version_no = models.IntegerField(default=0, verbose_name='版本号')
    # Order weight.
    order_weight = models.IntegerField(default=0, verbose_name='排序权重')
    # Associated emoticon types
    e_type = models.ForeignKey(EmoticonType, verbose_name='表情类型')
    #
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    updated_at = models.DateTimeField(auto_now=True, editable=False)
    # Override the default manager
    objects = EmoticonManager()

    def save(self, force=True, *args, **kwargs):
        """ Save the instance to the database.

        Inactive emoticon is not allowed to be modified.

         :param force Set it to True to ignore any check before saving.
         :return If the saving is actually done.
        """
        if force:
            # Save anyway.
            super(Emoticon, self).save(*args, **kwargs)
            return True
        else:
            try:
                Emoticon.objects.get(pk=self.pk)
                super(Emoticon, self).save(*args, **kwargs)
                if self.is_published:
                    self.e_type.version_no_expired = True
                    self.e_type.save()
                return True
            except ObjectDoesNotExist:
                # Nothing to be done if the emoticon is inactive.
                return False

    class Meta:
        verbose_name_plural = '表情'
        verbose_name = '表情'
        ordering = ('-order_weight', )


