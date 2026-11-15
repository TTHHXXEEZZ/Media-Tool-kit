import os

# ตั้งค่า thread ป้องกันแคลชและจัดการ AI
os.environ["OMP_NUM_THREADS"] = "1"
os.environ["MKL_NUM_THREADS"] = "1"
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"

import uuid
import logging
import threading
import time
import subprocess
import shutil
import traceback
import zipfile
import glob

# นำเข้าโมดูลหลัก
from flask import Flask, request, jsonify, send_file, render_template
from flask_cors import CORS
from werkzeug.utils import secure_filename
from PIL import Image
import yt_dlp
import static_ffmpeg

# นำเข้า rembg แบบปลอดภัย
try:
    from rembg import remove
    REMBG_AVAILABLE = True
except ImportError:
    REMBG_AVAILABLE = False
    print("Warning: ไม่พบไลบรารี rembg ฟีเจอร์ลบพื้นหลังจะไม่ทำงาน")
except Exception as e:
    REMBG_AVAILABLE = False
    print(f"Warning: rembg เกิดข้อผิดพลาด: {e}")

# 1. ตั้งค่าระบบ
print("กำลังเตรียม FFmpeg...")
static_ffmpeg.add_paths()

app = Flask(__name__)

# ตั้งค่าโฟลเดอร์สำหรับเก็บไฟล์
BASE_DIR = os.getcwd()
DOWNLOAD_DIR = os.path.join(BASE_DIR, 'downloads')
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

# ตั้งค่าเซิร์ฟเวอร์
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-change-me')
app.config['UPLOAD_FOLDER'] = DOWNLOAD_DIR
app.config['MAX_CONTENT_LENGTH'] = 4 * 1024 * 1024 * 1024

CORS(app)

# บันทึก Log
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('MediaToolkit')

# 2. ตัวประมวลผลไฟล์หลัก
class Processor:
    @staticmethod
    def get_path(filename):
        # คืนค่า path เต็มของไฟล์ใน downloads
        return os.path.join(app.config['UPLOAD_FOLDER'], filename)

    @staticmethod
    def save_file(f):
        # บันทึกไฟล์อัปโหลดพร้อมตั้งชื่อใหม่ไม่ให้ซ้ำ
        filename = f.filename if f.filename else 'upload.bin'
        original_ext = filename.rsplit('.', 1)[1].lower() if '.' in filename else 'bin'
        unique_name = f"{uuid.uuid4().hex}_{int(time.time())}.{original_ext}"
        save_path = Processor.get_path(unique_name)
        f.save(save_path)
        return save_path, unique_name

    @staticmethod
    def run_ffmpeg(cmd):
        # รันคำสั่ง FFmpeg ซ่อนหน้าต่างคอนโซลบน Windows
        if '-y' not in cmd:
            cmd.insert(1, '-y')
        creationflags = subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
        try:
            subprocess.run(
                cmd,
                check=True,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.PIPE,
                creationflags=creationflags
            )
        except subprocess.CalledProcessError as e:
            raise Exception(f"FFmpeg Error: {e.stderr.decode()}")

    # ดึงข้อมูลวิดีโอ
    @staticmethod
    def get_video_info(url):
        # ดึงข้อมูลคลิป เช่น ชื่อ ภาพปก ความยาว ความละเอียด
        ydl_opts = {
            'quiet': True,
            'skip_download': True,
            'no_warnings': True,
            'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
        }
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                qualities = set()
                if 'formats' in info:
                    for f in info['formats']:
                        if f.get('height'):
                            qualities.add(f['height'])
                return {
                    'title': info.get('title', 'Unknown Video'),
                    'thumbnail': info.get('thumbnail', ''),
                    'duration': info.get('duration_string', '0:00'),
                    'qualities': sorted(list(qualities), reverse=True),
                    'platform': info.get('extractor_key', 'Unknown')
                }
        except Exception as e:
            raise Exception(f"ดึงข้อมูลวิดีโอไม่สำเร็จ: {str(e)}")

    # แปลงไฟล์
    @staticmethod
    def process_convert(path, target_fmt):
        # แปลงไฟล์รูปภาพ หรือแตกเฟรมวิดีโอเป็น ZIP
        name = os.path.splitext(os.path.basename(path))[0]

        if target_fmt == 'FRAME-ZIP':
            # ดึงเฟรมวิดีโอทุก 1 วินาทีแล้วบีบอัดเป็น ZIP
            temp_dir = os.path.join(app.config['UPLOAD_FOLDER'], f"{name}_frames")
            os.makedirs(temp_dir, exist_ok=True)
            cmd = ['ffmpeg', '-i', path, '-vf', 'fps=1', os.path.join(temp_dir, 'frame_%04d.jpg')]
            Processor.run_ffmpeg(cmd)
            zip_name = f"{name}_frames.zip"
            zip_path = Processor.get_path(zip_name)
            with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zf:
                for root, _, files in os.walk(temp_dir):
                    for file in files:
                        zf.write(os.path.join(root, file), file)
            try:
                shutil.rmtree(temp_dir)
            except Exception:
                pass
            return zip_name

        out_name = f"{name}.{target_fmt.lower()}"
        out_path = Processor.get_path(out_name)

        if target_fmt.lower() in ['jpg', 'jpeg', 'png', 'webp', 'ico', 'bmp']:
            with Image.open(path) as img:
                if target_fmt.lower() == 'jpg':
                    # ลบพื้นหลังโปร่งใสสำหรับภาพ JPEG
                    if img.mode in ('RGBA', 'LA'):
                        bg = Image.new("RGB", img.size, (255, 255, 255))
                        bg.paste(img, mask=img.split()[-1])
                        img = bg
                    else:
                        img = img.convert("RGB")
                else:
                    img = img.convert("RGBA")
                img.save(out_path, quality=95)

        elif target_fmt.lower() == 'gif':
            cmd = [
                'ffmpeg', '-i', path,
                '-vf', 'fps=10,scale=480:-1:flags=lanczos,split[s0][s1];[s0]palettegen[p];[s1][p]paletteuse',
                '-loop', '0', out_path
            ]
            Processor.run_ffmpeg(cmd)

        return out_name

    # ดาวน์โหลดวิดีโอ
    @staticmethod
    def process_download(url, quality='best'):
        # ดาวน์โหลดวิดีโอผ่าน yt-dlp
        temp_id = uuid.uuid4().hex
        out_tmpl = os.path.join(app.config['UPLOAD_FOLDER'], f"{temp_id}.%(ext)s")

        if quality == 'audio':
            fmt_str = 'bestaudio/best'
        elif quality == 'best':
            fmt_str = 'bestvideo+bestaudio/best'
        else:
            try:
                h = int(quality)
                fmt_str = f'bestvideo[height<={h}]+bestaudio/best[height<={h}]/best'
            except ValueError:
                fmt_str = 'best'

        ydl_opts = {
            'format': fmt_str,
            'outtmpl': out_tmpl,
            'noplaylist': True,
            'quiet': True,
            'no_warnings': True,
            'restrictfilenames': True,
            'nocheckcertificate': True,
            'ignoreerrors': True,
            'merge_output_format': 'mp4',
            'extractor_args': {'youtube': {'player_client': ['android']}},
            'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
        }

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)

                # ค้นหาไฟล์ที่เพิ่งดาวน์โหลดด้วย temp_id
                search_pattern = os.path.join(app.config['UPLOAD_FOLDER'], f"{temp_id}.*")
                found_files = glob.glob(search_pattern)
                if not found_files:
                    raise Exception("ดาวน์โหลดเสร็จสิ้นแต่ไม่พบไฟล์ผลลัพธ์")

                downloaded_file = found_files[0]

                # ตั้งชื่อไฟล์ใหม่ให้ปลอดภัย
                raw_title = info.get('title', 'video') if info else 'video'
                safe_title = secure_filename(raw_title)
                if not safe_title:
                    safe_title = f"video_{temp_id[:6]}"
                safe_title = safe_title[:50]

                ext = os.path.splitext(downloaded_file)[1]
                final_filename = f"{safe_title}_{temp_id[:8]}{ext}"
                final_path = Processor.get_path(final_filename)

                if os.path.exists(final_path):
                    os.remove(final_path)
                os.rename(downloaded_file, final_path)

                return final_filename

        except Exception as e:
            # ลบไฟล์ชั่วคราวทิ้งหากมีข้อผิดพลาด
            for f in glob.glob(os.path.join(app.config['UPLOAD_FOLDER'], f"{temp_id}.*")):
                try:
                    os.remove(f)
                except Exception:
                    pass
            msg = str(e)
            if "403" in msg:
                raise Exception("เซิร์ฟเวอร์ปฏิเสธการเข้าถึง Error 403")
            raise Exception(f"ดาวน์โหลดล้มเหลว: {msg}")

    # สกัดเสียง MP3
    @staticmethod
    def process_audio(path):
        # สกัดเสียงจากไฟล์วิดีโอเป็น MP3
        out_name = f"{os.path.splitext(os.path.basename(path))[0]}.mp3"
        cmd = ['ffmpeg', '-i', path, '-vn', '-acodec', 'libmp3lame', '-q:a', '2', Processor.get_path(out_name)]
        Processor.run_ffmpeg(cmd)
        return out_name

    # ลบพื้นหลังด้วย AI
    @staticmethod
    def process_remove_bg(path):
        # ลบพื้นหลังรูปภาพด้วย rembg
        if not REMBG_AVAILABLE:
            raise Exception("ยังไม่ได้ติดตั้งไลบรารี AI rembg")
        out_name = f"{os.path.splitext(os.path.basename(path))[0]}_nobg.png"
        try:
            with open(path, 'rb') as i:
                output = remove(i.read())
            with open(Processor.get_path(out_name), 'wb') as o:
                o.write(output)
        except Exception as e:
            raise Exception(f"ลบพื้นหลังล้มเหลว: {e}")
        return out_name

    # ขยายขนาดภาพ 2 เท่า
    @staticmethod
    def process_upscale(path):
        # ขยายภาพ 2 เท่าด้วย Lanczos
        out_name = f"{os.path.splitext(os.path.basename(path))[0]}_2x.png"
        try:
            with Image.open(path) as img:
                img = img.resize((img.width * 2, img.height * 2), resample=Image.Resampling.LANCZOS)
                img.save(Processor.get_path(out_name))
        except Exception as e:
            raise Exception(f"ขยายขนาดภาพล้มเหลว: {e}")
        return out_name

    # บีบอัดไฟล์
    @staticmethod
    def process_compress(path, type_):
        # บีบอัดรูปภาพหรือวิดีโอ
        out_name = f"{os.path.splitext(os.path.basename(path))[0]}_min"
        if type_ == 'image':
            out_name += ".jpg"
            with Image.open(path) as img:
                img.convert("RGB").save(Processor.get_path(out_name), "JPEG", quality=40, optimize=True)
        else:
            out_name += ".mp4"
            cmd = ['ffmpeg', '-i', path, '-vcodec', 'libx264', '-crf', '28', Processor.get_path(out_name)]
            Processor.run_ffmpeg(cmd)
        return out_name

# 3. API Routes จุดรับส่งข้อมูล
@app.route('/')
def index():
    # ส่งหน้าเว็บหลัก
    return render_template('index.html')


@app.route('/api/process/<action>', methods=['POST'])
def process(action):
    # จุดประมวลผลมีเดียทุกรูปแบบ ไม่ต้องเข้าสู่ระบบ
    try:
        # ดึงข้อมูลวิดีโอ ไม่ต้องอัปโหลดไฟล์
        if action == 'info':
            url = request.json.get('url')
            if not url:
                return jsonify({"error": "ต้องระบุ URL"}), 400
            info = Processor.get_video_info(url)
            return jsonify(info)

        out_file = None

        # ดาวน์โหลดวิดีโอ ไม่ต้องอัปโหลดไฟล์
        if action == 'download':
            url = request.json.get('url')
            quality = request.json.get('quality', 'best')
            if not url:
                return jsonify({"error": "ต้องระบุ URL"}), 400
            out_file = Processor.process_download(url, quality)

        # งานประมวลผลที่ต้องใช้ไฟล์
        else:
            if 'file' not in request.files:
                return jsonify({"error": "ไม่พบไฟล์ที่อัปโหลด"}), 400
            f = request.files['file']
            input_path, _ = Processor.save_file(f)

            if action == 'convert':
                fmt = request.form.get('format', 'png')
                out_file = Processor.process_convert(input_path, fmt)
            elif action == 'audio':
                out_file = Processor.process_audio(input_path)
            elif action == 'remove-bg':
                out_file = Processor.process_remove_bg(input_path)
            elif action == 'upscale':
                out_file = Processor.process_upscale(input_path)
            elif action == 'compress':
                ctype = request.form.get('type', 'image')
                out_file = Processor.process_compress(input_path, ctype)
            else:
                return jsonify({"error": f"ไม่พบคำสั่ง: {action}"}), 400

        return jsonify({"url": f"/api/files/{out_file}", "filename": out_file, "status": "success"})

    except Exception as e:
        logger.error(traceback.format_exc())
        return jsonify({"error": str(e)}), 500


@app.route('/api/files/<filename>')
def serve(filename):
    # ส่งไฟล์ดาวน์โหลดกลับไปให้ผู้ใช้
    try:
        safe_name = secure_filename(filename)
        file_path = Processor.get_path(safe_name)
        if not os.path.exists(file_path):
            logger.error(f"ไม่พบไฟล์: {file_path}")
            return jsonify({"error": "ไม่พบไฟล์บนเซิร์ฟเวอร์"}), 404
        return send_file(file_path, as_attachment=True)
    except Exception as e:
        logger.error(f"เกิดข้อผิดพลาดในการส่งไฟล์: {e}")
        return jsonify({"error": "ไม่สามารถส่งไฟล์ได้"}), 500


# 4. เคลียร์ไฟล์เก่าอัตโนมัติ
def cleanup_old_files():
    # ลบไฟล์ใน downloads ที่มีอายุเกิน 24 ชั่วโมง
    while True:
        time.sleep(3600)  # เช็คทุก 1 ชั่วโมง
        now = time.time()
        for f in os.listdir(app.config['UPLOAD_FOLDER']):
            p = os.path.join(app.config['UPLOAD_FOLDER'], f)
            if os.path.isfile(p) and os.stat(p).st_mtime < now - 86400:
                try:
                    os.remove(p)
                except Exception:
                    pass


if __name__ == '__main__':
    threading.Thread(target=cleanup_old_files, daemon=True).start()
    app.run(debug=True, host='0.0.0.0', port=5000)
