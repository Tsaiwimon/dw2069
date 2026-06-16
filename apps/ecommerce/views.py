"""
Views for E-Commerce system.
"""
from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django_filters.rest_framework import DjangoFilterBackend
from .models import (
    Category, Product, Cart, CartItem, Order, OrderItem, Review, Payment
)
from .serializers import (
    CategorySerializer, ProductSerializer, CartSerializer, CartItemSerializer,
    OrderSerializer, ReviewSerializer, PaymentSerializer
)


class CategoryViewSet(viewsets.ModelViewSet):
    """ViewSet for Product Categories."""
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [AllowAny]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'created_at']

    def get_queryset(self):
        """Filter only active categories."""
        return Category.objects.filter(is_active=True)


class ProductViewSet(viewsets.ModelViewSet):
    """ViewSet for Products."""
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [AllowAny]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['category', 'is_active']
    search_fields = ['name', 'description', 'sku']
    ordering_fields = ['name', 'price', 'rating', 'created_at']
    lookup_field = 'slug'

    def get_queryset(self):
        """Filter only active products."""
        return Product.objects.filter(is_active=True)


class CartViewSet(viewsets.ViewSet):
    """ViewSet for Shopping Cart."""
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=['get'], url_path='current')
    def current(self, request):
        """Get user's cart."""
        cart, _ = Cart.objects.get_or_create(user=request.user)
        serializer = CartSerializer(cart)
        return Response(serializer.data)

    @action(detail=False, methods=['post'])
    def add_item(self, request):
        """Add item to cart."""
        cart, _ = Cart.objects.get_or_create(user=request.user)
        product_id = request.data.get('product_id')
        quantity = request.data.get('quantity', 1)

        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            return Response({'error': 'Product not found'}, status=status.HTTP_404_NOT_FOUND)

        cart_item, created = CartItem.objects.get_or_create(
            cart=cart, product=product,
            defaults={'price': product.get_sale_price(), 'quantity': quantity}
        )
        if not created:
            cart_item.quantity += quantity
            cart_item.save()

        serializer = CartSerializer(cart)
        return Response(serializer.data)

    @action(detail=False, methods=['post'])
    def update_item(self, request):
        """Update cart item quantity."""
        cart_item_id = request.data.get('cart_item_id')
        quantity = request.data.get('quantity')

        try:
            cart_item = CartItem.objects.get(id=cart_item_id, cart__user=request.user)
            cart_item.quantity = quantity
            cart_item.save()
            return Response({'success': True})
        except CartItem.DoesNotExist:
            return Response({'error': 'Cart item not found'}, status=status.HTTP_404_NOT_FOUND)

    @action(detail=False, methods=['post'])
    def remove_item(self, request):
        """Remove item from cart."""
        cart_item_id = request.data.get('cart_item_id')
        try:
            cart_item = CartItem.objects.get(id=cart_item_id, cart__user=request.user)
            cart_item.delete()
            return Response({'success': True})
        except CartItem.DoesNotExist:
            return Response({'error': 'Cart item not found'}, status=status.HTTP_404_NOT_FOUND)

    @action(detail=False, methods=['post'])
    def clear(self, request):
        """Clear cart."""
        cart, _ = Cart.objects.get_or_create(user=request.user)
        cart.items.all().delete()
        return Response({'success': True})


class OrderViewSet(viewsets.ModelViewSet):
    """ViewSet for Orders."""
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['status']
    ordering_fields = ['created_at']

    def get_queryset(self):
        """Return orders for the current user."""
        return Order.objects.filter(user=self.request.user)

    def create(self, request, *args, **kwargs):
        """Create a new order from cart."""
        user = request.user
        cart = Cart.objects.filter(user=user).first()

        if not cart or not cart.items.exists():
            return Response({'error': 'Cart is empty'}, status=status.HTTP_400_BAD_REQUEST)

        # Create order
        order_data = request.data
        order = Order.objects.create(
            user=user,
            order_number=f"ORD-{user.id}-{Order.objects.count() + 1}",
            shipping_address=order_data.get('shipping_address'),
            shipping_phone=order_data.get('shipping_phone'),
            shipping_name=order_data.get('shipping_name'),
            subtotal=cart.total_price,
            total=cart.total_price + order_data.get('shipping_cost', 0),
        )

        # Create order items
        for cart_item in cart.items.all():
            OrderItem.objects.create(
                order=order,
                product=cart_item.product,
                product_name=cart_item.product.name,
                quantity=cart_item.quantity,
                price=cart_item.price,
            )

        # Clear cart
        cart.items.all().delete()

        serializer = self.get_serializer(order)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class ReviewViewSet(viewsets.ModelViewSet):
    """ViewSet for Reviews."""
    serializer_class = ReviewSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['product', 'rating']

    def get_queryset(self):
        """Return reviews for the current user and approved reviews."""
        if self.request.user.is_staff:
            return Review.objects.all()
        return Review.objects.filter(is_approved=True)

    def create(self, request, *args, **kwargs):
        """Create a new review."""
        product_id = request.data.get('product')
        user = request.user

        # Check if user has already reviewed this product
        if Review.objects.filter(product_id=product_id, user=user).exists():
            return Response(
                {'error': 'You have already reviewed this product'},
                status=status.HTTP_400_BAD_REQUEST
            )

        return super().create(request, *args, **kwargs)

    def perform_create(self, serializer):
        """Set user when creating review."""
        serializer.save(user=self.request.user)


class PaymentViewSet(viewsets.ModelViewSet):
    """ViewSet for Payments."""
    serializer_class = PaymentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Return payments for current user's orders."""
        return Payment.objects.filter(order__user=self.request.user)
