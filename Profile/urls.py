from django.conf.urls import include, url, patterns

urlpatterns = patterns('Profile.views',
                       url('^new$', 'request_account', name='new_account'))