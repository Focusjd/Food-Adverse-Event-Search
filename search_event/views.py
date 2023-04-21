from django.shortcuts import render
from .models import *
from .forms import SearchForm
import requests
import json
import hashlib
import os

from collections import defaultdict
from datetime import datetime

import plotly.express as px
import plotly.io as pio

from random import sample
from django.shortcuts import render
import plotly.express as px
import plotly.io as pio
from .models import FoodAdverseEvent
from collections import defaultdict
import pandas as pd
from datetime import datetime

from plotly.subplots import make_subplots
import plotly.graph_objects as go
from plotly.offline import plot

CACHE_FILE = 'search_cache.json'


def build_tree_structure(products):
    tree = []
    for product in products:
        industry_code = product.industry_code
        industry_name = product.industry_name
        role = product.role
        tree.append({
            'id': f'{industry_code}-{role}-{product.id}',
            'parent': f'{industry_code}-{role}' if role else industry_code,
            'label': product.name_brand
        })

        if f'{industry_code}-{role}' not in [item['id'] for item in tree]:
            tree.append({
                'id': f'{industry_code}-{role}',
                'parent': industry_code,
                'label': role
            })

        if industry_code not in [item['id'] for item in tree]:
            tree.append({
                'id': industry_code,
                'parent': '',
                'label': f'{industry_code} - {industry_name}'
            })
    return tree

def build_tree_list(products):
    tree = {}

    for product in products:
        industry_code = product.industry_code
        industry_name = product.industry_name

        if industry_code not in tree:
            tree[industry_code] = {
                'name': industry_name,
                'roles': {}
            }

        role = product.role
        if role not in tree[industry_code]['roles']:
            tree[industry_code]['roles'][role] = []

        tree[industry_code]['roles'][role].append({
            'id': product.id,
            'name_brand': product.name_brand
        })

    with open('product_tree.json', 'w') as json_file:
        json.dump(tree, json_file)

    return tree


def build_sunburst_data(tree_structure):
    fig = make_subplots(1, 1, specs=[[{'type': 'sunburst'}]])

    fig.add_trace(go.Sunburst(
        ids=[item['id'] for item in tree_structure],
        labels=[item['label'] for item in tree_structure],
        parents=[item['parent'] for item in tree_structure],
        hovertext=[item['label'] for item in tree_structure],
        hoverinfo="text",
        insidetextorientation='radial'
    ))

    fig.update_layout(title_text='Tree Structure of Products', title_x=0.5, height=1000, width=1000)

    plot_div = plot(fig, output_type='div', include_plotlyjs=False)
    return plot_div

def product_stats_view(request):
    products = Product.objects.all()[:150]

    tree_list = build_tree_list(products)
    tree_structure = build_tree_structure(products)
    plot_div = build_sunburst_data(tree_structure)

    context = {
        'tree_structure': tree_list,
        'plot_div': plot_div,
    }
    return render(request, 'product_stat.html', context)

def line_charts(request):
    # Get data from the database
    events = FoodAdverseEvent.objects.all()

    # Process data to extract information for the charts
    data = defaultdict(lambda: defaultdict(int))

    for event in events:
        date_str = event.date_created
        date = datetime.strptime(date_str, '%Y%m%d')  # Updated format string
        data['year'][date.year] += 1
        data['month'][date.month] += 1
        data['day'][date.day] += 1

    # Convert dictionaries to DataFrames
    df_year = pd.DataFrame(list(data['year'].items()), columns=['year', 'count']).sort_values('year')
    df_month = pd.DataFrame(list(data['month'].items()), columns=['month', 'count']).sort_values('month')
    df_day = pd.DataFrame(list(data['day'].items()), columns=['day', 'count']).sort_values('day')

    # Map month numbers to month names
    month_names = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']
    df_month['month'] = df_month['month'].apply(lambda x: month_names[x-1])

    # Create Plotly figures
    fig_year = px.line(df_year, x='year', y='count', title='Adverse event reports by year')
    fig_month = px.line(df_month, x='month', y='count', title='Adverse event reports by month')
    fig_day = px.line(df_day, x='day', y='count', title='Adverse event reports by day')

    # Convert the figures to HTML
    year_chart_html = pio.to_html(fig_year, full_html=False)
    month_chart_html = pio.to_html(fig_month, full_html=False)
    day_chart_html = pio.to_html(fig_day, full_html=False)
    data_number = len(events)
    context = {
        'year_chart': year_chart_html,
        'month_chart': month_chart_html,
        'day_chart': day_chart_html,
        'data_number': data_number,
    }

    return render(request, 'line_charts.html', context)


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
    api_url = f'https://api.fda.gov/food/event.json?sort=date_started:desc&search={query}&limit=15'
    data = None
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
