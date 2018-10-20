import copy, json, datetime

from django.utils import timezone
from django.http import HttpResponse
from django.shortcuts import render, render_to_response, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from skyscanner.skyscanner import Flights

# Create your views here.

def index(request):
    # read keys in from file, and strip newline characters
    # 0 is flight api key
    # 1 is flight app id
    # 2 is hotel api key
    with open('keys') as f:
        keys = f.readlines()
    
    keys = [key.strip() for key in keys]

    flights_service = Flights(keys[0])
    # places = flights_service.make_request('http://partners.api.skyscanner.net/apiservices/autosuggest/v1.0/UK/GBP/en-GB?query=manc&apiKey={keys[0]}')
    # return HttpResponse(places)
    
    # result = flights_service.get_result(
    #     country='UK',
    #     currency='GBP',
    #     local='en-GB',
    #     originplace=''
    # )

    return render_to_response('index.html')

def new(request):
    return render(request, 'new.html')

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