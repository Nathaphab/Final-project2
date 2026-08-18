# Industrial Amulet Comparator - Classroom Demo

Web App สำหรับเดโมในห้องเรียน โดยรับภาพอ้างอิง (REF) และภาพพระที่ต้องการตรวจ (Candidate) แล้วคำนวณคะแนนความต่างเชิง contour พร้อมตัดสิน PASS/FAIL

## จุดเด่นของเวอร์ชันนี้
- ปรับ preprocessing ให้ทนต่อคราบ ผิวไม่สม่ำเสมอ และแสงไม่เรียบมากขึ้น
- ใช้ adaptive threshold + CLAHE + morphology cleanup
- ใช้ median distance เป็นคะแนนหลัก เพื่อให้ robust กว่า trimmed mean
- เพิ่มช่อง `Amulet ID` เพื่อบันทึกรหัสพระแต่ละองค์ลง CSV
- บันทึกภาพ overlay และผลตรวจทุกครั้งอัตโนมัติ

## โครงสร้างไฟล์
- `app.py` : โปรแกรมหลัก
- `requirements.txt` : package ที่ต้องติดตั้ง
- `outputs/overlays/` : เก็บภาพผลลัพธ์
- `outputs/logs/inspection_log.csv` : เก็บผลตรวจทั้งหมด

## การติดตั้ง
```bash
pip install -r requirements.txt
```

## การรัน
```bash
python app.py
```
จากนั้นเปิดเบราว์เซอร์ที่:
- บนเครื่องเดียวกัน: `http://127.0.0.1:7860`
- บนมือถือใน Wi-Fi เดียวกัน: `http://<IP-เครื่องอาจารย์>:7860`

## วิธีใช้ในห้องเรียน
1. กรอก `Amulet ID` เช่น `AMU-001`
2. อัปโหลดภาพ REF
3. อัปโหลดภาพ Candidate
4. กด `Inspect`
5. ดูผล Score, Decision, และภาพ Overlay

## คำแนะนำเรื่องรหัสพระ (Amulet ID)
แนะนำให้ใช้รหัสที่อ่านง่ายและไม่ซ้ำ เช่น
- `AMU-001`, `AMU-002`
- `SMDJ-2401`, `SMDJ-2402`
- `REF-A`, `TEST-001`

ถ้าไม่กรอก ระบบจะสร้างรหัสอัตโนมัติในรูปแบบ `AUTO-YYYYMMDD-HHMMSS`

## รูปแบบข้อมูลใน CSV
ไฟล์ `inspection_log.csv` จะมีคอลัมน์หลักดังนี้
- `timestamp`
- `amulet_id`
- `score_px`
- `decision`
- `threshold_px`
- `num_pstar`
- `scoring_method`
- `overlay_path`

## หมายเหตุ
- เวอร์ชันนี้เหมาะกับงานสอนและเดโมในห้องเรียน
- ถ้ามุมภาพต่างกันมากหรือพื้นหลังรบกวนมาก ผลอาจคลาดเคลื่อน
- หากต้องการความแม่นยำสูงขึ้นในอนาคต ควรเพิ่ม registration ที่ละเอียดขึ้น และเพิ่มคุณลักษณะอื่นร่วมกับ contour


## New in this version
- Search box for **Amulet ID** on the History section
- **Inspection Thumbnails** gallery showing recent overlay results
- Search works with full or partial ID, for example `AMU-001` or `SMDJ`
- Refresh and Clear History still update the table, thumbnails, and CSV together
