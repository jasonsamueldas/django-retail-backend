from django.urls import path, include
from . import views
from rest_framework.routers import DefaultRouter
from .views import ProductViewSet, StoreViewSet, InventoryViewSet, DashboardSummaryView


app_name = "inventory"
router = DefaultRouter()
router.register('products',ProductViewSet, basename='product')
router.register('stores',StoreViewSet, basename='store')
router.register('inventory',InventoryViewSet, basename='inventory')

urlpatterns = [
    path('', views.home,name="home"),
    path('product/', views.product,name="product"),
    path('product/<int:product_id>/', views.product_detail,name="product_detail"),
    path('inventory/', views.inventory,name="inventory"),
    path('stores/', views.stores,name="stores"),
    path('stores/<int:store_id>/', views.store_detail,name="store_detail"),
    path('product/add/', views.add_product, name='add_product'),
    path('product/edit/<int:product_id>/', views.edit_product, name='edit_product'),
    path('product/delete/<int:product_id>/', views.delete_product, name='delete_product'),
    path('inventory/edit/<int:inventory_id>/', views.edit_inventory, name='edit_inventory'),
    path('inventory/add/', views.add_inventory, name='add_inventory'),
    path('stores/edit/<int:store_id>',views.edit_store,name='edit_store'),
    path('api/dashboard/summary/',DashboardSummaryView.as_view()),
    path('api/',include(router.urls)),
]

