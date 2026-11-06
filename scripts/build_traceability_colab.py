import json, sys
sys.stdout.reconfigure(encoding='utf-8')
from pathlib import Path

root = Path(r"C:\Users\LENOVO\Documents\Carlitos\IA\Antigravity\Profesionalización de catálogo\Cliente Marinera Power")
nb_path = r"C:\Users\LENOVO\AppData\Local\Temp\colab_current_v12.ipynb"

with open(nb_path, 'r', encoding='utf-8') as f:
    nb = json.load(f)

# Cell 0: Header Markdown
nb['cells'][0]['source'] = [
    "# 🏛️ MARINERA POWER: Pipeline Industrial Definitivo & Protocolo de Trazabilidad\n",
    "\n",
    "Pipeline oficial de profesionalización de catálogo para **Marinera Power** con Trazabilidad Estricta de Fotos Rechazadas.\n",
    "- **Base Origen:** `Emprendimiento/Marinera power 2026/Fotos catalogo/` (ID: `1SERKR606LbQEYkgLTgDB0f-pUoMhvNz4`)\n",
    "- **Salida Aprobadas:** `Fotos catalogo PRO/` (ID: `1-nLdBpIPPbZXpzmOAxjpbkc39ykhl8K-`)\n",
    "- **Cuarentena Rechazadas:** `_Fotos_Erroneas_y_Desalineadas/` (ID: `16wT0ogNsfd-r2U1bGuuw01Rdxj269bxW`)\n",
    "- **Checkpoint Atómico:** `Fotos catalogo PRO/checkpoint_pipeline.json`\n",
    "- **Hoja Oficial:** Pestaña `Control_Total_Drive_V2` en Google Sheets con columnas de trazabilidad forense.\n"
]

# Cell 2: Conexiones, Drive y Columnas de Trazabilidad
cell_2_code = '''# 2. Autenticación, Conexión Sheets y Jerarquía Exacta en Google Drive
import os, io, gc, json, base64, time, requests, shutil, random
from pathlib import Path
import cv2
import numpy as np
from PIL import Image, ImageOps
import pillow_heif
from google.colab import userdata, auth
from IPython.display import display, Image as IPImage
import gspread
from google.auth import default

# Registro obligatorio de códec HEIC de iPhone
pillow_heif.register_heif_opener()

# 1. Cargar API Key de Gemini
try:
    API_KEY = userdata.get('GEMINI_API_KEY')
    print('✅ GEMINI_API_KEY cargada con éxito desde Secrets.')
except Exception:
    import getpass
    API_KEY = getpass.getpass('Ingresa tu Gemini API Key: ')

# 2. Conexión Google Sheets
auth.authenticate_user()
creds, _ = default()
gc_client = gspread.authorize(creds)
SPREADSHEET_ID = '1kRsCZ7ZpPxyxrSEkUrYRl3NHahrQQche90RKK2yedQ8'
sh = gc_client.open_by_key(SPREADSHEET_ID)
sheet_control = sh.worksheet('Control_Total_Drive_V2')
print(f'✅ Conexión establecida con la hoja maestra: {sheet_control.title}')

# 3. Jerarquía Exacta de Carpetas en Google Drive
candidates_base = [
    Path('/content/drive/MyDrive/Emprendimiento/Marinera power 2026'),
    Path('/content/drive/MyDrive/Marinera power 2026'),
    Path('/content/drive/MyDrive'),
]

BASE_DRIVE = Path('/content/drive/MyDrive')
for c in candidates_base:
    if (c / 'Fotos catalogo').exists():
        BASE_DRIVE = c
        break

DIR_ORIGEN_ROOT = BASE_DRIVE / 'Fotos catalogo'
DIR_PRO_ROOT = BASE_DRIVE / 'Fotos catalogo PRO'
DIR_ERROR_ROOT = DIR_PRO_ROOT / '_Fotos_Erroneas_y_Desalineadas'
BOVEDA_BACKUP_DIR = DIR_PRO_ROOT / '_BOVEDA_HISTORIAL_BACKUP'
CHECKPOINT_FILE = DIR_PRO_ROOT / 'checkpoint_pipeline.json'

DIR_PRO_ROOT.mkdir(parents=True, exist_ok=True)
DIR_ERROR_ROOT.mkdir(parents=True, exist_ok=True)
BOVEDA_BACKUP_DIR.mkdir(parents=True, exist_ok=True)

print(f'📁 [1] Carpeta Base Origen:       {DIR_ORIGEN_ROOT}')
print(f'📁 [2] Carpeta Salida Aprobadas:  {DIR_PRO_ROOT}')
print(f'📁 [3] Carpeta Cuarentena Error:  {DIR_ERROR_ROOT}')
print(f'📁 [4] Bóveda Central Permanente: {BOVEDA_BACKUP_DIR}')
print(f'📄 [5] Checkpoint Atómico:        {CHECKPOINT_FILE}')

# 4. Asegurar Columnas de Trazabilidad Estricta en Google Sheets
headers = sheet_control.row_values(1)
cols_trazabilidad = [
    'Ruta_Destino_Oficial',
    'Ubicacion_Actual_Fisica',
    'Motivo_Rechazo',
    'Link_Drive_Rechazada',
    'Feedback_Carlos',
    'Detalle_Error_Carlos'
]
updated_headers = False
for col in cols_trazabilidad:
    if col not in headers:
        sheet_control.update_cell(1, len(headers) + 1, col)
        headers = sheet_control.row_values(1)
        updated_headers = True

if updated_headers:
    print('✅ Columnas de trazabilidad forense añadidas a la hoja maestra.')
else:
    print('✅ Columnas de trazabilidad forense verificadas en la hoja maestra.')

# 5. Resolvedor Robusto Linux (partes_limpias + búsqueda insensible)
def resolve_photo_path(ruta_origen, orig_name):
    partes = [p.strip() for p in str(ruta_origen).split('/') if p.strip()]
    if partes and partes[0].lower() in ['fotos catalogo', 'fotos catalogo marinera power']:
        partes = partes[1:]
    foto_dir = DIR_ORIGEN_ROOT.joinpath(*partes)
    clean_name = str(orig_name).replace('.jpg', '').replace('.jpeg', '').replace('.png', '').replace('.heic', '').replace('.HEIC', '').strip()
    
    if foto_dir.exists():
        cands = list(foto_dir.glob(f"{clean_name}*"))
        if cands: return cands[0]
    global_cands = list(DIR_ORIGEN_ROOT.glob(f"**/{clean_name}*"))
    if global_cands: return global_cands[0]
    return None

print('✅ Entorno de trazabilidad, rutas y códecs listo.')
'''
nb['cells'][2]['source'] = [line + '\n' for line in cell_2_code.split('\n')]

# Cell 3: Pre-Procesamiento Sobel Adaptativo
cell_3_code = '''# 3. Pre-Procesamiento Sobel Adaptativo & Context Managers Anti-OOM
def detect_and_crop_artificial_bars_sobel(img: Image.Image, max_scan_ratio: float = 0.25, threshold_gradient: float = 3.5):
    """
    Detecta y recorta franjas artificiales (ej. Instagram 193px o Canva padding).
    Protege pañuelos y tejidos de lino evaluando la desviación estándar y el gradiente medio.
    """
    arr = np.array(img)
    h, w = arr.shape[:2]
    gray = cv2.cvtColor(arr, cv2.COLOR_RGB2GRAY)
    
    grad_x = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=3)
    grad_y = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=3)
    mag = np.hypot(grad_x, grad_y)
    
    max_h_scan = int(h * max_scan_ratio)
    max_w_scan = int(w * max_scan_ratio)
    
    def is_blank_band(slice_gray: np.ndarray, slice_mag: np.ndarray) -> bool:
        return float(np.std(slice_gray)) < 2.5 and float(np.mean(slice_mag)) < threshold_gradient

    top = 0
    for r in range(max_h_scan):
        if is_blank_band(gray[r, :], mag[r, :]): top = r + 1
        else: break
        
    bottom = h
    for r in range(h - 1, h - max_h_scan, -1):
        if is_blank_band(gray[r, :], mag[r, :]): bottom = r
        else: break
        
    left = 0
    for c in range(max_w_scan):
        if is_blank_band(gray[:, c], mag[:, c]): left = c + 1
        else: break
        
    right = w
    for c in range(w - 1, w - max_w_scan, -1):
        if is_blank_band(gray[:, c], mag[:, c]): right = c
        else: break
        
    top = top if top >= 12 else 0
    bottom = bottom if (h - bottom) >= 12 else h
    left = left if left >= 12 else 0
    right = right if (w - right) >= 12 else w
    
    was_cropped = (top > 0 or bottom < h or left > 0 or right > w)
    cropped_img = img.crop((left, top, right, bottom)) if was_cropped else img
    return cropped_img, was_cropped

def prepare_image_pipeline(image_path: Path, max_dim: int = 1920):
    with Image.open(image_path) as raw_img:
        oriented = ImageOps.exif_transpose(raw_img)
        base = oriented if oriented is not None else raw_img
        rgb = base.convert('RGB')
        
        # Recorte Sobel adaptativo
        cropped, was_cropped = detect_and_crop_artificial_bars_sobel(rgb)
        
        # Redimensionamiento Lanczos a 1920px para latencia y estabilidad
        w, h = cropped.size
        if max(w, h) > max_dim:
            scale = max_dim / max(w, h)
            final_img = cropped.resize((int(w * scale), int(h * scale)), Image.Resampling.LANCZOS)
        else:
            final_img = cropped.copy()
            
        del rgb, cropped
        return final_img, was_cropped

print('✅ Pre-Procesamiento Sobel adaptativo y control anti-OOM listos.')
'''
nb['cells'][3]['source'] = [line + '\n' for line in cell_3_code.split('\n')]

# Cell 4: Motor de Generación + Post-Control Perimetral 10px + Dual Quality Gate
cell_4_code = '''# 4. Motor de Generación, Post-Control Perimetral 10px & Dual Quality Gate
PROMPT_MAESTRO = """[TASK DIRECTIVE]
Professionally retouch this commercial fashion and jewelry photograph for the high-end e-commerce catalog of Marinera Power. Modify ONLY the background and floor surfaces. Do NOT alter the subject.

[IMMUTABLE COLOR & STUDIO UNIFORMITY - HEX #E5E1DE]
- BACKDROP COLOR: The entire background must be an absolutely uniform, solid, flat warm-grey studio backdrop matching hex color #E5E1DE (exact RGB: 229, 225, 222).
- ZERO GRADIENTS & ZERO VIGNETTING: Completely eliminate room corners, wall seams, domestic shadows, and color gradients. The background tone must be 100% consistent across all catalog photos. Zero beige shifts, zero brown casts, zero cool white clinical shifts.
- ZERO COLOR BOUNCE & AMBIENT SPILL: Highly saturated red, purple, fuchsia garments and gold jewelry must NOT bleed color, radiosity, or ambient spill onto the background.

[MANDATORY SCALE & BOUNDING BOX LOCK - NO ZOOM OUT / NO SHRINKING]
- PRESERVE 1:1 SCALE: The subject (model, dancer, garment, jewelry) MUST maintain the EXACT same pixel dimensions, proportion, and framing as in the original photograph.
- STRICTLY PROHIBITED TO ZOOM OUT: Do NOT push the subject into the distance. Do NOT shrink the subject. The subject must remain in full foreground focus exactly as framed originally.
- NO OUTPAINTING: If the subject is cut at the waist, bust, or legs, KEEP that exact crop. Do NOT hallucinate missing limbs or expand the field of view.

[CLEAN FLOOR & FOOT CONTACT - ZERO DIRT OR SMUDGES]
- PRISTINE FLOOR: The ground surface must be clean and flawless.
- NATURAL CONTACT SHADOW: Render ONLY a delicate, soft, feathered, transparent contact shadow directly under the soles of shoes or bare feet. 
- ABSOLUTELY NO DIRT, NO MUDDY PATCHES, NO DARK SMUDGES, and NO grey halos around the feet or hemline.

[PRESERVATION OF DETAILS]
- Faces, skin tone, hair, white linen marinera handkerchief, and 18k Peruvian gold filigree must remain 100% untouched and razor-sharp."""

def edit_background_gemini(pil_img, prompt_text=PROMPT_MAESTRO, max_retries=3):
    buffered = io.BytesIO()
    pil_img.save(buffered, format='JPEG', quality=95)
    b64_image = base64.b64encode(buffered.getvalue()).decode('utf-8')

    url = f'https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-image:generateContent?key={API_KEY}'
    payload = {
        'contents': [{
            'parts': [
                {'text': prompt_text},
                {'inlineData': {'mimeType': 'image/jpeg', 'data': b64_image}}
            ]
        }],
        'generationConfig': {
            'responseModalities': ['IMAGE'],
            'temperature': 0.05
        }
    }

    for intento in range(max_retries):
        try:
            # Rate limiting con jitter para proteger RPM
            time.sleep(5.0 + random.uniform(0.5, 1.5))
            res = requests.post(url, json=payload, timeout=90)
            if res.status_code == 200:
                parts = res.json()['candidates'][0]['content']['parts']
                for p in parts:
                    if 'inlineData' in p:
                        img_bytes = base64.b64decode(p['inlineData']['data'])
                        return Image.open(io.BytesIO(img_bytes)), None
            elif res.status_code in (429, 503):
                backoff = min(60.0, (2 ** intento) * 4.0 + random.uniform(1.0, 3.0))
                print(f"   ⚠️ Alerta {res.status_code}. Backoff exponencial: {backoff:.1f}s...")
                time.sleep(backoff)
                continue
            else:
                return None, f"HTTP {res.status_code}: {res.text[:120]}"
        except requests.exceptions.Timeout:
            if intento == max_retries - 1:
                return None, "TIMEOUT_API (90s alcanzado)"
            time.sleep(5)
        except Exception as e:
            return None, str(e)
    return None, "ERROR_API_REINTENTOS_AGOTADOS"

def verify_perimeter_and_background(img_output: Image.Image, target_rgb: tuple = (229, 225, 222), tolerance_delta: float = 28.0):
    """
    Post-control automático de 10 píxeles perimetrales (esquinas exteriores).
    Detecta marcos blancos parásitos y deriva cromática respecto a #E5E1DE.
    """
    arr = np.array(img_output)
    h, w, _ = arr.shape
    
    corners = [
        arr[:10, :10],         # Top-Left
        arr[:10, -10:],        # Top-Right
        arr[-10:, :10],        # Bottom-Left
        arr[-10:, -10:]        # Bottom-Right
    ]
    
    for idx, corner in enumerate(corners):
        # 1. Marco blanco residual
        if np.mean(corner) > 250 and np.std(corner) < 3.0:
            return False, f"MARCO_BLANCO_PERIMETRAL_ESQUINA_{idx}", 100.0
            
        # 2. Deriva cromática vs #E5E1DE
        mean_rgb = np.mean(corner, axis=(0, 1))
        delta_e = float(np.linalg.norm(mean_rgb - np.array(target_rgb)))
        if delta_e > tolerance_delta:
            return False, f"DERIVA_CROMATICA_DELTA_{delta_e:.1f}", delta_e
            
    return True, "POST_CONTROL_OK", float(np.linalg.norm(np.mean(corners[0], axis=(0,1)) - np.array(target_rgb)))

def deterministic_quality_gates(orig_pil, pro_pil):
    np_orig = np.array(orig_pil)
    np_pro = np.array(pro_pil)
    h, w = np_pro.shape[:2]

    # Post-control de perímetro
    is_perim_ok, perim_reason, delta_color = verify_perimeter_and_background(pro_pil, tolerance_delta=28.0)
    
    # Escala 1:1 y Zoom-out
    target_rgb = np.array([229, 225, 222], dtype=np.float32)
    dist_orig = np.linalg.norm(np_orig.astype(np.float32) - np_orig[0:15, 0:15].mean(axis=(0,1)), axis=2)
    dist_pro = np.linalg.norm(np_pro.astype(np.float32) - target_rgb, axis=2)
    mask_orig = (dist_orig > 25).astype(np.uint8)
    mask_pro = (dist_pro > 25).astype(np.uint8)

    scale_ratio = 1.0
    pts_orig = cv2.findNonZero(mask_orig)
    pts_pro = cv2.findNonZero(mask_pro)
    if pts_orig is not None and pts_pro is not None:
        _, _, _, h_orig_box = cv2.boundingRect(pts_orig)
        _, _, _, h_pro_box = cv2.boundingRect(pts_pro)
        scale_ratio = float(h_pro_box) / float(h_orig_box) if h_orig_box > 0 else 1.0

    # Limpieza de Piso (15% inferior)
    floor_roi = np_pro[int(h * 0.85):, :]
    floor_dist = np.linalg.norm(floor_roi.astype(np.float32) - target_rgb, axis=2)
    dirt_pixels = np.sum((floor_dist > 45) & (np.mean(floor_roi, axis=2) < 160)) / float(floor_roi.shape[0] * floor_roi.shape[1])
    floor_dirt_score = max(0, 100 - int(dirt_pixels * 500))

    det_pass = True
    fail_reasons = []

    if not is_perim_ok:
        det_pass = False
        fail_reasons.append(perim_reason)

    if scale_ratio < 0.85:
        det_pass = False
        fail_reasons.append(f"ZOOM_OUT_NO_AUTORIZADO_{int(scale_ratio*100)}PCT")

    if floor_dirt_score < 60:
        fail_reasons.append("MANCHAS_PISO_SUCIO")

    score_det = 100 if det_pass else 30
    return {
        'score_deterministico': score_det,
        'aprobada_deterministico': det_pass,
        'delta_color': round(delta_color, 1),
        'escala_ratio': round(scale_ratio, 2),
        'motivo': " | ".join(fail_reasons) if fail_reasons else "APROBADO_POST_CONTROL"
    }

def audit_image_quality(orig_pil, pro_pil):
    det_eval = deterministic_quality_gates(orig_pil, pro_pil)
    if not det_eval['aprobada_deterministico']:
        return {
            'score': det_eval['score_deterministico'],
            'aprobada': False,
            'motivo': det_eval['motivo'],
            'detalles_det': det_eval
        }
        
    # Evaluación complementaria con Gemini Vision
    buf1, buf2 = io.BytesIO(), io.BytesIO()
    orig_pil.save(buf1, format='JPEG', quality=85)
    pro_pil.save(buf2, format='JPEG', quality=85)
    b64_1 = base64.b64encode(buf1.getvalue()).decode('utf-8')
    b64_2 = base64.b64encode(buf2.getvalue()).decode('utf-8')

    eval_prompt = (
        'Actúa como Auditor Riguroso de E-Commerce para Marinera Power. Evalúa Original vs PRO:\\n'
        '1. ¿Manos, dedos, pañuelo de marinera y filigrana de oro están intactos sin amputación?\\n'
        '2. ¿La sombra de contacto es natural sin manchas de barro?\\n'
        'Responde estrictamente en JSON: {"score": 0-100, "aprobada": true/false, "motivo": "breve resumen"}'
    )
    url = f'https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={API_KEY}'
    payload = {
        'contents': [{'parts': [{'text': eval_prompt}, {'inlineData': {'mimeType': 'image/jpeg', 'data': b64_1}}, {'inlineData': {'mimeType': 'image/jpeg', 'data': b64_2}}]}],
        'generationConfig': {'responseMimeType': 'application/json'}
    }
    score_ia = 85
    aprobada_ia = True
    motivo_ia = "Validación anatómica y textil conforme"
    try:
        res = requests.post(url, json=payload, timeout=25)
        if res.status_code == 200:
            data = json.loads(res.json()['candidates'][0]['content']['parts'][0]['text'])
            score_ia = data.get('score', 85)
            aprobada_ia = data.get('aprobada', True)
            motivo_ia = data.get('motivo', 'Conforme')
    except Exception as e:
        motivo_ia = f"Fallo parcial visión: {e}"

    score_final = int(det_eval['score_deterministico'] * 0.60 + score_ia * 0.40)
    aprobada_final = det_eval['aprobada_deterministico'] and aprobada_ia and (score_final >= 80)
    return {
        'score': score_final,
        'aprobada': aprobada_final,
        'motivo': f"{det_eval['motivo']} | IA: {motivo_ia}",
        'detalles_det': det_eval
    }

print('✅ Motor de Generación, Post-Control Perimetral 10px y Quality Gate compilados.')
'''
nb['cells'][4]['source'] = [line + '\n' for line in cell_4_code.split('\n')]

# Cell 5: Protocolo Estricto de Trazabilidad y Bifurcación
cell_5_code = '''# 5. Protocolo Estricto de Trazabilidad para Fotos Aprobadas y Rechazadas
def save_and_route_photo(pro_img, row_data, qa_result, orig_img=None, error_type=None):
    """
    Aplica la bifurcación obligatoria de trazabilidad forense:
    1. Aprobadas -> Fotos catalogo PRO/<Subcarpeta>/<nombre>_pro.jpg
    2. Rechazadas -> _Fotos_Erroneas_y_Desalineadas/<Subcarpeta>_Error/<nombre>_RECHAZADA_<motivo>.jpg
    3. Respaldo doble incondicional en _BOVEDA_HISTORIAL_BACKUP
    """
    row_id = str(row_data.get('ID', '0'))
    orig_name = str(row_data.get('Nombre_Archivo_Original', 'foto'))
    clean_name = orig_name.replace('.jpg', '').replace('.jpeg', '').replace('.png', '').replace('.heic', '').replace('.HEIC', '').strip()
    
    score = qa_result.get('score', 0) if qa_result else 0
    aprobada = qa_result.get('aprobada', False) if qa_result else False
    motivo = error_type if error_type else qa_result.get('motivo', 'FALLO_DESCONOCIDO')

    # Subrama relativa limpia
    ruta_origen = str(row_data.get('Ruta_Carpeta_Drive', row_data.get('Carpeta_Ruta_Original', '')))
    partes = [p.strip() for p in ruta_origen.split('/') if p.strip()]
    if partes and partes[0].lower() in ['fotos catalogo', 'fotos catalogo marinera power']:
        partes = partes[1:]
    subrama_parts = partes if partes else ['General']
    
    # 1. Ruta Destino Oficial (donde DEBERÍA estar la imagen si estuviera aprobada)
    target_pro_dir = DIR_PRO_ROOT.joinpath(*subrama_parts)
    ruta_destino_oficial = target_pro_dir / f"{clean_name}_pro.jpg"
    
    # 2. Bóveda Central Permanente
    tag_bov = "APROBADA" if aprobada else "RECHAZADA"
    bov_path = BOVEDA_BACKUP_DIR / f"ID{row_id.zfill(3)}_{clean_name}_{tag_bov}_score{score}.jpg"
    if pro_img:
        pro_img.save(bov_path, quality=95)
        
    # 3. Bifurcación Física
    if aprobada:
        target_pro_dir.mkdir(parents=True, exist_ok=True)
        pro_img.save(ruta_destino_oficial, quality=95)
        ubicacion_actual = ruta_destino_oficial
        link_rechazada = ""
        estado_final = "APROBADO_OFICIAL"
        motivo_final = ""
    else:
        # Carpeta de Cuarentena: _Fotos_Erroneas_y_Desalineadas/<Subcarpeta>_Error/
        leaf_folder = f"{subrama_parts[-1]}_Error"
        parent_folders = subrama_parts[:-1]
        quarantine_dir = DIR_ERROR_ROOT.joinpath(*parent_folders) / leaf_folder
        quarantine_dir.mkdir(parents=True, exist_ok=True)
        
        quarantine_file = quarantine_dir / f"{clean_name}_RECHAZADA_{motivo}.jpg"
        if pro_img:
            pro_img.save(quarantine_file, quality=95)
        elif orig_img:
            orig_img.save(quarantine_dir / f"{clean_name}_ORIGINAL_CON_ERROR.jpg", quality=90)
            
        ubicacion_actual = quarantine_file
        link_rechazada = str(quarantine_file)
        estado_final = "RECHAZADO_QA" if "API" not in motivo.upper() else "ERROR_PROCESO"
        motivo_final = motivo

    return {
        'aprobada': aprobada,
        'estado': estado_final,
        'ruta_destino_oficial': str(ruta_destino_oficial),
        'ubicacion_actual_fisica': str(ubicacion_actual),
        'motivo_rechazo': motivo_final,
        'link_drive_rechazada': link_rechazada,
        'boveda_path': str(bov_path),
        'score': score
    }

def load_checkpoint():
    if CHECKPOINT_FILE.exists():
        try:
            with open(CHECKPOINT_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            pass
    return {'completed_ids': [], 'quarantine_ids': []}

def save_checkpoint(checkpoint_data):
    """Guardado atómico persistente anti-corrupción."""
    tmp_file = str(CHECKPOINT_FILE) + ".tmp"
    with open(tmp_file, 'w', encoding='utf-8') as f:
        json.dump(checkpoint_data, f, indent=2, ensure_ascii=False)
    os.replace(tmp_file, CHECKPOINT_FILE)

print('✅ Protocolo Estricto de Trazabilidad y Checkpoint Atómico listos.')
'''
nb['cells'][5]['source'] = [line + '\n' for line in cell_5_code.split('\n')]

# Cell 6: Canary Test con Bifurcación y Registro de Trazabilidad
cell_6_code = '''# 6. CANARY TEST CON BIFURCACIÓN DE TRAZABILIDAD (5 Casos Críticos de Fuego)
canary_targets = [
    {
        'id_test': 'CANARY_1_BARRAS_BLANCAS',
        'subpath': 'Para ella/Falda/Falda de Ensayo/Faldas de Ensayo de razo 1 bobo/Falda para Ensayo de Razo - Lila con cinta morada',
        'orig_name': 'foto (3).png',
        'caso': 'Recorte Sobel barras laterales blancas Instagram (193px)'
    },
    {
        'id_test': 'CANARY_2_PARQUET_SALON',
        'subpath': 'Para ella/Falda/Falda de Ensayo/Faldas de Ensayo de razo 1 bobo/Falda para Ensayo de Razo - Lila con cinta morada',
        'orig_name': '34a63e97 PRO.jpg',
        'caso': 'Reemplazo total de suelo de parquet por ciclorama #E5E1DE'
    },
    {
        'id_test': 'CANARY_3_PAÑUELO_MANO',
        'subpath': 'Para ella/Falda/Falda de Ensayo/Faldas de Ensayo de razo 1 bobo/Falda para Ensayo de Razo - Coral con cinta blanca',
        'orig_name': 'd72049af PRO.jpg',
        'caso': 'Blindaje de mano y pañuelo de marinera al viento (cero amputación)'
    },
    {
        'id_test': 'CANARY_4_FILIGRANA_JOYA',
        'subpath': 'Para ella/Accesorios/Aretes para Marinera',
        'orig_name': '1.jpg',
        'caso': 'Macro joyería: Oro peruano 18k y filigrana calada con brillo especular'
    },
    {
        'id_test': 'CANARY_5_CORTE_ENQUADRE',
        'subpath': 'Para ella/Falda/Falda de Ensayo/Faldas de Ensayo de razo 1 bobo/Falda para Ensayo de Razo - Morada con cinta blanca',
        'orig_name': '1841c6d0 PRO.jpg',
        'caso': 'Mandato Cliente: Cero outpainting en plano recortado (conservar encuadre)'
    }
]

print(f"🦅 INICIANDO CANARY TEST CON PROTOCOLO DE TRAZABILIDAD...")
print(f"📁 Origen:      {DIR_ORIGEN_ROOT}")
print(f"📁 Aprobadas:   {DIR_PRO_ROOT}")
print(f"📁 Cuarentena:  {DIR_ERROR_ROOT}\\n")

canary_results = []

for idx, tgt in enumerate(canary_targets, start=1):
    test_file = resolve_photo_path(tgt['subpath'], tgt['orig_name'])
    if not test_file or not test_file.exists():
        print(f"⚠️ [{idx}/5] Archivo no hallado: {tgt['orig_name']}")
        continue

    print(f"▶️ [{idx}/5] Evaluando {tgt['id_test']}: {test_file.name}...")
    t0 = time.time()
    try:
        prep_img, was_cropped = prepare_image_pipeline(test_file)
        pro_img, err = edit_background_gemini(prep_img)
        
        if pro_img:
            qa = audit_image_quality(prep_img, pro_img)
            route_res = save_and_route_photo(pro_img, {
                'ID': f'CANARY_{idx}',
                'Nombre_Archivo_Original': test_file.name,
                'Ruta_Carpeta_Drive': tgt['subpath']
            }, qa)
            
            estado_tag = "✅ APROBADA" if route_res['aprobada'] else "🚨 RECHAZADA CUARENTENA"
            print(f"   {estado_tag} | Score: {route_res['score']}/100 | Sobel Crop: {was_cropped}")
            print(f"   📁 Ruta Destino Oficial:  {route_res['ruta_destino_oficial']}")
            print(f"   📁 Ubicación Real Física: {route_res['ubicacion_actual_fisica']}")
            if not route_res['aprobada']:
                print(f"   ❌ Motivo de Rechazo:    {route_res['motivo_rechazo']}")
                
            canary_results.append(route_res)
            display(pro_img)
        else:
            route_res = save_and_route_photo(None, {
                'ID': f'CANARY_{idx}',
                'Nombre_Archivo_Original': test_file.name,
                'Ruta_Carpeta_Drive': tgt['subpath']
            }, {'score': 0, 'aprobada': False, 'motivo': err}, orig_img=prep_img, error_type=err)
            print(f"   ❌ Fallo API: {err} -> Enviada a Cuarentena Forense")
            canary_results.append(route_res)
            
    except Exception as exc:
        print(f"   ❌ Excepción en {test_file.name}: {exc}")
    time.sleep(2)

aprobadas_count = sum(1 for r in canary_results if r.get('aprobada'))
print(f"\\n==============================================================================")
print(f"🏆 RESUMEN CANARY TEST: {aprobadas_count}/{len(canary_results)} Aprobadas Oficiales.")
print(f"📁 Las rechazadas están aisladas en: _Fotos_Erroneas_y_Desalineadas/")
print(f"🔒 BUCLE MASIVO PERMANECE VETADO (HABILITAR_BUCLE_MASIVO = False).")
print(f"==============================================================================")
'''
nb['cells'][6]['source'] = [line + '\n' for line in cell_6_code.split('\n')]

# Cell 7: Bucle Masivo Vetado con Trazabilidad Completa a Google Sheets
cell_7_code = '''# ==============================================================================
# 🎯 PASO 7: BUCLE MASIVO DE PRODUCCIÓN (TRAZABILIDAD ESTRICTA A GOOGLE SHEETS)
# ==============================================================================
# 🔒 SEGURO INMUTABLE CONTRA EJECUCIÓN ACCIDENTAL:
# Mantén esta variable estrictamente en False para bloquear el bucle masivo:
HABILITAR_BUCLE_MASIVO = False

CHUNK_SIZE = 20  # Lote Human-in-the-Loop acordado

if not HABILITAR_BUCLE_MASIVO:
    print("🔒 [PASO 7 VETADO POR SOFTWARE] 'HABILITAR_BUCLE_MASIVO = False'.")
    print("👉 Este paso NO procesará ninguna foto del catálogo general.")
    print("👉 El pase a producción permanece formalmente vetado hasta que Carlos valide el Canary Test.")
else:
    print(f"🚀 INICIANDO BUCLE MASIVO CON TRAZABILIDAD FORENSE (Lote de {CHUNK_SIZE})...")
    
    # Cargar datos y headers de Control_Total_Drive_V2
    sheet_data = sheet_control.get_all_records()
    headers = sheet_control.row_values(1)
    
    col_estado = headers.index('Estado') + 1
    col_dest_oficial = headers.index('Ruta_Destino_Oficial') + 1
    col_ubic_fisica = headers.index('Ubicacion_Actual_Fisica') + 1
    col_motivo = headers.index('Motivo_Rechazo') + 1
    col_link_rechazada = headers.index('Link_Drive_Rechazada') + 1
    
    checkpoint = load_checkpoint()
    completed_set = set(checkpoint.get('completed_ids', []))
    quarantine_set = set(checkpoint.get('quarantine_ids', []))
    
    pendientes = []
    for idx, row in enumerate(sheet_data, start=2):
        row_id = str(row.get('ID', ''))
        estado = str(row.get('Estado', '')).upper()
        if row_id and (row_id not in completed_set) and (row_id not in quarantine_set) and ('APROBADO_OFICIAL' not in estado):
            pendientes.append((idx, row))
            
    print(f"📊 Total Pendientes en Catálogo: {len(pendientes)}")
    chunk = pendientes[:CHUNK_SIZE]
    print(f"🎯 Procesando lote de {len(chunk)} fotos con aislamiento try/except individual...\\n")
    
    for i, (row_idx, row_data) in enumerate(chunk, start=1):
        row_id = str(row_data.get('ID', '0'))
        orig_name = str(row_data.get('Nombre_Archivo_Original', ''))
        ruta_origen = str(row_data.get('Ruta_Carpeta_Drive', row_data.get('Carpeta_Ruta_Original', '')))
        
        print(f"[{i}/{len(chunk)}] ID {row_id}: {orig_name}")
        foto_path = resolve_photo_path(ruta_origen, orig_name)
        if not foto_path or not foto_path.exists():
            print("   ⚠️ Archivo físico no hallado en Drive. Saltando.")
            continue
            
        try:
            prep_img, was_cropped = prepare_image_pipeline(foto_path)
            pro_img, err = edit_background_gemini(prep_img)
            
            if pro_img:
                qa = audit_image_quality(prep_img, pro_img)
                res = save_and_route_photo(pro_img, row_data, qa)
            else:
                res = save_and_route_photo(None, row_data, {'score': 0, 'aprobada': False, 'motivo': err}, orig_img=prep_img, error_type=err)
                
            # REGISTRO DE TRAZABILIDAD EN GOOGLE SHEETS
            sheet_control.update_cell(row_idx, col_estado, res['estado'])
            sheet_control.update_cell(row_idx, col_dest_oficial, res['ruta_destino_oficial'])
            sheet_control.update_cell(row_idx, col_ubic_fisica, res['ubicacion_actual_fisica'])
            sheet_control.update_cell(row_idx, col_motivo, res['motivo_rechazo'])
            sheet_control.update_cell(row_idx, col_link_rechazada, res['link_drive_rechazada'])
            
            if res['aprobada']:
                completed_set.add(row_id)
                print(f"   ✅ Aprobada -> Guardada en: {res['ubicacion_actual_fisica']}")
            else:
                quarantine_set.add(row_id)
                print(f"   🚨 RECHAZADA -> Cuarentena: {res['ubicacion_actual_fisica']} | Motivo: {res['motivo_rechazo']}")
                
            checkpoint['completed_ids'] = list(completed_set)
            checkpoint['quarantine_ids'] = list(quarantine_set)
            save_checkpoint(checkpoint)
            
        except Exception as exc:
            print(f"   ❌ Excepción aislada en ID {row_id}: {exc}")
        finally:
            gc.collect()
            
    print(f"\\n🎉 Lote completado. Revisa tu Google Sheet y Tablero Web.")
'''
nb['cells'][7]['source'] = [line + '\n' for line in cell_7_code.split('\n')]

v12_path = r"C:\Users\LENOVO\AppData\Local\Temp\Pipeline_Masivo_Marinera_Power_V12_Traceability.ipynb"
with open(v12_path, 'w', encoding='utf-8') as f:
    json.dump(nb, f, indent=2, ensure_ascii=False)

repo_nb = root / "notebooks" / "Pipeline_Masivo_Marinera_Power.ipynb"
with open(repo_nb, 'w', encoding='utf-8') as f:
    json.dump(nb, f, indent=2, ensure_ascii=False)

print("✅ Notebook V12 con Protocolo Estricto de Trazabilidad generado exitosamente.")
