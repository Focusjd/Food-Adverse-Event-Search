from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('charts/', views.line_charts, name='line_charts'),
    path('product-stat/', views.product_stats_view, name='product_stats_view'),
]