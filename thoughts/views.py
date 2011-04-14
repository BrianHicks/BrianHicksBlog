import datetime

from django.http import Http404
from django.shortcuts import render_to_response

from thoughts.models import Thought

# thoughts returns year-month-day-slug
def thoughts(request, year=None, month=None, day=None, template='thoughts/index.html'):
    thoughts = Thought.objects.published()
    
    return render_to_response(
        template,
        {'thoughts': thoughts,
         'year': year,
         'month': month,
         'day': day}
    )
    
    #if year:
    #    thoughts = thoughts.filter(pub_date__year=year)
    #    
    #if month:
    #    thoughts = thoughts.filter(pub_date__month=month)
    #    
    #if day:
    #    thoughts = thoughts.filter(pub_date__day=day)
    #    
    #return render_to_response(
    #    template,
    #    {'thoughts': thoughts,
    #     'year': year,
    #     'month': month,
    #     'day': day}
    #)


#####def events(request, state=None, year=None, template='events/index.html'):
#####  events = Event.objects.upcoming()
#####  
#####  # filter by state
#####  if state:
#####	state = state.upper()
#####	if state not in [abbr for abbr, verbose_state in STATE_CHOICES]:
#####	  raise Http404('%s is not a valid US state' % state)
#####	events = events.filter(venue__state__iexact=state)
#####  
#####  # filter by year
#####  if year:
#####	events = events.filter(date__year=year)
#####  
#####  return render_to_response(
#####	template,
#####	{'events': events,
#####	 'state': state,
#####	 'year': year},
#####  )
