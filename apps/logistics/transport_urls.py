from django.urls import path
from . import views

app_name = 'transportation'

urlpatterns = [
    # เรียกใช้ฟังก์ชัน transport_dashboard จากไฟล์ views.py
    path('', views.transport_dashboard, name='dashboard'),
]