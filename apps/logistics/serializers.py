"""
Serializers for Logistics System.
"""
from rest_framework import serializers
from .models import (
    ShippingProvider, Shipment, ShipmentTracking, Return, ReturnItem,
    DeliverySlot, ShippingReport
)


class ShippingProviderSerializer(serializers.ModelSerializer):
    """Serializer for ShippingProvider model."""
    class Meta:
        model = ShippingProvider
        fields = [
            'id', 'name', 'code', 'website', 'phone', 'email',
            'base_rate', 'rate_per_kg', 'is_active'
        ]
        read_only_fields = ['id']


class ShipmentTrackingSerializer(serializers.ModelSerializer):
    """Serializer for ShipmentTracking model."""
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = ShipmentTracking
        fields = ['id', 'status', 'status_display', 'location', 'description', 'timestamp']
        read_only_fields = ['id', 'timestamp']


class ShipmentSerializer(serializers.ModelSerializer):
    """Serializer for Shipment model."""
    provider_name = serializers.CharField(source='provider.name', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    tracking_history = ShipmentTrackingSerializer(many=True, read_only=True)

    class Meta:
        model = Shipment
        fields = [
            'id', 'shipment_number', 'order', 'provider', 'provider_name',
            'tracking_number', 'origin_address', 'destination_address',
            'recipient_name', 'recipient_phone', 'weight', 'dimensions',
            'status', 'status_display', 'picked_up_date', 'shipped_date',
            'delivered_date', 'estimated_delivery', 'shipping_cost',
            'insurance_cost', 'notes', 'tracking_history', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'shipment_number', 'created_at', 'updated_at']


class ReturnItemSerializer(serializers.ModelSerializer):
    """Serializer for ReturnItem model."""
    product_name = serializers.CharField(source='product.name', read_only=True)

    class Meta:
        model = ReturnItem
        fields = ['id', 'return_request', 'product', 'product_name', 'quantity', 'condition', 'notes']
        read_only_fields = ['id']


class ReturnSerializer(serializers.ModelSerializer):
    """Serializer for Return model."""
    items = ReturnItemSerializer(many=True, read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    reason_display = serializers.CharField(source='get_reason_display', read_only=True)

    class Meta:
        model = Return
        fields = [
            'id', 'return_number', 'order', 'reason', 'reason_display', 'description',
            'status', 'status_display', 'refund_amount', 'return_shipment',
            'requested_by', 'approval_notes', 'items', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'return_number', 'requested_by', 'created_at', 'updated_at']


class DeliverySlotSerializer(serializers.ModelSerializer):
    """Serializer for DeliverySlot model."""
    is_available = serializers.SerializerMethodField()
    available_slots = serializers.SerializerMethodField()

    class Meta:
        model = DeliverySlot
        fields = [
            'id', 'date', 'start_time', 'end_time', 'max_deliveries',
            'current_deliveries', 'is_available', 'available_slots'
        ]
        read_only_fields = ['id', 'current_deliveries']

    def get_is_available(self, obj):
        return obj.is_available()

    def get_available_slots(self, obj):
        return obj.max_deliveries - obj.current_deliveries


class ShippingReportSerializer(serializers.ModelSerializer):
    """Serializer for ShippingReport model."""
    average_delivery_cost = serializers.SerializerMethodField()

    class Meta:
        model = ShippingReport
        fields = [
            'id', 'report_date', 'total_shipments', 'delivered_count', 'failed_count',
            'in_transit_count', 'total_weight', 'total_shipping_cost',
            'total_insurance_cost', 'average_delivery_cost', 'notes'
        ]
        read_only_fields = ['id']

    def get_average_delivery_cost(self, obj):
        if obj.total_shipments > 0:
            return str(obj.total_shipping_cost / obj.total_shipments)
        return '0'
