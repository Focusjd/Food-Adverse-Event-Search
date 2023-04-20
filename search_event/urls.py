from django.urls import path

from . import views

urlpatterns = [
    path('product-stat/', views.product_stats_view, name='product_stats_view'),
    path('tree/', views.tree_structure_view, name='tree_structure'),
    path('tree-plotly/', views.tree_structure_plotly_view, name='tree_plotly'),
    path('', views.index, name='index'),
    path('results', views.results, name='results'),
    path('search/', views.search, name='search'),
    path('charts/', views.line_charts, name='line_charts'),
    path('line-charts/', views.line_charts, name='line_charts'),
]