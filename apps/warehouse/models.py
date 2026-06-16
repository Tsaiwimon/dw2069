"""
Models for Warehouse Management System.
"""
from django.db import models
from django.contrib.auth.models import User
from apps.core.models import BaseModel
from apps.ecommerce.models import Product
from django.core.validators import MinValueValidator


# Warehouse Models
class Warehouse(BaseModel):
    """Warehouse location."""
    name = models.CharField(max_length=200, unique=True, verbose_name='ชื่อคลัง')
    code = models.CharField(max_length=50, unique=True, verbose_name='รหัสคลัง')
    address = models.TextField(verbose_name='ที่อยู่')
    phone = models.CharField(max_length=20, verbose_name='เบอร์โทรศัพท์')
    manager = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, 
                               related_name='warehouses', verbose_name='ผู้จัดการ')

    class Meta:
        verbose_name = 'คลังสินค้า'
        verbose_name_plural = 'คลังสินค้า'
        ordering = ['name']

    def __str__(self):
        return self.name


# Stock Management Models
class StockLocation(BaseModel):
    """Storage location in warehouse."""
    warehouse = models.ForeignKey(Warehouse, on_delete=models.CASCADE, 
                                 related_name='locations', verbose_name='คลัง')
    zone = models.CharField(max_length=50, verbose_name='โซน')
    shelf = models.CharField(max_length=50, verbose_name='ชั้น')
    bin = models.CharField(max_length=50, verbose_name='ตู้')

    class Meta:
        verbose_name = 'ตำแหน่งเก็บสินค้า'
        verbose_name_plural = 'ตำแหน่งเก็บสินค้า'
        unique_together = ['warehouse', 'zone', 'shelf', 'bin']
        ordering = ['zone', 'shelf', 'bin']

    def __str__(self):
        return f'{self.warehouse.code}-{self.zone}-{self.shelf}-{self.bin}'


class Stock(BaseModel):
    """Stock information for a product in a warehouse."""
    product = models.ForeignKey(Product, on_delete=models.CASCADE, 
                               related_name='stock_records', verbose_name='สินค้า')
    warehouse = models.ForeignKey(Warehouse, on_delete=models.CASCADE, 
                                 related_name='stocks', verbose_name='คลัง')
    location = models.ForeignKey(StockLocation, on_delete=models.SET_NULL, 
                                null=True, blank=True, verbose_name='ตำแหน่ง')
    quantity = models.IntegerField(default=0, validators=[MinValueValidator(0)], verbose_name='จำนวน')
    reserved_quantity = models.IntegerField(default=0, validators=[MinValueValidator(0)], 
                                           verbose_name='จำนวนสำรอง')
    received_date = models.DateTimeField(verbose_name='วันที่รับสินค้า')

    class Meta:
        verbose_name = 'สต็อก'
        verbose_name_plural = 'สต็อก'
        unique_together = ['product', 'warehouse']
        ordering = ['product']

    def __str__(self):
        return f'{self.product.name} - {self.warehouse.name}: {self.quantity}'

    def get_available_quantity(self):
        """Get available quantity for sale."""
        return self.quantity - self.reserved_quantity


class StockHistory(BaseModel):
    """History of stock changes."""
    OPERATION_TYPE = [
        ('in', 'รับเข้า'),
        ('out', 'ออก'),
        ('adjustment', 'ปรับปรุง'),
        ('damage', 'เสียหาย'),
        ('return', 'คืน'),
    ]

    stock = models.ForeignKey(Stock, on_delete=models.CASCADE, 
                             related_name='history', verbose_name='สต็อก')
    operation_type = models.CharField(max_length=20, choices=OPERATION_TYPE, verbose_name='ประเภท')
    quantity_change = models.IntegerField(verbose_name='เปลี่ยนแปลงจำนวน')
    reference_number = models.CharField(max_length=100, blank=True, verbose_name='เลขที่อ้างอิง')
    notes = models.TextField(blank=True, verbose_name='หมายเหตุ')
    performed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, verbose_name='ผู้ทำ')

    class Meta:
        verbose_name = 'ประวัติสต็อก'
        verbose_name_plural = 'ประวัติสต็อก'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.stock.product.name} - {self.get_operation_type_display()}: {self.quantity_change}'


# Receiving Models
class PurchaseOrder(BaseModel):
    """Purchase order from supplier."""
    STATUS_CHOICES = [
        ('pending', 'รอการยืนยัน'),
        ('confirmed', 'ยืนยันแล้ว'),
        ('shipped', 'ส่งออกแล้ว'),
        ('received', 'รับแล้ว'),
        ('cancelled', 'ยกเลิก'),
    ]

    po_number = models.CharField(max_length=100, unique=True, verbose_name='เลขที่ PO')
    supplier_name = models.CharField(max_length=200, verbose_name='ชื่อผู้จัดส่ง')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name='สถานะ')
    warehouse = models.ForeignKey(Warehouse, on_delete=models.SET_NULL, null=True, verbose_name='คลังสินค้า')
    expected_date = models.DateField(verbose_name='วันที่คาดว่าจะมาถึง')
    notes = models.TextField(blank=True, verbose_name='หมายเหตุ')

    class Meta:
        verbose_name = 'ใบสั่งซื้อ'
        verbose_name_plural = 'ใบสั่งซื้อ'
        ordering = ['-created_at']

    def __str__(self):
        return self.po_number


class GoodsReceipt(BaseModel):
    """Record of received goods."""
    receipt_number = models.CharField(max_length=100, unique=True, verbose_name='เลขที่ใบรับ')
    purchase_order = models.ForeignKey(PurchaseOrder, on_delete=models.SET_NULL, 
                                       null=True, blank=True, verbose_name='ใบสั่งซื้อ')
    warehouse = models.ForeignKey(Warehouse, on_delete=models.PROTECT, verbose_name='คลัง')
    received_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, verbose_name='ผู้รับ')
    receipt_date = models.DateTimeField(auto_now_add=True, verbose_name='วันที่รับ')
    notes = models.TextField(blank=True, verbose_name='หมายเหตุ')

    class Meta:
        verbose_name = 'ใบเสร็จการรับสินค้า'
        verbose_name_plural = 'ใบเสร็จการรับสินค้า'
        ordering = ['-receipt_date']

    def __str__(self):
        return self.receipt_number


class GoodsReceiptItem(BaseModel):
    """Items in goods receipt."""
    receipt = models.ForeignKey(GoodsReceipt, on_delete=models.CASCADE, 
                               related_name='items', verbose_name='ใบเสร็จ')
    product = models.ForeignKey(Product, on_delete=models.PROTECT, verbose_name='สินค้า')
    quantity_ordered = models.IntegerField(verbose_name='จำนวนที่สั่ง')
    quantity_received = models.IntegerField(verbose_name='จำนวนที่รับ')
    unit_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='ราคาต่อหน่วย')
    notes = models.TextField(blank=True, verbose_name='หมายเหตุ')

    class Meta:
        verbose_name = 'รายการเสร็จการรับสินค้า'
        verbose_name_plural = 'รายการเสร็จการรับสินค้า'

    def __str__(self):
        return f'{self.receipt.receipt_number} - {self.product.name}'


# Picking/Packing Models
class PickingList(BaseModel):
    """List of items to pick from warehouse."""
    STATUS_CHOICES = [
        ('pending', 'รอการเก็บ'),
        ('in_progress', 'กำลังเก็บ'),
        ('completed', 'เสร็จแล้ว'),
    ]

    picking_number = models.CharField(max_length=100, unique=True, verbose_name='เลขที่เก็บสินค้า')
    order = models.ForeignKey('ecommerce.Order', on_delete=models.PROTECT, verbose_name='คำสั่งซื้อ')
    warehouse = models.ForeignKey(Warehouse, on_delete=models.PROTECT, verbose_name='คลัง')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name='สถานะ')
    picked_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='ผู้เก็บ')
    picked_date = models.DateTimeField(null=True, blank=True, verbose_name='วันที่เก็บ')

    class Meta:
        verbose_name = 'รายการเก็บสินค้า'
        verbose_name_plural = 'รายการเก็บสินค้า'
        ordering = ['-created_at']

    def __str__(self):
        return self.picking_number


class PickingItem(BaseModel):
    """Items in picking list."""
    picking_list = models.ForeignKey(PickingList, on_delete=models.CASCADE, 
                                    related_name='items', verbose_name='รายการเก็บ')
    product = models.ForeignKey(Product, on_delete=models.PROTECT, verbose_name='สินค้า')
    quantity_required = models.IntegerField(verbose_name='จำนวนที่ต้องเก็บ')
    quantity_picked = models.IntegerField(default=0, verbose_name='จำนวนที่เก็บได้')
    location = models.ForeignKey(StockLocation, on_delete=models.SET_NULL, 
                                null=True, blank=True, verbose_name='ตำแหน่ง')

    class Meta:
        verbose_name = 'รายการเก็บสินค้า'
        verbose_name_plural = 'รายการเก็บสินค้า'

    def __str__(self):
        return f'{self.product.name} - {self.quantity_required}'


class Parcel(BaseModel):
    """Packaged goods ready for shipping."""
    parcel_number = models.CharField(max_length=100, unique=True, verbose_name='เลขที่หีบห่อ')
    picking_list = models.ForeignKey(PickingList, on_delete=models.PROTECT, verbose_name='รายการเก็บ')
    weight = models.DecimalField(max_digits=8, decimal_places=2, verbose_name='น้ำหนัก (kg)')
    dimensions = models.CharField(max_length=100, blank=True, verbose_name='ขนาด (L x W x H)')
    packed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, verbose_name='ผู้บรรจุ')
    packed_date = models.DateTimeField(auto_now_add=True, verbose_name='วันที่บรรจุ')

    class Meta:
        verbose_name = 'หีบห่อ'
        verbose_name_plural = 'หีบห่อ'
        ordering = ['-packed_date']

    def __str__(self):
        return self.parcel_number


# Quality Control Models
class QualityCheck(BaseModel):
    """Quality check record."""
    STATUS_CHOICES = [
        ('passed', 'ผ่าน'),
        ('rejected', 'ปฏิเสธ'),
        ('conditional', 'ตามเงื่อนไข'),
    ]

    goods_receipt = models.ForeignKey(GoodsReceipt, on_delete=models.CASCADE, 
                                     related_name='quality_checks', verbose_name='ใบเสร็จการรับ')
    product = models.ForeignKey(Product, on_delete=models.PROTECT, verbose_name='สินค้า')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, verbose_name='สถานะ')
    quantity_checked = models.IntegerField(verbose_name='จำนวนที่ตรวจสอบ')
    quantity_defective = models.IntegerField(default=0, verbose_name='จำนวนที่มีข้อบกพร่อง')
    notes = models.TextField(blank=True, verbose_name='หมายเหตุ')
    checked_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, verbose_name='ผู้ตรวจสอบ')

    class Meta:
        verbose_name = 'การตรวจสอบคุณภาพ'
        verbose_name_plural = 'การตรวจสอบคุณภาพ'
        ordering = ['-created_at']

    def __str__(self):
        return f'QC - {self.goods_receipt.receipt_number} - {self.product.name}'
