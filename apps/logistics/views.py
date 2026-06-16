"""
Views for Logistics System.
"""
from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from django_filters.rest_framework import DjangoFilterBackend
from django.utils import timezone
from datetime import timedelta
from .models import (
    ShippingProvider, Shipment, ShipmentTracking, Return, ReturnItem,
    DeliverySlot, ShippingReport
)
from .serializers import (
    ShippingProviderSerializer, ShipmentSerializer, ShipmentTrackingSerializer,
    ReturnSerializer, DeliverySlotSerializer, ShippingReportSerializer
)


class ShippingProviderViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for Shipping Providers."""
    queryset = ShippingProvider.objects.all()
    serializer_class = ShippingProviderSerializer
    permission_classes = [IsAdminUser]
    filter_backends = [filters.SearchFilter]
    search_fields = ['name', 'code']

    def get_queryset(self):
        """Filter only active shipping providers."""
        return ShippingProvider.objects.filter(is_active=True)


class ShipmentViewSet(viewsets.ModelViewSet):
    """ViewSet for Shipments."""
    queryset = Shipment.objects.all()
    serializer_class = ShipmentSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'provider']
    search_fields = ['shipment_number', 'tracking_number', 'order__order_number']
    ordering_fields = ['created_at', 'shipped_date', 'delivered_date']

    def get_queryset(self):
        """Return shipments for current user's orders or all if staff."""
        if self.request.user.is_staff:
            return Shipment.objects.all()
        return Shipment.objects.filter(order__user=self.request.user)

    @action(detail=True, methods=['get'])
    def track_shipment(self, request, pk=None):
        """Get shipment tracking information."""
        shipment = self.get_object()
        tracking_data = {
            'shipment_number': shipment.shipment_number,
            'tracking_number': shipment.tracking_number,
            'status': shipment.get_status_display(),
            'estimated_delivery': shipment.estimated_delivery,
            'tracking_history': ShipmentTrackingSerializer(
                shipment.tracking_history.all(), many=True
            ).data
        }
        return Response(tracking_data)

    @action(detail=True, methods=['post'])
    def update_tracking(self, request, pk=None):
        """Update shipment tracking status (Admin only)."""
        if not request.user.is_staff:
            return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)

        shipment = self.get_object()
        status_update = request.data.get('status')
        location = request.data.get('location', '')
        description = request.data.get('description', '')

        # Create tracking record
        ShipmentTracking.objects.create(
            shipment=shipment,
            status=status_update,
            location=location,
            description=description
        )

        # Update shipment status
        shipment.status = status_update
        if status_update == 'delivered':
            shipment.delivered_date = timezone.now()
        shipment.save()

        return Response({'success': True})


class ReturnViewSet(viewsets.ModelViewSet):
    """ViewSet for Returns."""
    serializer_class = ReturnSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['status', 'reason']
    ordering_fields = ['created_at']

    def get_queryset(self):
        """Return returns for current user or all if staff."""
        if self.request.user.is_staff:
            return Return.objects.all()
        return Return.objects.filter(requested_by=self.request.user)

    def perform_create(self, serializer):
        """Set requested_by when creating return."""
        serializer.save(requested_by=self.request.user)

    @action(detail=True, methods=['post'])
    def approve_return(self, request, pk=None):
        """Approve return request (Admin only)."""
        if not request.user.is_staff:
            return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)

        return_request = self.get_object()
        return_request.status = 'approved'
        return_request.approval_notes = request.data.get('notes', '')
        return_request.save()

        return Response({'success': True})

    @action(detail=True, methods=['post'])
    def reject_return(self, request, pk=None):
        """Reject return request (Admin only)."""
        if not request.user.is_staff:
            return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)

        return_request = self.get_object()
        return_request.status = 'rejected'
        return_request.approval_notes = request.data.get('notes', '')
        return_request.save()

        return Response({'success': True})

    @action(detail=True, methods=['post'])
    def process_refund(self, request, pk=None):
        """Process refund (Admin only)."""
        if not request.user.is_staff:
            return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)

        return_request = self.get_object()
        refund_amount = request.data.get('refund_amount')

        return_request.status = 'refunded'
        return_request.refund_amount = refund_amount
        return_request.save()

        return Response({'success': True, 'refund_amount': refund_amount})


class DeliverySlotViewSet(viewsets.ModelViewSet):
    """ViewSet for Delivery Slots."""
    queryset = DeliverySlot.objects.filter(date__gte=timezone.now().date())
    serializer_class = DeliverySlotSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['date']
    ordering_fields = ['date', 'start_time']

    @action(detail=False, methods=['get'])
    def available_slots(self, request):
        """Get available delivery slots."""
        available = DeliverySlot.objects.filter(
            date__gte=timezone.now().date(),
            current_deliveries__lt=models.F('max_deliveries')
        )
        serializer = self.get_serializer(available, many=True)
        return Response(serializer.data)


class ShippingReportViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for Shipping Reports."""
    queryset = ShippingReport.objects.all()
    serializer_class = ShippingReportSerializer
    permission_classes = [IsAdminUser]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['report_date']
    ordering_fields = ['report_date']

    @action(detail=False, methods=['get'])
    def today_report(self, request):
        """Get today's shipping report."""
        today = timezone.now().date()
        try:
            report = ShippingReport.objects.get(report_date=today)
            serializer = self.get_serializer(report)
            return Response(serializer.data)
        except ShippingReport.DoesNotExist:
            return Response(
                {'error': 'No report for today'},
                status=status.HTTP_404_NOT_FOUND
            )


from django.shortcuts import render
def transport_dashboard(request):
    return render(request, 'logistics/transport_dashboard.html')