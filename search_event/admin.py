from django.contrib import admin

from .models import FoodAdverseEvent, Consumer, Product, ProductEvent


admin.site.register(FoodAdverseEvent)
admin.site.register(Consumer)
admin.site.register(Product)
admin.site.register(ProductEvent)