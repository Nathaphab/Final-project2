import time
import os
import cv2
import numpy as np
from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import uvicorn
from ultralytics import YOLO
from PIL import Image, ImageDraw, ImageFont
import shutil
from datetime import datetime
import hashlib
import pandas as pd
from scipy import ndimage
import psycopg2
from dotenv import load_dotenv
import cloudinary
import cloudinary.uploader
import cloudinary.api

# โหลดโมเดล YOLO เตรียมไว้ตั้งแต่เริ่มรันเซิร์ฟเวอร์
try:
    yolo_model = YOLO("models/best.pt")
    print("✅ โหลดโมเดล YOLO สำเร็จ!")
except Exception as e:
    yolo_model = None
    print(f"❌ ไม่สามารถโหลดโมเดลได้: {e}")

# ================= Settings =================
T_PX = 24.0
NUM_PSTAR = 12
GAUSS_SIGMA = 1.6
MAX_IMAGE_SIDE = 1280
MIN_COMPONENT_RATIO = 0.08
AREA_RATIO_TOL = 99.0
PERIMETER_RATIO_TOL = 99.0
MATCH_SHAPES_THRESH = 0.40
SSIM_THRESH = 0.70          
ORB_MATCH_THRESH = 20       
ORB_FEATURES = 500

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
OUT_DIR = os.path.join(BASE_DIR, "outputs")
OVERLAY_DIR = os.path.join(OUT_DIR, "overlays")
LOG_DIR = os.path.join(OUT_DIR, "logs")
LOG_CSV = os.path.join(LOG_DIR, "inspection_log.csv")
DEBUG_DIR = os.path.join(OUT_DIR, "debug")

os.makedirs(OVERLAY_DIR, exist_ok=True)
os.makedirs(LOG_DIR, exist_ok=True)
os.makedirs(DEBUG_DIR, exist_ok=True)
MARKET_DIR = os.path.join(OUT_DIR, "market_images")
os.makedirs(MARKET_DIR, exist_ok=True)

LOG_COLUMNS = [
    "timestamp",
    "amulet_id",
    "score_px",
    "decision",
    "threshold_px",
    "num_pstar",
    "scoring_method",
    "overlay_path",
]

if not os.path.exists(LOG_CSV):
    pd.DataFrame(columns=LOG_COLUMNS).to_csv(LOG_CSV, index=False)

# ================= Database & Cloudinary Setup =================
load_dotenv() 

DATABASE_URL = os.environ.get("DATABASE_URL", "")

cloudinary.config(
  cloud_name = os.environ.get("CLOUDINARY_CLOUD_NAME"),
  api_key = os.environ.get("CLOUDINARY_API_KEY"),
  api_secret = os.environ.get("CLOUDINARY_API_SECRET"),
  secure = True
)

def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

def get_db_connection():
    return psycopg2.connect(DATABASE_URL)

def init_db():
    if not DATABASE_URL:
        print("⚠️ ยังไม่ได้ตั้งค่า DATABASE_URL ในไฟล์ .env ระบบจะข้ามการสร้างตารางไปก่อน")
        return
        
    conn = get_db_connection()
    c = conn.cursor()
    
    c.execute('''CREATE TABLE IF NOT EXISTS history
                 (id SERIAL PRIMARY KEY,
                  amulet_id TEXT,
                  timestamp TEXT,
                  decision TEXT,
                  score_px REAL,
                  threshold_px REAL,
                  num_pstar INTEGER,
                  scoring_method TEXT,
                  overlay_path TEXT,
                  ref_contour_path TEXT)''')
                  
    c.execute('''CREATE TABLE IF NOT EXISTS amulets 
                 (id SERIAL PRIMARY KEY,
                  seller_id INTEGER,
                  name TEXT,
                  temple TEXT,
                  year TEXT,
                  price REAL,
                  image_path TEXT,
                  description TEXT,
                  status TEXT DEFAULT 'available',
                  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')

    c.execute('''CREATE TABLE IF NOT EXISTS users (
                    id SERIAL PRIMARY KEY,
                    username TEXT NOT NULL,
                    email TEXT UNIQUE NOT NULL,
                    password TEXT NOT NULL,
                    role TEXT NOT NULL,
                    status TEXT DEFAULT 'active'
                 )''')

    c.execute('''CREATE TABLE IF NOT EXISTS orders (
                    id SERIAL PRIMARY KEY,
                    amulet_id INTEGER,
                    buyer_id INTEGER,
                    buyer_name TEXT,
                    buyer_phone TEXT,
                    buyer_address TEXT,
                    total_amount REAL,
                    status TEXT DEFAULT 'pending',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                 )''')
    
    c.execute("SELECT * FROM users WHERE email = 'admin@system.com'")
    if not c.fetchone():
        hashed_pw = hash_password('admin123')
        c.execute("INSERT INTO users (username, email, password, role) VALUES ('admin', 'admin@system.com', %s, 'admin')", (hashed_pw,))

    conn.commit()
    conn.close()

init_db()

# ================= Pydantic Models =================
class UserRegister(BaseModel):
    username: str
    email: str
    password: str
    role: str

class UserLogin(BaseModel):
    email: str
    password: str

class OrderCreate(BaseModel):
    amulet_id: int
    buyer_id: int
    buyer_name: str
    buyer_phone: str
    buyer_address: str
    total_amount: float

# ================= Utility Functions =================
def ensure_rgb(img: np.ndarray) -> np.ndarray:
    if img is None:
        raise ValueError("Input image is None")
    if img.ndim == 2:
        return cv2.cvtColor(img, cv2.COLOR_GRAY2RGB)
    if img.shape[2] == 4:
        return cv2.cvtColor(img, cv2.COLOR_RGBA2RGB)
    return img.copy()

def to_gray(img: np.ndarray) -> np.ndarray:
    rgb = ensure_rgb(img)
    return cv2.cvtColor(rgb, cv2.COLOR_RGB2GRAY)

def compute_ssim_opencv(img1, img2):
    h, w = img1.shape
    if h < 11 or w < 11:
        return 0.0
    img1 = img1.astype(np.float64)
    img2 = img2.astype(np.float64)
    C1 = (0.01 * 255) ** 2
    C2 = (0.03 * 255) ** 2
    kernel = cv2.getGaussianKernel(11, 1.5)
    window = np.outer(kernel, kernel.transpose())
    mu1 = cv2.filter2D(img1, -1, window)[5:-5, 5:-5]
    mu2 = cv2.filter2D(img2, -1, window)[5:-5, 5:-5]
    mu1_sq = mu1 ** 2
    mu2_sq = mu2 ** 2
    mu1_mu2 = mu1 * mu2
    sigma1_sq = cv2.filter2D(img1 ** 2, -1, window)[5:-5, 5:-5] - mu1_sq
    sigma2_sq = cv2.filter2D(img2 ** 2, -1, window)[5:-5, 5:-5] - mu2_sq
    sigma12 = cv2.filter2D(img1 * img2, -1, window)[5:-5, 5:-5] - mu1_mu2
    ssim_map = ((2 * mu1_mu2 + C1) * (2 * sigma12 + C2)) / ((mu1_sq + mu2_sq + C1) * (sigma1_sq + sigma2_sq + C2))
    return float(ssim_map.mean())

def resize_keep_aspect(img: np.ndarray, max_side: int = MAX_IMAGE_SIDE) -> np.ndarray:
    h, w = img.shape[:2]
    scale = min(max_side / max(h, w), 1.0)
    if scale == 1.0:
        return img.copy()
    new_w = max(1, int(round(w * scale)))
    new_h = max(1, int(round(h * scale)))
    return cv2.resize(img, (new_w, new_h), interpolation=cv2.INTER_AREA)

def get_best_object_contour(mask: np.ndarray):
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if not contours:
        return None
    h, w = mask.shape
    img_area = h * w
    center_x, center_y = w / 2, h / 2
    best_cnt = None
    best_score = -1
    for cnt in contours:
        area = cv2.contourArea(cnt)
        if area < (img_area * 0.01) or area > (img_area * 0.98):
            continue
        x, y, w_box, h_box = cv2.boundingRect(cnt)
        if w_box >= w - 2 and h_box >= h - 2:
            continue
        M = cv2.moments(cnt)
        if M['m00'] != 0:
            cx, cy = int(M['m10'] / M['m00']), int(M['m01'] / M['m00'])
        else:
            cx, cy = x + w_box / 2, y + h_box / 2
        dist_to_center = np.sqrt((cx - center_x) ** 2 + (cy - center_y) ** 2)
        max_dist = np.sqrt(center_x**2 + center_y**2)
        area_score = area / img_area
        center_score = 1.0 - (dist_to_center / max_dist)
        score = (area_score * 0.6) + (center_score * 0.4)
        if score > best_score:
            best_score = score
            best_cnt = cnt
    if best_cnt is None and contours:
        valid_contours = [c for c in contours if cv2.contourArea(c) < img_area * 0.99]
        if valid_contours:
            best_cnt = max(valid_contours, key=cv2.contourArea)
    return best_cnt

def preprocess_and_contour(img: np.ndarray):
    rgb = resize_keep_aspect(ensure_rgb(img))
    gray = to_gray(rgb)
    h, w = gray.shape
    blur = cv2.GaussianBlur(gray, (5, 5), 0)
    cv2.rectangle(blur, (0, 0), (w-1, h-1), 0, thickness=2)
    best_cnt = None
    _, th_otsu = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    border_pixels = np.concatenate([th_otsu[0, :], th_otsu[-1, :], th_otsu[:, 0], th_otsu[:, -1]])
    if np.mean(border_pixels) > 127: 
        th_otsu = cv2.bitwise_not(th_otsu)
    filled_otsu = ndimage.binary_fill_holes(th_otsu > 0).astype(np.uint8) * 255
    kernel_clean = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
    mask_otsu = cv2.morphologyEx(filled_otsu, cv2.MORPH_OPEN, kernel_clean, iterations=1)
    best_cnt = get_best_object_contour(mask_otsu)
    
    if best_cnt is None or cv2.contourArea(best_cnt) < (h*w*0.05):
        th_adapt = cv2.adaptiveThreshold(blur, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 31, 5)
        filled_adapt = ndimage.binary_fill_holes(th_adapt > 0).astype(np.uint8) * 255
        mask_adapt = cv2.morphologyEx(filled_adapt, cv2.MORPH_OPEN, kernel_clean, iterations=1)
        cnt_adapt = get_best_object_contour(mask_adapt)
        if cnt_adapt is not None:
            if best_cnt is None or cv2.contourArea(cnt_adapt) > cv2.contourArea(best_cnt):
                best_cnt = cnt_adapt
                
    if best_cnt is None or cv2.contourArea(best_cnt) < (h*w*0.05):
        edges = cv2.Canny(blur, 20, 80)
        kernel_close = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (15, 15))
        closed_edges = cv2.morphologyEx(edges, cv2.MORPH_CLOSE, kernel_close, iterations=2)
        filled_edges = ndimage.binary_fill_holes(closed_edges > 0).astype(np.uint8) * 255
        mask_edges = cv2.morphologyEx(filled_edges, cv2.MORPH_OPEN, kernel_clean, iterations=1)
        cnt_edges = get_best_object_contour(mask_edges)
        if cnt_edges is not None:
            if best_cnt is None or cv2.contourArea(cnt_edges) > cv2.contourArea(best_cnt):
                best_cnt = cnt_edges
                
    final_mask = np.zeros_like(gray)
    final_edge = np.zeros_like(gray)
    if best_cnt is not None:
        epsilon = 0.001 * cv2.arcLength(best_cnt, True)
        best_cnt = cv2.approxPolyDP(best_cnt, epsilon, True)
        cv2.drawContours(final_mask, [best_cnt], -1, 255, thickness=cv2.FILLED)
        cv2.drawContours(final_edge, [best_cnt], -1, 255, thickness=2)
    return rgb, gray, final_mask, final_edge, best_cnt

def contour_to_points(cnt: np.ndarray) -> np.ndarray:
    pts = cnt.reshape(-1, 2)
    return pts.astype(np.int32)

def amulet_id_or_auto(amulet_id: str) -> str:
    raw = (amulet_id or "").strip()
    if raw:
        return raw
    return "AUTO-" + datetime.now().strftime("%Y%m%d-%H%M%S")

def sanitize_id(text: str) -> str:
    return "".join(ch if ch.isalnum() or ch in "-_" else "_" for ch in text)

def load_log_df() -> pd.DataFrame:
    if not os.path.exists(LOG_CSV):
        return pd.DataFrame(columns=LOG_COLUMNS)
    df = pd.read_csv(LOG_CSV)
    missing = [c for c in LOG_COLUMNS if c not in df.columns]
    for col in missing:
        df[col] = ""
    return df.loc[:, LOG_COLUMNS]

def to_web_overlay_path(overlay_path: str) -> str:
    if not overlay_path:
        return ""
    if str(overlay_path).startswith("http"):
        return overlay_path # ถ้าเป็นลิงก์ Cloudinary ให้ใช้ได้เลย
    filename = os.path.basename(overlay_path)
    return f"/outputs/overlays/{filename}"

def auto_pstar_from_contour(cnt: np.ndarray, num_p: int = NUM_PSTAR) -> np.ndarray:
    pts = contour_to_points(cnt)
    total_pts = len(pts)
    if total_pts == 0:
        return np.array([[1, 1]], dtype=np.int32)
    if total_pts <= num_p:
        return pts
    arc = np.zeros(total_pts, dtype=np.float32)
    for i in range(1, total_pts):
        arc[i] = arc[i-1] + np.linalg.norm(pts[i] - pts[i-1])
    total_len = arc[-1]
    if total_len == 0:
        return pts[:num_p]
    step = total_len / (num_p - 1) if num_p > 1 else total_len
    indices = []
    for i in range(num_p):
        target = i * step
        idx = np.searchsorted(arc, target)
        idx = min(idx, total_pts - 1)
        indices.append(idx)
    return pts[indices]

def align_candidate_to_ref(ref_rgb: np.ndarray, ref_cnt: np.ndarray,
                           cand_rgb: np.ndarray, cand_cnt: np.ndarray):
    M_ref = cv2.moments(ref_cnt)
    M_cand = cv2.moments(cand_cnt)
    cx_ref = M_ref['m10'] / M_ref['m00'] if M_ref['m00'] != 0 else 0
    cy_ref = M_ref['m01'] / M_ref['m00'] if M_ref['m00'] != 0 else 0
    cx_cand = M_cand['m10'] / M_cand['m00'] if M_cand['m00'] != 0 else 0
    cy_cand = M_cand['m01'] / M_cand['m00'] if M_cand['m00'] != 0 else 0
    area_ref = cv2.contourArea(ref_cnt)
    area_cand = cv2.contourArea(cand_cnt)
    if area_cand == 0:
        scale = 1.0
    else:
        scale = np.sqrt(area_ref / area_cand)
        scale = np.clip(scale, 0.3, 3.0)
    delta_angle = 0.0 
    cos_a = np.cos(delta_angle)
    sin_a = np.sin(delta_angle)
    tx = cx_ref - scale * (cx_cand * cos_a - cy_cand * sin_a)
    ty = cy_ref - scale * (cx_cand * sin_a + cy_cand * cos_a)
    M = np.float32([
        [scale * cos_a, -scale * sin_a, tx],
        [scale * sin_a,  scale * cos_a, ty]
    ])
    h, w = ref_rgb.shape[:2]
    warped = cv2.warpAffine(cand_rgb, M, (w, h), flags=cv2.INTER_LINEAR,
                            borderMode=cv2.BORDER_CONSTANT, borderValue=(0,0,0))
    return warped, M

def compute_chamfer_score(ref_edge: np.ndarray, cand_edge: np.ndarray, percentile: int = 95) -> tuple:
    if ref_edge is None or cand_edge is None:
        return float('inf'), 0.0
    if np.sum(ref_edge) == 0 or np.sum(cand_edge) == 0:
        return float('inf'), 0.0
    ref_bin = (ref_edge > 0).astype(np.uint8)
    dist_ref = cv2.distanceTransform(1 - ref_bin, cv2.DIST_L2, 3)
    cand_pts = np.column_stack(np.where(cand_edge > 0))
    if len(cand_pts) == 0:
        return float('inf'), 0.0
    distances = []
    for y, x in cand_pts:
        x = int(np.clip(x, 0, dist_ref.shape[1] - 1))
        y = int(np.clip(y, 0, dist_ref.shape[0] - 1))
        d = dist_ref[y, x]
        distances.append(d)
    if not distances:
        return float('inf'), 0.0
    score = np.percentile(distances, percentile)
    intersection = np.logical_and(ref_edge > 0, cand_edge > 0).sum()
    union = np.logical_or(ref_edge > 0, cand_edge > 0).sum()
    jaccard = intersection / union if union > 0 else 0.0
    return float(score), float(jaccard)

def nearest_edge_points(edge: np.ndarray, pstar: np.ndarray) -> np.ndarray:
    if len(pstar) == 0:
        return np.empty((0, 2), dtype=np.int32)
    edge_bin = (edge > 0).astype(np.uint8)
    dist_edge = cv2.distanceTransform(1 - edge_bin, cv2.DIST_L2, 3)
    nearest = []
    h, w = dist_edge.shape
    for x, y in pstar:
        x = int(np.clip(x, 0, w - 1))
        y = int(np.clip(y, 0, h - 1))
        found = False
        best_pt = (x, y)
        for r in range(1, 30):
            for dy in range(-r, r+1):
                for dx in range(-r, r+1):
                    nx = x + dx
                    ny = y + dy
                    if 0 <= nx < w and 0 <= ny < h:
                        if edge[ny, nx] > 0:
                            best_pt = (nx, ny)
                            found = True
                            break
                if found:
                    break
            if found:
                break
        nearest.append(best_pt)
    return np.array(nearest, dtype=np.int32)

def make_overlay(base_img: np.ndarray, edge: np.ndarray,
                 pstar: np.ndarray, nearest_pts: np.ndarray,
                 score: float, decision: str, status_line: str,
                 amulet_id: str) -> np.ndarray:
    overlay = ensure_rgb(base_img).copy()
    overlay[edge > 0] = np.array([255, 0, 0], dtype=np.uint8)
    for (x, y), (ex, ey) in zip(pstar, nearest_pts):
        cv2.circle(overlay, (int(x), int(y)), 6, (0, 255, 0), 2)
        cv2.drawMarker(overlay, (int(ex), int(ey)), (0, 255, 255),
                       markerType=cv2.MARKER_TILTED_CROSS, markerSize=12, thickness=2)
        cv2.line(overlay, (int(x), int(y)), (int(ex), int(ey)), (255, 255, 0), 1)
    cv2.putText(overlay, f"ID: {amulet_id}", (20, 32),
                cv2.FONT_HERSHEY_SIMPLEX, 0.80, (255, 255, 255), 2, cv2.LINE_AA)
    cv2.putText(overlay, f"Decision: {decision}", (20, 64),
                cv2.FONT_HERSHEY_SIMPLEX, 0.80, (0, 128, 255), 2, cv2.LINE_AA)
    cv2.putText(overlay, f"Score: {score:.3f} px   Threshold: {T_PX:.3f} px", (20, 96),
                cv2.FONT_HERSHEY_SIMPLEX, 0.68, (0, 128, 255), 2, cv2.LINE_AA)
    font_path = "THSarabunNew.ttf" 
    overlay = draw_thai_text_on_cv_image(overlay, status_line, (20, 128), font_path, 30, (255, 255, 255))
    return overlay

def make_early_fail_overlay(base_img: np.ndarray, edge: np.ndarray, amulet_id: str, reason: str) -> np.ndarray:
    overlay = ensure_rgb(base_img).copy()
    if edge is not None and np.sum(edge) > 0:
        overlay[edge > 0] = np.array([0, 0, 255], dtype=np.uint8)
    cv2.putText(overlay, f"ID: {amulet_id}", (20, 32),
                cv2.FONT_HERSHEY_SIMPLEX, 0.80, (255, 255, 255), 2, cv2.LINE_AA)
    cv2.putText(overlay, f"Decision: FAIL", (20, 64),
                cv2.FONT_HERSHEY_SIMPLEX, 0.80, (0, 0, 255), 2, cv2.LINE_AA)
    font_path = "THSarabunNew.ttf"
    overlay = draw_thai_text_on_cv_image(overlay, f"Error: {reason}", (20, 96), font_path, 30, (0, 128, 255))
    return overlay

def save_log(amulet_id: str, score: float, decision: str, overlay_path: str):
    df = load_log_df()
    df.loc[len(df)] = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "amulet_id": amulet_id,
        "score_px": score,
        "decision": decision,
        "threshold_px": T_PX,
        "num_pstar": NUM_PSTAR,
        "scoring_method": "chamfer+ssim+orb",
        "overlay_path": overlay_path,
    }
    df.to_csv(LOG_CSV, index=False)

def render_debug_view(ref_rgb: np.ndarray, ref_edge: np.ndarray, pstar: np.ndarray, amulet_id: str) -> np.ndarray:
    vis = ensure_rgb(ref_rgb).copy()
    vis[ref_edge > 0] = np.array([255, 0, 0], dtype=np.uint8)
    for x, y in pstar:
        cv2.circle(vis, (int(x), int(y)), 6, (0, 255, 0), 2)
    cv2.putText(vis, f"REF contour + P* ({len(pstar)} points)", (20, 32),
                cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 128, 255), 2, cv2.LINE_AA)
    cv2.putText(vis, f"Target ID: {amulet_id}", (20, 64),
                cv2.FONT_HERSHEY_SIMPLEX, 0.72, (255, 255, 255), 2, cv2.LINE_AA)
    return vis

# ================= FastAPI Application =================
app = FastAPI(title="Smart Amulet Verification API")

def draw_thai_text_on_cv_image(image_cv, text, position, font_path, font_size, color_bgr):
    image_rgb = cv2.cvtColor(image_cv, cv2.COLOR_BGR2RGB)
    image_pil = Image.fromarray(image_rgb)
    draw = ImageDraw.Draw(image_pil)
    try:
        font = ImageFont.truetype(font_path, font_size)
    except IOError:
        font = ImageFont.load_default()
    color_rgb = (color_bgr[2], color_bgr[1], color_bgr[0])
    draw.text(position, text, font=font, fill=color_rgb, stroke_width=2, stroke_fill=(0, 0, 0))
    image_final = cv2.cvtColor(np.array(image_pil), cv2.COLOR_RGB2BGR)
    return image_final

# ================= AI Inspect API =================
@app.post("/api/inspect")
async def inspect_amulet(
    amulet_id: str = Form(""), 
    ref_file: UploadFile = File(...), 
    cand_file: UploadFile = File(...)
):
    if yolo_model is None:
        return {"success": False, "error_message": "ระบบ AI ยังไม่พร้อมทำงาน"}

    try:
        ref_bytes = await ref_file.read()
        cand_bytes = await cand_file.read()
        ref_nparr = np.frombuffer(ref_bytes, np.uint8)
        cand_nparr = np.frombuffer(cand_bytes, np.uint8)
        ref_img = cv2.imdecode(ref_nparr, cv2.IMREAD_COLOR)
        cand_img = cv2.imdecode(cand_nparr, cv2.IMREAD_COLOR)

        if ref_img is None or cand_img is None:
            return {"success": False, "error_message": "กรุณาอัปโหลดรูปภาพที่ถูกต้อง"}

        final_id = amulet_id_or_auto(amulet_id)
        safe_id = sanitize_id(final_id)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        ref_results = yolo_model(ref_img)[0]
        cand_results = yolo_model(cand_img)[0]

        ref_cls, cand_cls = None, None
        best_conf_val = 0.0

        if hasattr(ref_results, 'boxes') and ref_results.boxes is not None and len(ref_results.boxes) > 0:
            ref_cls = ref_results.names[int(ref_results.boxes.cls[0])]
        if hasattr(cand_results, 'boxes') and cand_results.boxes is not None and len(cand_results.boxes) > 0:
            cand_cls = cand_results.names[int(cand_results.boxes.cls[0])]
            best_conf_val = float(cand_results.boxes.conf[0]) * 100

        ai_pass = False
        note = ""
        if not ref_cls or not cand_cls:
            note = "FAIL: AI มองไม่เห็นพระในภาพ"
        elif ref_cls != cand_cls:
            note = f"พระคนละพิมพ์ (อ้างอิง: {ref_cls} | ตรวจพบ: {cand_cls})"
        elif best_conf_val < 20:
            note = f"พิมพ์ตรงกัน ({cand_cls}) แต่ AI มั่นใจต่ำเกินไป ({best_conf_val:.2f}%)"
        else:
            ai_pass = True

        if not ai_pass:
            cand_annotated = cand_results.plot()
            cand_upload = cloudinary.uploader.upload(cv2.imencode('.jpg', cand_annotated)[1].tobytes())
            ref_upload = cloudinary.uploader.upload(ref_bytes)
            cand_url = cand_upload.get("secure_url")
            ref_url = ref_upload.get("secure_url")
            save_log(final_id, 999.0, "FAIL", cand_url)

            return {
                "success": True, "decision": "FAIL", "score": "N/A", "note": note,
                "overlay_url": cand_url,
                "ref_contour_url": ref_url
            }

        ref_img_rgb = cv2.cvtColor(ref_img, cv2.COLOR_BGR2RGB)
        cand_img_rgb = cv2.cvtColor(cand_img, cv2.COLOR_BGR2RGB)
        ref_rgb, _, _, ref_edge, ref_cnt = preprocess_and_contour(ref_img_rgb)
        cand_rgb, _, _, cand_edge, cand_cnt = preprocess_and_contour(cand_img_rgb)

        if ref_cnt is None or cand_cnt is None:
            cand_annotated = cand_results.plot()
            cand_upload = cloudinary.uploader.upload(cv2.imencode('.jpg', cand_annotated)[1].tobytes())
            cand_url = cand_upload.get("secure_url")
            save_log(final_id, 999.0, "FAIL", cand_url)
            return {
                "success": True, "decision": "FAIL", "score": "N/A",
                "note": "พิมพ์ตรงกัน แต่ระบบหาขอบรูปทรงไม่เจอ",
                "overlay_url": cand_url, "ref_contour_url": ""
            }

        pstar = auto_pstar_from_contour(ref_cnt, NUM_PSTAR)
        ref_debug = render_debug_view(ref_rgb, ref_edge, pstar, final_id)
        ref_debug_upload = cloudinary.uploader.upload(cv2.imencode('.png', cv2.cvtColor(ref_debug, cv2.COLOR_RGB2BGR))[1].tobytes())
        ref_contour_url = ref_debug_upload.get("secure_url")

        aligned_rgb, _ = align_candidate_to_ref(ref_rgb, ref_cnt, cand_rgb, cand_cnt)
        _, _, _, aligned_edge, aligned_cnt = preprocess_and_contour(aligned_rgb)

        chamfer_score, jaccard = compute_chamfer_score(ref_edge, aligned_edge, 95)
        if not np.isfinite(chamfer_score):
            chamfer_score = 999.0

        ref_gray = to_gray(ref_rgb)
        aligned_gray = to_gray(aligned_rgb)
        ssim_val = compute_ssim_opencv(ref_gray, aligned_gray)

        orb = cv2.ORB_create(nfeatures=ORB_FEATURES)
        kp1, des1 = orb.detectAndCompute(ref_gray, None)
        kp2, des2 = orb.detectAndCompute(aligned_gray, None)
        orb_matches = 0
        if des1 is not None and des2 is not None:
            bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)
            matches = bf.match(des1, des2)
            orb_matches = len(matches)

        if (chamfer_score <= T_PX and ssim_val >= SSIM_THRESH and orb_matches >= ORB_MATCH_THRESH):
            decision = "PASS"
            final_note = f"พิมพ์: {cand_cls} | แท้และเป็นองค์เดียวกัน (SSIM={ssim_val:.2f})"
        else:
            decision = "FAIL"
            final_note = f"พิมพ์: {cand_cls} | พิมพ์ตรง แต่ตำหนิ/พื้นผิวไม่ใช่องค์เดิม"

        nearest_pts = nearest_edge_points(aligned_edge, pstar)
        mask_internal = np.zeros_like(aligned_gray)
        if aligned_cnt is not None:
            cv2.drawContours(mask_internal, [aligned_cnt], -1, 255, thickness=cv2.FILLED)
            mask_internal = cv2.erode(mask_internal, np.ones((10,10), np.uint8), iterations=1)
            
        smooth_gray = cv2.bilateralFilter(aligned_gray, d=9, sigmaColor=75, sigmaSpace=75)
        inner_edges = cv2.Canny(smooth_gray, 30, 90)
        inner_edges = cv2.bitwise_and(inner_edges, inner_edges, mask=mask_internal)
        inner_edges = cv2.dilate(inner_edges, np.ones((2,2), np.uint8), iterations=1)
        
        vis_rgb = aligned_rgb.copy()
        vis_rgb[inner_edges > 0] = [255, 200, 0] 
        if 'kp2' in locals():
            for kp in kp2:
                kx, ky = int(kp.pt[0]), int(kp.pt[1])
                if mask_internal[ky, kx] > 0:
                    cv2.circle(vis_rgb, (kx, ky), 2, (255, 0, 255), -1)

        overlay = make_overlay(
            vis_rgb, aligned_edge, pstar, nearest_pts,
            chamfer_score, decision, f"SSIM={ssim_val:.2f}, ORB={orb_matches}", final_id
        )

        overlay_upload = cloudinary.uploader.upload(cv2.imencode('.png', cv2.cvtColor(overlay, cv2.COLOR_RGB2BGR))[1].tobytes())
        overlay_url = overlay_upload.get("secure_url")
        
        save_log(final_id, chamfer_score, decision, overlay_url)

        return {
            "success": True, "amulet_id": final_id, "score": chamfer_score, "decision": decision,
            "note": final_note, 
            "ref_contour_url": ref_contour_url,
            "overlay_url": overlay_url
        }

    except Exception as e:
        import traceback
        traceback.print_exc()
        return {"success": False, "error_message": f"เซิร์ฟเวอร์ขัดข้อง: {str(e)}"}

# ================= Other APIs =================
@app.get("/api/history")
def api_history(q: str = ""):
    df = load_log_df()
    q = q.strip().lower()
    if q:
        mask = df["amulet_id"].astype(str).str.lower().str.contains(q, na=False)
        df = df[mask].copy()

    df_sorted = df.sort_values("timestamp", ascending=False).reset_index(drop=True)
    count = len(df_sorted)

    gallery = []
    gallery_df = df_sorted.head(24)
    for _, row in gallery_df.iterrows():
        op = str(row.get("overlay_path", "") or "")
        if op: 
            gallery.append({
                "amulet_id": str(row.get("amulet_id", "")),
                "decision": str(row.get("decision", "")),
                "score": float(row.get("score_px", 0.0)) if pd.notna(row.get("score_px")) else 0.0,
                "overlay_path": to_web_overlay_path(op)
            })

    table = []
    for _, row in df_sorted.iterrows():
        score_val = row.get("score_px", "-")
        try:
            if pd.notna(score_val) and score_val != "-":
                score_val = float(score_val)
        except ValueError:
            pass

        table.append({
            "timestamp": str(row.get("timestamp", "")),
            "amulet_id": str(row.get("amulet_id", "")),
            "score_px": score_val,
            "decision": str(row.get("decision", "")),
            "threshold_px": float(row.get("threshold_px", 24.0)) if pd.notna(row.get("threshold_px")) else 24.0,
            "num_pstar": int(row.get("num_pstar", 12)) if pd.notna(row.get("num_pstar")) else 12,
            "scoring_method": str(row.get("scoring_method", "chamfer+ssim+orb")),
            "overlay_path": to_web_overlay_path(str(row.get("overlay_path", "")))
        })

    return {"count": count, "gallery": gallery, "table": table}

@app.post("/api/clear-history")
def api_clear_history():
    try:
        pd.DataFrame(columns=LOG_COLUMNS).to_csv(LOG_CSV, index=False)
        return {"success": True, "message": "ล้างประวัติเรียบร้อย"}
    except Exception as e:
        return {"success": False, "message": f"ไม่สามารถล้างได้: {str(e)}"}

@app.get("/api/download-csv")
def api_download_csv():
    if os.path.exists(LOG_CSV):
        return FileResponse(LOG_CSV, media_type="text/csv", filename="inspection_log.csv")
    return JSONResponse(status_code=404, content={"message": "ยังไม่มีไฟล์ประวัติ"})

@app.post("/api/register")
def api_register(user: UserRegister):
    import re  
    if user.role not in ['buyer', 'seller']:
        return {"success": False, "message": "Role ไม่ถูกต้อง"}
    email_regex = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
    if not re.match(email_regex, user.email):
        return {"success": False, "message": "รูปแบบอีเมลไม่ถูกต้อง กรุณากรอกอีเมลให้ถูกหลัก (เช่น name@gmail.com)"}
    conn = get_db_connection()
    c = conn.cursor()
    try:
        c.execute("SELECT id FROM users WHERE email=%s", (user.email,))
        if c.fetchone():
            return {"success": False, "message": "อีเมลนี้ถูกใช้สมัครไปแล้ว กรุณาใช้อีเมลอื่น"}
        hashed_pw = hash_password(user.password)
        c.execute("INSERT INTO users (username, email, password, role) VALUES (%s, %s, %s, %s)",
                  (user.username, user.email, hashed_pw, user.role))
        conn.commit()
        return {"success": True, "message": "สมัครสมาชิกสำเร็จ! สามารถเข้าสู่ระบบได้เลย"}
    except Exception as e:
        return {"success": False, "message": f"เกิดข้อผิดพลาด: {str(e)}"}
    finally:
        conn.close()

@app.post("/api/login")
def api_login(user: UserLogin):
    conn = get_db_connection()
    c = conn.cursor()
    hashed_pw = hash_password(user.password)
    c.execute("SELECT id, username, role, status FROM users WHERE email=%s AND password=%s", 
              (user.email, hashed_pw))
    row = c.fetchone()
    conn.close()
    if row:
        if row[3] == 'suspended':
            return {"success": False, "message": "บัญชีของคุณถูกระงับ"}
        return {
            "success": True, 
            "message": "เข้าสู่ระบบสำเร็จ!", 
            "user_id": row[0], 
            "username": row[1], 
            "role": row[2]
        }
    else:
        return {"success": False, "message": "อีเมลหรือรหัสผ่านไม่ถูกต้อง"}

@app.get("/api/admin/users")
def api_get_users():
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("SELECT id, username, email, role, status FROM users")
    users = [{"id": row[0], "username": row[1], "email": row[2], "role": row[3], "status": row[4]} for row in c.fetchall()]
    conn.close()
    return {"success": True, "users": users}

@app.post("/api/admin/update-user-status")
def api_update_user_status(user_id: int, status: str):
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("UPDATE users SET status=%s WHERE id=%s", (status, user_id))
    conn.commit()
    conn.close()
    return {"success": True, "message": f"อัปเดตสถานะผู้ใช้ {user_id} เป็น {status} เรียบร้อย"}

@app.get("/api/admin/stats")
def api_get_stats():
    df = load_log_df()
    total_inspections = len(df)
    pass_count = len(df[df["decision"] == "PASS"])
    fail_count = len(df[df["decision"] == "FAIL"])
    return {
        "success": True,
        "stats": {
            "total": total_inspections,
            "pass": pass_count,
            "fail": fail_count
        }
    }

@app.post("/api/amulets/add")
async def api_add_amulet(
    seller_id: int = Form(...),
    name: str = Form(...),
    temple: str = Form(""),
    year: str = Form(""),
    price: float = Form(0.0),
    description: str = Form(""),
    image: UploadFile = File(...)
):
    try:
        upload_result = cloudinary.uploader.upload(image.file)
        image_url = upload_result.get("secure_url")
        conn = get_db_connection()
        c = conn.cursor()
        c.execute('''INSERT INTO amulets (seller_id, name, temple, year, price, image_path, description)
                     VALUES (%s, %s, %s, %s, %s, %s, %s)''', 
                  (seller_id, name, temple, year, price, image_url, description))
        conn.commit()
        conn.close()
        return {"success": True, "message": "ลงประกาศขายพระเครื่องสำเร็จ!"}
    except Exception as e:
        import traceback
        traceback.print_exc()
        return {"success": False, "message": f"เกิดข้อผิดพลาด: {str(e)}"}

@app.get("/api/amulets")
def api_get_amulets():
    try:
        conn = get_db_connection()
        c = conn.cursor()
        try:
            c.execute("ALTER TABLE amulets ADD COLUMN IF NOT EXISTS status TEXT DEFAULT 'available'")
            conn.commit()
        except:
            conn.rollback()
            
        c.execute('''
            SELECT a.id, a.name, a.temple, a.year, a.price, a.image_path, a.description, u.username, a.seller_id, a.status 
            FROM amulets a
            JOIN users u ON a.seller_id = u.id
            ORDER BY a.created_at DESC
        ''')
        rows = c.fetchall()
        conn.close()
        
        amulets = []
        for r in rows:
            amulets.append({
                "id": r[0], "name": r[1], "temple": r[2], "year": r[3], 
                "price": r[4], "image_path": r[5], "description": r[6], 
                "seller_name": r[7], "seller_id": r[8], "status": r[9]
            })
        return {"success": True, "amulets": amulets}
    except Exception as e:
        import traceback
        traceback.print_exc()
        return JSONResponse(status_code=500, content={"success": False, "message": str(e)})

@app.post("/api/amulets/{amulet_id}/sold")
def api_mark_sold(amulet_id: int):
    try:
        conn = get_db_connection()
        c = conn.cursor()
        c.execute("UPDATE amulets SET status = 'sold' WHERE id = %s", (amulet_id,))
        conn.commit()
        conn.close()
        return {"success": True, "message": "อัปเดตสถานะเป็น Sold สำเร็จ!"}
    except Exception as e:
        return {"success": False, "message": str(e)}

@app.delete("/api/amulets/{amulet_id}")
def api_delete_amulet(amulet_id: int, role: str = ""):
    if role != 'admin':
        return {"success": False, "message": "ผู้ขายไม่อนุญาตให้ลบข้อมูลสินค้า เพื่อเก็บไว้เป็นประวัติการซื้อขาย"}
    try:
        conn = get_db_connection()
        c = conn.cursor()
        c.execute("DELETE FROM amulets WHERE id = %s", (amulet_id,))
        conn.commit()
        conn.close()
        return {"success": True, "message": "แอดมินลบรายการพระเครื่องสำเร็จ"}
    except Exception as e:
        return {"success": False, "message": f"เกิดข้อผิดพลาด: {str(e)}"}

@app.get("/api/users")
def get_all_users():
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("SELECT id, username, email, role FROM users ORDER BY id ASC")
    rows = c.fetchall()
    conn.close()
    users_list = []
    for r in rows:
        users_list.append({
            "id": r[0],
            "username": r[1],
            "email": r[2] if r[2] else "-",
            "role": r[3]
        })
    return users_list

@app.delete("/api/users/{user_id}")
def delete_user(user_id: int):
    try:
        conn = get_db_connection()
        c = conn.cursor()
        c.execute("SELECT username, role FROM users WHERE id = %s", (user_id,))
        user_info = c.fetchone()
        if not user_info:
            conn.close()
            return JSONResponse(status_code=404, content={"message": "ไม่พบผู้ใช้งาน"})
        if user_info[1] == 'admin':
            conn.close()
            return JSONResponse(status_code=400, content={"message": "ห้ามลบแอดมิน"})
        c.execute("DELETE FROM users WHERE id = %s", (user_id,))
        conn.commit()
        conn.close()
        return {"success": True, "message": "ลบสำเร็จ"}
    except Exception as e:
        return JSONResponse(status_code=500, content={"message": str(e)})

@app.get("/api/reports/daily-sales")
def api_daily_sales_report():
    try:
        conn = get_db_connection() 
        query = """
            SELECT 
                u.username,
                a.name,
                a.price,
                COALESCE(o.created_at, a.created_at) AS sold_date
            FROM amulets a
            LEFT JOIN orders o ON a.id = o.amulet_id
            JOIN users u ON a.seller_id = u.id
            WHERE a.status = 'sold'
        """
        df = pd.read_sql_query(query, conn)
        conn.close()
        if df.empty:
            return JSONResponse(status_code=404, content={"message": "ยังไม่มีประวัติการขายในระบบ"})
        df['sold_date'] = pd.to_datetime(df['sold_date']) + pd.Timedelta(hours=7)
        df['วันที่ขาย'] = df['sold_date'].dt.date
        df.rename(columns={'username': 'ชื่อผู้ขาย', 'name': 'ชื่อพระเครื่อง', 'price': 'ราคาที่ขายได้ (บาท)'}, inplace=True)
        df = df[['วันที่ขาย', 'ชื่อผู้ขาย', 'ชื่อพระเครื่อง', 'ราคาที่ขายได้ (บาท)']]
        df['ยอดรวมของคนนี้ (บาท)'] = df.groupby('ชื่อผู้ขาย')['ราคาที่ขายได้ (บาท)'].transform('sum')
        report_path = "daily_sales_report.csv"
        df.to_csv(report_path, index=False, encoding='utf-8-sig')
        return FileResponse(report_path, media_type="text/csv", filename="สรุปยอดขายรายวัน.csv")
    except Exception as e:
        return JSONResponse(status_code=500, content={"message": f"เกิดข้อผิดพลาด: {str(e)}"})
    
@app.post("/api/orders/create")
def api_create_order(order: OrderCreate):
    try:
        conn = get_db_connection()
        c = conn.cursor()
        c.execute('''INSERT INTO orders 
                     (amulet_id, buyer_id, buyer_name, buyer_phone, buyer_address, total_amount, status) 
                     VALUES (%s, %s, %s, %s, %s, %s, 'pending')''',
                  (order.amulet_id, order.buyer_id, order.buyer_name, order.buyer_phone, order.buyer_address, order.total_amount))
        c.execute("UPDATE amulets SET status = 'sold' WHERE id = %s", (order.amulet_id,))
        conn.commit()
        conn.close()
        return {"success": True, "message": "สั่งซื้อสำเร็จ! รอผู้ขายจัดส่ง"}
    except Exception as e:
        return {"success": False, "message": f"เกิดข้อผิดพลาด: {str(e)}"}

@app.get("/api/orders/seller/{seller_id}")
def api_get_seller_orders(seller_id: int):
    try:
        conn = get_db_connection()
        c = conn.cursor()
        c.execute('''
            SELECT o.id, a.name, a.price, o.buyer_name, o.buyer_phone, o.buyer_address, o.status, o.created_at, o.amulet_id
            FROM orders o
            JOIN amulets a ON o.amulet_id = a.id
            WHERE a.seller_id = %s
            ORDER BY o.created_at DESC
        ''', (seller_id,))
        rows = c.fetchall()
        conn.close()
        orders = []
        for r in rows:
            orders.append({
                "order_id": r[0],
                "amulet_name": r[1],
                "price": r[2],
                "buyer_name": r[3],
                "buyer_phone": r[4],
                "buyer_address": r[5],
                "status": r[6],
                "created_at": r[7],
                "amulet_id": r[8]
            })
        return {"success": True, "orders": orders}
    except Exception as e:
        return {"success": False, "message": str(e)}

@app.post("/api/orders/{order_id}/update-status")
def api_update_order_status(order_id: int, status: str = Form(...)):
    try:
        conn = get_db_connection()
        c = conn.cursor()
        c.execute("UPDATE orders SET status = %s WHERE id = %s", (status, order_id))
        conn.commit()
        conn.close()
        return {"success": True, "message": f"อัปเดตสถานะการจัดส่งเรียบร้อย!"}
    except Exception as e:
        return {"success": False, "message": str(e)}

# ================= Static File Mounting =================
app.mount("/market_images", StaticFiles(directory="outputs/market_images"), name="market_images")
app.mount("/outputs", StaticFiles(directory="outputs"), name="outputs")
app.mount("/", StaticFiles(directory="static", html=True), name="static")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 3001))
    print(f"Starting Amulet Verification Web Server at http://0.0.0.0:{port} ...")
    uvicorn.run("app:app", host="0.0.0.0", port=port, reload=False)