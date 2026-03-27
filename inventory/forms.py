from django import forms
from .models import Product, Inventory, Store

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name','price']

class InventoryForm(forms.ModelForm):
    class Meta:
        model = Inventory
        fields = ['product','store','quantity']

class InventoryUpdateForm(forms.ModelForm):
    class Meta:
        model = Inventory
        fields = ['quantity']

class StoreForm(forms.ModelForm):
    class Meta:
        model = Store
        fields = ['name']

