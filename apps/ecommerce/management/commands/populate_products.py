"""
Management command to populate products with mock data
"""
from django.core.management.base import BaseCommand
from django.core.files.base import ContentFile
from django.utils.text import slugify
from apps.ecommerce.models import Category, Product
import requests
from io import BytesIO


class Command(BaseCommand):
    help = 'Populate database with sample products and categories'

    def handle(self, *args, **options):
        # Create categories
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

        # Sample products data
        products_data = [
            # ความงาม
            {
                'category': 'ความงาม',
                'name': 'แป้งพัฟผ่อง Natural Glow',
                'description': 'แป้งพัฟแบบกดสไตล์เกาหลี ให้ความเนียนนุ่มขึ้นต่อเนื่อง',
                'price': 399.00,
                'stock': 50,
                'image_url': 'https://picsum.photos/400/400?random=1'
            },
            {
                'category': 'ความงาม',
                'name': 'ลิปสติก Velvet Matte',
                'description': 'ลิปสติกแมตท์สีชุ่มชื่น ติดทนนาน',
                'price': 299.00,
                'stock': 80,
                'image_url': 'https://picsum.photos/400/400?random=2'
            },
            {
                'category': 'ความงาม',
                'name': 'ไอชาโดว์พาเลต 12 สี',
                'description': 'ไอชาโดว์หลากสีให้เลือกสรร สีชัดเจนติดทน',
                'price': 549.00,
                'stock': 60,
                'image_url': 'https://picsum.photos/400/400?random=3'
            },
            {
                'category': 'ความงาม',
                'name': 'แมสคาร่า Black Volume',
                'description': 'แมสคาร่าปรับปริมาณ ให้ขนตาหนาพริ้ว',
                'price': 349.00,
                'stock': 75,
                'image_url': 'https://picsum.photos/400/400?random=4'
            },
            {
                'category': 'ความงาม',
                'name': 'บีบีครีม SPF 30',
                'description': 'บีบีครีมบำรุงผิว มีเนื้อที่ปกปิดเบาบาง',
                'price': 449.00,
                'stock': 100,
                'image_url': 'https://picsum.photos/400/400?random=5'
            },
            # เสื้อผ้า
            {
                'category': 'เสื้อผ้า',
                'name': 'เสื้อยืดคอกลม สีพื้น',
                'description': 'เสื้อยืดผ้านวม สวมใส่สบาย ใส่ได้ทุกวัน',
                'price': 199.00,
                'stock': 150,
                'image_url': 'https://picsum.photos/400/400?random=6'
            },
            {
                'category': 'เสื้อผ้า',
                'name': 'กระโปรงผ้ายืด มิดี่',
                'description': 'กระโปรงยาวกลาง ผ้ายืดใส่สะบาย สีเป็นทรงตัว',
                'price': 349.00,
                'stock': 85,
                'image_url': 'https://picsum.photos/400/400?random=7'
            },
            {
                'category': 'เสื้อผ้า',
                'name': 'เสื้อเชิ้ตคอปก Oversized',
                'description': 'เสื้อเชิ้ตแบบโอเวอร์ไซส์ สไตล์ลำลองแต่ดูดี',
                'price': 599.00,
                'stock': 60,
                'image_url': 'https://picsum.photos/400/400?random=8'
            },
            {
                'category': 'เสื้อผ้า',
                'name': 'กางเกงยีนส์ สกินนี่ ฟ้าอ่อน',
                'description': 'กางเกงยีนส์สกินนี่ทรงสวย แมตช์ได้หลายแบบ',
                'price': 699.00,
                'stock': 70,
                'image_url': 'https://picsum.photos/400/400?random=9'
            },
            {
                'category': 'เสื้อผ้า',
                'name': 'เดรสชีฟองออกงาน',
                'description': 'เดรสชีฟองพิมพ์ลาย ใส่ออกงานได้ดี',
                'price': 1299.00,
                'stock': 40,
                'image_url': 'https://picsum.photos/400/400?random=10'
            },
            # เครื่องสำอาง
            {
                'category': 'เครื่องสำอาง',
                'name': 'ครีมบำรุงผิววัย Night Repair',
                'description': 'ครีมบำรุงยามค่ำ สำหรับเซลล์ผิวยามค่ำ',
                'price': 799.00,
                'stock': 45,
                'image_url': 'https://picsum.photos/400/400?random=11'
            },
            {
                'category': 'เครื่องสำอาง',
                'name': 'เจลอาบน้ำ Moisturizing',
                'description': 'เจลอาบน้ำบำรุง ให้ผิวชุ่มชื่นไม่แห้ง',
                'price': 299.00,
                'stock': 120,
                'image_url': 'https://picsum.photos/400/400?random=12'
            },
            {
                'category': 'เครื่องสำอาง',
                'name': 'โลชั่นบำรุงผิวกาย Body Lotion',
                'description': 'โลชั่นบำรุงผิวกาย กลิ่นหอม ซึมเร็ว',
                'price': 349.00,
                'stock': 90,
                'image_url': 'https://picsum.photos/400/400?random=13'
            },
            {
                'category': 'เครื่องสำอาง',
                'name': 'เสรัจชำระล้างหน้า Facial Wash',
                'description': 'เสรัจล้างหน้าสำหรับผิวธรรมชาติ ล้างสะอาดไม่แห้ง',
                'price': 199.00,
                'stock': 150,
                'image_url': 'https://picsum.photos/400/400?random=14'
            },
            {
                'category': 'เครื่องสำอาง',
                'name': 'ซีรั่มบำรุงสกินแคร์ Vitamin C',
                'description': 'ซีรั่มเข้มข้น วิตามิน C สำหรับยกกระชับผิว',
                'price': 899.00,
                'stock': 55,
                'image_url': 'https://picsum.photos/400/400?random=15'
            },
            # อุปกรณ์ในบ้าน
            {
                'category': 'อุปกรณ์ในบ้าน',
                'name': 'หมอนผ้าฝ้ายลายลูกไม้',
                'description': 'หมอนขนาด 40x60 ผ้าฝ้ายเนื้อหนา ลายสวย',
                'price': 449.00,
                'stock': 30,
                'image_url': 'https://picsum.photos/400/400?random=16'
            },
            {
                'category': 'อุปกรณ์ในบ้าน',
                'name': 'ผ้าม่านกั้นแสงม่านบดเบา',
                'description': 'ผ้าม่านหนา 200x200 ซม บดเบาแสง สีเป็นทรงตัว',
                'price': 599.00,
                'stock': 25,
                'image_url': 'https://picsum.photos/400/400?random=17'
            },
            {
                'category': 'อุปกรณ์ในบ้าน',
                'name': 'โคมไฟอ่านหนังสือ LED',
                'description': 'โคมไฟ LED สว่างไม่วาวตา ปรับได้ 3 ระดับ',
                'price': 799.00,
                'stock': 40,
                'image_url': 'https://picsum.photos/400/400?random=18'
            },
            # อิเล็กทรอนิกส์
            {
                'category': 'อิเล็กทรอนิกส์',
                'name': 'แท่นชาร์จโทรศัพท์ Fast Charging',
                'description': 'แท่นชาร์จสมาร์ท ชาร์จเร็ว รองรับ 10 W',
                'price': 899.00,
                'stock': 100,
                'image_url': 'https://picsum.photos/400/400?random=19'
            },
            {
                'category': 'อิเล็กทรอนิกส์',
                'name': 'ลำโพงบลูทูธ Wireless',
                'description': 'ลำโพงบลูทูธเสียงดี เบส หนักแน่น เสียงใส',
                'price': 1299.00,
                'stock': 50,
                'image_url': 'https://picsum.photos/400/400?random=20'
            },
        ]

        # Create products
        for product_data in products_data:
            category = categories[product_data['category']]
            product_slug = slugify(product_data['name'].lower(), allow_unicode=True)
            
            product, created = Product.objects.get_or_create(
                name=product_data['name'],
                defaults={
                    'slug': product_slug,
                    'category': category,
                    'description': product_data['description'],
                    'price': product_data['price'],
                    'stock': product_data['stock'],
                    'sku': f"SKU-{product_data['name'][:10].upper().replace(' ', '-')}",
                }
            )
            
            if created:
                self.stdout.write(f"✓ Created: {product.name} (฿{product.price})")
                
                # Download and save image
                try:
                    response = requests.get(product_data['image_url'], timeout=5)
                    if response.status_code == 200:
                        image_name = f"{product.id}_main.jpg"
                        product.image.save(
                            image_name,
                            ContentFile(response.content),
                            save=True
                        )
                        self.stdout.write(f"  → Image saved for {product.name}")
                except Exception as e:
                    self.stdout.write(f"  ⚠ Could not download image: {str(e)}")
            else:
                self.stdout.write(f"→ Already exists: {product.name}")

        self.stdout.write(self.style.SUCCESS(
            '\n✓ Successfully populated database with products!'
        ))
