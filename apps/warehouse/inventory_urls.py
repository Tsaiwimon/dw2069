from django.urls import path
from . import views

app_name = 'inventory'

urlpatterns = [
    # เรียกใช้ฟังก์ชัน inventory_dashboard จากไฟล์ views.py
    path('', views.inventory_dashboard, name='dashboard'),
]