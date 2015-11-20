# coding=utf-8
from django.contrib import admin

from .models import Emoticon, EmoticonType
# Register your models here.


@admin.register(EmoticonType)
class EmoticonTypeAdmin(admin.ModelAdmin):

    list_display = ('name', 'version_no', 'is_active', 'updated_at', )
    list_filter = ('version_no_expired', 'is_active', )
    exclude = ('version_check_dict', )
    ordering = ('-order_weight', 'updated_at', )
    actions = ('deactivate', 'activate', 'apply', )
    search_fields = ('name', 'version_no', )

    def deactivate(self, request, query_set):
        count = query_set.update(is_active=False)
        self.message_user(request, u'总共注销了{0}个类别'.format(count))
    deactivate.short_description = u'注销类别'

    def activate(self, request, query_set):
        count = query_set.update(is_active=True)
        self.message_user(request, u'重新启用{0}个类别'.format(count))
    activate.short_description = u'重新启用'

    def apply(self, request, query_set):
        for e_type in query_set:
            e_type.synchronize()
        self.message_user(request, u'应用了{0}个更改'.format(query_set.count()))
    apply.short_description = u'应用更改'


@admin.register(Emoticon)
class EmoticonAdmin(admin.ModelAdmin):

    list_display = ('code', 'version_no', 'order_weight', 'description', 'is_active', 'is_published', 'e_type')
    list_filter = ('is_active', 'is_published')
    exclude = ('created_at', )
    ordering = ('-order_weight', 'updated_at', )
    search_fields = ('code', 'version_no', 'description', )
    actions = ('deactivate', 'activate', )

    def deactivate(self, request, query_set):
        count = query_set.update(is_active=False)
        self.message_user(request, u'总共注销了{0}个类别'.format(count))
    deactivate.short_description = u'注销类别'

    def activate(self, request, query_set):
        count = query_set.update(is_active=True)
        self.message_user(request, u'重新启用{0}个类别'.format(count))
    activate.short_description = u'重新启用'