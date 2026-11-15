# Media Toolkit (คู่มือภาษาไทย)

เครื่องมือจัดการไฟล์มีเดีย (รูปภาพและวิดีโอ) แบบครบวงจร พัฒนาด้วย Python (Flask) และ Vue 3 + Vuetify  
รันบนเครื่องของคุณเอง (Local Host) ไม่ต้องสมัครสมาชิก ไม่ต้องต่ออินเทอร์เน็ตสำหรับการแก้ไขรูป/แปลงไฟล์ และไม่ต้อง Login

---

## ฟีเจอร์หลัก (Features)

| เมนู | ฟีเจอร์ | รายละเอียดการทำงาน |
| :--- | :--- | :--- |
| **Converter** | แปลงรูปแบบไฟล์ | แปลงรูปภาพระหว่าง PNG, JPG, WEBP, GIF, ICO |
| **Basic Editor** | แต่งรูปภาพพื้นฐาน | วาดลายเส้น, ลบด้วยยางลบ, ครอปภาพ (Crop), หมุนภาพ (Rotate 90°), พลิกภาพ (Flip), ใส่ข้อความ/ลายน้ำ (Text) |
| **Frame Extractor** | ดึงรูปจากวิดีโอ | สกัดเฟรมวิดีโอทุกๆ 1 วินาทีออกมาเป็นไฟล์รูปภาพ และบีบอัดเป็น .zip ให้อัตโนมัติ |
| **Downloader** | ดาวน์โหลดวิดีโอ | ดาวน์โหลดคลิปจาก YouTube, Facebook, TikTok, Instagram, Twitter/X พร้อมเลือกความละเอียดหรือเลือกดาวน์โหลดเฉพาะเสียง (Audio Only) ได้ |
| **AI Studio** | ตกแต่งด้วย AI | Remove BG: ไดคัทลบพื้นหลังรูปภาพอัตโนมัติด้วย AI (rembg)<br>Upscale 2x: ขยายความละเอียดรูปภาพ 2 เท่าคมชัดสูง |
| **Compressor** | ย่อขนาดไฟล์ | บีบอัดขนาดไฟล์รูปภาพ (JPEG Quality 40) และวิดีโอ (H.264 CRF 28) ช่วยลดขนาดไฟล์โดยคงคุณภาพ |
| **Audio Extractor** | สกัดเสียงจากคลิป | แปลงไฟล์วิดีโอ (MP4, MKV, AVI, WebM) ออกมาเป็นไฟล์เสียง MP3 (320kbps) |

---

## ความต้องการของระบบ (Prerequisites)

- Python 3.10 ขึ้นไป
- ระบบปฏิบัติการ: Windows 10/11, macOS, หรือ Linux
- FFmpeg: ไม่จำเป็นต้องติดตั้งแยกในเครื่อง เพราะโปรเจกต์ติดตั้งผ่าน static-ffmpeg ให้อัตโนมัติ
- การเชื่อมต่ออินเทอร์เน็ต: จำเป็นเฉพาะเมื่อต้องการใช้งาน Video Downloader และการดาวน์โหลดโมเดล AI ในครั้งแรก

---

## ขั้นตอนการติดตั้งและเปิดใช้งาน (Installation)

### 1. ดาวน์โหลดโค้ด (Clone หรือ Download)
```bash
git clone https://github.com/TTHHXXEEZZ/Media-Took-kit.git
cd Media-Took-kit
```

### 2. สร้าง Virtual Environment (แนะนำ)
เพื่อป้องกันไม่ให้ dependency ตีกับโปรเจกต์อื่น:

บน Windows:
```powershell
python -m venv venv
venv\Scripts\activate
```

บน macOS / Linux:
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. ติดตั้งไลบรารีที่จำเป็น
```bash
pip install -r requirements.txt
```
หมายเหตุ: การติดตั้ง rembg และ onnxruntime อาจใช้เวลาสักครู่เนื่องจากมีโมเดล AI สำหรับลบพื้นหลัง

### 4. ตั้งค่า Environment Variable (ไม่บังคับ)
สามารถคัดลอกไฟล์ .env.example เป็น .env ได้:
```bash
# Windows
copy .env.example .env

# macOS / Linux
cp .env.example .env
```

### 5. เริ่มต้นใช้งาน (Run Application)

บน Windows:
ดับเบิลคลิกที่ไฟล์ run.bat หรือพิมพ์คำสั่ง:
```powershell
run.bat
```

บน macOS / Linux:
```bash
chmod +x run.sh
./run.sh
```

หรือรันตรงๆ ด้วยคำสั่ง Python:
```bash
python app.py
```

### 6. เข้าใช้งานผ่านหน้าเว็บ
เปิดเบราว์เซอร์ไปที่:
http://localhost:5000 หรือ http://127.0.0.1:5000

---

## โครงสร้างโฟลเดอร์ของโปรเจกต์ (Clean Open-Source Architecture)

โครงสร้างถูกจัดเรียงตามมาตรฐานงาน Open-source แยก HTML, CSS และ JavaScript ออกจากกันชัดเจน:

```text
media-toolkit/
├── app.py                  # Backend หลัก (Flask API + Image/Video Processor)
├── requirements.txt        # รายการ Python dependencies สำหรับ pip install
├── .env.example            # แม่แบบไฟล์ config ตัวแปรระบบ (ไม่มี Secret จริงหลุด)
├── .gitignore              # ละเว้นไฟล์ขยะ, venv, cache และโฟลเดอร์ downloads/
├── README.md               # เอกสารคู่มือภาษาอังกฤษ (Official README)
├── README_TH.md            # เอกสารคู่มือภาษาไทย (ฉบับสมบูรณ์)
├── run.bat                 # สคริปต์คลิกรันแบบง่ายบน Windows
├── run.sh                  # สคริปต์รันบน Linux/macOS
├── templates/
│   └── index.html          # HTML Template โครงร่างหน้าเว็บ
└── static/
    ├── css/
    │   └── style.css       # ไฟล์ตกแต่งหน้าตา (Custom CSS + Theme)
    └── js/
        └── main.js         # Frontend Logic (Vue 3, Vuetify 3, Cropper.js, Canvas Engine)
```

---

## รายละเอียดการใช้งานเครื่องมือแต่ละตัว

### 1. Universal Converter (แปลงไฟล์)
1. เลือกแท็บ Converter จากแถบเมนูด้านซ้าย
2. คลิกเลือกไฟล์รูปภาพที่ต้องการแปลง
3. ในช่อง Target Format เลือกนามสกุลที่ต้องการ (PNG, JPG, WEBP, GIF, ICO)
4. กดปุ่ม Convert Now ระบบจะประมวลผลและเปิดแท็บดาวน์โหลดไฟล์ใหม่ให้อัตโนมัติ

### 2. Basic Editor (แก้ไขภาพ & ลายน้ำ)
1. เลือกแท็บ Basic Editor แล้วอัปโหลดภาพที่ต้องการ
2. วาดภาพ (Paint): เลือกสีที่ต้องการ และปรับขนาดหัวแปรงด้วย Slider
3. ตัดขอบ (Crop): คลิก Crop Mode ปรับกรอบตัดภาพตามต้องการ แล้วคลิก Apply Crop
4. หมุน/พลิก: คลิกปุ่มหมุนซ้าย 90°, หมุนขวา 90°, หรือพลิกภาพแนวนอน/แนวตั้ง
5. ใส่ตัวอักษร: พิมพ์ข้อความลงในช่อง Add Text แล้วกดไอคอนลูกศรส่ง ตัวหนังสือจะประทับลงบนภาพ
6. คลิก Save & Download เพื่อบันทึกภาพผลลัพธ์เป็นไฟล์ PNG

### 3. Video Downloader (ดาวน์โหลดวิดีโอออนไลน์)
1. วางลิงก์วิดีโอจาก YouTube, TikTok, Facebook หรือแพลตฟอร์มอื่นในช่อง URL
2. ระบบจะดึงข้อมูลตัวอย่าง เช่น ชื่อคลิป, ภาพปก, ความยาว และตัวเลือกความละเอียดมาแสดง
3. เลือกคุณภาพที่ต้องการ (เช่น 1080p, 720p, Best หรือเลือก Audio Only เพื่อเอาเฉพาะเสียง)
4. กดปุ่ม Download เพื่อรับไฟล์

### 4. AI Studio (ไดคัทและเพิ่มความคมชัด)
1. อัปโหลดภาพที่ต้องการ
2. กดปุ่ม Remove BG เพื่อลบพื้นหลังออกอัตโนมัติ (จะได้ไฟล์ PNG โปร่งใส)
3. กดปุ่ม Upscale 2x เพื่อขยายความกว้างและยาวของภาพเป็น 2 เท่าด้วยอัลกอริทึม Lanczos คมชัดสูง

---

## ความปลอดภัยและความเป็นส่วนตัว (Privacy & Security)

- Local Processing: การแปลงไฟล์, แก้ไขรูปภาพ, แตกเฟรม, และประมวลผล AI ทำงานอยู่บนเครื่องของคุณเอง 100% ข้อมูลของคุณไม่ถูกส่งไปยังเซิร์ฟเวอร์ภายนอกใดๆ
- Auto Cleanup: มี Background Thread คอยตรวจสอบโฟลเดอร์ downloads/ ทุกๆ 1 ชั่วโมง และจะลบไฟล์ชั่วคราวที่มีอายุเกิน 24 ชั่วโมงทิ้งให้อัตโนมัติ เพื่อป้องกันไม่ให้พื้นที่ฮาร์ดดิสก์เต็ม
- No Credentials: ระบบไม่มีการเก็บรหัสผ่าน ไม่มีการใช้ฐานข้อมูลผู้ใช้ และไม่มี Token เพื่อความเรียบง่ายและปลอดภัยสูงสุดสำหรับการเปิดเผยโค้ดแบบ Open-source

---

## ใบอนุญาต (License)

โปรเจกต์นี้เผยแพร่ภายใต้สัญญาอนุญาต MIT License — คุณสามารถนำโค้ดไปศึกษา ใช้งาน ดัดแปลง หรือต่อยอดได้ฟรีอย่างอิสระ
