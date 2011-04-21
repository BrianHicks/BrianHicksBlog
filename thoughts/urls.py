from django.conf.urls.defaults import patterns, include, url

from thoughts.views import ThoughtsIndexView, ThoughtsByYearView, ThoughtsByMonthView

urlpatterns = patterns('thoughts.views',
    url(r'^$', ThoughtsIndexView.as_view(), name='thoughts'),
    url(r'^(?P<year>\d{4})/$', ThoughtsByYearView.as_view(), name='thoughts_year'),
    url(r'^(?P<year>\d{4})/(?P<month>\w{3})/$', ThoughtsByMonthView.as_view(), name='thoughts_month'),
)
