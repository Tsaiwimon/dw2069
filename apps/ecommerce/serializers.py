"""
Serializers for E-Commerce system.
"""
from rest_framework import serializers
from .models import (
    Category, Product, ProductImage, Cart, CartItem, Order, 
    OrderItem, Review, Payment
)


class CategorySerializer(serializers.ModelSerializer):
    """Serializer for Category model."""
    class Meta:
        model = Category
        fields = ['id', 'name', 'slug', 'description', 'image', 'parent', 'is_active']
        read_only_fields = ['id']


class ProductImageSerializer(serializers.ModelSerializer):
    """Serializer for ProductImage model."""
    class Meta:
        model = ProductImage
        fields = ['id', 'image', 'alt_text']


class ProductSerializer(serializers.ModelSerializer):
    """Serializer for Product model."""
    images = ProductImageSerializer(many=True, read_only=True)
    category_name = serializers.CharField(source='category.name', read_only=True)
    sale_price = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = [
            'id', 'sku', 'name', 'slug', 'description', 'category', 'category_name',
            'price', 'cost', 'discount_percent', 'sale_price', 'image', 'images',
            'stock', 'min_stock', 'rating', 'review_count', 'is_active'
        ]
        read_only_fields = ['id', 'rating', 'review_count']

    def get_sale_price(self, obj):
        return str(obj.get_sale_price())


class CartItemSerializer(serializers.ModelSerializer):
    """Serializer for CartItem model."""
    product = ProductSerializer(read_only=True)
    product_id = serializers.PrimaryKeyRelatedField(
        queryset=Product.objects.all(), write_only=True, source='product'
    )
    total = serializers.SerializerMethodField()

    class Meta:
        model = CartItem
        fields = ['id', 'product', 'product_id', 'quantity', 'price', 'total']

    def get_total(self, obj):
        return str(obj.get_total())


class CartSerializer(serializers.ModelSerializer):
    """Serializer for Cart model."""
    items = CartItemSerializer(many=True, read_only=True)

    class Meta:
        model = Cart
        fields = ['id', 'user', 'quantity', 'total_price', 'items']
        read_only_fields = ['id', 'user', 'quantity', 'total_price']


class OrderItemSerializer(serializers.ModelSerializer):
    """Serializer for OrderItem model."""
    product = ProductSerializer(read_only=True)
    total = serializers.SerializerMethodField()

    class Meta:
        model = OrderItem
        fields = ['id', 'product', 'product_name', 'quantity', 'price', 'total']

    def get_total(self, obj):
        return str(obj.get_total())


class OrderSerializer(serializers.ModelSerializer):
    """Serializer for Order model."""
    items = OrderItemSerializer(many=True, read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = Order
        fields = [
            'id', 'order_number', 'user', 'status', 'status_display',
            'shipping_address', 'shipping_phone', 'shipping_name',
            'subtotal', 'shipping_cost', 'discount', 'total',
            'notes', 'tracking_number', 'items',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'order_number', 'user', 'created_at', 'updated_at']


class ReviewSerializer(serializers.ModelSerializer):
    """Serializer for Review model."""
    username = serializers.CharField(source='user.username', read_only=True)

    class Meta:
        model = Review
        fields = ['id', 'product', 'user', 'username', 'rating', 'title', 
                  'comment', 'is_approved', 'created_at']
        read_only_fields = ['id', 'user', 'is_approved', 'created_at']


class PaymentSerializer(serializers.ModelSerializer):
    """Serializer for Payment model."""
    method_display = serializers.CharField(source='get_method_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = Payment
        fields = [
            'id', 'order', 'method', 'method_display', 'status', 'status_display',
            'amount', 'reference', 'notes', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
