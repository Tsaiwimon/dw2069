# Tsaiwimon Django Project

ระบบจัดการบริษัทค้าขายออนไลน์แบบครบวงจร

## ภาพรวม

Tsaiwimon เป็นแพลตฟอร์มการค้าขายออนไลน์ที่สมบูรณ์ สร้างด้วย Django และ Django REST Framework พร้อม 4 ระบบหลัก:

1. **ระบบขายหน้าเว็บ (E-Commerce)** - จัดการสินค้า ตะกร้า คำสั่งซื้อ การชำระเงิน และรีวิว
2. **ระบบคลังสินค้า (Warehouse)** - ติดตามสต็อก การรับสินค้า การเก็บ การบรรจุ และการตรวจสอบคุณภาพ
3. **ระบบการตลาด (Marketing)** - แคมเปญ คูปอง ส่งอีเมล และโปรแกรมจำนนลูกค้า
4. **ระบบขนส่ง (Logistics)** - จัดการจัดส่ง ติดตาม การคืนสินค้า และรายงาน

## ข้อกำหนดก่อนการติดตั้ง

- Python 3.10+
- uv (Python package manager)
- PostgreSQL (ฐานข้อมูล)
- Redis (Celery broker - ไม่บังคับ)

## การติดตั้ง

### 1. โคลนโปรเจกต์
```bash
git clone <repository-url>
cd tsaiwimon
```

### 2. ติดตั้ง uv และสร้าง Virtual Environment
```bash
# ติดตั้ง uv (ถ้ายังไม่ได้ติดตั้ง)
pip install uv

# สร้าง virtual environment และติดตั้ง dependencies
uv venv
source .venv/bin/activate  # บน Linux/Mac
# หรือ
.venv\Scripts\activate  # บน Windows

# ติดตั้ง dependencies
uv pip install -r pyproject.toml
```

### 3. ตั้งค่าสภาพแวดล้อม
```bash
# คัดลอก .env.example และแก้ไข
cp .env.example .env

# แก้ไขไฟล์ .env ตามตัวอย่าง
```

### 4. การ Migrate ฐานข้อมูล
```bash
# สร้างไฟล์ migrations
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# สร้างผู้ดูแลระบบ
python manage.py createsuperuser
```

### 5. สร้างไฟล์ static และ media
```bash
python manage.py collectstatic --no-input
mkdir -p media logs
```

## การรัน Development Server

```bash
python manage.py runserver
```

เปิดใน: http://localhost:8000

### Admin Panel
- URL: http://localhost:8000/admin/
- API Documentation: http://localhost:8000/api/docs/

## โครงสร้างโปรเจกต์

```
tsaiwimon/
├── manage.py
├── pyproject.toml
├── .env.example
├── .gitignore
│
├── tsaiwimon/          # Django project settings
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
│   ├── asgi.py
│
├── apps/               # Django applications
│   ├── core/           # Base models and utilities
│   ├── ecommerce/      # E-Commerce system
│   ├── warehouse/      # Warehouse Management
│   ├── marketing/      # Marketing system
│   └── logistics/      # Logistics system
│
├── templates/          # HTML templates
├── static/            # Static files (CSS, JS, images)
├── media/             # User uploaded files
└── logs/              # Application logs
```

## API Endpoints

### E-Commerce
- `GET/POST /api/v1/ecommerce/products/` - สินค้า
- `GET/POST /api/v1/ecommerce/categories/` - หมวดหมู่
- `GET/POST /api/v1/ecommerce/orders/` - คำสั่งซื้อ
- `GET/POST /api/v1/ecommerce/reviews/` - รีวิว
- `GET/POST /api/v1/ecommerce/payments/` - การชำระเงิน

### Warehouse
- `GET/POST /api/v1/warehouse/stock/` - สต็อก
- `GET/POST /api/v1/warehouse/purchase-orders/` - ใบสั่งซื้อ
- `GET/POST /api/v1/warehouse/goods-receipts/` - ใบรับสินค้า
- `GET/POST /api/v1/warehouse/picking-lists/` - รายการเก็บสินค้า

### Marketing
- `GET /api/v1/marketing/campaigns/` - แคมเปญ
- `GET/POST /api/v1/marketing/coupons/` - คูปอง
- `GET/POST /api/v1/marketing/loyalty-points/` - แต้มความจงรักษ์

### Logistics
- `GET/POST /api/v1/logistics/shipments/` - ใบจัดส่ง
- `GET/POST /api/v1/logistics/returns/` - การคืนสินค้า
- `GET /api/v1/logistics/delivery-slots/` - ช่วงเวลาจัดส่ง

## การทำงานกับ Database

### PostgreSQL Setup
```bash
# ถ้าใช้ PostgreSQL ให้อัปเดต .env
DB_ENGINE=django.db.backends.postgresql
DB_NAME=tsaiwimon
DB_USER=your_user
DB_PASSWORD=your_password
DB_HOST=localhost
DB_PORT=5432

# ติดตั้ง psycopg2 (อยู่ในมาตรฐานแล้ว)
```

## Testing

```bash
# รัน tests ทั้งหมด
pytest

# รัน tests กับ coverage
pytest --cov=apps

# รัน tests สำหรับ app เฉพาะ
pytest apps/ecommerce/tests.py
```

## Code Quality

```bash
# Linting
flake8 apps/

# Format code
black apps/

# Check imports
isort apps/
```

## Deployment

### สำหรับ Production
1. ตั้งค่า `DEBUG=False` ใน `.env`
2. สร้าง `SECRET_KEY` ใหม่
3. ตั้งค่า `ALLOWED_HOSTS` ตามโดเมนจริง
4. ใช้ Gunicorn/Daphne สำหรับ WSGI/ASGI server
5. ตั้งค่า Nginx reverse proxy
6. ใช้ PostgreSQL แทน SQLite
7. ตั้งค่า Redis สำหรับ Celery

### Docker Deployment
```bash
docker-compose up -d
```

## API Authentication

ระบบใช้ Session Authentication และ Token Authentication

```bash
# ขอ Token
curl -X POST http://localhost:8000/api-token-auth/ \
  -H "Content-Type: application/json" \
  -d '{"username": "user", "password": "pass"}'

# ใช้ Token ใน Request
curl -H "Authorization: Token YOUR_TOKEN" \
  http://localhost:8000/api/v1/ecommerce/products/
```

## การตั้งค่า Celery (ไม่บังคับ)

```bash
# Start Celery worker
celery -A tsaiwimon worker -l info

# Start Celery beat scheduler
celery -A tsaiwimon beat -l info
```

## Troubleshooting

### Issue: ModuleNotFoundError
```bash
# ตรวจสอบ virtual environment ถูกเปิดใจหรือไม่
source .venv/bin/activate
```

### Issue: Database connection error
```bash
# ตรวจสอบ .env มีข้อมูล database ถูกต้องหรือไม่
python manage.py dbshell
```

### Issue: Static files not found
```bash
python manage.py collectstatic --no-input
```

## Documentation

- [Django Documentation](https://docs.djangoproject.com/)
- [Django REST Framework](https://www.django-rest-framework.org/)
- [Functional Requirements Document](./Tsaiwimon_FRD.md)

## Contributors

Development Team

## License

MIT License

## Support

สำหรับการสนับสนุนและคำถาม กรุณาติดต่อทีมพัฒนา
