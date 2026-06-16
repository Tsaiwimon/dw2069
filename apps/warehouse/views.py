"""
Views for Warehouse Management System.
"""
from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from .models import (
    Warehouse, Stock, StockHistory, PurchaseOrder, GoodsReceipt,
    GoodsReceiptItem, PickingList, PickingItem, Parcel, QualityCheck
)
from .serializers import (
    WarehouseSerializer, StockSerializer, StockHistorySerializer, 
    PurchaseOrderSerializer, GoodsReceiptSerializer, PickingListSerializer,
    ParcelSerializer, QualityCheckSerializer
)


class WarehouseViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for Warehouses."""
    queryset = Warehouse.objects.all()
    serializer_class = WarehouseSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter]
    search_fields = ['name', 'location']

    def get_queryset(self):
        """Filter only active warehouses."""
        return Warehouse.objects.filter(is_active=True)


class StockViewSet(viewsets.ModelViewSet):
    """ViewSet for Stock management."""
    queryset = Stock.objects.all()
    serializer_class = StockSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['warehouse', 'product']
    search_fields = ['product__name', 'product__sku']

    @action(detail=True, methods=['post'])
    def adjust_stock(self, request, pk=None):
        """Adjust stock quantity."""
        stock = self.get_object()
        quantity_change = request.data.get('quantity_change', 0)
        notes = request.data.get('notes', '')

        try:
            quantity_change = int(quantity_change)
        except (ValueError, TypeError):
            return Response({'error': 'Invalid quantity'}, status=status.HTTP_400_BAD_REQUEST)

        new_quantity = stock.quantity + quantity_change
        if new_quantity < 0:
            return Response({'error': 'Insufficient stock'}, status=status.HTTP_400_BAD_REQUEST)

        stock.quantity = new_quantity
        stock.save()

        # Create history record
        StockHistory.objects.create(
            stock=stock,
            operation_type='adjustment',
            quantity_change=quantity_change,
            notes=notes,
            performed_by=request.user
        )

        return Response({'success': True, 'new_quantity': stock.quantity})

    @action(detail=False, methods=['get'])
    def low_stock(self, request):
        """Get products with low stock."""
        low_stock_items = Stock.objects.filter(quantity__lt=5)
        serializer = self.get_serializer(low_stock_items, many=True)
        return Response(serializer.data)


class StockHistoryViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for Stock History."""
    queryset = StockHistory.objects.all()
    serializer_class = StockHistorySerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['stock', 'operation_type']
    ordering_fields = ['created_at']


class PurchaseOrderViewSet(viewsets.ModelViewSet):
    """ViewSet for Purchase Orders."""
    queryset = PurchaseOrder.objects.all()
    serializer_class = PurchaseOrderSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['status', 'warehouse']
    search_fields = ['po_number', 'supplier_name']


class GoodsReceiptViewSet(viewsets.ModelViewSet):
    """ViewSet for Goods Receipts."""
    queryset = GoodsReceipt.objects.all()
    serializer_class = GoodsReceiptSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['warehouse']
    search_fields = ['receipt_number']

    def perform_create(self, serializer):
        """Set received_by when creating receipt."""
        serializer.save(received_by=self.request.user)


class PickingListViewSet(viewsets.ModelViewSet):
    """ViewSet for Picking Lists."""
    queryset = PickingList.objects.all()
    serializer_class = PickingListSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['status', 'warehouse']

    @action(detail=True, methods=['post'])
    def complete_picking(self, request, pk=None):
        """Mark picking as completed."""
        picking_list = self.get_object()
        picking_list.status = 'completed'
        picking_list.picked_by = request.user
        picking_list.save()
        
        return Response({'success': True})


class ParcelViewSet(viewsets.ModelViewSet):
    """ViewSet for Parcels."""
    queryset = Parcel.objects.all()
    serializer_class = ParcelSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter]
    search_fields = ['parcel_number']


class QualityCheckViewSet(viewsets.ModelViewSet):
    """ViewSet for Quality Checks."""
    queryset = QualityCheck.objects.all()
    serializer_class = QualityCheckSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['status', 'goods_receipt']

    def perform_create(self, serializer):
        """Set checked_by when creating quality check."""
        serializer.save(checked_by=self.request.user)


from django.shortcuts import render
def inventory_dashboard(request):
    return render(request, 'warehouse/inventory_dashboard.html')