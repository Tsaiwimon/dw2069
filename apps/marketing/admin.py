"""
Admin configuration for Marketing app.
"""
from django.contrib import admin
from .models import (
    Campaign, Coupon, CouponUsage, EmailCampaign, EmailLog,
    LoyaltyProgram, MembershipTier, LoyaltyPoints, PointsTransaction
)


@admin.register(Campaign)
class CampaignAdmin(admin.ModelAdmin):
    list_display = ['name', 'campaign_type', 'start_date', 'end_date', 'budget']
    list_filter = ['campaign_type', 'start_date']
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ['used_budget', 'created_at', 'updated_at']
    filter_horizontal = ['target_products']


@admin.register(Coupon)
class CouponAdmin(admin.ModelAdmin):
    list_display = ['code', 'coupon_type', 'discount_value', 'usage_count', 'is_valid']
    list_filter = ['coupon_type', 'start_date']
    search_fields = ['code', 'description']
    readonly_fields = ['usage_count', 'created_at', 'updated_at']
    filter_horizontal = ['limited_to_users']
    fieldsets = (
        ('ข้อมูลคูปอง', {
            'fields': ('code', 'description', 'coupon_type')
        }),
        ('ส่วนลด', {
            'fields': ('discount_value', 'max_discount', 'min_purchase')
        }),
        ('ระยะเวลา', {
            'fields': ('start_date', 'end_date')
        }),
        ('การใช้งาน', {
            'fields': ('usage_limit', 'usage_count', 'limited_to_users')
        }),
        ('สถานะ', {
            'fields': ('created_at', 'updated_at')
        }),
    )


@admin.register(CouponUsage)
class CouponUsageAdmin(admin.ModelAdmin):
    list_display = ['coupon', 'user', 'order', 'discount_amount', 'created_at']
    list_filter = ['created_at']
    search_fields = ['coupon__code', 'user__username']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(EmailCampaign)
class EmailCampaignAdmin(admin.ModelAdmin):
    list_display = ['name', 'status', 'sent_count', 'open_count', 'click_count']
    list_filter = ['status', 'created_at']
    search_fields = ['name', 'subject']
    readonly_fields = ['open_count', 'click_count', 'sent_count', 'sent_date', 'created_at', 'updated_at']


@admin.register(EmailLog)
class EmailLogAdmin(admin.ModelAdmin):
    list_display = ['campaign', 'recipient', 'status', 'opened', 'clicked']
    list_filter = ['status', 'opened', 'clicked', 'created_at']
    search_fields = ['recipient', 'campaign__name']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(LoyaltyProgram)
class LoyaltyProgramAdmin(admin.ModelAdmin):
    list_display = ['name', 'points_per_purchase', 'points_expiry_days']
    search_fields = ['name', 'description']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(MembershipTier)
class MembershipTierAdmin(admin.ModelAdmin):
    list_display = ['program', 'name', 'min_points', 'discount_percent']
    list_filter = ['program']
    search_fields = ['name']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(LoyaltyPoints)
class LoyaltyPointsAdmin(admin.ModelAdmin):
    list_display = ['user', 'program', 'total_points', 'current_tier', 'lifetime_value']
    list_filter = ['program', 'current_tier']
    search_fields = ['user__username', 'user__email']
    readonly_fields = ['user', 'created_at', 'updated_at']


@admin.register(PointsTransaction)
class PointsTransactionAdmin(admin.ModelAdmin):
    list_display = ['loyalty_points', 'transaction_type', 'points_amount', 'reference', 'created_at']
    list_filter = ['transaction_type', 'created_at']
    search_fields = ['loyalty_points__user__username', 'reference']
    readonly_fields = ['created_at', 'updated_at']
