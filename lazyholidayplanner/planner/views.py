import copy, json, datetime

from django.utils import timezone
from django.http import HttpResponse
from django.shortcuts import render, render_to_response, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.db.models import Q

from django.contrib.auth.models import User
from itinerary.models import Trip


from skyscanner.skyscanner import Flights

# Create your views here.

def index(request):
    # Current user's details
    current_user = request.user

    if current_user.is_authenticated is False:
        return render(request, 'planner/index.html')

    user_trips = Trip.objects.filter(Q(creator=current_user) | Q(members=current_user)).distinct()
    if not user_trips.exists():
        user_trips = None
    print(user_trips)
    
    return render(request, 'planner/index.html',  {
        'user_trips': user_trips,
    })

def new(request):
    return render(request, 'planner/new.html')

"""
Webhook for handling information submitted to typeform. The url is '.../api/typeform'
"""
@csrf_exempt
@require_POST
def typeform_result(request):
    jsondata = request.body
    data = json.loads(jsondata)
    query_answers = data['form_response']['answers']
    # meta = copy.copy(request.META)

    trip = {}
    trip['location'] = query_answers[0]['text']
    trip['start_date'] = query_answers[1]['date']
    trip['end_date'] = query_answers[2]['date']
    trip['party_size'] = query_answers[3]['number']
    trip['budget'] = query_answers[4]['choice']['label']
    print(data)

    """
    for k, v in meta.items():
        if not isinstance(v, basestring):
            del meta[k]


    WebhookTransaction.objects.create(
        date_event_generated=datetime.datetime.fromtimestamp(
            data['timestamp']/1000.0, 
            tz=timezone.get_current_timezone()
        ),
        body=data,
        request_meta=meta
    )
    """

    return HttpResponse(status=200)