from django.shortcuts import render, get_object_or_404, redirect
from .models import Product, Store, Inventory, InventoryTransaction
from .forms import ProductForm, InventoryForm, InventoryUpdateForm, StoreForm
from .permissions import IsAdminOrManagerWithStore, IsAdmin, IsSameStore
from django.db.models import Sum
from django.db import transaction
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.views import APIView
from rest_framework.exceptions import ValidationError
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from rest_framework import status, filters
from rest_framework.permissions import IsAuthenticated, AllowAny
from .pagination import CustomPagination 
from .serializer import ProductSerializer, StoreSerializer, InventorySerializer, InventoryTransactionSerializer
from .utils import get_inventory_queryset_for_user


def home(request):
    return render(request,"inventory/home.html")

def product(request):
    products = Product.objects.all()
    context = {
        "products": products
    }
    return render(request,"inventory/product.html",context)

def product_detail(request,product_id):
    product = get_object_or_404(Product,id = product_id)
    inv_items = Inventory.objects.filter(product=product)
    context = {
        "product":product,
        "inventory_items":inv_items
        }
    return render(request,"inventory/product_detail.html",context)

def inventory(request):
    inventory_items = Inventory.objects.all()
    context = {
        "inventory_items": inventory_items
    }
    return render(request, "inventory/inventory.html", context)

def stores(request):
    stores = Store.objects.all()
    context = {
        "stores": stores
    }
    return render(request,"inventory/stores.html",context)

def store_detail(request,store_id):
    store = get_object_or_404(Store,id=store_id)
    inventory_items = Inventory.objects.filter(store=store)
    context = {
        "store": store,
        "inventory_items":inventory_items
    }
    return render(request,"inventory/store_detail.html",context)

def add_product(request):
    if request.method == "POST":
        form = ProductForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('inventory:product')
    else:
        form = ProductForm()
    return render(request,"inventory/add_product.html",{"form":form})

def edit_product(request,product_id):
    product = get_object_or_404(Product, id = product_id)
    if request.method == "POST":
        form = ProductForm(request.POST,instance = product)
        if form.is_valid():
            form.save()
            return redirect('inventory:product')
    else:
        form = ProductForm(instance = product)
    return render(request,"inventory/edit_product.html",{'form':form})

def delete_product(request,product_id):
    product = get_object_or_404(Product,id = product_id)
    if request.method == "POST":
        product.delete()
        return redirect('inventory:product')
    return render(request, "inventory/delete_product.html",{"product":product})

def add_inventory(request):

    if request.method == "POST":
        form = InventoryForm(request.POST)

        if form.is_valid():

            product = form.cleaned_data['product']
            store = form.cleaned_data['store']
            quantity = form.cleaned_data['quantity']

            inventory_item, created = Inventory.objects.get_or_create(
                product=product,
                store=store,
                defaults={'quantity': quantity}
            )

            if not created:
                inventory_item.quantity = quantity
                inventory_item.save()

            return redirect('inventory:inventory')

    else:
        form = InventoryForm()

    return render(request, "inventory/add_inventory.html", {"form": form})

def edit_inventory(request,inventory_id):
    inventory_item = get_object_or_404(Inventory, id = inventory_id)
    if request.method == "POST":
        form = InventoryUpdateForm(request.POST,instance = inventory_item)
        if form.is_valid():
            form.save()
            return redirect('inventory:inventory')
    else:
        form = InventoryUpdateForm(instance = inventory_item)
    return render(request,"inventory/edit_inventory.html",{'form':form})

def edit_store(request, store_id):
    store = get_object_or_404(Store, id=store_id)
    if request.method == "POST":
        form = StoreForm(request.POST, instance = store)
        if form.is_valid():
            form.save()
            return redirect('inventory:stores')
    else:
        form = StoreForm(instance=store)
    return render(request,"inventory/edit_store.html",{"form":form})



class ProductViewSet(ModelViewSet):
    
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    filter_backends = [filters.OrderingFilter, filters.SearchFilter]
    search_fields = ['name']
    ordering_fields = ['price','name']

    def get_permissions(self):
        if self.request.method == 'GET':
            return [AllowAny()]
        return [IsAdmin()]
    
    def perform_create(self,serializer):
        print("Creating product...")
        serializer.save()
    
    @action(detail=False,methods=['get'])
    def budget(self,request):
        products = Product.objects.filter(price__lt=39999)
        serializer = self.get_serializer(products, many=True)
        return Response(serializer.data)

class StoreViewSet(ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = StoreSerializer
    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return Store.objects.none()
        user = self.request.user

        if user.role == 'admin':
            return Store.objects.all()

        if not user.store:
            return Store.objects.none()

        return Store.objects.filter(id=user.store.id)
    
class InventoryViewSet(ModelViewSet):
    permission_classes = [IsAdminOrManagerWithStore]
    pagination_class = CustomPagination
    serializer_class = InventorySerializer
    filter_backends = [DjangoFilterBackend,filters.OrderingFilter,filters.SearchFilter]
    filterset_fields = ['product','store']
    ordering_fields = ['quantity','product__name', 'store__name']
    search_fields = ['product__name','store__name']

    http_method_names = ['get']

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return Inventory.objects.none()
        return get_inventory_queryset_for_user(self.request.user).select_related('product', 'store')

    @action(detail=False, methods=['get'])
    def low_stock(self, request):
        threshold = request.query_params.get('threshold', 15)
        try:
            threshold = int(threshold)
        except ValueError:
            return Response({"error": "Threshold must be a number"}, status=400)

        queryset = self.get_queryset().filter(quantity__lt=threshold)
        queryset = self.filter_queryset(queryset)
        
        count = queryset.count() 
        serializer = self.get_serializer(queryset, many=True)
        
        return Response({
            "count": count,
            "results": serializer.data
        })
    

    @action(detail=False, methods=['get'])
    def out_of_stock(self, request):
        queryset = self.get_queryset().filter(quantity=0)
        queryset = self.filter_queryset(queryset)
        
        count = queryset.count()
        serializer = self.get_serializer(queryset, many=True)
        
        return Response({
            "count": count,
            "results": serializer.data
        })

    @action(detail=False, methods=['get'])
    def total_by_product(self, request):
        queryset = (
            self.get_queryset()
            .values('product__id', 'product__name')
            .annotate(total_quantity=Sum('quantity'))
            .order_by('product__name')
        )
        queryset = self.filter_queryset(queryset)

        page = self.paginate_queryset(queryset)
        if page is not None:
            return self.get_paginated_response(page)

        return Response(list(queryset))

    @action(detail=False, methods=['get'])
    def total_by_store(self, request):
        queryset = (
            self.get_queryset()
            .values('store__id', 'store__name')
            .annotate(total_quantity=Sum('quantity'))
            .order_by('store__name')
        )
        queryset = self.filter_queryset(queryset)
        page = self.paginate_queryset(queryset)
        if page is not None:
            return self.get_paginated_response(page)
        return Response(list(queryset))

class DashboardSummaryView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        threshold = request.query_params.get('threshold', 15)
        try:
            threshold = int(threshold)
        except ValueError:
            return Response({"error": "Threshold must be a number"}, status=400)
        
        user = request.user
        inventory_qs = get_inventory_queryset_for_user(user)

        total_products = Product.objects.count() 
        total_stores = Store.objects.count() if user.role == 'admin' else 1

        total_inventory = inventory_qs.aggregate(total=Sum('quantity'))['total'] or 0
        low_stock_count = inventory_qs.filter(quantity__lt=threshold).count()

        return Response({
            "total_products" : total_products,
            "total_stores" : total_stores,
            "total_inventory" : total_inventory,
            "low_stock_count" : low_stock_count
        })
    
class MeView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        user = request.user
        return Response({
            "id":user.id,
            "username":user.username,
            "email":user.email,
            "role": user.role,
            "store": user.store.id if user.store else None
        })
    
class InventoryTransactionViewSet(ModelViewSet):
    serializer_class = InventoryTransactionSerializer
    permission_classes = [IsAdminOrManagerWithStore, IsSameStore]

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return InventoryTransaction.objects.none()
        user = self.request.user
        qs = InventoryTransaction.objects.select_related('product', 'store', 'created_by')

        if user.store:
            return qs.filter(store=user.store).order_by('-timestamp')

        return qs.order_by('-timestamp')
        
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['product', 'store', 'type']

    def perform_create(self, serializer):
        with transaction.atomic():
            user = self.request.user
            product = serializer.validated_data['product']
            quantity = serializer.validated_data['quantity']
            t_type = serializer.validated_data['type']
            if user.store:
                store = user.store

                requested_store = serializer.validated_data.get('store')
                if requested_store and requested_store != user.store:
                    raise ValidationError("Managers can only create transactions for their own store.")
            else:
                store = serializer.validated_data['store']

            if quantity <= 0:
                raise ValidationError("Quantity must be greater than 0")
            inventory, created = Inventory.objects.get_or_create(
                product = product,
                store = store,
                defaults = {'quantity':0}
            )

            if t_type == 'sale':
                if inventory.quantity < quantity:
                    raise ValidationError("Not enough stock")
                inventory.quantity -= quantity
            elif t_type == 'restock':
                    inventory.quantity += quantity
            inventory.save()
            serializer.save(created_by=user, store=store)
    
    @action(detail=False, methods=['get'])
    def my_transactions(self,request):
        transactions = self.get_queryset().filter(created_by=request.user)
        serializer = self.get_serializer(transactions, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def recent_transaction(self,request):
        limit = int(request.query_params.get('limit', 10))
        transactions = self.get_queryset()[:limit]  # already ordered by -timestamp
        serializer = self.get_serializer(transactions, many=True)
        return Response(serializer.data)
