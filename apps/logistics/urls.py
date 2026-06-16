"""
URLs for Logistics System.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    ShippingProviderViewSet, ShipmentViewSet, ReturnViewSet,
    DeliverySlotViewSet, ShippingReportViewSet
)

app_name = 'logistics'

router = DefaultRouter()
router.register(r'shipping-providers', ShippingProviderViewSet, basename='shipping-provider')
router.register(r'shipments', ShipmentViewSet, basename='shipment')
router.register(r'returns', ReturnViewSet, basename='return')
router.register(r'delivery-slots', DeliverySlotViewSet, basename='delivery-slot')
router.register(r'reports', ShippingReportViewSet, basename='shipping-report')

urlpatterns = [
    path('', include(router.urls)),
]
