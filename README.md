# Smart Amulet Verification & Marketplace
ระบบตรวจสอบพระเครื่องอัจฉริยะด้วย AI และแพลตฟอร์มตลาดกลางสำหรับซื้อขายพระเครื่อง (Full-Stack Web Application)

## 🌟 จุดเด่นของระบบ (Key Features)
โปรเจกต์นี้ได้รับการอัปเกรดจาก Classroom Demo เป็นระบบ Production-ready ที่มีฟีเจอร์ครบถ้วน:

### 🤖 1. AI & Computer Vision (ระบบตรวจสอบพระเครื่องอัจฉริยะ)
- **YOLOv8 Object Detection:** ใช้ AI ตรวจจับพระเครื่องในภาพอัตโนมัติ เพื่อคัดกรองพิมพ์พระและประเมินความมั่นใจ (Confidence Score) ก่อนเข้ากระบวนการเทียบตำหนิ
- **Advanced Verification:** ผสมผสาน 3 อัลกอริทึมหลักในการเทียบภาพ:
  1. **Contour & Chamfer Distance:** เทียบโครงร่างและขอบภาพ
  2. **SSIM (Structural Similarity Index):** เทียบความคล้ายคลึงของพื้นผิว
  3. **ORB Feature Matching:** เทียบจุดเด่นเฉพาะ (Keypoints) บนองค์พระ
- **Auto-Overlay & Debug View:** วาดจุด P* Points และสร้างภาพผลลัพธ์การเปรียบเทียบ (Overlay) ให้ผู้ใช้ดูได้ทันที

### 🛒 2. E-Commerce & Role-Based System (ระบบตลาดและสมาชิก)
- **Secure Authentication:** ระบบสมัคสมาชิกพร้อมการยืนยันตัวตนผ่านอีเมล (Email Verification) และระบบลืม/รีเซ็ตรหัสผ่าน (Forgot Password) ที่ปลอดภัย
- **Role-Based Access Control:** แบ่งผู้ใช้งานเป็น 3 ระดับ:
  - **Buyer (ผู้ซื้อ):** เลือกชมตลาด, กดซื้อพระเครื่อง, ดูประวัติการสั่งซื้อและสถานะการจัดส่ง
  - **Seller (ผู้ขาย):** ใช้ AI ตรวจสอบพระ, ลงขายพระเครื่อง, จัดการออเดอร์และอัปเดตสถานะการจัดส่ง
  - **Admin (แอดมิน):** จัดการระงับ/ลบผู้ใช้, ดูภาพรวมออเดอร์ทั้งหมด, จัดการโพสต์ในตลาด, และดาวน์โหลดรายงานสรุปยอดขาย

### ☁ 3. System Architecture (สถาปัตยกรรมระบบ)
- **FastAPI Backend:** ใช้ Framework ประสิทธิภาพสูงสำหรับการจัดการ API และ Routing
- **PostgreSQL Database:** จัดการข้อมูล Users, Amulets, Orders และ History
- **Cloudinary Integration:** อัปโหลดภาพสินค้าและผลลัพธ์การตรวจ AI ขึ้น Cloud Storage อัตโนมัติ เพื่อลดภาระเซิร์ฟเวอร์
- **SMTP Email Service:** เชื่อมต่อเซิร์ฟเวอร์อีเมลสำหรับแจ้งเตือนและยืนยันตัวตนผู้ใช้งาน
- **Data Export:** ระบบดึงข้อมูลสร้างไฟล์ CSV สรุปยอดขายรายวันสำหรับแอดมิน (ไฟล์รายงานจะถูกละเว้นการนำขึ้น Git อัตโนมัติ)

### 🎨 4. Modern UI/UX
- รองรับ **Dark Mode / Light Mode** อัตโนมัติและจดจำการตั้งค่าผู้ใช้
- **Responsive Design:** แสดงผลได้สมบูรณ์ทั้งบนสมาร์ทโฟนและเดสก์ท็อป
- **Dynamic Modals & Date Formatting:** ระบบจัดการหน้าต่างแบบ Modals และการแสดงผลวันที่ที่ปรับแต่งให้สอดคล้องกับ Timezone ของผู้ใช้งาน

---

## 📂 โครงสร้างไฟล์หลัก (Directory Structure)
- `app.py` : Backend API หลักของระบบ (FastAPI / Python)
- `.env` : ไฟล์ตั้งค่า Environment Variables (Database URL, Cloudinary API, SMTP Email) *(ถูกละเว้นใน `.gitignore` เพื่อความปลอดภัย)*
- `static/index.html` : หน้า UI หลักของแอปพลิเคชัน
- `static/main.js` : ไฟล์ควบคุม Logic ฝั่ง Client-side (Frontend)
- `static/style.css` : สไตล์ชีทและการจัดรูปแบบหน้าจอ
- `models/best.pt` : ไฟล์โมเดล (Weights) ของ YOLOv8
- `requirements.txt` : รายการ Library ที่จำเป็นสำหรับรันระบบ

---

## ⚙️ การตั้งค่าและการใช้งาน (Setup & Run)

**1. ติดตั้ง Python Libraries:**
```bash
pip install -r requirements.txt
