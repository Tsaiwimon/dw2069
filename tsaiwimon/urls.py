"""
URL configuration for Tsaiwimon project.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import RedirectView
from rest_framework.routers import DefaultRouter

# หมายเหตุ: หากเกิด Error ตรงนี้ แปลว่าคุณยังไม่ได้ติดตั้ง drf-spectacular 
# สามารถติดตั้งด้วยคำสั่ง: uv run pip install drf-spectacular
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

# API routers
router = DefaultRouter()

urlpatterns = [
    # Root redirect (เข้าเว็บมาที่ / ให้เด้งไปหน้า /sales/ อัตโนมัติ)
    path('', RedirectView.as_view(url='sales/', permanent=False)),
    
    # Admin
    path('admin/', admin.site.urls),
    
    # ==========================================
    # 🌐 Frontend Web Views (ระบบหน้าเว็บทั้ง 4 ระบบ)
    # ==========================================
    # ดึงไฟล์ urls แยกของแต่ละแอปมาใช้สำหรับหน้าเว็บ
    path('sales/', include('apps.ecommerce.sales_urls', namespace='sales')),
    path('inventory/', include('apps.warehouse.inventory_urls', namespace='inventory')),
    path('marketing/', include('apps.marketing.marketing_urls', namespace='marketing_web')),
    path('transportation/', include('apps.logistics.transport_urls', namespace='transportation')),
    
    # ==========================================
    # 📄 API Documentation (สำหรับนักพัฒนาดูสเปค API)
    # ==========================================
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    
    # ==========================================
    # ⚙️ API Routes (สำหรับรับ-ส่งข้อมูล JSON)
    # ==========================================
    path('api/v1/', include(router.urls)),
    
    # เติม _api ไว้ที่ namespace เพื่อไม่ให้ชื่อชนกับฝั่งหน้าเว็บ
    path('api/v1/ecommerce/', include('apps.ecommerce.urls', namespace='ecommerce_api')),
    path('api/v1/warehouse/', include('apps.warehouse.urls', namespace='warehouse_api')),
    path('api/v1/marketing/', include('apps.marketing.urls', namespace='marketing_api')),
    path('api/v1/logistics/', include('apps.logistics.urls', namespace='logistics_api')),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)