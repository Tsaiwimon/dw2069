"""
URLs for Sales Frontend System.
"""
from django.urls import path
from .sales_views import (
    SalesHomeView, SalesProductsView, SalesProductDetailView,
    SalesCartView, SalesCheckoutView, SalesOrderHistoryView
)

app_name = 'sales'

urlpatterns = [
    # Sales Frontend
    path('', SalesHomeView.as_view(), name='home'),
    path('products/', SalesProductsView.as_view(), name='products'),
    path('product/<int:pk>/', SalesProductDetailView.as_view(), name='product-detail'),
    path('cart/', SalesCartView.as_view(), name='cart'),
    path('checkout/', SalesCheckoutView.as_view(), name='checkout'),
    path('orders/', SalesOrderHistoryView.as_view(), name='order-history'),
]
