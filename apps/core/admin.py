"""
Admin configuration for core app.
"""
from django.contrib import admin
from .models import UserProfile


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'phone', 'city', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at', 'country']
    search_fields = ['user__username', 'user__email', 'phone', 'city']
    readonly_fields = ['created_at', 'updated_at']
    fieldsets = (
        ('ข้อมูลผู้ใช้', {
            'fields': ('user', 'avatar')
        }),
        ('ที่อยู่', {
            'fields': ('phone', 'address', 'postal_code', 'city', 'province', 'country')
        }),
        ('สถานะ', {
            'fields': ('is_active', 'created_at', 'updated_at')
        }),
    )
