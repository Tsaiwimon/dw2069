"""
Management command to populate products with mock data supporting Variants.
"""
from django.core.management.base import BaseCommand
from django.core.files.base import ContentFile
from django.utils.text import slugify
from apps.ecommerce.models import Category, Product, ProductVariant
import requests
import random


class Command(BaseCommand):
    help = 'Populate database with sample products and variants'

    def handle(self, *args, **options):
        # 1. Create categories
        categories_data = [
            {'name': 'ความงาม', 'description': 'สินค้าความงามและแต่งหน้า'},
            {'name': 'เสื้อผ้า', 'description': 'เสื้อผ้าและแฟชั่น'},
            {'name': 'เครื่องสำอาง', 'description': 'เครื่องสำอางและผลิตภัณฑ์ดูแลผิว'},
            {'name': 'อุปกรณ์ในบ้าน', 'description': 'อุปกรณ์และเฟอร์นิเจอร์ในบ้าน'},
            {'name': 'อิเล็กทรอนิกส์', 'description': 'อุปกรณ์อิเล็กทรอนิกส์และเทคโนโลยี'},
        ]

        categories = {}
        for cat_data in categories_data:
            cat_slug = slugify(cat_data['name'].lower(), allow_unicode=True)
            cat, created = Category.objects.get_or_create(
                name=cat_data['name'],
                defaults={
                    'slug': cat_slug,
                    'description': cat_data['description']
                }
            )
            categories[cat_data['name']] = cat
            if created:
                self.stdout.write(f"✓ Created category: {cat.name}")
            else:
                self.stdout.write(f"→ Category already exists: {cat.name}")

        # 2. Sample products data
        products_data = [
            # ความงาม
            {
                'category': 'ความงาม',
                'name': 'แป้งพัฟผ่อง Natural Glow',
                'description': 'แป้งพัฟแบบกดสไตล์เกาหลี ให้ความเนียนนุ่มขึ้นต่อเนื่อง',
                'base_price': 399.00,
                'variants': [{'color': 'No.01 ผิวขาว', 'size': 'มาตรฐาน'}, {'color': 'No.02 ผิวสองสี', 'size': 'มาตรฐาน'}],
                'image_url': 'https://picsum.photos/400/400?random=1'
            },
            {
                'category': 'ความงาม',
                'name': 'ลิปสติก Velvet Matte',
                'description': 'ลิปสติกแมตท์สีชุ่มชื่น ติดทนนาน',
                'base_price': 299.00,
                'variants': [{'color': '01 Red Ruby', 'size': '3.5g'}, {'color': '02 Pink Rose', 'size': '3.5g'}, {'color': '03 Peach Nude', 'size': '3.5g'}],
                'image_url': 'https://picsum.photos/400/400?random=2'
            },
            {
                'category': 'ความงาม',
                'name': 'ไอชาโดว์พาเลต 12 สี',
                'description': 'ไอชาโดว์หลากสีให้เลือกสรร สีชัดเจนติดทน',
                'base_price': 549.00,
                'variants': [{'color': 'โทนส้มอิฐ', 'size': '12 เฉด'}, {'color': 'โทนชมพูตุ่น', 'size': '12 เฉด'}],
                'image_url': 'https://picsum.photos/400/400?random=3'
            },
            {
                'category': 'ความงาม',
                'name': 'แมสคาร่า Black Volume',
                'description': 'แมสคาร่าปรับปริมาณ ให้ขนตาหนาพริ้ว',
                'base_price': 349.00,
                'variants': [{'color': 'สีดำสนิท', 'size': 'มาตรฐาน'}],
                'image_url': 'https://picsum.photos/400/400?random=4'
            },
            {
                'category': 'ความงาม',
                'name': 'บีบีครีม SPF 30',
                'description': 'บีบีครีมบำรุงผิว มีเนื้อที่ปกปิดเบาบาง',
                'base_price': 449.00,
                'variants': [{'color': 'ผิวขาวชมพู', 'size': '30ml'}, {'color': 'ผิวขาวเหลือง', 'size': '30ml'}],
                'image_url': 'https://picsum.photos/400/400?random=5'
            },
            # เสื้อผ้า
            {
                'category': 'เสื้อผ้า',
                'name': 'เสื้อยืดคอกลม สีพื้น',
                'description': 'เสื้อยืดผ้านวม สวมใส่สบาย ใส่ได้ทุกวัน',
                'base_price': 199.00,
                'variants': [{'color': 'สีขาว', 'size': 'M'}, {'color': 'สีขาว', 'size': 'L'}, {'color': 'สีดำ', 'size': 'M'}, {'color': 'สีดำ', 'size': 'L'}],
                'image_url': 'https://picsum.photos/400/400?random=6'
            },
            {
                'category': 'เสื้อผ้า',
                'name': 'กระโปรงผ้ายืด มิดี่',
                'description': 'กระโปรงยาวกลาง ผ้ายืดใส่สะบาย สีเป็นทรงตัว',
                'base_price': 349.00,
                'variants': [{'color': 'สีครีม', 'size': 'Free Size'}, {'color': 'สีน้ำตาล', 'size': 'Free Size'}],
                'image_url': 'https://picsum.photos/400/400?random=7'
            },
            {
                'category': 'เสื้อผ้า',
                'name': 'เสื้อเชิ้ตคอปก Oversized',
                'description': 'เสื้อเชิ้ตแบบโอเวอร์ไซส์ สไตล์ลำลองแต่ดูดี',
                'base_price': 599.00,
                'variants': [{'color': 'สีฟ้าอ่อน', 'size': 'Oversize'}, {'color': 'สีขาว', 'size': 'Oversize'}],
                'image_url': 'https://picsum.photos/400/400?random=8'
            },
            {
                'category': 'เสื้อผ้า',
                'name': 'กางเกงยีนส์ สกินนี่ ฟ้าอ่อน',
                'description': 'กางเกงยีนส์สกินนี่ทรงสวย แมตช์ได้หลายแบบ',
                'base_price': 699.00,
                'variants': [{'color': 'ยีนส์ฟอกฟ้า', 'size': 'S'}, {'color': 'ยีนส์ฟอกฟ้า', 'size': 'M'}, {'color': 'ยีนส์ฟอกฟ้า', 'size': 'L'}],
                'image_url': 'https://picsum.photos/400/400?random=9'
            },
            {
                'category': 'เสื้อผ้า',
                'name': 'เดรสชีฟองออกงาน',
                'description': 'เดรสชีฟองพิมพ์ลาย ใส่ออกงานได้ดี',
                'base_price': 1299.00,
                'variants': [{'color': 'ลายดอกชมพู', 'size': 'M'}, {'color': 'ลายดอกชมพู', 'size': 'L'}],
                'image_url': 'https://picsum.photos/400/400?random=10'
            },
            # เครื่องสำอาง
            {
                'category': 'เครื่องสำอาง',
                'name': 'ครีมบำรุงผิววัย Night Repair',
                'description': 'ครีมบำรุงยามค่ำ สำหรับเซลล์ผิวยามค่ำ',
                'base_price': 799.00,
                'variants': [{'color': 'สูตรกลางคืน', 'size': '50g'}],
                'image_url': 'https://picsum.photos/400/400?random=11'
            },
            {
                'category': 'เครื่องสำอาง',
                'name': 'เจลอาบน้ำ Moisturizing',
                'description': 'เจลอาบน้ำบำรุง ให้ผิวชุ่มชื่นไม่แห้ง',
                'base_price': 299.00,
                'variants': [{'color': 'กลิ่น Honey & Milk', 'size': '500ml'}],
                'image_url': 'https://picsum.photos/400/400?random=12'
            },
        ]

        # 3. Create products and their variants
        for product_data in products_data:
            category = categories[product_data['category']]
            product_slug = slugify(product_data['name'].lower(), allow_unicode=True)
            
            # บันทึกลงตาราง Product หลัก
            product, created = Product.objects.get_or_create(
                name=product_data['name'],
                defaults={
                    'slug': product_slug,
                    'category': category,
                    'description': product_data['description'],
                    'base_price': product_data['base_price'],
                    'base_cost': round(product_data['base_price'] * 0.5, 2), # สมมติว่าต้นทุน 50%
                }
            )
            
            if created:
                self.stdout.write(f"✓ Created Base Product: {product.name}")
                
                # ลูปสร้างตัวย่อย (Variants) พ่วงเข้ากับตัวหลัก
                for idx, v_info in enumerate(product_data['variants']):
                    sku_name = f"SKU-{product.id}-{idx+1:02d}-{v_info['size'].upper()[:2]}"
                    ProductVariant.objects.get_or_create(
                        product=product,
                        sku=sku_name,
                        color=v_info['color'],
                        size=v_info['size'],
                        defaults={
                            'stock': random.randint(30, 100),
                            'min_stock': 5
                        }
                    )
                    self.stdout.write(f"   → Variant Created: SKU: {sku_name} ({v_info['color']} / {v_info['size']})")

                # ดาวน์โหลดรูปภาพ
                try:
                    response = requests.get(product_data['image_url'], timeout=5)
                    if response.status_code == 200:
                        image_name = f"{product.id}_main.jpg"
                        product.image.save(
                            image_name,
                            ContentFile(response.content),
                            save=True
                        )
                        self.stdout.write(f"   → Image saved for {product.name}")
                except Exception as e:
                    self.stdout.write(f"   ⚠ Could not download image: {str(e)}")
            else:
                self.stdout.write(f"→ Base Product already exists: {product.name}")

        self.stdout.write(self.style.SUCCESS(
            '\n✓ Successfully populated database with products and variants!'
        ))