"""
Admin configuration for E-Commerce app.
"""
from django.contrib import admin
from .models import (
    Category, Product, ProductVariant, ProductImage, Cart, CartItem, Order, 
    OrderItem, Review, Payment
)

#เพิ่ม Inline เพื่อให้จัดการข้อมูลตัวเลือกสินค้าและรูปภาพในหน้าสินค้าหลักได้ทันที
class ProductVariantInline(admin.TabularInline):
    model = ProductVariant
    extra = 1
    fields = ('sku', 'color', 'size', 'stock', 'min_stock', 'price_override')


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1


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
    # 📌 ปรับปรุงลากฟิลด์ ราคาเริ่มต้น และ คะแนน มาโชว์แทนสต็อก/SKU เดิม
    list_display = ['name', 'category', 'base_price', 'discount_percent', 'rating', 'is_active']
    list_filter = ['category', 'is_active', 'created_at']
    search_fields = ['name']
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ['rating', 'review_count', 'created_at', 'updated_at']
    
    # ดึง Inline ของราการย่อย (สี/ไซส์) และรูปภาพเพิ่มเติมมาแสดง
    inlines = [ProductVariantInline, ProductImageInline]
    
    fieldsets = (
        ('ข้อมูลสินค้า', {
            'fields': ('name', 'slug', 'description', 'category') # เอา sku ออกเพราะย้ายไปอยู่ใน Variant
        }),
        ('ราคาเริ่มต้น', {
            'fields': ('base_price', 'base_cost', 'discount_percent') # เปลี่ยนเป็น base_price และ base_cost
        }),
        # หมายเหตุ: นำหัวข้อ "สต็อก" ออกจากสินค้าหลัก เนื่องจากระบบย้ายสต็อกไปคำนวณแยกตาม สี/ไซส์ ใน Variant แล้ว
        ('รูปภาพหลัก', {
            'fields': ('image',)
        }),
        ('คะแนน', {
            'fields': ('rating', 'review_count')
        }),
        ('สถานะ', {
            'fields': ('is_active', 'created_at', 'updated_at')
        }),
    )


# 📌 ลงทะเบียนเมนูจัดการตัวเลือกสินค้า (สี/ไซส์/สต็อก) เผื่อต้องการเช็คสต็อกแยกชิ้นแบบละเอียด
@admin.register(ProductVariant)
class ProductVariantAdmin(admin.ModelAdmin):
    list_display = ['sku', 'product', 'color', 'size', 'stock', 'min_stock', 'price_override']
    list_filter = ['product__category', 'stock']
    search_fields = ['sku', 'product__name', 'color', 'size']


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
    # 📌 เปลี่ยนจาก product เป็น variant ให้ตรงตามโมเดลตัวใหม่
    list_display = ['variant', 'cart', 'quantity', 'price', 'created_at']
    list_filter = ['created_at']
    search_fields = ['variant__product__name', 'variant__sku', 'cart__user__username']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['order_number', 'user', 'status', 'total', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['order_number', 'user__username', 'shipping_name']
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
    # 📌 เพิ่มส่องดู variant ในรายการออเดอร์
    list_display = ['order', 'product_name', 'variant', 'quantity', 'price', 'created_at']
    list_filter = ['order__created_at', 'created_at']
    search_fields = ['product_name', 'order__order_number', 'variant__sku']
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