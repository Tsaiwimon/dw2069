"""
Models for Logistics System.
"""
from django.db import models
from django.contrib.auth.models import User
from apps.core.models import BaseModel
from django.core.validators import MinValueValidator


# Shipping Provider Models
class ShippingProvider(BaseModel):
    """Third-party shipping provider."""
    name = models.CharField(max_length=200, unique=True, verbose_name='ชื่อบริษัทจัดส่ง')
    code = models.CharField(max_length=50, unique=True, verbose_name='รหัส')
    website = models.URLField(blank=True, verbose_name='เว็บไซต์')
    phone = models.CharField(max_length=20, blank=True, verbose_name='เบอร์โทรศัพท์')
    email = models.EmailField(blank=True, verbose_name='อีเมล')
    
    api_endpoint = models.URLField(blank=True, verbose_name='API Endpoint')
    api_key = models.CharField(max_length=500, blank=True, verbose_name='API Key')
    
    base_rate = models.DecimalField(max_digits=10, decimal_places=2, default=0, 
                                   verbose_name='อัตราพื้นฐาน')
    rate_per_kg = models.DecimalField(max_digits=10, decimal_places=2, default=0, 
                                     verbose_name='อัตราต่อ kg')

    class Meta:
        verbose_name = 'บริษัทจัดส่ง'
        verbose_name_plural = 'บริษัทจัดส่ง'
        ordering = ['name']

    def __str__(self):
        return self.name


# Shipping Models
class Shipment(BaseModel):
    """Shipment record."""
    STATUS_CHOICES = [
        ('pending', 'รอการจัดส่ง'),
        ('picked_up', 'เก็บสินค้าแล้ว'),
        ('in_transit', 'กำลังขนส่ง'),
        ('out_for_delivery', 'ออกส่งแล้ว'),
        ('delivered', 'ส่งมอบแล้ว'),
        ('failed', 'ล้มเหลว'),
        ('returned', 'คืนแล้ว'),
    ]

    shipment_number = models.CharField(max_length=100, unique=True, verbose_name='เลขที่จัดส่ง')
    order = models.OneToOneField('ecommerce.Order', on_delete=models.PROTECT, 
                                related_name='shipment', verbose_name='คำสั่งซื้อ')
    
    provider = models.ForeignKey(ShippingProvider, on_delete=models.SET_NULL, null=True, 
                                verbose_name='บริษัทจัดส่ง')
    
    tracking_number = models.CharField(max_length=100, unique=True, blank=True, 
                                      verbose_name='หมายเลขติดตาม')
    
    # Shipping details
    origin_address = models.TextField(verbose_name='ที่อยู่ต้นทาง')
    destination_address = models.TextField(verbose_name='ที่อยู่ปลายทาง')
    recipient_name = models.CharField(max_length=200, verbose_name='ชื่อผู้รับ')
    recipient_phone = models.CharField(max_length=20, verbose_name='เบอร์โทรศัพท์ผู้รับ')
    
    # Shipment info
    weight = models.DecimalField(max_digits=8, decimal_places=2, verbose_name='น้ำหนัก (kg)')
    dimensions = models.CharField(max_length=100, blank=True, verbose_name='ขนาด')
    
    # Status and dates
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', 
                             verbose_name='สถานะ')
    picked_up_date = models.DateTimeField(null=True, blank=True, verbose_name='วันที่เก็บสินค้า')
    shipped_date = models.DateTimeField(null=True, blank=True, verbose_name='วันที่ส่ง')
    delivered_date = models.DateTimeField(null=True, blank=True, verbose_name='วันที่ส่งมอบ')
    estimated_delivery = models.DateField(null=True, blank=True, verbose_name='วันที่คาดว่าจะมาถึง')
    
    # Cost
    shipping_cost = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='ค่าจัดส่ง')
    insurance_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0, 
                                        verbose_name='ค่าประกัน')
    
    notes = models.TextField(blank=True, verbose_name='หมายเหตุ')

    class Meta:
        verbose_name = 'ใบจัดส่ง'
        verbose_name_plural = 'ใบจัดส่ง'
        ordering = ['-created_at']

    def __str__(self):
        return self.shipment_number


class ShipmentTracking(BaseModel):
    """Tracking information for shipment."""
    STATUS_CHOICES = [
        ('picked_up', 'เก็บสินค้า'),
        ('in_transit', 'กำลังขนส่ง'),
        ('at_facility', 'อยู่ที่สถานีกลาง'),
        ('out_for_delivery', 'ออกส่ง'),
        ('delivery_attempted', 'พยายามส่ง'),
        ('delivered', 'ส่งมอบแล้ว'),
        ('returned', 'คืนแล้ว'),
    ]

    shipment = models.ForeignKey(Shipment, on_delete=models.CASCADE, 
                                related_name='tracking_history', verbose_name='ใบจัดส่ง')
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, verbose_name='สถานะ')
    location = models.CharField(max_length=200, blank=True, verbose_name='ตำแหน่ง')
    description = models.TextField(verbose_name='คำอธิบาย')
    
    timestamp = models.DateTimeField(auto_now_add=True, verbose_name='เวลา')

    class Meta:
        verbose_name = 'ประวัติติดตาม'
        verbose_name_plural = 'ประวัติติดตาม'
        ordering = ['-timestamp']

    def __str__(self):
        return f'{self.shipment.shipment_number} - {self.get_status_display()}'


# Return/Refund Models
class Return(BaseModel):
    """Return request."""
    STATUS_CHOICES = [
        ('pending', 'รอการยืนยัน'),
        ('approved', 'อนุมัติแล้ว'),
        ('shipped', 'ส่งคืนแล้ว'),
        ('received', 'รับแล้ว'),
        ('refunded', 'คืนเงินแล้ว'),
        ('rejected', 'ปฏิเสธ'),
    ]

    REASON_CHOICES = [
        ('not_satisfied', 'ไม่พอใจ'),
        ('defective', 'สินค้าเสียหาย'),
        ('wrong_item', 'ผิดรายการ'),
        ('damaged_in_shipping', 'เสียหายระหว่างขนส่ง'),
        ('missing_parts', 'ขาดชิ้นส่วน'),
        ('other', 'อื่นๆ'),
    ]

    return_number = models.CharField(max_length=100, unique=True, verbose_name='เลขที่การคืน')
    order = models.ForeignKey('ecommerce.Order', on_delete=models.PROTECT, 
                             related_name='returns', verbose_name='คำสั่งซื้อ')
    
    reason = models.CharField(max_length=50, choices=REASON_CHOICES, verbose_name='สาเหตุ')
    description = models.TextField(verbose_name='คำอธิบายรายละเอียด')
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', 
                             verbose_name='สถานะ')
    
    refund_amount = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True, 
                                       verbose_name='จำนวนเงินคืน')
    
    return_shipment = models.OneToOneField(Shipment, on_delete=models.SET_NULL, null=True, 
                                          blank=True, related_name='return_request', 
                                          verbose_name='ใบจัดส่งคืน')
    
    requested_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, 
                                    verbose_name='ขอโดย')
    approval_notes = models.TextField(blank=True, verbose_name='หมายเหตุการอนุมัติ')

    class Meta:
        verbose_name = 'การคืนสินค้า'
        verbose_name_plural = 'การคืนสินค้า'
        ordering = ['-created_at']

    def __str__(self):
        return self.return_number


class ReturnItem(BaseModel):
    """Items in return request."""
    return_request = models.ForeignKey(Return, on_delete=models.CASCADE, 
                                      related_name='items', verbose_name='การคืน')
    product = models.ForeignKey('ecommerce.Product', on_delete=models.SET_NULL, null=True, 
                               verbose_name='สินค้า')
    quantity = models.IntegerField(validators=[MinValueValidator(1)], verbose_name='จำนวน')
    condition = models.CharField(
        max_length=50,
        choices=[('unused', 'ยังไม่ใช้'), ('like_new', 'เหมือนใหม่'), ('good', 'ดี'), ('fair', 'พอใช้')],
        default='fair',
        verbose_name='สภาพ'
    )
    notes = models.TextField(blank=True, verbose_name='หมายเหตุ')

    class Meta:
        verbose_name = 'รายการคืนสินค้า'
        verbose_name_plural = 'รายการคืนสินค้า'

    def __str__(self):
        return f'{self.return_request.return_number} - {self.product.name}'


# Delivery Models
class DeliverySlot(BaseModel):
    """Available delivery time slots."""
    date = models.DateField(verbose_name='วันที่')
    start_time = models.TimeField(verbose_name='เวลาเริ่ม')
    end_time = models.TimeField(verbose_name='เวลาสิ้นสุด')
    max_deliveries = models.IntegerField(default=10, verbose_name='จำนวนการส่งสูงสุด')
    current_deliveries = models.IntegerField(default=0, verbose_name='จำนวนการส่งปัจจุบัน')

    class Meta:
        verbose_name = 'ช่วงเวลาจัดส่ง'
        verbose_name_plural = 'ช่วงเวลาจัดส่ง'
        unique_together = ['date', 'start_time', 'end_time']
        ordering = ['date', 'start_time']

    def __str__(self):
        return f'{self.date} {self.start_time}-{self.end_time}'

    def is_available(self):
        """Check if slot is available."""
        return self.current_deliveries < self.max_deliveries


# Logistics Reports Models
class ShippingReport(BaseModel):
    """Daily shipping report."""
    report_date = models.DateField(unique=True, verbose_name='วันที่รายงาน')
    total_shipments = models.IntegerField(default=0, verbose_name='รวมใบจัดส่ง')
    delivered_count = models.IntegerField(default=0, verbose_name='จำนวนที่ส่งมอบ')
    failed_count = models.IntegerField(default=0, verbose_name='จำนวนที่ล้มเหลว')
    in_transit_count = models.IntegerField(default=0, verbose_name='จำนวนที่กำลังขนส่ง')
    
    total_weight = models.DecimalField(max_digits=12, decimal_places=2, default=0, 
                                      verbose_name='น้ำหนักรวม (kg)')
    total_shipping_cost = models.DecimalField(max_digits=12, decimal_places=2, default=0, 
                                             verbose_name='ค่าจัดส่งรวม')
    total_insurance_cost = models.DecimalField(max_digits=12, decimal_places=2, default=0, 
                                              verbose_name='ค่าประกันรวม')
    
    notes = models.TextField(blank=True, verbose_name='หมายเหตุ')

    class Meta:
        verbose_name = 'รายงานการจัดส่ง'
        verbose_name_plural = 'รายงานการจัดส่ง'
        ordering = ['-report_date']

    def __str__(self):
        return f'Report - {self.report_date}'
