# dw2069 - Live Operations Dashboard

ระบบแดชบอร์ดแสดงผลภาพรวมธุรกิจแบบเรียลไทม์ พัฒนาด้วย **Django** สำหรับติดตามยอดขาย สต็อกสินค้า และสถานะการจัดส่งในรอบ 24 ชั่วโมง

---

## 📊 ฟีเจอร์ของแดชบอร์ด (Dashboard Features)
* **Real-time Metrics:** แสดงผลตัวเลขสำคัญ 4 ช่องหลัก ได้แก่ รายได้รวม 24 ชั่วโมง, ออร์เดอร์ที่ชำระแล้ว, สินค้าคงเหลือ, และสถานะการจัดส่ง
* **Live Sales Chart:** กราฟแสดงจังหวะยอดขายรายชั่วโมงแบบอัปเดตต่อเนื่อง
* **Top Products:** ตารางจัดอันดับสินค้าขายดีพร้อมรหัส SKU และยอดขายล่าสุด
* **Auto-refresh UI:** หน้าจอถูกออกแบบมาให้จำลองและอัปเดตความเคลื่อนไหวของข้อมูลธุรกิจแบบสด ๆ

---

## 🛠️ เทคโนโลยีในส่วนแดชบอร์ด (Tech Stack)
* **Backend:** Python, Django 4.2.14, Django REST Framework
* **Database:** PostgreSQL / SQLite
* **Frontend:** HTML5, Tailwind CSS, JavaScript (Interactive UI)

---

## 🚀 วิธีการเข้าใช้งานแดชบอร์ด (Getting Started)

1. **เปิดโปรเจคผ่าน VS Code และเลือก Interpreter `.venv`**
2. **รันเซิร์ฟเวอร์พัฒนา:**
   ```bash
   python manage.py runserver
