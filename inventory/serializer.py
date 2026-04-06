from rest_framework import serializers
from rest_framework.response import Response
from .models import Product, Inventory, Store, InventoryTransaction
from django.db import transaction

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = '__all__'

    def validate_price(self, value):
        if value < 0:
            raise serializers.ValidationError("Price cannot be negative")
        return value

class StoreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Store
        fields = '__all__'
    
class InventorySerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)
    store_name = serializers.CharField(source='store.name', read_only=True)
    
    class Meta:
        model = Inventory
        fields = '__all__'

class InventoryTransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = InventoryTransaction
        fields = '__all__'
        read_only_fields = ['created_by', 'timestamp']
    
    def validate(self, attrs):
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            user = request.user
            if user.role == 'manager':
                if not user.store:
                    raise serializers.ValidationError("Manager must be assigned to a store")
                requested_store = attrs.get('store')
                if requested_store and requested_store != user.store:
                    raise serializers.ValidationError("Managers can only create transactions for their own store.")
                attrs['store'] = user.store  # still enforce it even if none was sent
        return attrs

    product_name = serializers.CharField(source='product.name', read_only=True)
    store_name = serializers.CharField(source='store.name', read_only=True)
    created_by_username = serializers.CharField(source='created_by.username', read_only=True)
   