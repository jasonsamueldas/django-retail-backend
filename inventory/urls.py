from django.urls import path, include
from . import views
from rest_framework.routers import DefaultRouter
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from .views import ProductViewSet, StoreViewSet, InventoryViewSet, DashboardSummaryView, MeView, InventoryTransactionViewSet
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

app_name = "inventory"
router = DefaultRouter()
router.register('products',ProductViewSet, basename='product')
router.register('stores',StoreViewSet, basename='store')
router.register('inventory',InventoryViewSet, basename='inventory')
router.register('transactions', InventoryTransactionViewSet, basename='transaction')

schema_view = get_schema_view(
    openapi.Info(
        title="Retail Management API",
        default_version='v1',
        description="API for managing products, stores, inventory, and transactions",
    ),
    public=True,
    permission_classes=[permissions.AllowAny],
)

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
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/me/', MeView.as_view(), name='me'),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0)),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0)),
]

