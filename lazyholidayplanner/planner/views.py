import copy, json, datetime

from django.utils import timezone
from django.http import HttpResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

# Create your views here.
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
    meta = copy.copy(request.META)
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