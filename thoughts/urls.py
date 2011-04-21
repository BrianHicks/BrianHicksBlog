from django.conf.urls.defaults import patterns, include, url

from thoughts.views import ThoughtsIndexView, ThoughtsByYearView, ThoughtsByMonthView, ThoughtsByDayView, ThoughtDetailView

urlpatterns = patterns('thoughts.views',
    url(r'^$', ThoughtsIndexView.as_view(), name='thoughts'),
    url(r'^(?P<year>\d{4})/$', ThoughtsByYearView.as_view(), name='thoughts_year'),
    url(r'^(?P<year>\d{4})/(?P<month>\w{3})/$', ThoughtsByMonthView.as_view(), name='thoughts_month'),
    url(r'^(?P<year>\d{4})/(?P<month>\w{3})/(?P<day>\d{2})/$', ThoughtsByDayView.as_view(), name='thoughts_day'),
    url(r'^(?P<year>\d{4})/(?P<month>\w{3})/(?P<day>\d{2})/(?P<slug>[\w\-]+)/$', ThoughtDetailView.as_view(), name='thought'),
)
