"""
Models for Marketing System.
"""
from django.db import models
from django.contrib.auth.models import User
from apps.core.models import BaseModel
from apps.ecommerce.models import Product
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from datetime import timedelta


# Campaign Models
class Campaign(BaseModel):
    """Marketing campaign."""
    CAMPAIGN_TYPE = [
        ('discount', 'ส่วนลด'),
        ('bundle', 'สินค้าจำหน่ายเพิ่มเติม'),
        ('seasonal', 'ตามฤดูกาล'),
        ('flash_sale', 'ลดราคาเบิกน้อย'),
        ('new_customer', 'ลูกค้าใหม่'),
    ]

    name = models.CharField(max_length=200, verbose_name='ชื่อแคมเปญ')
    slug = models.SlugField(unique=True, verbose_name='slug')
    description = models.TextField(verbose_name='คำอธิบาย')
    campaign_type = models.CharField(max_length=20, choices=CAMPAIGN_TYPE, verbose_name='ประเภท')
    
    start_date = models.DateTimeField(verbose_name='วันเริ่มต้น')
    end_date = models.DateTimeField(verbose_name='วันสิ้นสุด')
    
    discount_percent = models.DecimalField(max_digits=5, decimal_places=2, default=0, 
                                          verbose_name='ส่วนลด (%)')
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0, 
                                         verbose_name='ส่วนลด (ราคา)')
    
    target_products = models.ManyToManyField(Product, related_name='campaigns', 
                                            verbose_name='สินค้าเป้าหมาย')
    min_purchase = models.DecimalField(max_digits=10, decimal_places=2, default=0, 
                                      verbose_name='การซื้อขั้นต่ำ')
    
    budget = models.DecimalField(max_digits=12, decimal_places=2, verbose_name='งบประมาณ')
    used_budget = models.DecimalField(max_digits=12, decimal_places=2, default=0, 
                                     verbose_name='งบประมาณที่ใช้')
    
    image = models.ImageField(upload_to='campaigns/', null=True, blank=True, verbose_name='รูปภาพ')

    class Meta:
        verbose_name = 'แคมเปญ'
        verbose_name_plural = 'แคมเปญ'
        ordering = ['-start_date']

    def __str__(self):
        return self.name

    def is_active(self):
        """Check if campaign is currently active."""
        now = timezone.now()
        return self.start_date <= now <= self.end_date


# Coupon Models
class Coupon(BaseModel):
    """Discount coupon."""
    COUPON_TYPE = [
        ('fixed', 'ราคาคงที่'),
        ('percent', 'เปอร์เซ็นต์'),
    ]

    code = models.CharField(max_length=50, unique=True, verbose_name='รหัสคูปอง')
    description = models.TextField(blank=True, verbose_name='คำอธิบาย')
    coupon_type = models.CharField(max_length=20, choices=COUPON_TYPE, verbose_name='ประเภท')
    
    discount_value = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='มูลค่าส่วนลด')
    max_discount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, 
                                      verbose_name='ส่วนลดสูงสุด')
    
    min_purchase = models.DecimalField(max_digits=10, decimal_places=2, default=0, 
                                      verbose_name='การซื้อขั้นต่ำ')
    
    start_date = models.DateTimeField(verbose_name='วันเริ่มต้น')
    end_date = models.DateTimeField(verbose_name='วันสิ้นสุด')
    
    usage_limit = models.IntegerField(null=True, blank=True, verbose_name='ขีดจำกัดการใช้งาน')
    usage_count = models.IntegerField(default=0, verbose_name='นับการใช้งาน')
    
    limited_to_users = models.ManyToManyField(User, blank=True, related_name='coupons', 
                                             verbose_name='จำกัดเฉพาะผู้ใช้')

    class Meta:
        verbose_name = 'คูปอง'
        verbose_name_plural = 'คูปอง'
        ordering = ['-created_at']

    def __str__(self):
        return self.code

    def is_valid(self):
        """Check if coupon is valid."""
        now = timezone.now()
        if self.start_date > now or now > self.end_date:
            return False
        if self.usage_limit and self.usage_count >= self.usage_limit:
            return False
        return True

    def can_use(self, user=None):
        """Check if coupon can be used by specific user."""
        if not self.is_valid():
            return False
        if self.limited_to_users.exists() and user and user not in self.limited_to_users.all():
            return False
        return True


class CouponUsage(BaseModel):
    """Record of coupon usage."""
    coupon = models.ForeignKey(Coupon, on_delete=models.CASCADE, related_name='usages', 
                              verbose_name='คูปอง')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='coupon_usages', 
                            verbose_name='ผู้ใช้')
    order = models.ForeignKey('ecommerce.Order', on_delete=models.SET_NULL, null=True, 
                             verbose_name='คำสั่งซื้อ')
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='จำนวนส่วนลด')

    class Meta:
        verbose_name = 'การใช้งานคูปอง'
        verbose_name_plural = 'การใช้งานคูปอง'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.coupon.code} - {self.user.username}'


# Email Campaign Models
class EmailCampaign(BaseModel):
    """Email marketing campaign."""
    STATUS_CHOICES = [
        ('draft', 'ร่าง'),
        ('scheduled', 'กำหนดเวลา'),
        ('sending', 'กำลังส่ง'),
        ('sent', 'ส่งแล้ว'),
        ('cancelled', 'ยกเลิก'),
    ]

    name = models.CharField(max_length=200, verbose_name='ชื่อแคมเปญ')
    subject = models.CharField(max_length=255, verbose_name='หัวข้อ')
    body = models.TextField(verbose_name='เนื้อหา')
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft', 
                             verbose_name='สถานะ')
    
    send_to_new_users = models.BooleanField(default=False, verbose_name='ส่งไปยังผู้ใช้ใหม่')
    send_to_vip = models.BooleanField(default=False, verbose_name='ส่งไปยัง VIP')
    send_to_inactive = models.BooleanField(default=False, verbose_name='ส่งไปยังผู้ใช้ที่ไม่ใช้งาน')
    
    scheduled_date = models.DateTimeField(null=True, blank=True, verbose_name='วันที่กำหนด')
    sent_date = models.DateTimeField(null=True, blank=True, verbose_name='วันที่ส่ง')
    
    open_count = models.IntegerField(default=0, verbose_name='จำนวนการเปิด')
    click_count = models.IntegerField(default=0, verbose_name='จำนวนการคลิก')
    sent_count = models.IntegerField(default=0, verbose_name='จำนวนที่ส่ง')

    class Meta:
        verbose_name = 'แคมเปญส่งอีเมล'
        verbose_name_plural = 'แคมเปญส่งอีเมล'
        ordering = ['-created_at']

    def __str__(self):
        return self.name


class EmailLog(BaseModel):
    """Log of sent emails."""
    STATUS_CHOICES = [
        ('pending', 'รอการส่ง'),
        ('sent', 'ส่งแล้ว'),
        ('failed', 'ล้มเหลว'),
    ]

    campaign = models.ForeignKey(EmailCampaign, on_delete=models.CASCADE, related_name='logs', 
                                verbose_name='แคมเปญ')
    recipient = models.EmailField(verbose_name='ผู้รับ')
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, 
                            verbose_name='ผู้ใช้')
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', 
                             verbose_name='สถานะ')
    
    opened = models.BooleanField(default=False, verbose_name='เปิดแล้ว')
    opened_date = models.DateTimeField(null=True, blank=True, verbose_name='วันที่เปิด')
    
    clicked = models.BooleanField(default=False, verbose_name='คลิกแล้ว')
    clicked_date = models.DateTimeField(null=True, blank=True, verbose_name='วันที่คลิก')

    class Meta:
        verbose_name = 'บันทึกอีเมล'
        verbose_name_plural = 'บันทึกอีเมล'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.campaign.name} - {self.recipient}'


# Loyalty Program Models
class LoyaltyProgram(BaseModel):
    """Customer loyalty program."""
    name = models.CharField(max_length=200, unique=True, verbose_name='ชื่อโปรแกรม')
    description = models.TextField(verbose_name='คำอธิบาย')
    
    points_per_purchase = models.DecimalField(max_digits=8, decimal_places=2, default=1, 
                                            verbose_name='แต้มต่อการซื้อ')
    points_expiry_days = models.IntegerField(default=365, verbose_name='วันหมดอายุแต้ม')

    class Meta:
        verbose_name = 'โปรแกรมจำนนลูกค้า'
        verbose_name_plural = 'โปรแกรมจำนนลูกค้า'

    def __str__(self):
        return self.name


class MembershipTier(BaseModel):
    """Membership tier level."""
    program = models.ForeignKey(LoyaltyProgram, on_delete=models.CASCADE, 
                               related_name='tiers', verbose_name='โปรแกรม')
    name = models.CharField(max_length=100, verbose_name='ชื่อระดับ')
    min_points = models.IntegerField(default=0, verbose_name='คะแนนขั้นต่ำ')
    discount_percent = models.DecimalField(max_digits=5, decimal_places=2, default=0, 
                                          verbose_name='ส่วนลด (%)')
    benefits = models.TextField(blank=True, verbose_name='สิทธิพิเศษ')

    class Meta:
        verbose_name = 'ระดับสมาชิก'
        verbose_name_plural = 'ระดับสมาชิก'
        ordering = ['min_points']

    def __str__(self):
        return f'{self.program.name} - {self.name}'


class LoyaltyPoints(BaseModel):
    """Customer loyalty points."""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='loyalty_points', 
                               verbose_name='ผู้ใช้')
    program = models.ForeignKey(LoyaltyProgram, on_delete=models.PROTECT, verbose_name='โปรแกรม')
    total_points = models.IntegerField(default=0, verbose_name='รวมแต้ม')
    current_tier = models.ForeignKey(MembershipTier, on_delete=models.SET_NULL, 
                                    null=True, verbose_name='ระดับปัจจุบัน')
    lifetime_value = models.DecimalField(max_digits=12, decimal_places=2, default=0, 
                                        verbose_name='มูลค่าตลอดชีวิต')

    class Meta:
        verbose_name = 'แต้มความจงรักษ์'
        verbose_name_plural = 'แต้มความจงรักษ์'

    def __str__(self):
        return f'{self.user.username} - {self.total_points} points'


class PointsTransaction(BaseModel):
    """Transaction of loyalty points."""
    TRANSACTION_TYPE = [
        ('earn', 'ได้รับ'),
        ('redeem', 'แลก'),
        ('expire', 'หมดอายุ'),
        ('adjust', 'ปรับปรุง'),
    ]

    loyalty_points = models.ForeignKey(LoyaltyPoints, on_delete=models.CASCADE, 
                                      related_name='transactions', verbose_name='แต้ม')
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPE, 
                                       verbose_name='ประเภท')
    points_amount = models.IntegerField(verbose_name='จำนวนแต้ม')
    reference = models.CharField(max_length=200, blank=True, verbose_name='อ้างอิง')
    description = models.TextField(blank=True, verbose_name='คำอธิบาย')

    class Meta:
        verbose_name = 'ธุรกรรมแต้ม'
        verbose_name_plural = 'ธุรกรรมแต้ม'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.loyalty_points.user.username} - {self.points_amount} {self.get_transaction_type_display()}'
