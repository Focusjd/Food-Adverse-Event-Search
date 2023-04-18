from django.db import models


class Consumer(models.Model):
    age = models.CharField(max_length=20, null=True)
    age_unit = models.CharField(max_length=20, null=True)
    gender = models.CharField(max_length=20, null=True)

class Product(models.Model):
    role = models.CharField(max_length=20, null=True)
    name_brand = models.CharField(max_length=200, null=True)
    inductry_code = models.CharField(max_length=20, null=True)
    inductry_name = models.CharField(max_length=200, null=True)

class FoodAdverseEvent(models.Model):
    repot_number = models.CharField(max_length=20)
    date_created = models.CharField(max_length=20, null=True)
    date_started = models.CharField(max_length=20, null=True)
    outcome = models.CharField(max_length=500, null=True)
    reactions = models.CharField(max_length=500, null=True)
    consumer = models.ForeignKey(Consumer, on_delete=models.CASCADE, null=True)
    products = models.ManyToManyField(Product, through='ProductEvent', null=True)

class ProductEvent(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    adverse_event = models.ForeignKey(FoodAdverseEvent, on_delete=models.CASCADE)