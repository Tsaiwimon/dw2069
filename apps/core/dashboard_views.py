from django.http import JsonResponse
from django.views.generic import TemplateView, View

from .analytics import dashboard_snapshot


class DashboardView(TemplateView):
    template_name = 'dashboard/home.html'


class DashboardDataView(View):
    def get(self, request, *args, **kwargs):
        return JsonResponse(dashboard_snapshot())