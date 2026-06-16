"""
URLs for Marketing System.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    CampaignViewSet, CouponViewSet, EmailCampaignViewSet,
    EmailLogViewSet, LoyaltyProgramViewSet, LoyaltyPointsViewSet
)

app_name = 'marketing'

router = DefaultRouter()
router.register(r'campaigns', CampaignViewSet, basename='campaign')
router.register(r'coupons', CouponViewSet, basename='coupon')
router.register(r'email-campaigns', EmailCampaignViewSet, basename='email-campaign')
router.register(r'email-logs', EmailLogViewSet, basename='email-log')
router.register(r'loyalty-programs', LoyaltyProgramViewSet, basename='loyalty-program')
router.register(r'loyalty-points', LoyaltyPointsViewSet, basename='loyalty-points')

urlpatterns = [
    path('', include(router.urls)),
]
