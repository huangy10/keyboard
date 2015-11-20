from django.conf.urls import include, url, patterns

urlpatterns = patterns('Emoticon.views',
                       url(r'^check_update$', 'check_update', name='check_update'),
                       url(r'^all$', 'all_emoticon_types', name='all'),
                       url(r'^report$', 'usage_report_types', name='report'),
                       url(r'^download/(?P<emoticon_code>\S+)/(?P<version_no>\d+)$', 'fetch_emoticon', name='download'),
                       url(r'^thumbnail/(?P<type_id>\d+)$', 'get_thumbnail_for_type', name='thumbnail')
                       )