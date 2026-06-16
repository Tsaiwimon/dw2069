"""
Admin configuration for Logistics app.
"""
from django.contrib import admin
from .models import (
    ShippingProvider, Shipment, ShipmentTracking, Return, ReturnItem,
    DeliverySlot, ShippingReport
)


@admin.register(ShippingProvider)
class ShippingProviderAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'phone', 'base_rate', 'rate_per_kg', 'is_active']
    list_filter = ['is_active']
    search_fields = ['name', 'code']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(Shipment)
class ShipmentAdmin(admin.ModelAdmin):
    list_display = ['shipment_number', 'order', 'provider', 'status', 'tracking_number', 'delivered_date']
    list_filter = ['status', 'provider', 'created_at']
    search_fields = ['shipment_number', 'tracking_number']
    readonly_fields = ['shipment_number', 'created_at', 'updated_at']
    fieldsets = (
        ('ข้อมูลจัดส่ง', {
            'fields': ('shipment_number', 'order', 'provider', 'tracking_number')
        }),
        ('ที่อยู่', {
            'fields': ('origin_address', 'destination_address', 'recipient_name', 'recipient_phone')
        }),
        ('รายละเอียดสินค้า', {
            'fields': ('weight', 'dimensions')
        }),
        ('สถานะและวันที่', {
            'fields': ('status', 'picked_up_date', 'shipped_date', 'delivered_date', 'estimated_delivery')
        }),
        ('ค่าใช้จ่าย', {
            'fields': ('shipping_cost', 'insurance_cost')
        }),
        ('อื่น ๆ', {
            'fields': ('notes', 'created_at', 'updated_at')
        }),
    )


@admin.register(ShipmentTracking)
class ShipmentTrackingAdmin(admin.ModelAdmin):
    list_display = ['shipment', 'status', 'location', 'timestamp']
    list_filter = ['status', 'timestamp']
    search_fields = ['shipment__shipment_number', 'location']
    readonly_fields = ['timestamp', 'created_at', 'updated_at']


@admin.register(Return)
class ReturnAdmin(admin.ModelAdmin):
    list_display = ['return_number', 'order', 'reason', 'status', 'refund_amount', 'requested_by']
    list_filter = ['status', 'reason', 'created_at']
    search_fields = ['return_number', 'order__order_number']
    readonly_fields = ['return_number', 'created_at', 'updated_at']


@admin.register(ReturnItem)
class ReturnItemAdmin(admin.ModelAdmin):
    list_display = ['return_request', 'product', 'quantity', 'condition']
    list_filter = ['condition', 'created_at']
    search_fields = ['product__name', 'return_request__return_number']


@admin.register(DeliverySlot)
class DeliverySlotAdmin(admin.ModelAdmin):
    list_display = ['date', 'start_time', 'end_time', 'max_deliveries', 'current_deliveries']
    list_filter = ['date']
    search_fields = ['date']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(ShippingReport)
class ShippingReportAdmin(admin.ModelAdmin):
    list_display = ['report_date', 'total_shipments', 'delivered_count', 'total_shipping_cost']
    list_filter = ['report_date']
    readonly_fields = ['created_at', 'updated_at']
    fieldsets = (
        ('วันที่รายงาน', {
            'fields': ('report_date',)
        }),
        ('สถิติการส่ง', {
            'fields': ('total_shipments', 'delivered_count', 'failed_count', 'in_transit_count')
        }),
        ('ข้อมูลน้ำหนักและค่าใช้จ่าย', {
            'fields': ('total_weight', 'total_shipping_cost', 'total_insurance_cost')
        }),
        ('หมายเหตุ', {
            'fields': ('notes',)
        }),
    )
