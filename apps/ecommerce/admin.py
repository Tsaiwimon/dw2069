"""
Admin configuration for E-Commerce app.
"""
from django.contrib import admin
from .models import (
    Category, Product, ProductImage, Cart, CartItem, Order, 
    OrderItem, Review, Payment
)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name']
    prepopulated_fields = {'slug': ('name',)}
    fieldsets = (
        ('ข้อมูลทั่วไป', {
            'fields': ('name', 'slug', 'description', 'parent')
        }),
        ('รูปภาพ', {
            'fields': ('image',)
        }),
        ('สถานะ', {
            'fields': ('is_active',)
        }),
    )


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'sku', 'category', 'price', 'stock', 'rating', 'is_active']
    list_filter = ['category', 'is_active', 'created_at']
    search_fields = ['name', 'sku']
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ['rating', 'review_count', 'created_at', 'updated_at']
    fieldsets = (
        ('ข้อมูลสินค้า', {
            'fields': ('sku', 'name', 'slug', 'description', 'category')
        }),
        ('ราคา', {
            'fields': ('price', 'cost', 'discount_percent')
        }),
        ('สต็อก', {
            'fields': ('stock', 'min_stock')
        }),
        ('รูปภาพ', {
            'fields': ('image',)
        }),
        ('คะแนน', {
            'fields': ('rating', 'review_count')
        }),
        ('สถานะ', {
            'fields': ('is_active', 'created_at', 'updated_at')
        }),
    )


@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    list_display = ['product', 'alt_text', 'created_at']
    list_filter = ['product', 'created_at']
    search_fields = ['product__name', 'alt_text']


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ['user', 'quantity', 'total_price', 'created_at']
    list_filter = ['created_at']
    search_fields = ['user__username']
    readonly_fields = ['user', 'quantity', 'total_price', 'created_at', 'updated_at']


@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ['product', 'cart', 'quantity', 'price', 'created_at']
    list_filter = ['created_at']
    search_fields = ['product__name', 'cart__user__username']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['order_number', 'user', 'status', 'total', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['order_number', 'user__username']
    readonly_fields = ['order_number', 'created_at', 'updated_at']
    fieldsets = (
        ('ข้อมูลคำสั่ง', {
            'fields': ('order_number', 'user', 'status', 'tracking_number')
        }),
        ('ข้อมูลจัดส่ง', {
            'fields': ('shipping_name', 'shipping_phone', 'shipping_address')
        }),
        ('ราคา', {
            'fields': ('subtotal', 'shipping_cost', 'discount', 'total')
        }),
        ('อื่น ๆ', {
            'fields': ('notes', 'created_at', 'updated_at')
        }),
    )


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ['order', 'product_name', 'quantity', 'price', 'created_at']
    list_filter = ['order__created_at', 'created_at']
    search_fields = ['product_name', 'order__order_number']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ['product', 'user', 'rating', 'is_approved', 'created_at']
    list_filter = ['rating', 'is_approved', 'created_at']
    search_fields = ['product__name', 'user__username', 'title']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ['order', 'method', 'status', 'amount', 'created_at']
    list_filter = ['method', 'status', 'created_at']
    search_fields = ['order__order_number', 'reference']
    readonly_fields = ['created_at', 'updated_at']
