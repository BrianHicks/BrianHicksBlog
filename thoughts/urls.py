from django.conf.urls.defaults import patterns, include, url
from django.views.generic import ArchiveIndexView

urlpatterns = patterns('thoughts.views',
    url(r'^$', 'thoughts', name='thoughts'),
    url(r'^(?P<year>\d{4})/$', 'thoughts', name='thoughts_year'),
    url(r'^(?P<year>\d{4})/(?P<month>\d{2})/$', 'thoughts', name='thoughts_month'),
)
