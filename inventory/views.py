from django.shortcuts import render, get_object_or_404, redirect
from .models import Product, Store, Inventory
from .forms import ProductForm, InventoryForm, InventoryUpdateForm, StoreForm
from django.db.models import Sum
from rest_framework.views import APIView
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from rest_framework import status, filters
from .serializer import ProductSerializer, StoreSerializer, InventorySerializer


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
    
    def perform_create(self,serializer):
        print("Creating product...")
        serializer.save()
    
    @action(detail=False,methods=['get'])
    def budget(self,request):
        products = Product.objects.filter(price__lt=39999)
        serializer = self.get_serializer(products, many=True)
        return Response(serializer.data)

class StoreViewSet(ModelViewSet):
    queryset = Store.objects.all()
    serializer_class = StoreSerializer
    
class InventoryViewSet(ModelViewSet):
    queryset = Inventory.objects.select_related('product','store').all()
    serializer_class = InventorySerializer
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ['quantity']

    def create(self, request, *args, **kwargs):
        product_id = request.data.get('product')
        store_id = request.data.get('store')
        if not Product.objects.filter(id=product_id).exists():
            return Response({"error": "Invalid product"}, status=400)
        if not Store.objects.filter(id=store_id).exists():
            return Response({"error": "Invalid store"}, status=400)
        try:
            quantity = int(request.data.get('quantity',0))
        except ValueError:
            return Response({"error":"Invalid quantity"},status=400)

        try:
            inventory = Inventory.objects.get(product_id = product_id, store_id = store_id)
            if inventory.quantity + quantity < 0:
                return Response({"error":"Not enough stock"},status=400)
            inventory.quantity += quantity
            inventory.save()

            serializer = self.get_serializer(inventory)
            return Response(serializer.data,status=status.HTTP_200_OK)
        except Inventory.DoesNotExist:
            return super().create(request,*args,**kwargs)
    
    @action(detail=False,methods=['get'])
    def low_stock(self, request):
        threshold = request.query_params.get('threshold',15)
        try:
            threshold = int(threshold)
        except ValueError:
            return Response({"error":"Threshold must be a number"},status=400)
        ordering = request.query_params.get('ordering', 'quantity')

        low_stock_items = self.queryset.filter(quantity__lt=threshold).order_by(ordering)

        data = [
            {
            "product_id": item.product.id,
            "product_name": item.product.name,
            "store_id": item.store.id,
            "store_name": item.store.name,
            "quantity": item.quantity
            }
            for item in low_stock_items
        ]
        return Response({   
            "count": len(data),
            "results": data
        })

    @action(detail=False,methods=['get'])
    def out_of_stock(self, request):
        items = self.queryset.filter(quantity=0)
        data = [
            {
            "product_id": item.product.id,
            "product_name": item.product.name,
            "store_id": item.store.id,
            "store_name": item.store.name,
            "quantity": item.quantity
            }
            for item in items
        ]
        return Response({   
            "count": len(data),
            "results": data
        })

    @action(detail=False,methods=['get'])
    def total_by_product(self, request):
        ordering = request.query_params.get('ordering', 'product__name')
        data = (
            self.queryset.values('product__id','product__name').annotate(total_quantity=Sum('quantity')).order_by(ordering)
        )
        result = [
            {
                "product_id":item['product__id'],
                "product_name":item['product__name'],
                "total_quantity":item['total_quantity']
            }
            for item in data
        ]
        return Response({   
            "count": len(result),
            "results": result
        })

    @action(detail=False,methods=['get'])
    def total_by_store(self, request):
        ordering = request.query_params.get('ordering', 'store__name')
        data = (
            self.queryset.values('store__id','store__name').annotate(total_quantity=Sum('quantity')).order_by(ordering)
        )
        result = [
            {
                "store_id":item['store__id'],
                "store_name":item['store__name'],
                "total_quantity":item['total_quantity']
            }
            for item in data
        ]
        return Response({   
            "count": len(result),
            "results": result
        })

class DashboardSummaryView(APIView):
    def get(self, request):
        threshold = request.query_params.get('threshold', 15)
        try:
            threshold = int(threshold)
        except ValueError:
            return Response({"error": "Threshold must be a number"}, status=400)
        total_products = Product.objects.count()
        total_stores = Store.objects.count()
        total_inventory = Inventory.objects.aggregate(total=Sum('quantity'))['total'] or 0
        low_stock_count = Inventory.objects.filter(quantity__lt=threshold).count()

        return Response({
            "total_products" : total_products,
            "total_stores" : total_stores,
            "total_inventory" : total_inventory,
            "low_stock_count" : low_stock_count
        })