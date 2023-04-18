from django.shortcuts import render
from django.http import HttpResponse

from .models import FoodAdverseEvent
from .forms import SearchForm

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

    # print(events)

    context = {
        'form': form,
        'events': events,
    }
    return render(request, 'index.html', context)