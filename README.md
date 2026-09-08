# Real-time E-Commerce & POS Analytics Dashboard

ระบบแดชบอร์ดวิเคราะห์ยอดขายและสินค้าคงคลังแบบเรียลไทม์สำหรับธุรกิจเสื้อผ้าและเครื่องสำอาง พัฒนาขึ้นเพื่อติดตามข้อมูลธุรกรรม ยอดขาย คำสั่งซื้อ และสถานะสต็อกแบบสดๆ โดยดึงข้อมูลเชิงวิเคราะห์จาก ClickHouse

## 🚀 Key Features
* **Real-time Sales Monitoring:** ติดตามยอดขายและคำสั่งซื้อแบบวินาทีต่อวินาทีผ่านหน้าแดชบอร์ด
* **Inventory & Stock Tracking:** มอนิเตอร์สถานะสต็อกสินค้าและตัวเลือกสินค้า (SKU) แบบเรียลไทม์
* **Multi-Dashboard Support:** แดชบอร์ดแยกตามหมวดหมู่การใช้งาน เช่น สินค้าคงคลัง, การตลาด, และการขนส่ง
* **Data Stream Simulation:** มีสคริปต์จำลองข้อมูลการขาย (`generate_fake_sales.py`) เพื่อทดสอบการสตรีมข้อมูลเข้า ClickHouse แบบเรียลไทม์
* **Live Operations Dashboard:** หน้า `/dashboard/` รีเฟรชข้อมูลทุก 10 วินาที พร้อม API `/dashboard/api/` และ fallback ไปยังฐานข้อมูล Django เมื่อ ClickHouse ไม่พร้อม

## 🛠️ Tech Stack
* **Database:** ClickHouse
* **Backend:** Python / Django
* **Frontend:** HTML5, Tailwind CSS, JavaScript