"""
Models for E-Commerce and POS system (Cosmetics & Clothing).
"""
from django.db import models
from django.contrib.auth.models import User
from apps.core.models import BaseModel
from django.core.validators import MinValueValidator, MaxValueValidator

# ==========================================
# 1. CATEGORY
# ==========================================
class Category(BaseModel):
    """Product category."""
    name = models.CharField(max_length=200, unique=True, verbose_name='ชื่อหมวดหมู่')
    slug = models.SlugField(unique=True, verbose_name='slug')
    description = models.TextField(blank=True, verbose_name='คำอธิบาย')
    image = models.ImageField(upload_to='categories/', null=True, blank=True, verbose_name='รูปภาพ')
    parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE, 
                               related_name='children', verbose_name='หมวดหมู่หลัก')

    class Meta:
        verbose_name = 'หมวดหมู่สินค้า'
        verbose_name_plural = 'หมวดหมู่สินค้า'
        ordering = ['name']

    def __str__(self):
        return self.name

# ==========================================
# 2. PRODUCT & VARIANT (ปรับปรุงใหม่สำหรับ เสื้อผ้า/เครื่องสำอาง)
# ==========================================
class Product(BaseModel):
    """Product base information."""
    name = models.CharField(max_length=255, verbose_name='ชื่อสินค้า')
    slug = models.SlugField(unique=True, verbose_name='slug')
    description = models.TextField(verbose_name='คำอธิบาย')
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, 
                                 related_name='products', verbose_name='หมวดหมู่')
    
    # ย้าย SKU และ Stock ไปไว้ที่ Variant แทน เพราะแต่ละสี/ไซส์ สต๊อกไม่เท่ากัน
    base_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='ราคาเริ่มต้น')
    base_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name='ต้นทุนเริ่มต้น')
    discount_percent = models.DecimalField(max_digits=5, decimal_places=2, default=0, verbose_name='ส่วนลด (%)')
    
    image = models.ImageField(upload_to='products/', verbose_name='รูปภาพหลัก')
    
    rating = models.DecimalField(max_digits=3, decimal_places=2, default=0, 
                                validators=[MinValueValidator(0), MaxValueValidator(5)], verbose_name='คะแนน')
    review_count = models.IntegerField(default=0, verbose_name='จำนวนรีวิว')

    class Meta:
        verbose_name = 'สินค้าหลัก'
        verbose_name_plural = 'สินค้าหลัก'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['category']),
        ]

    def __str__(self):
        return self.name

class ProductVariant(BaseModel):
    """Product variations (Size, Color) for inventory tracking."""
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='variants', verbose_name='สินค้าหลัก')
    sku = models.CharField(max_length=100, unique=True, verbose_name='รหัสสินค้า (SKU)')
    
    # เพิ่มตัวเลือก สี และ ไซส์
    color = models.CharField(max_length=50, blank=True, null=True, verbose_name='สี/เฉดสี')
    size = models.CharField(max_length=50, blank=True, null=True, verbose_name='ขนาด/ไซส์')
    
    # กรณีรุ่นย่อยราคาไม่เท่ารุ่นหลัก (เช่น ไซส์ XXL แพงกว่าปกติ)
    price_override = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name='ราคาพิเศษ')
    
    stock = models.IntegerField(default=0, validators=[MinValueValidator(0)], verbose_name='สต็อก')
    min_stock = models.IntegerField(default=5, verbose_name='สต็อกขั้นต่ำ')

    class Meta:
        verbose_name = 'ตัวเลือกสินค้า (SKU)'
        verbose_name_plural = 'ตัวเลือกสินค้า (SKU)'
        unique_together = ['product', 'color', 'size'] # ป้องกันการสร้าง สี/ไซส์ ซ้ำในสินค้าเดียวกัน

    def get_price(self):
        price = self.price_override if self.price_override else self.product.base_price
        discount_amount = price * (self.product.discount_percent / 100)
        return price - discount_amount

    def __str__(self):
        variant_name = self.product.name
        if self.color: variant_name += f" - {self.color}"
        if self.size: variant_name += f" - {self.size}"
        return f"{self.sku} : {variant_name}"

class ProductImage(BaseModel):
    """Additional product images."""
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images', verbose_name='สินค้า')
    image = models.ImageField(upload_to='products/', verbose_name='รูปภาพ')
    alt_text = models.CharField(max_length=255, blank=True, verbose_name='ข้อความทดแทน')

    class Meta:
        verbose_name = 'รูปภาพสินค้า'
        verbose_name_plural = 'รูปภาพสินค้า'

    def __str__(self):
        return f'{self.product.name} - Image'

# ==========================================
# 3. CART (ตะกร้าสินค้าออนไลน์)
# ==========================================
class Cart(BaseModel):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='cart', verbose_name='ผู้ใช้')
    quantity = models.IntegerField(default=0, verbose_name='จำนวนรายการ')
    total_price = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name='ราคารวม')

    class Meta:
        verbose_name = 'ตะกร้าสินค้า'
        verbose_name_plural = 'ตะกร้าสินค้า'

    def __str__(self):
        return f'Cart - {self.user.username}'

class CartItem(BaseModel):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items', verbose_name='ตะกร้า')
    variant = models.ForeignKey(ProductVariant, on_delete=models.CASCADE, verbose_name='ตัวเลือกสินค้า')
    quantity = models.IntegerField(validators=[MinValueValidator(1)], verbose_name='จำนวน')
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='ราคา')

    class Meta:
        verbose_name = 'รายการในตะกร้า'
        verbose_name_plural = 'รายการในตะกร้า'
        unique_together = ['cart', 'variant']

    def __str__(self):
        return f'{self.variant} - {self.quantity} ชิ้น'

    def get_total(self):
        return self.price * self.quantity

# ==========================================
# 4. ORDER & PAYMENT (คำสั่งซื้อและใบเสร็จ)
# ==========================================
class Order(BaseModel):
    ORDER_STATUS = [
        ('pending', 'รอการยืนยัน'),
        ('confirmed', 'ยืนยันแล้ว'),
        ('preparing', 'กำลังเตรียมสินค้า'),
        ('shipped', 'ส่งออกแล้ว'),
        ('delivered', 'จัดส่งแล้ว'),
        ('cancelled', 'ยกเลิก'),
        ('pos_completed', 'ขายหน้าร้านสำเร็จ'), # เพิ่มสถานะสำหรับขายหน้าร้าน (POS)
    ]
    
    order_number = models.CharField(max_length=50, unique=True, verbose_name='เลขที่คำสั่ง/ใบเสร็จ')
    user = models.ForeignKey(User, on_delete=models.PROTECT, null=True, blank=True, related_name='orders', verbose_name='ลูกค้า') # null ได้กรณีลูกค้าหน้าร้าน
    status = models.CharField(max_length=20, choices=ORDER_STATUS, default='pending', verbose_name='สถานะ')
    
    # Shipping info (อนุญาตให้ว่างได้ กรณีซื้อหน้าร้าน)
    shipping_address = models.TextField(blank=True, null=True, verbose_name='ที่อยู่จัดส่ง')
    shipping_phone = models.CharField(max_length=20, blank=True, null=True, verbose_name='เบอร์โทรศัพท์')
    shipping_name = models.CharField(max_length=200, blank=True, null=True, verbose_name='ชื่อผู้รับ')
    
    subtotal = models.DecimalField(max_digits=12, decimal_places=2, verbose_name='ยอดรวมสินค้า')
    shipping_cost = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name='ค่าจัดส่ง')
    discount = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name='ส่วนลด')
    total = models.DecimalField(max_digits=12, decimal_places=2, verbose_name='ยอดรวมทั้งสิ้น')
    
    notes = models.TextField(blank=True, verbose_name='หมายเหตุ')
    tracking_number = models.CharField(max_length=100, blank=True, verbose_name='หมายเลขติดตาม')

    class Meta:
        verbose_name = 'คำสั่งซื้อ / ใบเสร็จ'
        verbose_name_plural = 'คำสั่งซื้อ / ใบเสร็จ'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['order_number']),
            models.Index(fields=['status']),
        ]

    def __str__(self):
        return self.order_number

class OrderItem(BaseModel):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items', verbose_name='คำสั่งซื้อ')
    variant = models.ForeignKey(ProductVariant, on_delete=models.SET_NULL, null=True, verbose_name='ตัวเลือกสินค้า')
    product_name = models.CharField(max_length=255, verbose_name='ชื่อสินค้า (บันทึกประวัติ)')
    quantity = models.IntegerField(validators=[MinValueValidator(1)], verbose_name='จำนวน')
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='ราคา')

    class Meta:
        verbose_name = 'รายการคำสั่งซื้อ'
        verbose_name_plural = 'รายการคำสั่งซื้อ'

    def __str__(self):
        return f'{self.product_name} - {self.quantity} ชิ้น'

    def get_total(self):
        return self.price * self.quantity

# ==========================================
# 5. REVIEW & PAYMENT
# ==========================================
class Review(BaseModel):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews', verbose_name='สินค้า')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews', verbose_name='ผู้ใช้')
    rating = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)], verbose_name='คะแนน')
    title = models.CharField(max_length=200, verbose_name='หัวข้อ')
    comment = models.TextField(verbose_name='ความเห็น')
    is_approved = models.BooleanField(default=False, verbose_name='อนุมัติแล้ว')

    class Meta:
        verbose_name = 'รีวิว'
        verbose_name_plural = 'รีวิว'
        ordering = ['-created_at']
        unique_together = ['product', 'user']

    def __str__(self):
        return f'{self.product.name} - {self.user.username}'

class Payment(BaseModel):
    PAYMENT_METHOD = [
        ('bank_transfer', 'โอนเงินผ่านธนาคาร'),
        ('credit_card', 'บัตรเครดิต/เดบิต'),
        ('ebanking', 'ธนาคารอิเล็กทรอนิกส์'),
        ('wallet', 'กระเป๋าดิจิทัล'),
        ('cod', 'ชำระเงินเมื่อรับสินค้า'),
        ('cash', 'เงินสด (หน้าร้าน)'), # เพิ่มชำระเงินสด
    ]
    PAYMENT_STATUS = [
        ('pending', 'รอการชำระ'),
        ('completed', 'ชำระแล้ว'),
        ('failed', 'ล้มเหลว'),
        ('refunded', 'คืนเงินแล้ว'),
    ]
    
    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name='payment', verbose_name='คำสั่งซื้อ')
    method = models.CharField(max_length=20, choices=PAYMENT_METHOD, verbose_name='วิธีการชำระ')
    status = models.CharField(max_length=20, choices=PAYMENT_STATUS, default='pending', verbose_name='สถานะ')
    amount = models.DecimalField(max_digits=12, decimal_places=2, verbose_name='จำนวนเงิน')
    reference = models.CharField(max_length=200, blank=True, verbose_name='เลขที่อ้างอิง')
    notes = models.TextField(blank=True, verbose_name='หมายเหตุ')

    class Meta:
        verbose_name = 'การชำระเงิน'
        verbose_name_plural = 'การชำระเงิน'
        ordering = ['-created_at']

    def __str__(self):
        return f'Payment - {self.order.order_number}'