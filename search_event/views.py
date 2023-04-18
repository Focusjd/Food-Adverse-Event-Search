from django.shortcuts import render
from django.http import HttpResponse

from .models import FoodAdverseEvent
from .forms import SearchForm
import requests
import json
import hashlib
import os

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


def index_(request):
    form = SearchForm(request.GET or None)
    events = FoodAdverseEvent.objects.none()  # Set the default queryset to none

    if form.is_valid() and request.GET:  # Check if the form is submitted
        events = FoodAdverseEvent.objects.all()
        gender = form.cleaned_data['gender']
        age = form.cleaned_data['age']
        reactions = form.cleaned_data['reactions']
        product_name = form.cleaned_data['product_name']

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
                    events = events.filter(products__name_brand__icontains=product_name)  # Filter by product name
    context = {
        'form': form,
        'events': events,
    }

    return render(request, 'index.html', context)


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
        data = load_from_cache(query)

        if data is None:
            api_url = f'https://api.fda.gov/food/event.json?search={query}&limit=10'
            response = requests.get(api_url)
            if response.status_code == 200:
                data = response.json()
                save_to_cache(query, data)

        if data is not None and 'results' in data:
            events = data['results']

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