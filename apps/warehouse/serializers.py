"""
Serializers for Warehouse Management System.
"""
from rest_framework import serializers
from .models import (
    Warehouse, StockLocation, Stock, StockHistory, PurchaseOrder,
    GoodsReceipt, GoodsReceiptItem, PickingList, PickingItem, 
    Parcel, QualityCheck
)


class WarehouseSerializer(serializers.ModelSerializer):
    """Serializer for Warehouse model."""
    manager_name = serializers.CharField(source='manager.get_full_name', read_only=True)

    class Meta:
        model = Warehouse
        fields = ['id', 'name', 'code', 'address', 'phone', 'manager', 'manager_name', 'is_active']
        read_only_fields = ['id']


class StockLocationSerializer(serializers.ModelSerializer):
    """Serializer for StockLocation model."""
    class Meta:
        model = StockLocation
        fields = ['id', 'warehouse', 'zone', 'shelf', 'bin', 'is_active']
        read_only_fields = ['id']


class StockSerializer(serializers.ModelSerializer):
    """Serializer for Stock model."""
    product_name = serializers.CharField(source='product.name', read_only=True)
    warehouse_name = serializers.CharField(source='warehouse.name', read_only=True)
    location_str = serializers.CharField(source='__str__', read_only=True)
    available_quantity = serializers.SerializerMethodField()

    class Meta:
        model = Stock
        fields = [
            'id', 'product', 'product_name', 'warehouse', 'warehouse_name',
            'location', 'location_str', 'quantity', 'reserved_quantity',
            'available_quantity', 'received_date', 'is_active'
        ]
        read_only_fields = ['id', 'available_quantity']

    def get_available_quantity(self, obj):
        return obj.get_available_quantity()


class StockHistorySerializer(serializers.ModelSerializer):
    """Serializer for StockHistory model."""
    performed_by_name = serializers.CharField(source='performed_by.get_full_name', read_only=True)
    operation_display = serializers.CharField(source='get_operation_type_display', read_only=True)

    class Meta:
        model = StockHistory
        fields = [
            'id', 'stock', 'operation_type', 'operation_display', 'quantity_change',
            'reference_number', 'notes', 'performed_by', 'performed_by_name', 'created_at'
        ]
        read_only_fields = ['id', 'created_at', 'performed_by']


class PurchaseOrderSerializer(serializers.ModelSerializer):
    """Serializer for PurchaseOrder model."""
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = PurchaseOrder
        fields = [
            'id', 'po_number', 'supplier_name', 'status', 'status_display',
            'warehouse', 'expected_date', 'notes', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class GoodsReceiptItemSerializer(serializers.ModelSerializer):
    """Serializer for GoodsReceiptItem model."""
    product_name = serializers.CharField(source='product.name', read_only=True)

    class Meta:
        model = GoodsReceiptItem
        fields = [
            'id', 'receipt', 'product', 'product_name', 'quantity_ordered',
            'quantity_received', 'unit_price', 'notes'
        ]
        read_only_fields = ['id']


class GoodsReceiptSerializer(serializers.ModelSerializer):
    """Serializer for GoodsReceipt model."""
    items = GoodsReceiptItemSerializer(many=True, read_only=True)
    received_by_name = serializers.CharField(source='received_by.get_full_name', read_only=True)

    class Meta:
        model = GoodsReceipt
        fields = [
            'id', 'receipt_number', 'purchase_order', 'warehouse',
            'received_by', 'received_by_name', 'receipt_date', 'notes', 'items'
        ]
        read_only_fields = ['id', 'receipt_date']


class PickingItemSerializer(serializers.ModelSerializer):
    """Serializer for PickingItem model."""
    product_name = serializers.CharField(source='product.name', read_only=True)
    location_str = serializers.CharField(source='location.__str__', read_only=True)

    class Meta:
        model = PickingItem
        fields = [
            'id', 'picking_list', 'product', 'product_name', 'quantity_required',
            'quantity_picked', 'location', 'location_str'
        ]
        read_only_fields = ['id']


class PickingListSerializer(serializers.ModelSerializer):
    """Serializer for PickingList model."""
    items = PickingItemSerializer(many=True, read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    picked_by_name = serializers.CharField(source='picked_by.get_full_name', read_only=True)

    class Meta:
        model = PickingList
        fields = [
            'id', 'picking_number', 'order', 'warehouse', 'status', 'status_display',
            'picked_by', 'picked_by_name', 'picked_date', 'items', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class ParcelSerializer(serializers.ModelSerializer):
    """Serializer for Parcel model."""
    picking_number = serializers.CharField(source='picking_list.picking_number', read_only=True)
    packed_by_name = serializers.CharField(source='packed_by.get_full_name', read_only=True)

    class Meta:
        model = Parcel
        fields = [
            'id', 'parcel_number', 'picking_list', 'picking_number',
            'weight', 'dimensions', 'packed_by', 'packed_by_name', 'packed_date'
        ]
        read_only_fields = ['id', 'packed_date']


class QualityCheckSerializer(serializers.ModelSerializer):
    """Serializer for QualityCheck model."""
    product_name = serializers.CharField(source='product.name', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    checked_by_name = serializers.CharField(source='checked_by.get_full_name', read_only=True)

    class Meta:
        model = QualityCheck
        fields = [
            'id', 'goods_receipt', 'product', 'product_name', 'status', 'status_display',
            'quantity_checked', 'quantity_defective', 'notes',
            'checked_by', 'checked_by_name', 'created_at'
        ]
        read_only_fields = ['id', 'created_at', 'checked_by']
