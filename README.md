# Smart Amulet Verification & Marketplace
ระบบตรวจสอบพระเครื่องอัจฉริยะด้วย AI และแพลตฟอร์มตลาดกลางสำหรับซื้อขายพระเครื่อง (Full-Stack Web Application)

## 🌟 จุดเด่นของเวอร์ชันปัจจุบัน (Major Update)
โปรเจกต์นี้ได้รับการอัปเกรดจาก Classroom Demo เป็นระบบ Production-ready ที่มีฟีเจอร์ครบถ้วน:

### 🤖 1. AI & Computer Vision (ระบบตรวจสอบพระเครื่องอัจฉริยะ)
- **YOLOv8 Object Detection:** ใช้ AI ตรวจจับพระเครื่องในภาพอัตโนมัติ เพื่อคัดกรองพิมพ์พระและตรวจสอบความมั่นใจ (Confidence Score) ก่อนเทียบตำหนิ
- **Advanced Verification:** ผสมผสาน 3 อัลกอริทึมในการเทียบภาพ:
  1. **Contour & Chamfer Distance:** เทียบโครงร่างและขอบภาพ
  2. **SSIM (Structural Similarity Index):** เทียบความคล้ายคลึงของพื้นผิว
  3. **ORB Feature Matching:** เทียบจุดเด่นเฉพาะ (Keypoints) บนองค์พระ
- **Auto-Overlay & Debug View:** วาดจุด P* Points และแสดงผลลัพธ์การเทียบภาพให้ผู้ใช้ดูได้ทันที

### 🛒 2. E-Commerce & Role-Based System (ระบบตลาดและสมาชิก)
- **ระบบ Role-Based Access Control:** แบ่งผู้ใช้งานเป็น 3 ระดับ (ผู้ซื้อ, ผู้ขาย, แอดมิน)
  - **Buyer (ผู้ซื้อ):** เลือกชมตลาด, กดซื้อพระเครื่อง, ดูประวัติการสั่งซื้อและสถานะการจัดส่ง
  - **Seller (ผู้ขาย):** อัปโหลดภาพตรวจ AI, ลงขายพระเครื่องในตลาด, จัดการออเดอร์และอัปเดตสถานะการจัดส่งให้ลูกค้า
  - **Admin (แอดมิน):** จัดการแบน/ลบผู้ใช้, ดูภาพรวมออเดอร์ทั้งหมดในระบบ, ลบโพสต์พระเครื่อง, และโหลดรายงานสรุปยอดขาย

### ☁ 3. Cloud & Database Architecture
- **Local PostgreSQL Database:** ระบบฐานข้อมูลแบบ Relational รันบนเครื่อง (Localhost) สำหรับจัดการ Users, Amulets, Orders และ History
- **Cloudinary Integration:** อัปโหลดภาพและรูปผลลัพธ์การตรวจ (Overlay) ขึ้น Cloud Storage อัตโนมัติ เพื่อประหยัดพื้นที่เซิร์ฟเวอร์
- **Data Export:** ระบบสร้างไฟล์ CSV รายงานสรุปยอดขายรายวันสำหรับแอดมิน

### 🎨 4. Modern UI/UX
- รองรับ **Dark Mode / Light Mode** อัตโนมัติและจดจำการตั้งค่าผู้ใช้
- Responsive Design รองรับการใช้งานบนหน้าจอมือถือและเดสก์ท็อป
- ระบบจัดการหน้าต่างแบบ Modals ตลอดทั้งแอปพลิเคชัน

---

## 📂 โครงสร้างไฟล์หลัก
- `app.py` : Backend API หลักของระบบ (Python)
- `clean_db.py` : สคริปต์สำหรับเคลียร์และรีเซ็ตข้อมูลในตารางฐานข้อมูล
- `.env` : ไฟล์สำหรับตั้งค่าสภาพแวดล้อม เช่น การเชื่อมต่อฐานข้อมูลและ API Keys (ถูกซ่อนไว้เพื่อความปลอดภัยและไม่อัปขึ้น GitHub)
- `static/index.html` : หน้า UI หลักของแอปพลิเคชัน
- `static/main.js` : ไฟล์ควบคุม Logic ฝั่ง Client-side (Frontend)
- `static/style.css` : สไตล์ชีทและการจัดรูปแบบหน้าจอ
- `models/best.pt` : โมเดลน้ำหนัก (Weights) ของ YOLO 
- `requirements.txt` : รายการ Library ที่จำเป็นต้องติดตั้ง

---

## ⚙️ การตั้งค่าและการใช้งาน (Setup & Run)

1. **ติดตั้ง Python Libraries:**
   ```bash
   pip install -r requirements.txt
