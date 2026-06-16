"""
Admin configuration for Warehouse app.
"""
from django.contrib import admin
from .models import (
    Warehouse, StockLocation, Stock, StockHistory, PurchaseOrder,
    GoodsReceipt, GoodsReceiptItem, PickingList, PickingItem,
    Parcel, QualityCheck
)


@admin.register(Warehouse)
class WarehouseAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'phone', 'manager', 'is_active']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'code']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(StockLocation)
class StockLocationAdmin(admin.ModelAdmin):
    list_display = ['warehouse', 'zone', 'shelf', 'bin', 'is_active']
    list_filter = ['warehouse', 'is_active']
    search_fields = ['warehouse__name']


@admin.register(Stock)
class StockAdmin(admin.ModelAdmin):
    list_display = ['product', 'warehouse', 'quantity', 'reserved_quantity', 'received_date']
    list_filter = ['warehouse', 'is_active', 'received_date']
    search_fields = ['product__name', 'product__sku']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(StockHistory)
class StockHistoryAdmin(admin.ModelAdmin):
    list_display = ['stock', 'operation_type', 'quantity_change', 'reference_number', 'performed_by']
    list_filter = ['operation_type', 'created_at']
    search_fields = ['stock__product__name', 'reference_number']
    readonly_fields = ['created_at', 'updated_at', 'stock']


@admin.register(PurchaseOrder)
class PurchaseOrderAdmin(admin.ModelAdmin):
    list_display = ['po_number', 'supplier_name', 'status', 'warehouse', 'expected_date']
    list_filter = ['status', 'created_at', 'warehouse']
    search_fields = ['po_number', 'supplier_name']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(GoodsReceipt)
class GoodsReceiptAdmin(admin.ModelAdmin):
    list_display = ['receipt_number', 'purchase_order', 'warehouse', 'received_by', 'receipt_date']
    list_filter = ['warehouse', 'receipt_date']
    search_fields = ['receipt_number']
    readonly_fields = ['receipt_date', 'created_at', 'updated_at']


@admin.register(GoodsReceiptItem)
class GoodsReceiptItemAdmin(admin.ModelAdmin):
    list_display = ['receipt', 'product', 'quantity_ordered', 'quantity_received', 'unit_price']
    list_filter = ['receipt__created_at']
    search_fields = ['product__name', 'receipt__receipt_number']


@admin.register(PickingList)
class PickingListAdmin(admin.ModelAdmin):
    list_display = ['picking_number', 'order', 'warehouse', 'status', 'picked_by']
    list_filter = ['status', 'warehouse', 'created_at']
    search_fields = ['picking_number', 'order__order_number']


@admin.register(PickingItem)
class PickingItemAdmin(admin.ModelAdmin):
    list_display = ['picking_list', 'product', 'quantity_required', 'quantity_picked', 'location']
    list_filter = ['picking_list__created_at']
    search_fields = ['product__name']


@admin.register(Parcel)
class ParcelAdmin(admin.ModelAdmin):
    list_display = ['parcel_number', 'picking_list', 'weight', 'packed_by', 'packed_date']
    list_filter = ['packed_date']
    search_fields = ['parcel_number']
    readonly_fields = ['packed_date', 'created_at', 'updated_at']


@admin.register(QualityCheck)
class QualityCheckAdmin(admin.ModelAdmin):
    list_display = ['goods_receipt', 'product', 'status', 'quantity_checked', 'quantity_defective']
    list_filter = ['status', 'created_at']
    search_fields = ['product__name', 'goods_receipt__receipt_number']
    readonly_fields = ['created_at', 'updated_at']
