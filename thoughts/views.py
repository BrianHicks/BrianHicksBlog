import datetime

from django.http import Http404
from django.shortcuts import render_to_response
from django.views.generic import ArchiveIndexView, YearArchiveView, MonthArchiveView, DayArchiveView, DetailView

from thoughts.models import Thought

class ThoughtsIndexView(ArchiveIndexView):
    queryset = Thought.objects.published()
    date_field = 'pub_date'
    context_object_name = 'thought_list'
    paginate_by = 10
    
class ThoughtsByYearView(YearArchiveView):
    date_field = 'pub_date'
    queryset = Thought.objects.published()
    make_object_list = True
    paginate_by = 10
    
#def thoughts(request, year=None, month=None, day=None, template='thoughts/index.html'):
#    thoughts = Thought.objects.published()
#    
#    return render_to_response(
#        template,
#        {'thoughts': thoughts,
#         'year': year,
#         'month': month,
#         'day': day}
#    )