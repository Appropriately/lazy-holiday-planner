import copy, json, datetime

from django.utils import timezone
from django.http import HttpResponse
from django.shortcuts import render, render_to_response, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from itinerary.models import Trip, ItineraryItem, Flight
from django.db.models import Q
from django.contrib.auth.decorators import login_required
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

    return render(request, 'planner/index.html',  {
        'user_trips': user_trips,
    })

@login_required
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
    username = data['form_response']['hidden']['username']
    print(data)

    trip = {}
    trip['origin_location'] = query_answers[0]['text']
    trip['destination_location'] = query_answers[1]['text']
    trip['start_date'] = query_answers[2]['date']
    trip['end_date'] = query_answers[3]['date']
    trip['party_size'] = query_answers[4]['number']
    trip['class'] = parse_budget(query_answers[5]['choice']['label'])

    flights_service = get_flights_service()
    origin_locations = get_location_results(flights_service, trip['origin_location'])
    trip['origin_location'] = get_first_location(origin_locations)
    destination_locations = get_location_results(flights_service, trip['destination_location'])
    trip['destination_location'] = get_first_location(destination_locations)
    
    print(trip)

    if not trip['origin_location']:
        return HttpResponse(status=500, content="Origin location not valid")

    if not trip['destination_location']:
        return HttpResponse(status=500, content="Destination location not valid")

    if not are_dates_valid(trip['start_date'], trip['end_date']):
        return HttpResponse(status=500, content="Dates are invalid")

    if trip['party_size'] <= 0:
        return HttpResponse(status=500, content="Party size must be greater than 0")

    if not trip['class']:
        return HttpResponse(status=500, content="Invalid flight class")    
    
    # Get the user
    user = User.objects.get_by_natural_key(username)

    # Get the flights and price
    flight = get_flight(flights_service, trip)
    if not flight:
        return HttpResponse(status=500, content="No flights found")

    # Create the trip
    print('Gets to create trip')
    destination_name = destination_locations['Places'][0]['PlaceName']
    trip_title = f"{username}'s trip to {destination_name}"
    party_size = trip['party_size']
    price = flight['Itineraries']['PricingOptions']['Price']
    new_trip = Trip.objects.create(creator=user, title=trip_title, destination=destination_name, party_size=party_size, price=price)
    print('initial create success')
    new_trip.members.add(user)
    print('added members')
    new_trip.save()

    # add outbound flight
    departure_time = convert_to_datetime(flight['Legs']['outbound']['Departure'])
    arrival_time = convert_to_datetime(flight['Legs']['outbound']['Arrival'])
    departure_location = flight['Locations']['outbound_origin']
    arrival_location = flight['Locations']['outbound_destination']
    outbound_flight = Flight.objects.create(trip=new_trip, created_by=user, leaving_time=departure_time, arrival_time=arrival_time, departs_from=departure_location, destination=arrival_location)
    outbound_flight.save()

    # add returning flight
    departure_time = convert_to_datetime(flight['Legs']['inbound']['Departure'])
    arrival_time = convert_to_datetime(flight['Legs']['inbound']['Arrival'])
    departure_location = flight['Locations']['inbound_origin']
    arrival_location = flight['Locations']['inbound_destination']
    inbound_flight = Flight.objects.create(trip=new_trip, created_by=user, leaving_time=departure_time, arrival_time=arrival_time, departs_from=departure_location, destination=arrival_location)
    inbound_flight.save()

    print(data)
    return HttpResponse(status=200, content="Trip added")

def get_keys():
    # read keys in from file, and strip newline characters
    # 0 is flight api key
    # 1 is flight app id
    # 2 is hotel api key
    with open('keys') as file:
        keys = file.readlines()

    keys = [key.strip() for key in keys]
    return keys

def get_location_results(flights_service, location_string, market='UK', currency='GBP', locale='en-GB'):
    locations_response = flights_service.make_request(f'http://partners.api.skyscanner.net/apiservices/autosuggest/v1.0/{market}/{currency}/{locale}?query={location_string}')
    return json.loads(locations_response.text)

def get_flights_service():
    keys = get_keys()
    return Flights(keys[0])

def get_first_location(locations):
    if not locations:
        return False

    location = locations['Places'][0]
    return location['PlaceId'] if location['CityId'] == '' else location['CityId']

def are_dates_valid(start_date, end_date):
    start_date = datetime.datetime.strptime(start_date, '%Y-%m-%d')
    end_date = datetime.datetime.strptime(end_date, '%Y-%m-%d')
    time_diff = end_date - start_date

    return True if time_diff.days > 0 else False

def parse_budget(budget_type):
    budget_options = {
        'No money': "economy",
        'Doing okay': "business",
        'Big money': "first"
    }
    return budget_options[budget_type] if budget_type in budget_options else False

def get_flight(flights_service, trip, country='UK', currency='GBP', locale='en-GB'):
    response = flights_service.get_result(country=f'{country}',
        currency=f'{currency}',
        locale=f'{locale}',
        originplace=f"{trip['origin_location']}",
        destinationplace=f"{trip['destination_location']}",
        outbounddate=f"{trip['start_date']}",
        inbounddate=f"{trip['end_date']}",
        adults=f"{trip['party_size']}",
        cabinClass=f"{trip['class']}",
        groupPricing=True).parsed

    session_key = response['SessionKey']
    flights = poll_results(flights_service, session_key, 'price', 'asc')
    itineraries = flights['Itineraries']

    if not itineraries:
        return False

    cheapest_leg = itineraries[0]
    for leg in itineraries:
        if leg['PricingOptions'][0]['Price'] < cheapest_leg['PricingOptions'][0]['Price']:
            cheapest_leg = leg
            
    cheapest_leg['PricingOptions'] = cheapest_leg['PricingOptions'][0]
    flights['Itineraries'] = cheapest_leg

    return parse_flight_data(flights)

def poll_results(flights_service, session_key, sort_type='price', sort_order='asc'):
    flights_response = flights_service.make_request(f'http://partners.api.skyscanner.net/apiservices/pricing/uk1/v1.0/{session_key}?stops=0&sortType={sort_type}&sortOrder={sort_order}')
    return json.loads(flights_response.text)

def parse_flight_data(flight):
    legs = flight['Legs']
    outbound_leg_id = flight['Itineraries']['OutboundLegId']
    inbound_leg_id = flight['Itineraries']['InboundLegId']

    final_legs = {}
    for leg in legs:
        if leg['Id'] == outbound_leg_id:
            final_legs['outbound'] = leg
        if leg['Id'] == inbound_leg_id:
            final_legs['inbound'] = leg

    flight['Legs'] = final_legs

    places = flight['Places']
    outbound_origin_id = final_legs['outbound']['OriginStation']
    outbound_destination_id = final_legs['outbound']['DestinationStation']
    inbound_origin_id = final_legs['inbound']['OriginStation']
    inbound_destination_id = final_legs['inbound']['DestinationStation']

    locations = {}
    for place in places:
        if place['Id'] == outbound_origin_id:
            locations['outbound_origin'] = parse_location_name(place)
        if place['Id'] == outbound_destination_id:
            locations['outbound_destination'] = parse_location_name(place)
        if place['Id'] == inbound_origin_id:
            locations['inbound_origin'] = parse_location_name(place)
        if place['Id'] == inbound_destination_id:
            locations['inbound_destination'] = parse_location_name(place)

    flight['Locations'] = locations

    # price is flight['Itineraries][0]['PricingOptions']['Price']
    # time is flight['Legs']['inbound']['Departure'|'Arrival']
    # airport is flight['Locations'][LOCATION_NAME]
    # where LOCATION_NAME = 'outbound|inbound_origin|destination'
    return flight

def parse_location_name(location):
    name = ''
    if location['Type'] == 'Airport':
        name += location['Name'] + ' Airport'
    if location['Type'] == 'City':
        name += location['Name']

    return name

def convert_to_datetime(flight_datetime):
    return datetime.datetime.strptime(flight_datetime, '%Y-%m-%dT%H:%M:%S')