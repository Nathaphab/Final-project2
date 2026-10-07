<div align="center">

# 🏛️ Smart Amulet Verification & Marketplace

### ระบบตรวจสอบพระเครื่องอัจฉริยะด้วย AI และแพลตฟอร์มตลาดกลางสำหรับซื้อขายพระเครื่อง

Full-Stack Web Application ที่รวมการวิเคราะห์ภาพพระเครื่อง การจัดการสินค้า และระบบซื้อขายไว้ในแพลตฟอร์มเดียว

![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-4169E1?style=for-the-badge&logo=postgresql&logoColor=white)
![YOLOv8](https://img.shields.io/badge/YOLOv8-Object_Detection-111827?style=for-the-badge)
![JavaScript](https://img.shields.io/badge/JavaScript-F7DF1E?style=for-the-badge&logo=javascript&logoColor=black)
![Cloudinary](https://img.shields.io/badge/Cloudinary-3448C5?style=for-the-badge&logo=cloudinary&logoColor=white)

</div>

---

## 📑 สารบัญ

- [ภาพรวมของโปรเจกต์](#overview)
- [ฟีเจอร์หลัก](#features)
- [บทบาทและสิทธิ์ผู้ใช้งาน](#roles)
- [เทคโนโลยีที่ใช้](#tech-stack)
- [แนวทางการวิเคราะห์ภาพ](#verification)
- [โครงสร้างไฟล์](#structure)
- [การติดตั้งและใช้งาน](#setup)
- [ตัวแปรสภาพแวดล้อม](#environment)
- [การใช้งานเบื้องต้น](#usage)
- [การแก้ไขปัญหาเบื้องต้น](#troubleshooting)
- [ขอบเขตและข้อจำกัด](#limitations)

---

<a id="overview"></a>

## 📖 ภาพรวมของโปรเจกต์

**Smart Amulet Verification & Marketplace** เป็นเว็บแอปพลิเคชันที่พัฒนาต่อยอดจาก Classroom Demo โดยผสานเทคโนโลยี **Artificial Intelligence (AI)** และ **Computer Vision** เข้ากับแพลตฟอร์มตลาดกลางสำหรับซื้อขายพระเครื่อง

ระบบช่วยตรวจจับพระเครื่องในภาพ คัดกรองพิมพ์พระ และเปรียบเทียบลักษณะของภาพกับภาพอ้างอิง พร้อมแสดงผลการวิเคราะห์เพื่อประกอบการพิจารณา นอกจากนี้ยังรองรับการสมัครสมาชิก การลงขายสินค้า การสั่งซื้อ การจัดการออเดอร์ และรายงานสำหรับผู้ดูแลระบบ

> **หมายเหตุ:** ผลการวิเคราะห์แสดงความคล้ายคลึงของภาพตามโมเดลและอัลกอริทึมที่ใช้ ไม่ใช่ใบรับรองความแท้ของพระเครื่อง และ Confidence Score ไม่ใช่เปอร์เซ็นต์ความแท้

---

<a id="features"></a>

## 🌟 ฟีเจอร์หลัก

### 🔍 AI Detection & Image Verification

- **YOLOv8 Object Detection** — ตรวจจับพระเครื่องในภาพ พร้อมแสดงคลาสที่โมเดลทำนายและค่าความมั่นใจ (Confidence Score)
- **Multi-language Display Mapping** — แสดงชื่อพิมพ์พระเป็นภาษาอังกฤษควบคู่กับภาษาไทย เช่น `Somdej Wat Rakang (พระสมเด็จวัดระฆัง)`
- **Advanced Verification** — ใช้การวิเคราะห์ภาพ 3 แนวทางร่วมกัน:
  - **Contour & Chamfer Distance:** เปรียบเทียบโครงร่างและระยะห่างของขอบภาพ
  - **SSIM:** เปรียบเทียบความคล้ายคลึงเชิงโครงสร้างของภาพ
  - **ORB Feature Matching:** จับคู่จุดเด่นเฉพาะ (Keypoints) ระหว่างภาพ
- **Auto-Overlay & Debug View** — แสดงจุด P* และภาพซ้อนทับ (Overlay) เพื่อช่วยตรวจสอบผลการเปรียบเทียบ

### 🛒 Marketplace & Order Management

- แสดงรายการพระเครื่องสำหรับเลือกชมและสั่งซื้อ
- รองรับการลงขายและจัดการรายการสินค้าของผู้ขาย
- จัดการออเดอร์และข้อมูลการจัดส่ง
- ดูประวัติการสั่งซื้อและประวัติการตรวจสอบตามสิทธิ์ผู้ใช้งาน

### 🔐 Authentication & Access Control

- สมัครสมาชิกและเข้าสู่ระบบ
- ยืนยันอีเมลผ่าน **Email Verification**
- ขอรีเซ็ตรหัสผ่านผ่าน **Forgot Password / Reset Password**
- แบ่งสิทธิ์การใช้งานด้วย **Role-Based Access Control (RBAC)**
- รองรับบทบาท **Buyer**, **Seller** และ **Admin**

### ☁️ Storage, Email & Reports

- จัดเก็บภาพสินค้าและภาพผลลัพธ์การวิเคราะห์บน **Cloudinary**
- เชื่อมต่อ **SMTP Email Service** สำหรับส่งอีเมลยืนยันตัวตนและการแจ้งเตือน
- ดาวน์โหลดรายงานสรุปยอดขายรายวันในรูปแบบ **CSV**
- กำหนดให้ไฟล์รายงานที่สร้างขึ้นถูกละเว้นจาก Git ผ่าน `.gitignore`

### 🎨 User Interface & Experience

- รองรับ **Light Mode / Dark Mode** พร้อมจดจำการตั้งค่าผู้ใช้
- ออกแบบแบบ **Responsive** สำหรับมือถือและเดสก์ท็อป
- ใช้ **Dynamic Modals** สำหรับแสดงข้อมูลและโต้ตอบกับผู้ใช้
- รองรับการแสดงวันที่และเวลาตาม **Timezone**

---

<a id="roles"></a>

## 👥 บทบาทและสิทธิ์ผู้ใช้งาน

| บทบาท | ความสามารถหลัก |
| :--- | :--- |
| **Buyer — ผู้ซื้อ** | เลือกชมสินค้า สั่งซื้อพระเครื่อง และดูประวัติการสั่งซื้อ |
| **Seller — ผู้ขาย** | ใช้ AI ตรวจสอบภาพพระเครื่อง ลงขายสินค้า และจัดการออเดอร์กับข้อมูลการจัดส่ง |
| **Admin — ผู้ดูแลระบบ** | จัดการระงับหรือลบผู้ใช้ ดูภาพรวมออเดอร์ และดาวน์โหลดรายงานยอดขาย |

---

<a id="tech-stack"></a>

## 🧰 เทคโนโลยีที่ใช้

| ส่วนของระบบ | เทคโนโลยี / เครื่องมือ | หน้าที่ |
| :--- | :--- | :--- |
| **Frontend** | HTML, CSS, JavaScript | ส่วนติดต่อผู้ใช้และการเรียกใช้งาน API |
| **Backend** | Python, FastAPI | จัดการ API และตรรกะการทำงานของระบบ |
| **Database** | PostgreSQL | จัดเก็บข้อมูลผู้ใช้ พระเครื่อง ออเดอร์ และประวัติ |
| **Object Detection** | YOLOv8 | ตรวจจับพระเครื่องและทำนายคลาส |
| **Image Verification** | Contour, Chamfer Distance, SSIM, ORB | เปรียบเทียบลักษณะของภาพ |
| **Image Storage** | Cloudinary | จัดเก็บภาพสินค้าและผลลัพธ์การวิเคราะห์ |
| **Email Service** | SMTP | ส่งอีเมลยืนยันตัวตน รีเซ็ตรหัสผ่าน และแจ้งเตือน |
| **Data Export** | CSV | ส่งออกรายงานสรุปยอดขาย |

---

<a id="verification"></a>

## 🧠 แนวทางการวิเคราะห์ภาพ

ระบบใช้การตรวจจับวัตถุร่วมกับการเปรียบเทียบภาพ เพื่อช่วยประเมินลักษณะของพระเครื่องจากข้อมูลภาพ

1. **รับภาพพระเครื่อง** — ผู้ใช้อัปโหลดภาพที่ต้องการตรวจสอบ
2. **ตรวจจับและคัดกรองพิมพ์พระ** — YOLOv8 ทำนายคลาสและแสดงค่าความมั่นใจ
3. **เปรียบเทียบกับภาพอ้างอิง** — วิเคราะห์โครงร่าง โครงสร้างภาพ และจุดเด่นเฉพาะ
4. **แสดงผลการเปรียบเทียบ** — แสดงผลวิเคราะห์ จุด P* และภาพ Overlay
5. **จัดเก็บประวัติ** — บันทึกข้อมูลและภาพผลลัพธ์สำหรับเรียกดูภายหลัง

### องค์ประกอบของการเปรียบเทียบ

| วิธีการ | สิ่งที่วิเคราะห์ | ประโยชน์ |
| :--- | :--- | :--- |
| **Contour & Chamfer Distance** | โครงร่างและระยะห่างระหว่างขอบภาพ | ช่วยตรวจสอบความแตกต่างด้านรูปทรง |
| **SSIM** | ความคล้ายคลึงเชิงโครงสร้างของภาพ | ช่วยเปรียบเทียบรายละเอียดและรูปแบบของภาพ |
| **ORB Feature Matching** | จุดเด่นเฉพาะและการจับคู่ระหว่างภาพ | ช่วยระบุตำแหน่งรายละเอียดที่สอดคล้องกัน |

> คุณภาพภาพ แสง มุมถ่าย และภาพอ้างอิงมีผลต่อผลการวิเคราะห์ การรวมคะแนนและเกณฑ์ตัดสินขึ้นอยู่กับการตั้งค่าในโค้ดของระบบ

---

<a id="structure"></a>

## 📂 โครงสร้างไฟล์

| ไฟล์ / ตำแหน่ง | รายละเอียด |
| :--- | :--- |
| `app.py` | Backend API หลักและจุดเริ่มต้นการทำงานของแอปพลิเคชัน |
| `requirements.txt` | รายการ Python dependencies |
| `.env` | ตัวแปรเชื่อมต่อฐานข้อมูล Cloudinary และบริการอีเมล |
| `.gitignore` | กำหนดไฟล์ที่ไม่ต้องติดตามด้วย Git |
| `static/index.html` | หน้าเว็บหลัก |
| `static/main.js` | ตรรกะฝั่ง Frontend และการเรียก API |
| `static/style.css` | รูปแบบการแสดงผล Responsive และ Light/Dark Theme |
| `models/best.pt` | ไฟล์ weights ของโมเดล YOLOv8 ที่ฝึกสำหรับโปรเจกต์ |
| `README.md` | คำอธิบายโปรเจกต์และคู่มือเริ่มต้นใช้งาน |

---

<a id="setup"></a>

## ⚙️ การติดตั้งและใช้งาน

### 1. เตรียมสิ่งที่จำเป็น

- Python และ pip เวอร์ชันที่รองรับ dependencies ใน `requirements.txt`
- PostgreSQL พร้อมฐานข้อมูลและบัญชีผู้ใช้ที่มีสิทธิ์เหมาะสม
- บัญชี Cloudinary พร้อม API credentials
- บัญชีอีเมลหรือบริการ SMTP
- ไฟล์โมเดลที่ฝึกแล้ว วางไว้ที่ `models/best.pt`

### 2. เปิด Terminal ในโฟลเดอร์โปรเจกต์

ตรวจสอบว่าโฟลเดอร์ปัจจุบันมีไฟล์ `app.py` และ `requirements.txt`

### 3. สร้าง Virtual Environment

```bash
python -m venv .venv
```

เปิดใช้งานบน **Windows PowerShell**:

```powershell
.\.venv\Scripts\Activate.ps1
```

เปิดใช้งานบน **Windows Command Prompt**:

```bat
.venv\Scripts\activate.bat
```

เปิดใช้งานบน **macOS / Linux**:

```bash
source .venv/bin/activate
```

> หากเครื่องใช้คำสั่ง `python3` ให้ใช้ `python3 -m venv .venv` ในขั้นตอนสร้าง environment

### 4. ติดตั้ง Dependencies

```bash
python -m pip install -r requirements.txt
```

### 5. ตั้งค่า Environment Variables

สร้างไฟล์ `.env` ไว้ในโฟลเดอร์เดียวกับ `app.py` แล้วกำหนดค่าตามหัวข้อ [ตัวแปรสภาพแวดล้อม](#environment)

ตรวจสอบว่าฐานข้อมูล PostgreSQL พร้อมใช้งาน และมีไฟล์ `models/best.pt` อยู่ในตำแหน่งที่ถูกต้อง

### 6. เริ่มต้นเซิร์ฟเวอร์

```bash
python app.py
```

ระบบจะเชื่อมต่อฐานข้อมูลและดำเนินการตั้งค่าเริ่มต้นตามที่กำหนดไว้ใน `app.py`

### 7. เปิดใช้งานผ่านเว็บเบราว์เซอร์

**URL สำหรับใช้งานบนเครื่อง:**

[http://localhost:3001](http://localhost:3001)

---

<a id="environment"></a>

## 🔧 ตัวแปรสภาพแวดล้อม

ตัวอย่างไฟล์ `.env` — เปลี่ยนค่าตัวอย่างทั้งหมดให้เป็นข้อมูลของคุณ:

```dotenv
# PostgreSQL
DATABASE_URL=postgresql://your_db_user:your_db_password@localhost:5432/your_db_name

# Cloudinary
CLOUDINARY_CLOUD_NAME=your_cloud_name
CLOUDINARY_API_KEY=your_api_key
CLOUDINARY_API_SECRET=your_api_secret

# SMTP Email
SMTP_EMAIL=your_email@example.com
SMTP_PASSWORD=your_smtp_password

# Frontend
FRONTEND_URL=http://localhost:3001
```

| ตัวแปร | รายละเอียด |
| :--- | :--- |
| `DATABASE_URL` | URL เชื่อมต่อ PostgreSQL โดยใช้รูปแบบที่ตรงกับไดรเวอร์ของโปรเจกต์ |
| `CLOUDINARY_CLOUD_NAME` | Cloud name ของบัญชี Cloudinary |
| `CLOUDINARY_API_KEY` | API key สำหรับเชื่อมต่อ Cloudinary |
| `CLOUDINARY_API_SECRET` | API secret สำหรับยืนยันสิทธิ์กับ Cloudinary |
| `SMTP_EMAIL` | อีเมลที่ระบบใช้ส่งข้อความ |
| `SMTP_PASSWORD` | รหัสผ่าน SMTP หรือ App Password ตามผู้ให้บริการ |
| `FRONTEND_URL` | URL หน้าเว็บสำหรับสร้างลิงก์ที่ส่งไปยังผู้ใช้ |

**ข้อควรทราบในการตั้งค่า**

- ไฟล์ `.env` มีข้อมูลลับและต้องถูกละเว้นด้วย `.gitignore`
- หากแชร์ตัวอย่างการตั้งค่า ให้ใช้ `.env.example` ที่มีเฉพาะค่าตัวอย่าง
- การตั้งค่า SMTP host, port และ TLS/SSL ต้องตรงกับผู้ให้บริการและการกำหนดค่าใน `app.py`
- เมื่อเปลี่ยน URL ที่ใช้งานจริง ให้ปรับ `FRONTEND_URL` ให้ตรงกับหน้าเว็บ
- หลังแก้ไข `.env` ให้รีสตาร์ตเซิร์ฟเวอร์เพื่อโหลดค่าใหม่

---

<a id="usage"></a>

## 🚀 การใช้งานเบื้องต้น

### สำหรับผู้ซื้อ — Buyer

1. สมัครสมาชิกและยืนยันอีเมล
2. เข้าสู่ระบบและเลือกชมรายการพระเครื่อง
3. ตรวจสอบรายละเอียดสินค้าก่อนสั่งซื้อ
4. ดูรายการและประวัติการสั่งซื้อของตนเอง

### สำหรับผู้ขาย — Seller

1. เข้าสู่ระบบด้วยบัญชีที่มีสิทธิ์ Seller
2. อัปโหลดภาพพระเครื่องเพื่อวิเคราะห์
3. ตรวจสอบผล AI และภาพเปรียบเทียบ
4. ลงขายพระเครื่องพร้อมข้อมูลสินค้า
5. จัดการออเดอร์และข้อมูลการจัดส่ง

### สำหรับผู้ดูแลระบบ — Admin

1. เข้าสู่ระบบด้วยบัญชีที่มีสิทธิ์ Admin
2. จัดการบัญชีผู้ใช้และตรวจสอบภาพรวมออเดอร์
3. ดาวน์โหลดรายงานสรุปยอดขายรายวันเป็นไฟล์ CSV

---

<a id="troubleshooting"></a>

## 🛠️ การแก้ไขปัญหาเบื้องต้น

| ปัญหา | จุดที่ควรตรวจสอบ |
| :--- | :--- |
| ติดตั้ง dependencies ไม่สำเร็จ | เปิดใช้ virtual environment และตรวจสอบเวอร์ชัน Python กับข้อความผิดพลาดจาก pip |
| เชื่อมต่อฐานข้อมูลไม่ได้ | ตรวจสอบบริการ PostgreSQL, `DATABASE_URL`, ชื่อฐานข้อมูล และสิทธิ์ของบัญชี |
| โหลดโมเดลไม่สำเร็จ | ตรวจสอบไฟล์ `models/best.pt` และความเข้ากันได้กับ dependencies ของโปรเจกต์ |
| อัปโหลดภาพไม่ได้ | ตรวจสอบ Cloudinary credentials และข้อความผิดพลาดจากเซิร์ฟเวอร์ |
| ไม่ได้รับอีเมล | ตรวจสอบ SMTP credentials, การตั้งค่า host/port และโฟลเดอร์ Spam |
| ลิงก์ยืนยันอีเมลหรือรีเซ็ตรหัสผ่านเปิดไม่ได้ | ตรวจสอบ `FRONTEND_URL` และการเข้าถึง URL จากอุปกรณ์ที่เปิดอีเมล |
| เปิดเว็บที่พอร์ต 3001 ไม่ได้ | ตรวจสอบว่าเซิร์ฟเวอร์ทำงานอยู่ และไม่มีโปรแกรมอื่นใช้พอร์ตเดียวกัน |

> เมื่อเกิดข้อผิดพลาด ให้ตรวจสอบข้อความใน Terminal ที่รัน `app.py` เพื่อระบุสาเหตุเพิ่มเติม

---

<a id="limitations"></a>

## 📌 ขอบเขตและข้อจำกัด

- โมเดลรองรับพิมพ์พระตามคลาสและข้อมูลที่ใช้ในการฝึก
- Confidence Score สื่อถึงความมั่นใจของโมเดลในการตรวจจับหรือทำนายคลาส ไม่ใช่ความน่าจะเป็นที่พระเครื่องเป็นของแท้
- คะแนนความคล้ายคลึงขึ้นอยู่กับคุณภาพภาพอ้างอิง แสง มุมถ่าย ความคมชัด และการจัดแนวภาพ
- ภาพที่มีเงาสะท้อน วัตถุบดบัง หรือรายละเอียดไม่ชัดอาจทำให้ผลคลาดเคลื่อน
- ควรใช้ผลวิเคราะห์ร่วมกับการตรวจสอบรายละเอียดและความเห็นจากผู้เชี่ยวชาญ
- คำสั่งติดตั้งในเอกสารนี้ใช้สำหรับเริ่มต้นระบบบนเครื่อง การยืนยันความพร้อมสำหรับ Production ต้องอาศัยการทดสอบระบบและสภาพแวดล้อมที่นำไปใช้งานจริง

---

<div align="center">

**Smart Amulet Verification & Marketplace**  
AI-Assisted Image Verification · Amulet Marketplace · Full-Stack Web Application

</div>
