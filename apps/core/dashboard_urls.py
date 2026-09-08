"""URLs for the real-time business dashboard."""
from django.urls import path

from .dashboard_views import (
    DashboardDataView,
    DashboardView,
    DashboardStreamView,
    RealtimeTestCreateView,
    RealtimeTestDataView,
    RealtimeTestStreamView,
    RealtimeTestView,
)

app_name = 'dashboard'

urlpatterns = [
    path('', DashboardView.as_view(), name='home'),
    path('api/', DashboardDataView.as_view(), name='data'),
    path('stream/', DashboardStreamView.as_view(), name='stream'),
    path('test/', RealtimeTestView.as_view(), name='test'),
    path('test/api/', RealtimeTestDataView.as_view(), name='test-data'),
    path('test/stream/', RealtimeTestStreamView.as_view(), name='test-stream'),
    path('test/api/create/', RealtimeTestCreateView.as_view(), name='test-create'),
]