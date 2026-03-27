from django.contrib import admin
from .models import Product,Store,Inventory

admin.site.register(Product)
admin.site.register(Store)
admin.site.register(Inventory)