"""URLs for the real-time business dashboard."""
from django.urls import path

from .dashboard_views import DashboardDataView, DashboardView

app_name = 'dashboard'

urlpatterns = [
    path('', DashboardView.as_view(), name='home'),
    path('api/', DashboardDataView.as_view(), name='data'),
]