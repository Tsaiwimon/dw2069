"""
Views for Marketing System.
"""
from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from django_filters.rest_framework import DjangoFilterBackend
from django.utils import timezone
from .models import (
    Campaign, Coupon, CouponUsage, EmailCampaign, EmailLog,
    LoyaltyProgram, MembershipTier, LoyaltyPoints, PointsTransaction
)
from .serializers import (
    CampaignSerializer, CouponSerializer, CouponUsageSerializer,
    EmailCampaignSerializer, EmailLogSerializer, LoyaltyProgramSerializer,
    LoyaltyPointsSerializer, PointsTransactionSerializer
)


class CampaignViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for Campaigns."""
    queryset = Campaign.objects.all()
    serializer_class = CampaignSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'description']
    ordering_fields = ['start_date', 'created_at']

    def get_queryset(self):
        """Filter active campaigns only."""
        now = timezone.now()
        return Campaign.objects.filter(
            start_date__lte=now,
            end_date__gte=now
        )


class CouponViewSet(viewsets.ModelViewSet):
    """ViewSet for Coupons."""
    queryset = Coupon.objects.all()
    serializer_class = CouponSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter]
    search_fields = ['code', 'description']

    def get_queryset(self):
        """Filter active coupons only."""
        now = timezone.now()
        return Coupon.objects.filter(
            start_date__lte=now,
            end_date__gte=now
        )

    @action(detail=False, methods=['post'])
    def validate_coupon(self, request):
        """Validate coupon code."""
        code = request.data.get('code')
        user = request.user

        try:
            coupon = Coupon.objects.get(code=code)
        except Coupon.DoesNotExist:
            return Response(
                {'error': 'Coupon not found'},
                status=status.HTTP_404_NOT_FOUND
            )

        if not coupon.can_use(user):
            return Response(
                {'error': 'Coupon cannot be used'},
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer = self.get_serializer(coupon)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def apply_coupon(self, request, pk=None):
        """Apply coupon to order."""
        coupon = self.get_object()
        order_id = request.data.get('order_id')
        user = request.user

        if not coupon.can_use(user):
            return Response(
                {'error': 'Coupon cannot be used'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Create usage record
        try:
            from apps.ecommerce.models import Order
            order = Order.objects.get(id=order_id, user=user)
            
            # Calculate discount amount
            if coupon.coupon_type == 'fixed':
                discount_amount = coupon.discount_value
            else:  # percent
                discount_amount = (order.total * coupon.discount_value) / 100
                if coupon.max_discount:
                    discount_amount = min(discount_amount, coupon.max_discount)

            CouponUsage.objects.create(
                coupon=coupon,
                user=user,
                order=order,
                discount_amount=discount_amount
            )
            coupon.usage_count += 1
            coupon.save()

            return Response({
                'success': True,
                'discount_amount': str(discount_amount)
            })
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )


class EmailCampaignViewSet(viewsets.ModelViewSet):
    """ViewSet for Email Campaigns."""
    queryset = EmailCampaign.objects.all()
    serializer_class = EmailCampaignSerializer
    permission_classes = [IsAdminUser]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['status']
    search_fields = ['name', 'subject']

    @action(detail=True, methods=['post'])
    def send_campaign(self, request, pk=None):
        """Send email campaign."""
        campaign = self.get_object()
        # Implementation would handle actual email sending
        campaign.status = 'sending'
        campaign.save()
        return Response({'success': True, 'message': 'Campaign sending'})


class EmailLogViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for Email Logs."""
    queryset = EmailLog.objects.all()
    serializer_class = EmailLogSerializer
    permission_classes = [IsAdminUser]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['campaign', 'status', 'opened', 'clicked']
    ordering_fields = ['created_at']


class LoyaltyProgramViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for Loyalty Programs."""
    queryset = LoyaltyProgram.objects.all()
    serializer_class = LoyaltyProgramSerializer
    permission_classes = [IsAuthenticated]


class LoyaltyPointsViewSet(viewsets.ModelViewSet):
    """ViewSet for Loyalty Points."""
    serializer_class = LoyaltyPointsSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Return loyalty points for current user or all if admin."""
        if self.request.user.is_staff:
            return LoyaltyPoints.objects.all()
        return LoyaltyPoints.objects.filter(user=self.request.user)

    @action(detail=False, methods=['get'])
    def my_points(self, request):
        """Get current user's loyalty points."""
        try:
            loyalty_points = LoyaltyPoints.objects.get(user=request.user)
            serializer = self.get_serializer(loyalty_points)
            return Response(serializer.data)
        except LoyaltyPoints.DoesNotExist:
            return Response(
                {'error': 'No loyalty points found'},
                status=status.HTTP_404_NOT_FOUND
            )

    @action(detail=False, methods=['get'])
    def transactions(self, request):
        """Get current user's points transactions."""
        try:
            loyalty_points = LoyaltyPoints.objects.get(user=request.user)
            transactions = loyalty_points.transactions.all()
            serializer = PointsTransactionSerializer(transactions, many=True)
            return Response(serializer.data)
        except LoyaltyPoints.DoesNotExist:
            return Response(
                {'error': 'No loyalty points found'},
                status=status.HTTP_404_NOT_FOUND
            )


from django.shortcuts import render
def marketing_dashboard(request):
    return render(request, 'marketing/marketing_dashboard.html')