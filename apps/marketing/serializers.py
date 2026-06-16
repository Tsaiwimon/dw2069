"""
Serializers for Marketing System.
"""
from rest_framework import serializers
from .models import (
    Campaign, Coupon, CouponUsage, EmailCampaign, EmailLog,
    LoyaltyProgram, MembershipTier, LoyaltyPoints, PointsTransaction
)


class CampaignSerializer(serializers.ModelSerializer):
    """Serializer for Campaign model."""
    is_active = serializers.SerializerMethodField()
    product_count = serializers.SerializerMethodField()

    class Meta:
        model = Campaign
        fields = [
            'id', 'name', 'slug', 'description', 'campaign_type', 'start_date',
            'end_date', 'discount_percent', 'discount_amount', 'min_purchase',
            'budget', 'used_budget', 'image', 'is_active', 'product_count', 'is_active'
        ]
        read_only_fields = ['id']

    def get_is_active(self, obj):
        return obj.is_active()

    def get_product_count(self, obj):
        return obj.target_products.count()


class CouponSerializer(serializers.ModelSerializer):
    """Serializer for Coupon model."""
    is_valid = serializers.SerializerMethodField()
    remaining_usage = serializers.SerializerMethodField()

    class Meta:
        model = Coupon
        fields = [
            'id', 'code', 'description', 'coupon_type', 'discount_value',
            'max_discount', 'min_purchase', 'start_date', 'end_date',
            'usage_limit', 'usage_count', 'is_valid', 'remaining_usage', 'is_active'
        ]
        read_only_fields = ['id', 'usage_count']

    def get_is_valid(self, obj):
        return obj.is_valid()

    def get_remaining_usage(self, obj):
        if obj.usage_limit:
            return obj.usage_limit - obj.usage_count
        return None


class CouponUsageSerializer(serializers.ModelSerializer):
    """Serializer for CouponUsage model."""
    coupon_code = serializers.CharField(source='coupon.code', read_only=True)
    username = serializers.CharField(source='user.username', read_only=True)

    class Meta:
        model = CouponUsage
        fields = ['id', 'coupon', 'coupon_code', 'user', 'username', 'order', 'discount_amount', 'created_at']
        read_only_fields = ['id', 'created_at']


class EmailLogSerializer(serializers.ModelSerializer):
    """Serializer for EmailLog model."""
    campaign_name = serializers.CharField(source='campaign.name', read_only=True)

    class Meta:
        model = EmailLog
        fields = [
            'id', 'campaign', 'campaign_name', 'recipient', 'status',
            'opened', 'opened_date', 'clicked', 'clicked_date', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class EmailCampaignSerializer(serializers.ModelSerializer):
    """Serializer for EmailCampaign model."""
    logs = EmailLogSerializer(many=True, read_only=True)
    log_count = serializers.SerializerMethodField()

    class Meta:
        model = EmailCampaign
        fields = [
            'id', 'name', 'subject', 'body', 'status', 'send_to_new_users',
            'send_to_vip', 'send_to_inactive', 'scheduled_date', 'sent_date',
            'open_count', 'click_count', 'sent_count', 'log_count', 'logs', 'created_at'
        ]
        read_only_fields = ['id', 'open_count', 'click_count', 'sent_count', 'sent_date']

    def get_log_count(self, obj):
        return obj.logs.count()


class MembershipTierSerializer(serializers.ModelSerializer):
    """Serializer for MembershipTier model."""
    class Meta:
        model = MembershipTier
        fields = ['id', 'program', 'name', 'min_points', 'discount_percent', 'benefits', 'is_active']
        read_only_fields = ['id']


class LoyaltyProgramSerializer(serializers.ModelSerializer):
    """Serializer for LoyaltyProgram model."""
    tiers = MembershipTierSerializer(many=True, read_only=True)

    class Meta:
        model = LoyaltyProgram
        fields = ['id', 'name', 'description', 'points_per_purchase', 'points_expiry_days', 'tiers', 'is_active']
        read_only_fields = ['id']


class PointsTransactionSerializer(serializers.ModelSerializer):
    """Serializer for PointsTransaction model."""
    transaction_type_display = serializers.CharField(source='get_transaction_type_display', read_only=True)

    class Meta:
        model = PointsTransaction
        fields = [
            'id', 'loyalty_points', 'transaction_type', 'transaction_type_display',
            'points_amount', 'reference', 'description', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class LoyaltyPointsSerializer(serializers.ModelSerializer):
    """Serializer for LoyaltyPoints model."""
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)
    tier_name = serializers.CharField(source='current_tier.name', read_only=True)
    transactions = PointsTransactionSerializer(many=True, read_only=True)

    class Meta:
        model = LoyaltyPoints
        fields = [
            'id', 'user', 'user_name', 'program', 'total_points', 'current_tier',
            'tier_name', 'lifetime_value', 'transactions', 'is_active'
        ]
        read_only_fields = ['id', 'total_points', 'current_tier', 'lifetime_value']
