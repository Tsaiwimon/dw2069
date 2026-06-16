from django.urls import path
from . import views

app_name = 'marketing_web'

urlpatterns = [
    # เรียกใช้ฟังก์ชัน marketing_dashboard จากไฟล์ views.py
    path('', views.marketing_dashboard, name='dashboard'),
]