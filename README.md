# Smart Amulet Verification & Marketplace
ระบบตรวจสอบพระเครื่องอัจฉริยะด้วย AI และแพลตฟอร์มตลาดกลางสำหรับซื้อขายพระเครื่อง (Full-Stack Web Application)

## 🌟 จุดเด่นของระบบ (Key Features)
โปรเจกต์นี้ได้รับการอัปเกรดจาก Classroom Demo เป็นระบบ Production-ready ที่มีฟีเจอร์ครบถ้วน:
- **YOLOv8 Object Detection:** ใช้ AI ตรวจจับพระเครื่องในภาพอัตโนมัติ เพื่อคัดกรองพิมพ์พระและประเมินความมั่นใจ (Confidence Score) ก่อนเข้ากระบวนการเทียบตำหนิ
- **Multi-language Display Mapping:** แปลงชื่อพิมพ์พระจากโมเดลให้อยู่ในรูปแบบชื่อสากลและชื่อภาษาไทยในวงเล็บโดยอัตโนมัติ (เช่น Somdej Wat Rakang (พระสมเด็จวัดระฆัง))
- **Advanced Verification:** ผสมผสาน 3 อัลกอริทึมหลักในการเทียบภาพ ได้แก่ Contour & Chamfer Distance เทียบโครงร่างและขอบภาพ, SSIM (Structural Similarity Index) เทียบความคล้ายคลึงของพื้นผิว, และ ORB Feature Matching เทียบจุดเด่นเฉพาะ (Keypoints) บนองค์พระ
- **Auto-Overlay & Debug View:** วาดจุด P* Points และสร้างภาพผลลัพธ์การเปรียบเทียบ (Overlay) ให้ผู้ใช้ดูได้ทันที
- **Secure Authentication:** ระบบสมัครสมาชิกพร้อมการยืนยันตัวตนผ่านอีเมล (Email Verification) และระบบลืม/รีเซ็ตรหัสผ่าน (Forgot Password) ที่ปลอดภัย
- **Role-Based Access Control:** แบ่งผู้ใช้งานเป็น Buyer (ผู้ซื้อเลือกชมตลาด กดซื้อพระ และดูประวัติ), Seller (ผู้ใช้ AI ตรวจสอบพระ ลงขาย และจัดการออเดอร์จัดส่ง), และ Admin (แอดมินจัดการระงับ/ลบผู้ใช้ ดูภาพรวมออเดอร์ และดาวน์โหลดรายงานสรุปยอดขาย)
- **FastAPI Backend & PostgreSQL Database:** ใช้ Framework ประสิทธิภาพสูงสำหรับการจัดการ API, Routing, และจัดการข้อมูล Users, Amulets, Orders, History
- **Cloudinary Integration & SMTP Email Service:** อัปโหลดภาพสินค้าและผลลัพธ์การตรวจ AI ขึ้น Cloud Storage อัตโนมัติ พร้อมเชื่อมต่อเซิร์ฟเวอร์อีเมลสำหรับแจ้งเตือนและยืนยันตัวตน
- **Data Export:** ระบบดึงข้อมูลสร้างไฟล์ CSV สรุปยอดขายรายวันสำหรับแอดมิน (ไฟล์รายงานจะถูกละเว้นการนำขึ้น Git อัตโนมัติ)
- **Modern UI/UX:** รองรับ Dark Mode / Light Mode อัตโนมัติพร้อมจำค่าผู้ใช้, Responsive Design แสดงผลสมบูรณ์ทั้งมือถือและเดสก์ท็อป, รวมถึง Dynamic Modals และระบบจัดการวันที่ตาม Timezone

---

## 📂 โครงสร้างไฟล์หลัก (Directory Structure)
- `app.py` : Backend API หลักของระบบ (FastAPI / Python)
- `.env` : ไฟล์ตั้งค่า Environment Variables (Database URL, Cloudinary API, SMTP Email) *(ถูกละเว้นใน `.gitignore` เพื่อความปลอดภัย)*
- `static/index.html` : หน้า UI หลักของแอปพลิเคชัน
- `static/main.js` : ไฟล์ควบคุม Logic ฝั่ง Client-side (Frontend)
- `static/style.css` : สไตล์ชีทและการจัดรูปแบบหน้าจอ (รองรับ Light/Dark Theme)
- `models/best.pt` : ไฟล์โมเดล (Weights) ของ YOLOv8 สำหรับจำแนกพิมพ์พระเครื่อง
- `requirements.txt` : รายการ Library ที่จำเป็นสำหรับรันระบบ

---

## ⚙️ การตั้งค่าและการใช้งาน (Setup & Run)

ติดตั้ง Python Libraries ด้วยคำสั่ง pip install -r requirements.txt จากนั้นสร้างไฟล์ .env ไว้ในโฟลเดอร์หลักของโปรเจกต์และกำหนดค่าตัวแปรเชื่อมต่อฐานข้อมูล DATABASE_URL, คีย์ระบบ Cloudinary CLOUDINARY_CLOUD_NAME, CLOUDINARY_API_KEY, CLOUDINARY_API_SECRET รวมถึงตั้งค่า SMTP_EMAIL, SMTP_PASSWORD สำหรับส่งอีเมล และกำหนดค่า FRONTEND_URL ให้เรียบร้อย เมื่อตั้งค่าเสร็จแล้วให้รันเซิร์ฟเวอร์ด้วยคำสั่ง python app.py เพื่อให้ระบบทำการเชื่อมต่อฐานข้อมูลและตั้งค่าเริ่มต้นให้อัตโนมัติ จากนั้นเปิดเว็บเบราว์เซอร์แล้วเข้าใช้งานผ่าน http://localhost:3001 ได้ทันที
