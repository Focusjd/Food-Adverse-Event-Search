from django.shortcuts import render
from django.http import HttpResponse

from .models import *
from .forms import SearchForm
import requests
import json
import hashlib
import os
import threading


# url:f"https://api.fda.gov/food/event.json?search=reactions:{reactions}+AND+consumer.gender:{gender}+AND+consumer.age:{age}+AND+products.name_brand:{brand}.&limit=10"

CACHE_FILE = 'search_cache.json'


def results(request):
    events = FoodAdverseEvent.objects.all()
    context = {'events': events}
    return render(request, 'event_results.html', context)

def search(request):
    form = SearchForm(request.GET or None)
    events = FoodAdverseEvent.objects.all()

    if form.is_valid():
        gender = form.cleaned_data['gender']
        age = form.cleaned_data['age']
        reactions = form.cleaned_data['reactions']

        if gender:
            events = events.filter(consumer__gender=gender)
        if age:
            events = events.filter(consumer__age=age)
        if reactions:
            reactions_list = reactions.split(',')
            events = events.filter(reactions__icontains=reactions_list[0])
            for reaction in reactions_list[1:]:
                events = events.filter(reactions__icontains=reaction.strip())

    context = {
        'form': form,
        'events': events,
    }
    return render(request, 'search.html', context)


def index(request):
    form = SearchForm(request.GET or None)

    events = []

    if form.is_valid() and request.GET:
        gender = form.cleaned_data['gender']
        age = form.cleaned_data['age']
        reactions = form.cleaned_data['reactions']
        product_name = form.cleaned_data['product_name']

        query_parts = []
        if gender:
            query_parts.append(f'consumer.gender:{gender}')
        if age:
            query_parts.append(f'consumer.age:{age}')
        if reactions:
            query_parts.append(f'reactions:"{reactions}"')
        if product_name:
            query_parts.append(f'products.name_brand:"{product_name}"')

        query = '+AND+'.join(query_parts)

        # Try to load the data from cache
        events = load_from_cache(query)

        if events is None:
            result = search_api(query, timeout=3)

            if result:
                events = result['results']
                save_to_cache(query, events)
                save_api_results_to_database(events)
                print('Search using API')
            else:
                events = search_local_database(gender, age, reactions, product_name)
                print('Search using local database')

        else:
            print('Search using cache')
    context = {
        'form': form,
        'events': events,
    }

    return render(request, 'index.html', context)



def cache_filename(query):
    hashed_query = hashlib.md5(query.encode('utf-8')).hexdigest()
    return f'cache_{hashed_query}.json'

def save_to_cache(query, data):
    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE, 'r') as f:
            cache = json.load(f)
    else:
        cache = {}

    cache[query] = data

    with open(CACHE_FILE, 'w') as f:
        json.dump(cache, f)

def load_from_cache(query):
    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE, 'r') as f:
            cache = json.load(f)
        if query in cache:
            return cache[query]
    return None


def search_api(query, timeout=2):
    api_url = f'https://api.fda.gov/food/event.json?sort=date_started:desc&search={query}&limit=10'
    try:
        response = requests.get(api_url, timeout=timeout)
        if response.status_code == 200:
            data = response.json()
        return data
    except Exception as e:
        print("You have network expection: ", e)
    return None

def search_local_database(gender, age, reactions, product_name):
    events = FoodAdverseEvent.objects.all()

    if gender:
        events = events.filter(consumer__gender=gender)
    if age:
        events = events.filter(consumer__age=age)
    if reactions:
        reactions_list = reactions.split(',')
        events = events.filter(reactions__icontains=reactions_list[0])
        for reaction in reactions_list[1:]:
            events = events.filter(reactions__icontains=reaction.strip())
    if product_name:
        events = events.filter(products__name_brand__icontains=product_name)

    events_list = []
    for event in events:
        event_dict = {
            "report_number": event.repot_number if event.repot_number else None,
            "date_created": event.date_created if event.date_created else None,
            "date_started": event.date_started if event.date_started else None,
            "outcomes": event.outcome.split(', ') if event.outcome else None,
            "reactions": event.reactions.split(', ') if event.reactions else None,
            "consumer": {
                "age": event.consumer.age if event.consumer.age else None,
                "age_unit": event.consumer.age_unit if event.consumer.age_unit else None,
                "gender": event.consumer.gender if event.consumer.gender else None,
            },
            "products": [
                {
                    "role": product_event.product.role if product_event.product.role else None,
                    "name_brand": product_event.product.name_brand if product_event.product.name_brand else None,
                    "industry_code": product_event.product.industry_code if product_event.product.industry_code else None,
                    "industry_name": product_event.product.industry_name if product_event.product.industry_name else None,
                }
                for product_event in event.productevent_set.all()
            ],
        }
        events_list.append(event_dict)
    return events_list

def save_api_results_to_database(results):
    for event_data in results:
        consumer_data = event_data.get('consumer', {})
        consumer, _ = Consumer.objects.get_or_create(
            age=consumer_data.get('age'),
            age_unit=consumer_data.get('age_unit'),
            gender=consumer_data.get('gender')
        )

        event = FoodAdverseEvent.objects.create(
            repot_number=event_data.get('report_number'),
            date_created=event_data.get('date_created'),
            date_started=event_data.get('date_started'),
            outcome=', '.join(event_data.get('outcomes', [])),
            reactions=', '.join(event_data.get('reactions', [])),
            consumer=consumer,
        )

        for product_data in event_data.get('products', []):
            product, _ = Product.objects.get_or_create(
                role=product_data.get('role'),
                name_brand=product_data.get('name_brand'),
                industry_code=product_data.get('industry_code'),
                industry_name=product_data.get('industry_name')
            )
            ProductEvent.objects.create(product=product, adverse_event=event)
