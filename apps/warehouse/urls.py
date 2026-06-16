"""
URLs for Warehouse Management System.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    WarehouseViewSet, StockViewSet, StockHistoryViewSet, PurchaseOrderViewSet,
    GoodsReceiptViewSet, PickingListViewSet, ParcelViewSet, QualityCheckViewSet
)

app_name = 'warehouse'

router = DefaultRouter()
router.register(r'warehouses', WarehouseViewSet, basename='warehouse')
router.register(r'stock', StockViewSet, basename='stock')
router.register(r'stock-history', StockHistoryViewSet, basename='stock-history')
router.register(r'purchase-orders', PurchaseOrderViewSet, basename='purchase-order')
router.register(r'goods-receipts', GoodsReceiptViewSet, basename='goods-receipt')
router.register(r'picking-lists', PickingListViewSet, basename='picking-list')
router.register(r'parcels', ParcelViewSet, basename='parcel')
router.register(r'quality-checks', QualityCheckViewSet, basename='quality-check')

urlpatterns = [
    path('', include(router.urls)),
]
