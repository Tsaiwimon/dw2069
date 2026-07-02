"""
Management command to generate 200,000 completed transactions 
from 2,000 users across 2024-2026.
"""
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone
from faker import Faker
import random
from datetime import datetime
from apps.ecommerce.models import Order, OrderItem, ProductVariant, Payment

class Command(BaseCommand):
    help = 'Generate 200,000 completed sales transactions from 2,000 users (2024-2026)'

    def handle(self, *args, **options):
        fake = Faker()
        
        # ตั้งค่าเป้าหมายตามโจทย์
        target_users = 2000
        total_records = 200000
        batch_size = 5000  # แบ่งรอบบันทึกรอบละ 5,000 รายการเพื่อความปลอดภัยของ RAM

        start_date = datetime(2024, 1, 1)
        end_date = datetime(2026, 12, 31)

        # 1. ตรวจสอบและเตรียมสินค้า
        variants = list(ProductVariant.objects.all())
        if not variants:
            self.stdout.write(self.style.ERROR('❌ ไม่พบสินค้าในคลัง กรุณารัน python manage.py populate_products ก่อน'))
            return

        # 2. ตรวจสอบและสร้างผู้ใช้จำลองให้ครบ 2,000 คนอัตโนมัติ
        self.stdout.write(self.style.WARNING('กำลังตรวจสอบจำนวนบัญชีลูกค้า...'))
        existing_users_count = User.objects.filter(is_staff=False).count()
        
        if existing_users_count < target_users:
            needed_users = target_users - existing_users_count
            self.stdout.write(self.style.WARNING(f'พบลูกค้าเดิม {existing_users_count} คน กำลังสร้างเพิ่มอีก {needed_users} คนให้ครบ 2,000 คน...'))
            
            users_to_create = []
            for i in range(existing_users_count + 1, target_users + 1):
                username = f'customer_{i}'
                users_to_create.append(User(
                    username=username,
                    email=f'{username}@example.com',
                    first_name=f'ลูกค้าคนที่',
                    last_name=str(i)
                ))
            
            # บันทึกผู้ใช้เข้าฐานข้อมูลแบบเร็ว
            User.objects.bulk_create(users_to_create)
            self.stdout.write(self.style.SUCCESS(f'✓ เตรียมบัญชีลูกค้าครบ {target_users} คนเรียบร้อยแล้ว'))
        
        # ดึงรายชื่อลูกค้าทั้งหมดมาเก็บไว้ใน Memory สำหรับสุ่ม
        users = list(User.objects.filter(is_staff=False))

        # 3. เริ่มกระบวนการสร้างออเดอร์ 200,000 รายการ
        # 📌 แก้ไขจาก SET_COLOR_LOG เป็น style.SUCCESS มาตรฐานของ Django
        self.stdout.write(self.style.SUCCESS(f'🚀 กำลังเริ่มสร้างยอดขายจำลอง {total_records} รายการ (ช่วงปี 2024-2026)...'))

        for i in range(0, total_records, batch_size):
            current_batch_size = min(batch_size, total_records - i)
            orders_to_create = []
            
            # บล็อกสร้าง Order ใน Memory
            for _ in range(current_batch_size):
                subtotal = round(random.uniform(150, 3500), 2)
                shipping_cost = random.choice([0, 40, 50])
                discount = round(random.uniform(0, float(subtotal) * 0.1), 2)
                total = subtotal + shipping_cost - discount
                
                # 📌 แก้ไข ลบ start_date ตัวที่ซ้ำซ้อนทิ้ง ป้องกัน SyntaxError
                fake_date = timezone.make_aware(fake.date_time_between(start_date=start_date, end_date=end_date))
                user = random.choice(users)
                
                order = Order(
                    order_number=f"ORD-{fake.unique.random_number(digits=12)}",
                    user=user,
                    status='pos_completed',  # 📌 บังคับสถานะ ออเดอร์เสร็จสิ้น ทันที
                    shipping_name=f"{user.first_name} {user.last_name}",
                    shipping_phone=fake.phone_number()[:20],
                    shipping_address="ซื้อหน้าร้าน / สำเร็จการขาย",
                    subtotal=subtotal,
                    shipping_cost=shipping_cost,
                    discount=discount,
                    total=total,
                )
                order.created_at = fake_date
                order.updated_at = fake_date
                orders_to_create.append(order)
            
            # บันทึก Order ลงฐานข้อมูลเพื่อรับ ID กลับมาพ่วงตัวอื่น
            created_orders = Order.objects.bulk_create(orders_to_create)
            
            order_items_to_create = []
            payments_to_create = []
            
            # บล็อกสร้างสินค้าในคำสั่งซื้อ และรายการจ่ายเงิน
            for order in created_orders:
                # 📌 ย้ายตรรกะ random.sample เข้ามาในลูปย่อย เพื่อให้อัตราการสุ่มคละสินค้าต่างกันในทุกใบเสร็จอย่างสมจริง
                num_items = random.randint(1, 3)
                chosen_variants = random.sample(variants, min(num_items, len(variants)))
                
                for variant in chosen_variants:
                    qty = random.randint(1, 2)
                    price = variant.get_price() if hasattr(variant, 'get_price') else variant.price_override or 299.00
                    
                    item = OrderItem(
                        order=order,
                        variant=variant,
                        product_name=variant.__str__()[:255],
                        quantity=qty,
                        price=price,
                    )
                    item.created_at = order.created_at
                    item.updated_at = order.created_at
                    order_items_to_create.append(item)
                
                payment = Payment(
                    order=order,
                    method=random.choice(['bank_transfer', 'credit_card', 'wallet', 'cash']),
                    status='completed',  # 📌 บังคับสถานะ จ่ายเงินเสร็จสมบูรณ์ ทันที
                    amount=order.total,
                    reference=f"REF-{fake.random_number(digits=10)}",
                )
                payment.created_at = order.created_at
                payment.updated_at = order.created_at
                payments_to_create.append(payment)
            
            # บันทึกข้อมูลทั้งหมดลงฐานข้อมูล
            OrderItem.objects.bulk_create(order_items_to_create)
            Payment.objects.bulk_create(payments_to_create)
            
            self.stdout.write(f'⚡ ดำเนินการสำเร็จแล้ว {i + current_batch_size}/{total_records} รายการ...')

        self.stdout.write(self.style.SUCCESS(f'🎉 สำเร็จ! ปั๊มยอดขายเสร็จสมบูรณ์ {total_records} รายการ จากลูกค้า {target_users} คนเรียบร้อยแล้ว! '))