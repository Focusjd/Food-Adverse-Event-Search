from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('results', views.results, name='results'),
    path('search/', views.search, name='search'),
    path('charts/', views.line_charts, name='line_charts'),
    path('line-charts/', views.line_charts, name='line_charts'),
]