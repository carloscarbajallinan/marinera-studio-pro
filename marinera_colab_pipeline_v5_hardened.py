"""
MARINERA POWER - PIPELINE INDUSTRIAL V5.1 HARDENED (DEFINITIVO)
Arquitectura de 3 Niveles + Clasificador Jerárquico + Detector Anti-Zoom-Out ORB/RANSAC + Drive API v3
"""


# ============================================================
# CELDA 1
# ============================================================
# 1. Montar Google Drive & Dependencias Industriales
from google.colab import drive
drive.mount('/content/drive')

!pip install --quiet pillow pillow-heif gspread google-auth opencv-python-headless requests
print('✅ Google Drive montado y dependencias industriales (Pillow + HEIF + OpenCV) listas.')


# ============================================================
# CELDA 2
# ============================================================
# 2. Autenticación, Conexión Sheets y Cargador Infalible Dual de Imágenes
import os, io, gc, json, time, shutil, re
from pathlib import Path
from PIL import Image, ImageOps
import pillow_heif
import requests
import gspread
from google.colab import auth, userdata
from google.auth import default

pillow_heif.register_heif_opener()
Image.MAX_IMAGE_PIXELS = None

# API Key de Gemini desde Colab Secrets
try:
    API_KEY = userdata.get('GEMINI_API_KEY')
    print('✅ GEMINI_API_KEY cargada con éxito desde Secrets.')
except Exception:
    API_KEY = os.environ.get('GEMINI_API_KEY', '')
    if not API_KEY:
        raise ValueError('❌ GEMINI_API_KEY no encontrada en Secrets ni en variables de entorno.')

# Autenticación en Google Sheets & Drive API con credenciales Colab
auth.authenticate_user()
creds, _ = default()
gc_client = gspread.authorize(creds)

SHEET_ID = '1kRsCZ7ZpPxyxrSEkUrYRl3NHahrQQche90RKK2yedQ8'
sh = gc_client.open_by_key(SHEET_ID)

# 1. HOJA MAESTRA DE PRODUCCIÓN (863 registros limpios, nunca contaminada por tests)
TAB_MAESTRO = 'Control_Total_Drive_V2'
sheet_maestro = sh.worksheet(TAB_MAESTRO)

# 2. HOJA SANDBOX DE PRUEBAS (Bitácora acumulativa append-only de experimentos)
TAB_SANDBOX = 'Registro_Pruebas_Sandbox'
sheet_sandbox = sh.worksheet(TAB_SANDBOX)

print(f'✅ Conexión establecida con Catálogo Maestro: {TAB_MAESTRO}')
print(f'✅ Conexión establecida con Sandbox de Pruebas:  {TAB_SANDBOX}')

# IDENTIFICADORES MAESTROS DE CARPETAS EN GOOGLE DRIVE
FOLDER_ID_1_RAW_GEMINI = '16sEwryiHyamyhS8Whkkj89f-2DK_X528'
FOLDER_ID_2_MESA_REVISION = '1AamSIqeYU1hHQ8MXhjAPfvEm4jtlMjAY'
FOLDER_ID_3_CATALOGO_FINAL = '1R4sjNWRuh1N_go2SFH3Ld-cM1ql9UZW3'

# RESOLUCIÓN DINÁMICA DE LA RUTA EN GOOGLE DRIVE
candidates_base = [
    Path('/content/drive/MyDrive/Emprendimiento/Marinera power 2026'),
    Path('/content/drive/MyDrive/Marinera power 2026'),
    Path('/content/drive/MyDrive')
]
BASE_DRIVE = candidates_base[0]
for c in candidates_base:
    if (c / 'Fotos catalogo').exists():
        BASE_DRIVE = c
        break

DIR_CRUDAS = BASE_DRIVE / 'Fotos catalogo'
DIR_PRO_ROOT = BASE_DRIVE / 'Fotos catalogo PRO'

DIR_1_RAW_GEMINI = DIR_PRO_ROOT / '_1_RAW_GEMINI'
DIR_2_MESA_REVISION = DIR_PRO_ROOT / '_2_MESA_REVISION_CARLOS'
DIR_3_CATALOGO_FINAL = DIR_PRO_ROOT / '_3_CATALOGO_FINAL_APROBADO'
LEDGER_FILE = DIR_PRO_ROOT / '_PERMANENT_TRANSACTION_LEDGER.jsonl'

LOCAL_SCRATCH = Path('/content/local_scratch')
LOCAL_SCRATCH.mkdir(parents=True, exist_ok=True)

for d in [DIR_1_RAW_GEMINI, DIR_2_MESA_REVISION, DIR_3_CATALOGO_FINAL]:
    d.mkdir(parents=True, exist_ok=True)

def sanitize_safe_filename(name_str):
    clean = re.sub(r'[\\/*?:"<>|]', '_', str(name_str).strip())
    return re.sub(r'\s+', '_', clean)[:80]

def resolve_file_from_sheet_row(row_data):
    """
    Localizador determinista FUSE sin espacios en separadores de carpetas.
    """
    ruta_origen = str(row_data.get('Ruta_Carpeta_Drive', ''))
    file_name = str(row_data.get('Nombre_Archivo_Original', '')).strip()
    base_stem = Path(file_name).stem.strip()

    partes = [p.strip() for p in ruta_origen.replace('\\', '/').split('/') if p.strip()]
    if partes and partes[0].lower() in ['fotos catalogo', 'fotos catalogo marinera power', 'fotos catalogo pro']:
        partes = partes[1:]

    folder_candidates = [
        DIR_CRUDAS.joinpath(*partes),
        BASE_DRIVE.joinpath('Fotos catalogo', *partes),
        BASE_DRIVE.joinpath(*partes)
    ]
    
    for folder in folder_candidates:
        if folder.exists():
            exact = folder / file_name
            if exact.exists(): return exact
            for ext in ['.jpg', '.JPG', '.jpeg', '.JPEG', '.png', '.PNG', '.heic', '.HEIC', '.heif', '.HEIF']:
                with_ext = folder / f'{file_name}{ext}'
                if with_ext.exists(): return with_ext
            for entry in folder.iterdir():
                if entry.is_file() and (entry.stem == base_stem or entry.stem.startswith(base_stem)):
                    return entry
    return None

def load_source_image_infallible(row_data, auth_creds):
    """
    MOTOR DUAL INFALIBLE DE CARGA:
    1. Busca primero en FUSE local con normalización de rutas.
    2. Si FUSE falla por latencia o caché, descarga directamente por su Google Drive File ID.
    """
    p = resolve_file_from_sheet_row(row_data)
    if p and p.exists():
        try:
            with Image.open(p) as img:
                return ImageOps.exif_transpose(img).convert('RGB'), f'FUSE Local ({p.name})'
        except Exception:
            pass
            
    orig_id = str(row_data.get('ID_Archivo_Original', '')).strip()
    if orig_id and orig_id != '-' and auth_creds:
        try:
            if hasattr(auth_creds, 'valid') and not auth_creds.valid and hasattr(auth_creds, 'refresh'):
                from google.auth.transport.requests import Request
                auth_creds.refresh(Request())
            headers = {'Authorization': f'Bearer {auth_creds.token}'}
            url = f'https://www.googleapis.com/drive/v3/files/{orig_id}?alt=media'
            res = requests.get(url, headers=headers, timeout=45)
            if res.status_code == 200:
                with Image.open(io.BytesIO(res.content)) as img:
                    return ImageOps.exif_transpose(img).convert('RGB'), f'Drive API Directo (ID {orig_id[:8]}...)'
        except Exception as e:
            return None, f'Fallo Drive API: {e}'
            
    return None, 'No hallado en FUSE ni por Drive ID'

def sync_and_resolve_drive_file_id(local_path, folder_id, auth_creds):
    """
    Resuelve el ID de Google Drive de forma infalible evitando duplicados FUSE vs API:
    1. Espera brevemente y consulta Drive API por su nombre en la carpeta (ordenando por modifiedTime desc).
    2. Solo si tras 2 intentos FUSE no lo ha indexado, lo sube vía Drive API v3 (multipart).
    Retorna (drive_id, web_view_link).
    """
    try:
        if hasattr(auth_creds, 'valid') and not auth_creds.valid and hasattr(auth_creds, 'refresh'):
            from google.auth.transport.requests import Request
            auth_creds.refresh(Request())
        headers = {'Authorization': f'Bearer {auth_creds.token}'}
        
        filename = Path(local_path).name
        q = f"'{folder_id}' in parents and name = '{filename}' and trashed = false"
        q_url = f"https://www.googleapis.com/drive/v3/files?q={requests.utils.quote(q)}&orderBy=modifiedTime desc&fields=files(id,webViewLink,modifiedTime)"
        
        for wait_s in (0.3,):
            time.sleep(wait_s)
            q_res = requests.get(q_url, headers=headers, timeout=20)
            if q_res.status_code == 200:
                files = q_res.json().get('files', [])
                if files:
                    return files[0].get('id'), files[0].get('webViewLink')
                
        meta = {'name': filename, 'parents': [folder_id]}
        with open(local_path, 'rb') as f_bytes:
            files_payload = {
                'data': ('metadata', json.dumps(meta), 'application/json; charset=UTF-8'),
                'file': (filename, f_bytes, 'image/jpeg')
            }
            up_url = 'https://www.googleapis.com/upload/drive/v3/files?uploadType=multipart&fields=id,webViewLink'
            up_res = requests.post(up_url, headers=headers, files=files_payload, timeout=45)
            if up_res.status_code in (200, 201):
                f_data = up_res.json()
                return f_data.get('id'), f_data.get('webViewLink')
            else:
                print(f"   ⚠️ Upload Drive API status {up_res.status_code}: {up_res.text[:100]}")
    except Exception as e:
        print(f"   ⚠️ Excepción sincronizando Drive API: {e}")
    return None, None

print(f'📁 [Base Drive Detectada]:          {BASE_DRIVE}')
print(f'📁 [Origen Crudas]:                 {DIR_CRUDAS} (Existe: {DIR_CRUDAS.exists()})')
print(f'📁 [Mesa de Revisión Carlos]:       {DIR_2_MESA_REVISION}')
print(f'📁 [Catálogo Final Aprobado]:       {DIR_3_CATALOGO_FINAL}')


# ============================================================
# CELDA 3
# ============================================================
# 3. Plan de Normalización en Python (Pre-Gemini: Recorte Exacto de Barras Blancas | Post-Gemini: Alineación SIFT 1:1)
import numpy as np
import cv2

# Interruptor configurable: si es True, recorta automáticamente barras blancas de capturas antes de enviar a Gemini.
APLICAR_RECORTE_BARRAS_BLANCAS = True
# Interruptor configurable: si es True, re-encuadra con Python (SIFT+RANSAC) cuando Gemini aleja a la persona (zoom-out).
APLICAR_ALINEACION_SIFT_PYTHON = True

def detect_and_crop_artificial_borders(pil_img, tipo_prod='MODA_MODELO'):
    """
    FASE 1 DE NORMALIZACIÓN PYTHON (PRE-GEMINI):
    Recorta únicamente franjas blancas puras (promedio > 248 y gradiente Sobel percentil 90 < 6.0)
    desde el borde exterior hacia adentro y se detiene (break) en el primer píxel real de la foto,
    evitando cortar manos o faldas y soportando barras laterales de hasta 25% de ancho (ej. foto (3).png).
    """
    if not APLICAR_RECORTE_BARRAS_BLANCAS or tipo_prod == 'JOYERIA_ACCESORIO':
        return pil_img, '0px (Sin recorte)'
    cv_img = np.array(pil_img.convert('RGB'))
    gray = cv2.cvtColor(cv_img, cv2.COLOR_RGB2GRAY)
    h, w = gray.shape
    sobel_x = np.abs(cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=3))
    sobel_y = np.abs(cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=3))
    grad = np.maximum(sobel_x, sobel_y)

    max_crop_h = int(h * 0.22)
    max_crop_w = int(w * 0.25)
    top, bottom, left, right = 0, h, 0, w

    for y in range(max_crop_h):
        if np.mean(gray[y, :]) > 248 and np.percentile(grad[y, :], 90) < 6.0: top = y + 1
        else: break
    for y in range(h - 1, h - 1 - max_crop_h, -1):
        if np.mean(gray[y, :]) > 248 and np.percentile(grad[y, :], 90) < 6.0: bottom = y
        else: break
    for x in range(max_crop_w):
        if np.mean(gray[:, x]) > 248 and np.percentile(grad[:, x], 90) < 6.0: left = x + 1
        else: break
    for x in range(w - 1, w - 1 - max_crop_w, -1):
        if np.mean(gray[:, x]) > 248 and np.percentile(grad[:, x], 90) < 6.0: right = x
        else: break

    total_px = top + (h - bottom) + left + (w - right)
    if total_px < 6 or (bottom - top) < int(h * 0.6) or (right - left) < int(w * 0.5):
        return pil_img, '0px (Sin barras blancas)'
    cropped = pil_img.crop((left, top, right, bottom))
    return cropped, f'{total_px}px (L:{left},R:{w-right},T:{top},B:{h-bottom})'

def prepare_image_for_gemini(pil_img, tipo_prod='MODA_MODELO', max_side=1920):
    cleaned, crop_note = detect_and_crop_artificial_borders(pil_img, tipo_prod=tipo_prod)
    w, h = cleaned.size
    if max(w, h) > max_side:
        ratio = max_side / float(max(w, h))
        new_size = (int(w * ratio), int(h * ratio))
        return cleaned.resize(new_size, Image.Resampling.LANCZOS), crop_note
    return cleaned, crop_note

def normalize_and_align_pro_sift(orig_pil, pro_pil, tipo_prod='MODA_MODELO'):
    """
    FASE 2 DE NORMALIZACIÓN PYTHON (POST-GEMINI):
    Escala isotrópicamente por altura (cero deformación horizontal) y utiliza puntos clave SIFT
    (invariantes a escala) + RANSAC para re-encuadrar automáticamente la imagen PRO exactamente
    al tamaño y posición 1:1 de la imagen original (sin gastar otra llamada a la API).
    """
    orig_rgb = np.array(orig_pil.convert('RGB'))
    oh, ow = orig_rgb.shape[:2]
    pro_rgb = np.array(pro_pil.convert('RGB'))
    ph, pw = pro_rgb.shape[:2]

    scale_h = oh / float(ph)
    pw_iso = int(round(pw * scale_h))
    pro_iso = cv2.resize(pro_rgb, (pw_iso, oh), interpolation=cv2.INTER_LANCZOS4)

    if not APLICAR_ALINEACION_SIFT_PYTHON:
        pro_res = cv2.resize(pro_rgb, (ow, oh), interpolation=cv2.INTER_LANCZOS4)
        return Image.fromarray(pro_res), 1.0, 'Sin re-encuadre SIFT'

    try:
        g1 = cv2.cvtColor(orig_rgb, cv2.COLOR_RGB2GRAY)
        g2 = cv2.cvtColor(pro_iso, cv2.COLOR_RGB2GRAY)

        best_inl = 0
        best_zf = 1.0
        best_p_pro = None
        best_p_orig = None
        best_method = 'SIFT'

        for m_name, det, norm, ratio in [
            ('SIFT', cv2.SIFT_create(nfeatures=6000, contrastThreshold=0.015), cv2.NORM_L2, 0.76),
            ('ORB', cv2.ORB_create(nfeatures=6000), cv2.NORM_HAMMING, 0.78)
        ]:
            kp_pro, des_pro = det.detectAndCompute(g2, None)
            kp_orig, des_orig = det.detectAndCompute(g1, None)
            if des_pro is None or des_orig is None or len(kp_pro) < 10 or len(kp_orig) < 10:
                continue
            raw_matches = cv2.BFMatcher(norm).knnMatch(des_pro, des_orig, k=2)
            good = [m for m, n in (p for p in raw_matches if len(p) == 2) if m.distance < ratio * n.distance]
            if len(good) < 10:
                continue
            pts_pro = np.float32([kp_pro[m.queryIdx].pt for m in good]).reshape(-1, 1, 2)
            pts_orig = np.float32([kp_orig[m.trainIdx].pt for m in good]).reshape(-1, 1, 2)
            M, inliers = cv2.estimateAffinePartial2D(pts_pro, pts_orig, method=cv2.RANSAC, ransacReprojThreshold=6.0)
            if M is not None and inliers is not None:
                n_inl = int(np.sum(inliers))
                zf = float(np.sqrt(M[0, 0] ** 2 + M[1, 0] ** 2))
                if n_inl >= 10 and n_inl > best_inl and (0.50 <= zf <= 2.85):
                    best_inl = n_inl
                    best_zf = zf
                    best_method = m_name
                    inl_mask = inliers.ravel() == 1
                    best_p_pro = pts_pro[inl_mask].reshape(-1, 2)
                    best_p_orig = pts_orig[inl_mask].reshape(-1, 2)

        if best_p_pro is None:
            pro_res = cv2.resize(pro_rgb, (ow, oh), interpolation=cv2.INTER_LANCZOS4)
            return Image.fromarray(pro_res), 1.0, 'Escala nativa 1:1 (Sin desvío detectado)'

        escala_sujeto_gemini = round(1.0 / best_zf, 3) if best_zf > 0 else 1.0
        tx, ty = np.median(best_p_orig - best_zf * best_p_pro, axis=0)
        M_pure = np.array([[best_zf, 0.0, tx], [0.0, best_zf, ty]], dtype=np.float32)
        aligned = cv2.warpAffine(pro_iso, M_pure, (ow, oh), flags=cv2.INTER_LANCZOS4, borderMode=cv2.BORDER_REPLICATE)
        return Image.fromarray(aligned), 1.0, f'Normalizado {best_method} 1:1 Isótropo ({escala_sujeto_gemini}x -> 1.00x)'
    except Exception as e:
        pro_res = cv2.resize(pro_rgb, (ow, oh), interpolation=cv2.INTER_LANCZOS4)
        return Image.fromarray(pro_res), 1.0, f'Aviso SIFT: {e}'

print('✅ Plan de Normalización Python (Pre-Gemini Sobel Exacto + Post-Gemini SIFT/ORB 1:1) compilado.')


# ============================================================
# CELDA 4
# ============================================================
# 4. Motor de Prompts Condicionales Jerárquico + Auditoría QA OpenCV
import numpy as np
import cv2
import base64
import requests

# PROMPT TIPO A: JOYERÍA, ACCESORIOS Y FOTOPRODUCTO (STILL LIFE / MACRO)
PROMPT_JOYERIA_ACCESORIOS = """Eres un retocador profesional de alta gama de joyería tradicional, orfebrería y accesorios. Edita esta fotografía cambiando ÚNICAMENTE el fondo circundante. El producto (arete, collar, escapulario, joya de filigrana, faja, cinta o accesorio) debe permanecer 100% idéntico en su escala, forma, textura, metales, brillos y posición original.

1. PROHIBICIÓN ABSOLUTA DE PERSONAS NUEVAS: Está TERMINANTEMENTE PROHIBIDO inventar personas, rostros, modelos o bailarinas que no estén en la foto original.
2. FONDO CICLORAMA GRIS CÁLIDO #E5E1DE: Reemplaza todo el fondo existente por un fondo de estudio liso, mate, plano y uniforme en color gris cálido #E5E1DE (RGB 229, 225, 222). Cero degradados, cero viñetas oscuras y cero sombras duras.
3. SOMBRA DE APOYO SUTIL: Genera únicamente una sombra de contacto suave, difusa y transparente inmediatamente bajo la base del producto.
4. INTEGRIDAD DE FILIGRANA Y MATERIALES: Conserva íntegros los calados de oro 18k (#D4AF37), perlas, broches y texturas originales sin deformar ni recortar nada."""

# PROMPT TIPO B: MODA, DANZA, MANIQUÍES Y PRIMEROS PLANOS (BLOQUEO 1:1 Y CERO OUTPAINTING)
PROMPT_MODA_MODELO = """Eres un retocador fotográfico profesional especializado en catálogo e-commerce de indumentaria tradicional de marinera. Realiza un reemplazo quirúrgico ÚNICAMENTE del fondo y del suelo circundante, manteniendo un bloqueo geométrico 1:1 sobre el sujeto, maniquí o prenda principal:

1. BLOQUEO GEOMÉTRICO DE ESCALA Y ENCUADRE (PROHIBIDO HACER ZOOM-OUT): El sujeto, prenda o maniquí debe ocupar EXACTAMENTE la misma altura, anchura y posición que en la fotografía original. Está TERMINANTEMENTE PROHIBIDO encoger el producto o alejar la cámara.
2. RESPETO ABSOLUTO A PRIMEROS PLANOS, DETALLES Y MANIQUÍES CORTADOS (CERO OUTPAINTING): Si la foto original es un primer plano o plano cerrado (por ejemplo, detalle del cuello de una camisa, pechera, mangas, manos, pies con cintas o medio torso cortado por los bordes de la foto), MANTÉN EXACTAMENTE ESE MISMO PRIMER PLANO CORTADO EN LOS BORDES. Está TERMINANTEMENTE PROHIBIDO alejar la toma para completar el resto de la camisa, torso o maniquí que estaba fuera del cuadro original.
3. PROHIBICIÓN DE AGREGAR EXTREMIDADES O PAÑUELOS INEXISTENTES:
   - Si en la fotografía original la falda o el borde inferior oculta los pies, NO agregues pies debajo. (Si en la foto original sí aparecen pies o manos mostrando un producto, consérvalos 100% idénticos).
   - Si en la fotografía original NO hay un pañuelo en la mano, NO inventes un pañuelo.
4. PRESERVACIÓN DE LA FORMA Y VUELO DE LA PRENDA: Conserva intacta la forma, amplitud, pliegues, alforzas, bobos y cintas tal como se ven en la foto original.
5. FONDO Y PISO CICLORAMA GRIS CÁLIDO #E5E1DE: Reemplaza únicamente el fondo antiguo por un ciclorama de estudio liso, mate y uniforme en color gris cálido #E5E1DE (RGB 229, 225, 222), con una sombra de contacto suave cuando corresponda."""

def select_prompt_for_category(subfolder_str, file_name=''):
    """
    Selecciona el prompt idóneo según la naturaleza del producto:
    1. PRENDAS DE VESTIR / DANZA (Faldas, Blusas, Vestidos, Trajes, Enagues, Polos, Pantalones, Anacos) -> MODA_MODELO.
    2. JOYERÍA, ACCESORIOS Y STILL LIFE (Aretes, Collares, Escapularios, Filigrana, Sombreros, Tocados, Mantos) -> JOYERIA_ACCESORIO.
    """
    text = f"{subfolder_str} {file_name}".lower()
    
    clothing_keywords = [
        'falda', 'faldas', 'blusa', 'blusas', 'vestido', 'vestidos',
        'traje', 'trajes', 'enague', 'enagues', 'enagua', 'enaguas',
        'pantalon', 'pantalones', 'camisa', 'camisas', 'chaleco',
        'poncho', 'polo', 'bobo', 'bobos', 'razo', 'anaco', 'anacos'
    ]
    if any(ck in text for ck in clothing_keywords):
        return PROMPT_MODA_MODELO, 'MODA_MODELO'
        
    jewelry_keywords = [
        'accesorio', 'accesorios', 'arete', 'aretes', 'escapulario', 'escapularios',
        'collar', 'collares', 'filigrana', 'joya', 'joyas', 'joyeria', 'joyería',
        'prendedor', 'broche', 'tocado', 'sombrero', 'sombreros', 'faja', 'fajas',
        'manto', 'mantos', 'pardo', 'pardos'
    ]
    if any(jk in text for jk in jewelry_keywords):
        return PROMPT_JOYERIA_ACCESORIOS, 'JOYERIA_ACCESORIO'
        
    return PROMPT_MODA_MODELO, 'MODA_MODELO'

def measure_subject_scale(orig_img, pro_img, work_side=1024):
    """
    Mide geométricamente mediante puntos clave ORB + RANSAC si Gemini encogió al sujeto (zoom-out).
    Retorna (escala_relativa, num_inliers).
    escala_relativa ~ 1.0 significa tamaño 1:1 preservado; < 0.88 indica zoom-out (sujeto achicado).
    """
    try:
        def _prep(im):
            a = np.array(im.convert('L'))
            h, w = a.shape
            r = work_side / float(max(h, w))
            return cv2.resize(a, (int(w * r), int(h * r)), interpolation=cv2.INTER_AREA), r
        g1, r1 = _prep(orig_img)
        g2, r2 = _prep(pro_img)
        orb = cv2.ORB_create(nfeatures=4000)
        k1, d1 = orb.detectAndCompute(g1, None)
        k2, d2 = orb.detectAndCompute(g2, None)
        if d1 is None or d2 is None or len(k1) < 12 or len(k2) < 12:
            return 1.0, 0
        matches = cv2.BFMatcher(cv2.NORM_HAMMING).knnMatch(d1, d2, k=2)
        good = [m for m, n in (p for p in matches if len(p) == 2) if m.distance < 0.75 * n.distance]
        if len(good) < 12:
            return 1.0, len(good)
        p1 = np.float32([k1[m.queryIdx].pt for m in good]) / r1
        p2 = np.float32([k2[m.trainIdx].pt for m in good]) / r2
        M, inl = cv2.estimateAffinePartial2D(p1, p2, method=cv2.RANSAC, ransacReprojThreshold=4.0)
        if M is None:
            return 1.0, 0
        s_px = float(np.sqrt(M[0, 0] ** 2 + M[1, 0] ** 2))
        s_rel = s_px * (orig_img.size[1] / float(pro_img.size[1]))
        return round(s_rel, 3), int(inl.sum())
    except Exception:
        return 1.0, 0

def edit_background_gemini(pil_img, prompt_text=PROMPT_MODA_MODELO, max_retries=2):
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
            'responseModalities': ['TEXT', 'IMAGE'],
            'temperature': 0.05
        }
    }

    for intento in range(max_retries):
        try:
            res = requests.post(url, json=payload, timeout=90)
            if res.status_code == 200:
                res_data = res.json()
                candidates = res_data.get('candidates', [])
                if candidates:
                    first_c = candidates[0]
                    content = first_c.get('content')
                    if content and 'parts' in content:
                        for p in content['parts']:
                            if 'inlineData' in p:
                                img_bytes = base64.b64decode(p['inlineData']['data'])
                                return Image.open(io.BytesIO(img_bytes)), None
                    finish_reason = first_c.get('finishReason', 'SIN_PARTS')
                    return None, f"Gemini sin partes de imagen (finishReason: {finish_reason})"
                return None, f"Respuesta Gemini vacía: {res.text[:120]}"
            elif res.status_code in (429, 503):
                time.sleep(8 * (intento + 1))
                continue
            else:
                return None, f'HTTP {res.status_code}: {res.text[:120]}'
        except Exception as e:
            if intento < max_retries - 1:
                time.sleep(4)
                continue
            return None, str(e)
    return None, 'MAX_RETRIES_EXCEEDED'

def audit_image_quality(orig_img, pro_img, tipo_prod='MODA_MODELO'):
    """
    Evaluación Matemática en OpenCV:
    1. Delta E CIELAB 1976 en esquinas superiores respecto al gris #E5E1DE.
    2. Simetría de iluminación izquierda-derecha.
    3. Limpieza de suelo (para MODA_MODELO) o uniformidad perimetral (para JOYERIA_ACCESORIO).
    4. Escala geométrica 1:1 (ORB + RANSAC) para detectar zoom-out del sujeto.
    """
    pro_np = np.array(pro_img.convert('RGB'))
    h, w, _ = pro_np.shape

    target_lab = cv2.cvtColor(np.float32([[[229/255.0, 225/255.0, 222/255.0]]]), cv2.COLOR_RGB2LAB)[0, 0].astype(np.float64)
    roi_tl = pro_np[5:35, 5:35].reshape(-1, 3)
    roi_tr = pro_np[5:35, w-35:w-5].reshape(-1, 3)
    
    med_tl = np.median(roi_tl, axis=0).astype(np.float32) / 255.0
    med_tr = np.median(roi_tr, axis=0).astype(np.float32) / 255.0
    c_tl = cv2.cvtColor(np.float32([[med_tl]]), cv2.COLOR_RGB2LAB)[0, 0].astype(np.float64)
    c_tr = cv2.cvtColor(np.float32([[med_tr]]), cv2.COLOR_RGB2LAB)[0, 0].astype(np.float64)
    
    delta_tl = float(np.sqrt(np.sum((target_lab - c_tl) ** 2)))
    delta_tr = float(np.sqrt(np.sum((target_lab - c_tr) ** 2)))
    delta_e = round(max(delta_tl, delta_tr), 2)
    diff_lr = float(np.sqrt(np.sum((c_tl - c_tr) ** 2)))
    
    if tipo_prod == 'JOYERIA_ACCESORIO':
        # En bodegón macro los dijes/aretes llegan al borde inferior; evaluamos uniformidad de esquinas superiores
        score_suelo = round(max(75.0, min(100.0, 100.0 - diff_lr * 1.5)), 1)
    else:
        lower_roi = pro_np[int(h * 0.85):h, :]
        lower_lab = cv2.cvtColor(lower_roi, cv2.COLOR_RGB2LAB)[:, :, 0]
        dirty_pixels = np.sum(lower_lab < 90)
        ratio_sucio = float(dirty_pixels / lower_lab.size)
        score_suelo = round(max(0.0, min(100.0, (1.0 - ratio_sucio) * 100.0)), 1)

    escala_rel, inliers = measure_subject_scale(orig_img, pro_img)

    observaciones = []
    if inliers >= 25 and escala_rel < 0.86:
        observaciones.append(f'ALERTA ZOOM-OUT: Sujeto reducido al {int(round(escala_rel*100))}% (escala={escala_rel})')
    else:
        observaciones.append(f'Escala 1:1 preservada ({int(round(escala_rel*100))}%)')

    if delta_e <= 35.0:
        observaciones.append(f'Ciclorama #E5E1DE uniforme (ΔE={delta_e})')
    elif delta_e <= 65.0:
        observaciones.append(f'Tono estudio cálido homogéneo (ΔE={delta_e})')
    else:
        observaciones.append(f'Variación cromática (ΔE={delta_e})')

    if score_suelo >= 90.0:
        observaciones.append(f'Base limpia ({score_suelo}%)')
    else:
        observaciones.append(f'Posible sombra densa ({score_suelo}%)')

    score_color = max(45, 100 - int(delta_e * 0.7))
    score_simetria = max(55, 100 - int(diff_lr * 2.5))
    score_final = int(round(score_color * 0.40 + score_simetria * 0.30 + score_suelo * 0.30))

    # Penalización severa si hay zoom-out para que nunca se apruebe sin revisión
    if inliers >= 25 and escala_rel < 0.86:
        score_final = min(score_final, 59)

    score_final = max(35, min(99, score_final))
    
    return {
        'score': score_final,
        'delta_e': delta_e,
        'score_suelo': score_suelo,
        'escala_rel': escala_rel,
        'observaciones': ' | '.join(observaciones)
    }

print('✅ Motor de Prompts Condicionales y Evaluador QA con Detector ORB+RANSAC compilados.')


# ============================================================
# CELDA 5
# ============================================================
# 5. Guardado Separado en 3 Destinos: (1) _1_RAW_GEMINI, (2) _2_MESA_REVISION_CARLOS y (3) Copia directa en Carpeta _Pro del Cliente Final
def _fix_mojibake_str(s):
    if not s:
        return ''
    return (str(s)
        .replace('â€“', '–').replace('â€”', '—')
        .replace('Ã¡', 'á').replace('Ã©', 'é').replace('Ã­', 'í')
        .replace('Ã³', 'ó').replace('Ãº', 'ú').replace('Ã±', 'ñ')
        .replace('Ã', 'Á').replace('Ã', 'É').replace('Ã', 'Í')
        .replace('Ã', 'Ó').replace('Ã', 'Ú').replace('Ã', 'Ñ'))

def resolve_client_pro_folder(orig_ruta_str):
    clean_orig = _fix_mojibake_str(orig_ruta_str).strip()
    if clean_orig.startswith('Fotos catalogo / Para ella / Falda / Falda de Ensayo / Faldas de Ensayo de razo 1 bobo / '):
        rest = clean_orig.replace('Fotos catalogo / Para ella / Falda / Falda de Ensayo / Faldas de Ensayo de razo 1 bobo / ', '')
        segs = [f"{s.strip()}_Pro" for s in rest.split(' / ')]
        rel_parts = ['Para ella_Pro', 'Falda_Pro', 'Faldas de Ensayo de razo 1 bobo pro'] + segs
    elif clean_orig.startswith('Fotos catalogo / Para ella / Falda / Falda de Ensayo / Falda de Ensayo de razo 2 bobos con contrabobo / '):
        rest = clean_orig.replace('Fotos catalogo / Para ella / Falda / Falda de Ensayo / Falda de Ensayo de razo 2 bobos con contrabobo / ', '')
        segs = [f"{s.strip()}_Pro" for s in rest.split(' / ')]
        rel_parts = ['Para ella_Pro', 'Falda_Pro', 'Falda de Ensayo de razo 2 bobos con contrabobo pro'] + segs
    else:
        parts = [p.strip() for p in clean_orig.split(' / ') if p.strip()]
        if parts and parts[0] == 'Fotos catalogo':
            parts = parts[1:]
        rel_parts = [p if p.endswith('_Pro') else f'{p}_Pro' for p in parts]
    rel_pro_str = 'Fotos catalogo PRO / ' + ' / '.join(rel_parts)
    base_pro = globals().get('DIR_PRO_ROOT') or (DIR_2_MESA_REVISION.parent)
    target_dir = base_pro.joinpath(*rel_parts)
    return rel_pro_str, target_dir

def route_and_save_photo(orig_img, raw_gemini_img, python_pro_img, row_data, qa_metrics, latency_sec, batch_tag=''):
    row_id = str(row_data.get('ID', '0'))
    orig_name = _fix_mojibake_str(str(row_data.get('Nombre_Archivo_Original', 'foto')))
    orig_ruta = str(row_data.get('Ruta_Carpeta_Drive', ''))
    safe_stem = sanitize_safe_filename(Path(orig_name).stem)
    tag_suffix = f'_{batch_tag}' if batch_tag else ''
    score = qa_metrics.get('score', 90)

    # FASE 1: GUARDADO INMEDIATO EN NVME LOCAL DE AMBAS VERSIONES (Puro Gemini vs Post-Corrección Python)
    local_raw_gemini = LOCAL_SCRATCH / f'ID{row_id.zfill(3)}_{safe_stem}{tag_suffix}_GEMINI_RAW.jpg'
    local_python_pro = LOCAL_SCRATCH / f'ID{row_id.zfill(3)}_{safe_stem}{tag_suffix}_PYTHON_PRO_score{score}.jpg'
    raw_gemini_img.save(local_raw_gemini, format='JPEG', quality=95, optimize=True)
    python_pro_img.save(local_python_pro, format='JPEG', quality=95, optimize=True)

    # FASE 2: SUBIDA DIRECTA VÍA DRIVE API V3 DESDE NVME LOCAL (Cero archivos duplicados FUSE vs API)
    raw_drive_file = DIR_1_RAW_GEMINI / local_raw_gemini.name
    revision_drive_file = DIR_2_MESA_REVISION / local_python_pro.name

    raw_id, raw_link = sync_and_resolve_drive_file_id(local_raw_gemini, FOLDER_ID_1_RAW_GEMINI, creds)
    mesa_id, mesa_link = sync_and_resolve_drive_file_id(local_python_pro, FOLDER_ID_2_MESA_REVISION, creds)

    # Respaldo FUSE únicamente si Drive API no devolvió ID:
    if not raw_id:
        shutil.copy2(local_raw_gemini, raw_drive_file)
    if not mesa_id:
        shutil.copy2(local_python_pro, revision_drive_file)

    # FASE 3: COPIA AUTOMÁTICA EN LA CARPETA _Pro RESPECTIVA DEL CLIENTE FINAL (sin cambiar estado de aprobación)
    rel_pro_str, client_pro_dir = resolve_client_pro_folder(orig_ruta)
    prod_folder = _fix_mojibake_str(str(row_data.get('Nombre_Carpeta_Producto', ''))).strip()
    prod_folder = re.sub(r'[\/:*?"<>|]', '-', prod_folder).strip()
    clean_orig_stem = Path(orig_name).stem.strip() or f'Foto_{row_id}'
    clean_orig_stem = re.sub(r'[\/:*?"<>|]', '-', clean_orig_stem).strip()
    if prod_folder and clean_orig_stem:
        client_pro_filename = f'{prod_folder} {clean_orig_stem}.jpg'
    elif prod_folder:
        client_pro_filename = f'{prod_folder}.jpg'
    else:
        client_pro_filename = f'{clean_orig_stem}.jpg'
    if not batch_tag:
        try:
            client_pro_dir.mkdir(parents=True, exist_ok=True)
            shutil.copy2(local_python_pro, client_pro_dir / client_pro_filename)
        except Exception as cp_e:
            print(f'   ⚠️ Aviso copia carpeta cliente _Pro: {cp_e}')

    # FASE 5: REGISTRO PERMANENTE EN BITÁCORA INMUTABLE (.JSONL)
    record = {
        'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
        'batch_tag': batch_tag,
        'id': row_id,
        'archivo_original': orig_name,
        'raw_gemini_path': str(raw_drive_file),
        'raw_drive_id': raw_id,
        'mesa_revision_path': str(revision_drive_file),
        'mesa_drive_id': mesa_id,
        'ruta_carpeta_pro': rel_pro_str,
        'nombre_archivo_pro': client_pro_filename,
        'score_qa': score,
        'delta_e': qa_metrics.get('delta_e', 0.0),
        'escala_rel': qa_metrics.get('escala_rel', 1.0),
        'observaciones': qa_metrics.get('observaciones', ''),
        'latencia': latency_sec
    }
    with open(LEDGER_FILE, 'a', encoding='utf-8') as lf:
        lf.write(json.dumps(record, ensure_ascii=False) + '\n')

    return {
        'estado': 'PENDIENTE_REVISION_CARLOS',
        'score_qa': score,
        'motivo_qa': qa_metrics.get('observaciones', 'Listo para revisión tri-comparativa de Carlos'),
        'delta_e': qa_metrics.get('delta_e', 0.0),
        'latencia': latency_sec,
        'ruta_mesa_revision': str(revision_drive_file),
        'ruta_raw_gemini': str(raw_drive_file),
        'ruta_carpeta_pro_rel': rel_pro_str,
        'nombre_archivo_pro_cliente': client_pro_filename,
        'raw_id': raw_id,
        'raw_link': raw_link,
        'mesa_id': mesa_id,
        'mesa_link': mesa_link
    }

print('✅ Módulo de Enrutamiento en 3 Niveles con Drive API ID Resolver compilado.')


# ============================================================
# CELDA 6
# ============================================================
# 6. CANARY TEST & EXPERIMENTOS (REGISTRO EXCLUSIVO EN Registro_Pruebas_Sandbox)
EJECUTAR_PRUEBA_SANDBOX = False  # Poner en True solo si quieres correr un experimento en Sandbox
CANARY_IDS_OBJETIVO = ['28', '418', '421', '423', '424']
BATCH_EXPERIMENTO_ID = f'EXP_{time.strftime("%Y%m%d_%H%M%S")}'

if not EJECUTAR_PRUEBA_SANDBOX:
    print('🔒 [PASO 6 EN ESPERA] Modo Sandbox pausado para ir directo a Producción (Celda 7).')
else:
    print(f'🧪 INICIANDO SESIÓN DE PRUEBAS [{BATCH_EXPERIMENTO_ID}] EN SANDBOX...')
    all_maestro = sheet_maestro.get_all_records()

    target_rows = []
    for sheet_row_idx, row in enumerate(all_maestro, start=2):
        if str(row.get('ID', '')) in CANARY_IDS_OBJETIVO:
            target_rows.append((sheet_row_idx, row))

    print(f'✅ Se encontraron {len(target_rows)} fotos en el catálogo maestro para experimentar.')

    for idx, (m_row_num, row_data) in enumerate(target_rows, start=1):
        c_id = str(row_data.get('ID', ''))
        file_name = str(row_data.get('Nombre_Archivo_Original', ''))
        subfolder = str(row_data.get('Ruta_Carpeta_Drive', ''))
        orig_drive_id = str(row_data.get('ID_Archivo_Original', '')).strip()
        
        print(f'\n🔬 [{idx}/{len(target_rows)}] Prueba sobre ID {c_id}: {file_name}')
        print(f'   Carpeta: {subfolder}')
        
        t0 = time.time()
        raw_src_img, source_info = load_source_image_infallible(row_data, creds)
        if not raw_src_img:
            print(f'   ⚠️ Error de carga: {source_info}. Saltando.')
            continue
            
        try:
            prompt_elegido, tipo_prod = select_prompt_for_category(subfolder, file_name)
            prep_img, crop_note = prepare_image_for_gemini(raw_src_img, tipo_prod=tipo_prod)
            print(f'   📥 Imagen preparada ({crop_note}) vía: {source_info} | Modo: {tipo_prod}')
            
            raw_gemini_img, err = edit_background_gemini(prep_img, prompt_text=prompt_elegido)
            t_latencia = round(time.time() - t0, 2)
            
            if raw_gemini_img:
                # FASE 2 PYTHON POST-GEMINI: Genera la versión pulida en Python conservando aparte la versión pura de Gemini
                python_pro_img, escala_post, sift_note = normalize_and_align_pro_sift(prep_img, raw_gemini_img, tipo_prod=tipo_prod)
                try:
                    qa = audit_image_quality(prep_img, python_pro_img, tipo_prod=tipo_prod)
                    qa['observaciones'] = f"{qa.get('observaciones', '')} | {crop_note} | {sift_note}"
                except Exception as qa_err:
                    qa = {'score': 70, 'delta_e': 0.0, 'score_suelo': 90.0, 'escala_rel': escala_post, 'observaciones': f'Excepción OpenCV: {qa_err}'}
                    
                res = route_and_save_photo(prep_img, raw_gemini_img, python_pro_img, row_data, qa, t_latencia, batch_tag=BATCH_EXPERIMENTO_ID)
                
                mesa_drive_id = res.get('mesa_id') or ''
                link_drive_mesa = res.get('mesa_link') or (f'https://drive.google.com/file/d/{mesa_drive_id}/view' if mesa_drive_id else '')
                raw_drive_id = res.get('raw_id') or Path(res['ruta_raw_gemini']).name
                
                formula_orig = f'=IMAGE("https://lh3.googleusercontent.com/d/{orig_drive_id}=s400")' if orig_drive_id and orig_drive_id != '-' else '-'
                formula_pro = f'=IMAGE("https://lh3.googleusercontent.com/d/{mesa_drive_id}=s400")' if mesa_drive_id else '-'
                
                new_sandbox_row = [
                    time.strftime('%Y-%m-%d %H:%M:%S'),
                    BATCH_EXPERIMENTO_ID,
                    c_id,
                    'TEST_CANARY',
                    subfolder,
                    file_name,
                    tipo_prod,
                    'EXITO_REVISION' if res['score_qa'] >= 75 else 'REVISION_MANUAL',
                    str(res['score_qa']),
                    str(res['delta_e']),
                    f"{qa.get('score_suelo', 0.0)}%",
                    str(t_latencia),
                    formula_orig,
                    formula_pro,
                    raw_drive_id,
                    mesa_drive_id,
                    link_drive_mesa,
                    res['motivo_qa']
                ]
                sheet_sandbox.append_row(new_sandbox_row, value_input_option='USER_ENTERED')
                
                print(f'   ✅ Persistido en Drive y asentado en Sandbox | Score: {res["score_qa"]}/100 | Escala: {qa.get("escala_rel", 1.0)} | {t_latencia}s')
                print(f'   🛡️ Drive ID Mesa: {mesa_drive_id}')
                display(python_pro_img)
            else:
                print(f'   ❌ Fallo API Gemini: {err}')
                sheet_sandbox.append_row([
                    time.strftime('%Y-%m-%d %H:%M:%S'), BATCH_EXPERIMENTO_ID, c_id, 'TEST_CANARY',
                    subfolder, file_name, tipo_prod, 'ERROR_API', '0', '0.0', '0%', str(t_latencia),
                    '', '', '', '', '', f'Error API Gemini: {err}'
                ], value_input_option='USER_ENTERED')
                
        except Exception as exc:
            print(f'   ❌ Excepción: {exc}')
        time.sleep(3)

    print(f'\n🏆 SESIÓN DE PRUEBAS COMPLETADA. Revisa todos los intentos en la pestaña Registro_Pruebas_Sandbox.')


# ============================================================
# CELDA 7
# ============================================================
# 🔒 SEGURO DE ACTIVACIÓN MANUAL: LOTES DE FOTOS PARA CATÁLOGO MAESTRO (PRODUCCIÓN)
# Procesa de forma autónoma los ítems que NO TIENEN VERSIÓN PRO en el Catálogo Maestro.

# Bandera booleana de seguridad: en True procesa el lote de producción configurado en CHUNK_SIZE.
EJECUTAR_LOTE_PRODUCCION = True
# Cantidad máxima de fotografías pendientes por corrida (200 fotos por lote ~35 min; o pon 800 para barrer todo el catálogo de corrido).
CHUNK_SIZE = 200
# Cada cuántas fotos mostrar vista previa en Colab (20 evita saturar la memoria RAM del navegador en lotes de 200+ fotos; pon 1 si quieres ver todas).
MOSTRAR_PREVIEW_CADA_N = 20
# Lista opcional de IDs específicos que marcaste como INCORRECTO en la plataforma web para reintentar manualmente (si está vacía, procesa los PENDIENTES normales).
IDS_REINTENTAR_MANUAL = []

# Verifica si el seguro sigue puesto (EJECUTAR_LOTE_PRODUCCION == False).
if not EJECUTAR_LOTE_PRODUCCION:
    # Imprime un aviso en consola indicando que la celda está en espera y cómo activarla.
    print('🔒 [PASO 7 EN ESPERA] Seguro activo. Cambia EJECUTAR_LOTE_PRODUCCION = True para iniciar.')
# Si cambiaste EJECUTAR_LOTE_PRODUCCION a True, entra a este bloque para ejecutar el lote de producción.
else:
    # Muestra en consola el mensaje de inicio indicando el tamaño del lote configurado en CHUNK_SIZE.
    print(f'🚀 INICIANDO LOTE DE {CHUNK_SIZE} FOTOS HACIA LA MESA DE REVISIÓN EN CATÁLOGO MAESTRO...')
    # Descarga todas las filas de la pestaña maestra 'Control_Total_Drive_V2' como una lista de diccionarios (donde cada llave es el nombre de columna).
    all_records = sheet_maestro.get_all_records()
    # Lee la fila 1 (encabezados) de la hoja maestra para obtener los nombres exactos y posiciones de cada columna.
    headers = sheet_maestro.row_values(1)
    
    # Busca el índice (base 1 para gspread) de la columna 'Estado' donde se registrará 'PENDIENTE_REVISION_CARLOS'.
    col_estado = headers.index('Estado') + 1
    # Obtiene el número de columna de 'Score_QA' (puntaje de calidad 0-100) si existe en la hoja.
    col_score_qa = headers.index('Score_QA') + 1 if 'Score_QA' in headers else None
    # Obtiene el número de columna de 'Motivo_QA' (diagnóstico técnico de OpenCV) si existe en la hoja.
    col_motivo_qa = headers.index('Motivo_QA') + 1 if 'Motivo_QA' in headers else None
    # Obtiene el número de columna de 'Delta_E_Color' (desviación de color respecto al gris #E5E1DE) si existe.
    col_delta_e = headers.index('Delta_E_Color') + 1 if 'Delta_E_Color' in headers else None
    # Obtiene el número de columna de 'Latencia_Seg' (tiempo en segundos que tardó el procesamiento) si existe.
    col_latencia = headers.index('Latencia_Seg') + 1 if 'Latencia_Seg' in headers else None
    # Obtiene el número de columna de 'Ruta_Destino_PRO' (ruta del archivo en Drive) si existe.
    col_dest_pro = headers.index('Ruta_Destino_PRO') + 1 if 'Ruta_Destino_PRO' in headers else None
    # Obtiene el número de columna de 'ID_Archivo_PRO' (el ID único de Google Drive de la imagen generada) si existe.
    col_id_pro = headers.index('ID_Archivo_PRO') + 1 if 'ID_Archivo_PRO' in headers else None
    # Obtiene el número de columna de 'Link_Drive_PRO' (enlace web directo para abrir la foto en Drive) si existe.
    col_link_pro = headers.index('Link_Drive_PRO') + 1 if 'Link_Drive_PRO' in headers else None
    # Obtiene el número de columna de 'Vista_Original' (miniatura =IMAGE de la foto original) si existe.
    col_v_orig = headers.index('Vista_Original') + 1 if 'Vista_Original' in headers else None
    # Obtiene el número de columna de 'Vista_PRO' (miniatura =IMAGE de la foto pulida por Python) si existe.
    col_v_pro = headers.index('Vista_PRO') + 1 if 'Vista_PRO' in headers else None
    # Obtiene el número de columna de 'Link_Gemini_Raw' (enlace web a la versión pura de Gemini en _1_RAW_GEMINI) si existe.
    col_link_raw = headers.index('Link_Gemini_Raw') + 1 if 'Link_Gemini_Raw' in headers else None
    # Obtiene el número de columna de 'ID_Archivo_Gemini_Raw' (ID de Drive de la versión pura de Gemini en _1_RAW_GEMINI) si existe.
    col_id_raw = headers.index('ID_Archivo_Gemini_Raw') + 1 if 'ID_Archivo_Gemini_Raw' in headers else None
    # Obtiene el número de columna de 'Ruta_Carpeta_PRO' y 'Nombre_Archivo_PRO' para registrar la copia en la carpeta _Pro del cliente final.
    col_ruta_pro_cliente = headers.index('Ruta_Carpeta_PRO') + 1 if 'Ruta_Carpeta_PRO' in headers else None
    col_nombre_pro_cliente = headers.index('Nombre_Archivo_PRO') + 1 if 'Nombre_Archivo_PRO' in headers else None
    
    # Convierte la lista manual de reintentos a conjunto de strings para búsqueda rápida si decidiste reintentar IDs rechazados.
    reintentar_set = set(str(x).strip() for x in IDS_REINTENTAR_MANUAL)
    # Inicializa una lista vacía donde guardaremos únicamente las filas que se procesarán en esta corrida.
    pendientes = []
    # Recorre todas las filas del catálogo maestro enumerándolas desde la fila 2 (ya que la fila 1 son los encabezados).
    for sheet_row_num, row in enumerate(all_records, start=2):
        # Extrae el ID de la fila actual como cadena de texto limpia.
        rid = str(row.get('ID', '')).strip()
        # Si definiste IDs específicos en IDS_REINTENTAR_MANUAL, selecciona únicamente esos IDs para re-procesarlos.
        if reintentar_set:
            # Comprueba si el ID de la fila actual está dentro de tu lista manual de reintento.
            if rid in reintentar_set:
                # Agrega la fila a la cola de procesamiento manual.
                pendientes.append((sheet_row_num, row))
        # Si IDS_REINTENTAR_MANUAL está vacía, selecciona automáticamente las fotos pendientes que aún no tienen versión PRO.
        else:
            # Extrae el texto de la columna 'Estado' y lo convierte a mayúsculas para compararlo sin errores de formato.
            st = str(row.get('Estado', '')).upper()
            # Extrae el valor de 'ID_Archivo_PRO' quitando espacios en blanco para verificar si ya tiene una foto PRO asignada.
            id_pro_existente = str(row.get('ID_Archivo_PRO', '')).strip()
            # Filtra: selecciona la fila si su estado es 'PENDIENTE', 'RECHAZADO_CARLOS', 'ERROR_API_GEMINI' o vacío.
            if st in ['PENDIENTE', 'RECHAZADO_CARLOS', 'ERROR_API_GEMINI', ''] and (not id_pro_existente or id_pro_existente == '-' or st in ['RECHAZADO_CARLOS', 'ERROR_API_GEMINI']):
                # Agrega la tupla (número de fila en Google Sheets, diccionario de datos de la fila) a la lista de pendientes.
                pendientes.append((sheet_row_num, row))
            
    # Imprime en consola cuántas fotos pendientes o marcadas para reintento se encontraron en total.
    print(f'📊 Total fotos en cola para procesar: {len(pendientes)}')
    # Recorta la lista de pendientes para tomar únicamente las primeras CHUNK_SIZE fotos para esta tanda.
    chunk = pendientes[:CHUNK_SIZE]
    t_batch_start = time.time()
    
    # Inicia el bucle principal iterando sobre cada una de las fotos seleccionadas en el lote actual.
    for idx, (sheet_row_num, row_data) in enumerate(chunk, start=1):
        # Renovación preventiva de token OAuth cada 20 fotos para que lotes largos (200+ fotos) nunca expiren a mitad de camino.
        if idx > 1 and idx % 20 == 0:
            try:
                from google.auth.transport.requests import Request
                if hasattr(creds, 'refresh'):
                    creds.refresh(Request())
                gc_client = gspread.authorize(creds)
                sh = gc_client.open_by_key(SHEET_ID)
                sheet_maestro = sh.worksheet(TAB_MAESTRO)
                gc.collect()
            except Exception as auth_e:
                print(f'   🔄 Aviso renovación token: {auth_e}')

        # Extrae el identificador único de catálogo (columna 'ID') de la fotografía actual.
        c_id = str(row_data.get('ID', ''))
        # Extrae el nombre del archivo original (columna 'Nombre_Archivo_Original').
        file_name = str(row_data.get('Nombre_Archivo_Original', ''))
        # Extrae la ruta de carpetas en Drive (columna 'Ruta_Carpeta_Drive') que describe la categoría y el producto.
        subfolder = str(row_data.get('Ruta_Carpeta_Drive', ''))
        # Extrae el ID de Google Drive del archivo original (columna 'ID_Archivo_Original') para carga directa y miniaturas.
        orig_drive_id = str(row_data.get('ID_Archivo_Original', '')).strip()
        
        elapsed_min = (time.time() - t_batch_start) / 60.0
        avg_s = (time.time() - t_batch_start) / max(1, idx - 1) if idx > 1 else 11.5
        eta_min = ((len(chunk) - idx + 1) * avg_s) / 60.0
        # Muestra en consola el progreso actual dentro del lote con tiempo transcurrido y ETA estimado.
        print(f'\n[{idx}/{len(chunk)}] Procesando ID {c_id}: {file_name} | ⏱️ Transcurrido: {elapsed_min:.1f}m | ETA lote: ~{eta_min:.1f}m')
        # Muestra en consola la ruta de carpeta a la que pertenece el producto.
        print(f'   Carpeta: {subfolder}')
        
        # Registra el tiempo exacto de inicio (en segundos) para medir cuánto tarda todo el procesamiento de esta foto.
        t0 = time.time()
        # Carga la imagen original usando el motor dual (primero intenta por ruta FUSE en Drive montado y, si falla, la descarga por Drive API usando orig_drive_id).
        raw_src_img, source_info = load_source_image_infallible(row_data, creds)
        # Si la imagen no pudo cargarse por ninguna de las dos vías, entra a este bloque de protección.
        if not raw_src_img:
            # Informa el motivo por el cual no se pudo abrir el archivo y pasa a la siguiente foto sin gastar llamadas a la API.
            print(f'   ⚠️ Error de carga: {source_info}. Saltando.')
            # Salta inmediatamente a la siguiente iteración del bucle (siguiente foto del lote).
            continue
            
        # Abre un bloque try/except para capturar cualquier error inesperado sin detener el resto del lote.
        try:
            # Ejecuta el clasificador jerárquico: decide si usar PROMPT_MODA_MODELO (ropa/bailarina) o PROMPT_JOYERIA_ACCESORIOS (bodegón sin personas).
            prompt_elegido, tipo_prod = select_prompt_for_category(subfolder, file_name)
            # FASE 1 DE NORMALIZACIÓN PYTHON (PRE-GEMINI): Recorta barras blancas exactas (Sobel) sin tocar prendas ni joyas y ajusta el lado mayor a máx. 1920px.
            prep_img, crop_note = prepare_image_for_gemini(raw_src_img, tipo_prod=tipo_prod)
            # Confirma en consola desde qué fuente se cargó la imagen y cuántos píxeles de barra blanca se recortaron.
            print(f'   📥 Imagen preparada ({crop_note}) vía: {source_info} | Modo: {tipo_prod}')
            
            # Envía la imagen preparada y el prompt elegido a la API de Gemini 2.5 Flash Image (1 sola llamada, sin reintentos automáticos).
            raw_gemini_img, err = edit_background_gemini(prep_img, prompt_text=prompt_elegido)
            # Calcula el tiempo total transcurrido desde t0 en segundos (redondeado a 2 decimales).
            t_latencia = round(time.time() - t0, 2)
            
            # Si Gemini devolvió exitosamente una imagen generada (raw_gemini_img no es None), genera la versión pulida en Python y guarda ambas en carpetas separadas.
            if raw_gemini_img:
                # FASE 2 DE NORMALIZACIÓN PYTHON (POST-GEMINI): Crea la versión pulida re-encuadrada con SIFT+RANSAC 1:1 conservando intacta raw_gemini_img.
                python_pro_img, escala_post, sift_note = normalize_and_align_pro_sift(prep_img, raw_gemini_img, tipo_prod=tipo_prod)
                # Inicia bloque try/except para que ningún fallo matemático en OpenCV impida guardar ambas imágenes.
                try:
                    # Ejecuta el auditor de calidad OpenCV (mide Delta E del fondo, limpieza de piso y escala final).
                    qa = audit_image_quality(prep_img, python_pro_img, tipo_prod=tipo_prod)
                    # Anexa al diagnóstico técnico el detalle del recorte Pre-Gemini y de la alineación SIFT Post-Gemini.
                    qa['observaciones'] = f"{qa.get('observaciones', '')} | {crop_note} | {sift_note}"
                # Si ocurriera alguna excepción en el cálculo de OpenCV, asigna métricas neutras de respaldo.
                except Exception as qa_err:
                    # Define el diccionario qa de respaldo anotando el detalle de la excepción en las observaciones.
                    qa = {'score': 70, 'delta_e': 0.0, 'score_suelo': 90.0, 'escala_rel': escala_post, 'observaciones': f'Excepción OpenCV: {qa_err}'}
                    
                # Guarda raw_gemini_img en _1_RAW_GEMINI y python_pro_img en _2_MESA_REVISION_CARLOS, resolviendo ambos Drive IDs por separado.
                res = route_and_save_photo(prep_img, raw_gemini_img, python_pro_img, row_data, qa, t_latencia)
                # Extrae el Google Drive File ID de la versión pulida por Python en _2_MESA_REVISION_CARLOS.
                mesa_drive_id = res.get('mesa_id') or ''
                # Construye el enlace directo de visualización de la versión pulida por Python.
                link_drive_mesa = res.get('mesa_link') or (f'https://drive.google.com/file/d/{mesa_drive_id}/view' if mesa_drive_id else '')
                # Extrae el Google Drive File ID de la versión pura de Gemini en _1_RAW_GEMINI.
                raw_drive_id = res.get('raw_id') or ''
                # Construye el enlace directo de visualización de la versión pura de Gemini en _1_RAW_GEMINI.
                link_drive_raw = res.get('raw_link') or (f'https://drive.google.com/file/d/{raw_drive_id}/view' if raw_drive_id else '')
                
                # Agrupa todas las actualizaciones de celdas de esta fila en UNA SOLA llamada batch_update (ahorra ~10 segundos de red por foto).
                updates_batch = []
                def _add_upd(col_idx, val):
                    if col_idx and val is not None:
                        col_letter = gspread.utils.rowcol_to_a1(sheet_row_num, col_idx)
                        updates_batch.append({'range': col_letter, 'values': [[val]]})
                
                _add_upd(col_estado, 'PENDIENTE_REVISION_CARLOS')
                _add_upd(col_ruta_pro_cliente, res.get('ruta_carpeta_pro_rel'))
                _add_upd(col_nombre_pro_cliente, res.get('nombre_archivo_pro_cliente'))
                _add_upd(col_score_qa, str(res['score_qa']))
                _add_upd(col_motivo_qa, res['motivo_qa'])
                _add_upd(col_delta_e, str(res['delta_e']))
                _add_upd(col_latencia, str(res['latencia']))
                _add_upd(col_dest_pro, res['ruta_mesa_revision'])
                if mesa_drive_id: _add_upd(col_id_pro, mesa_drive_id)
                if link_drive_mesa: _add_upd(col_link_pro, link_drive_mesa)
                if raw_drive_id: _add_upd(col_id_raw, raw_drive_id)
                if link_drive_raw: _add_upd(col_link_raw, link_drive_raw)
                if orig_drive_id and orig_drive_id != '-':
                    _add_upd(col_v_orig, f'=IMAGE("https://lh3.googleusercontent.com/d/{orig_drive_id}=s400")')
                if mesa_drive_id:
                    _add_upd(col_v_pro, f'=IMAGE("https://lh3.googleusercontent.com/d/{mesa_drive_id}=s400")')
                
                # Ejecuta todas las escrituras de la fila en una sola petición HTTP hacia Google Sheets.
                sheet_maestro.batch_update(updates_batch, value_input_option='USER_ENTERED')
                
                # Confirma en consola que la imagen quedó guardada en Drive y asentada en la hoja maestra con su puntaje y tiempo.
                print(f'   ✅ Listo en Mesa de Revisión (Score {res["score_qa"]}/100 | {t_latencia}s)')
                # Muestra vista previa controlada cada MOSTRAR_PREVIEW_CADA_N fotos para no saturar la RAM del navegador en lotes de 200+.
                if MOSTRAR_PREVIEW_CADA_N and (idx == 1 or idx % MOSTRAR_PREVIEW_CADA_N == 0):
                    thumb = python_pro_img.copy()
                    thumb.thumbnail((360, 480))
                    display(thumb)
            # Si Gemini no devolvió imagen (por ejemplo, bloqueo o error de red agotando reintentos), entra aquí.
            else:
                # Registra en la columna 'Estado' de la hoja maestra el estado 'ERROR_API_GEMINI' para identificarla fácilmente.
                sheet_maestro.update_cell(sheet_row_num, col_estado, 'ERROR_API_GEMINI')
                # Imprime en consola el mensaje de error devuelto por la API.
                print(f'   ❌ Fallo API Gemini: {err}')
        # Captura cualquier otra excepción inesperada durante el procesamiento de esta fila.
        except Exception as exc:
            # Muestra el error en consola y continúa con la siguiente foto del lote sin abortar la corrida.
            print(f'   ❌ Excepción: {exc}')
        # Hace una pausa breve de 1 segundo entre fotos para mantener fluidez sin exceder cuotas.
        time.sleep(1)
    # Al terminar las fotos del bucle, muestra el mensaje de finalización del lote.
    print(f'\n🎉 Lote de {len(chunk)} fotos finalizado. Revisa en {TAB_MAESTRO} o en tu Tablero Web para aprobar.')


# ============================================================
# CELDA 8
# ============================================================
# 🎯 PASO 8: SINCRONIZAR DECISIONES DEL TABLERO WEB EN GOOGLE SHEETS Y PROMOVER APROBADAS AL CATÁLOGO FINAL
# 🔒 SEGURO DE ACTIVACIÓN MANUAL: En False impide que "Ejecutar todo" mueva o apruebe fotos sin que las hayas revisado manualmente.
EJECUTAR_PASO_8_CONSOLIDACION = False

# Pega aquí con 1 clic el diccionario copiado desde el botón "📋 Copiar Decisiones para Celda #8" de index.html:
DECISIONES_WEB = {}

if not EJECUTAR_PASO_8_CONSOLIDACION:
    print('🔒 [PASO 8 EN ESPERA] Consolidación desactivada por seguridad (compatible con "Ejecutar todo"). Cambia EJECUTAR_PASO_8_CONSOLIDACION = True solo cuando quieras asentar tus aprobaciones.')
else:
    print('📦 Sincronizando decisiones de validación y consolidando fotos aprobadas en Catálogo Maestro...')
    all_records = sheet_maestro.get_all_records()
    headers = sheet_maestro.row_values(1)

    col_estado = headers.index('Estado') + 1
    col_dest_pro = headers.index('Ruta_Destino_PRO') + 1 if 'Ruta_Destino_PRO' in headers else None
    col_id_pro = headers.index('ID_Archivo_PRO') + 1 if 'ID_Archivo_PRO' in headers else None
    col_link_pro = headers.index('Link_Drive_PRO') + 1 if 'Link_Drive_PRO' in headers else None
    col_v_pro = headers.index('Vista_PRO') + 1 if 'Vista_PRO' in headers else None
    col_motivo_rechazo = headers.index('Motivo_Rechazo') + 1 if 'Motivo_Rechazo' in headers else None

    promovidas = 0
    rechazadas_sync = 0
    batch_cells = []

    def _queue_cell(r_num, c_idx, val):
        if c_idx and val is not None:
            batch_cells.append({'range': gspread.utils.rowcol_to_a1(r_num, c_idx), 'values': [[val]]})

    for sheet_row_num, row in enumerate(all_records, start=2):
        rid = str(row.get('ID', '')).strip()
        estado = str(row.get('Estado', '')).upper()
        ruta_mesa = str(row.get('Ruta_Destino_PRO', ''))
        
        # 1. Si el ID viene en DECISIONES_WEB (copiado desde index.html), aplicamos la decisión del usuario:
        if rid in DECISIONES_WEB:
            dec_info = DECISIONES_WEB[rid]
            st_web = dec_info.get('status', '') if isinstance(dec_info, dict) else str(dec_info)
            reason_web = dec_info.get('reason', '') if isinstance(dec_info, dict) else ''
            
            if st_web == 'RECHAZADO':
                _queue_cell(sheet_row_num, col_estado, 'RECHAZADO_CARLOS')
                if col_motivo_rechazo:
                    _queue_cell(sheet_row_num, col_motivo_rechazo, reason_web or 'Marcado Incorrecto en Tablero Web')
                rechazadas_sync += 1
                print(f'   ❌ ID {rid}: Marcado como RECHAZADO_CARLOS en fila {sheet_row_num} ({reason_web})')
                continue
            elif st_web in ('APROBADO_PYTHON', 'APROBADO_GEMINI', 'APROBADO'):
                estado = 'APROBADO_CARLOS'
                # Si eligió aprobar la versión pura de Gemini (_1_RAW_GEMINI), usamos su archivo e ID raw:
                if st_web == 'APROBADO_GEMINI':
                    raw_id_col = str(row.get('ID_Archivo_Gemini_Raw', '')).strip()
                    if raw_id_col and raw_id_col != '-':
                        _queue_cell(sheet_row_num, col_id_pro, raw_id_col)
                        _queue_cell(sheet_row_num, col_link_pro, f'https://drive.google.com/file/d/{raw_id_col}/view')
                        _queue_cell(sheet_row_num, col_v_pro, f'=IMAGE("https://lh3.googleusercontent.com/d/{raw_id_col}=s400")')

        # 2. Promover a _3_CATALOGO_FINAL_APROBADO solo si fue aprobado explícitamente por Carlos:
        if (rid in DECISIONES_WEB and estado == 'APROBADO_CARLOS') or estado == 'APROBADO_CARLOS':
            if '_2_MESA_REVISION_CARLOS' in ruta_mesa and Path(ruta_mesa).exists():
                mesa_path = Path(ruta_mesa)
                destino_final = DIR_3_CATALOGO_FINAL / mesa_path.name.replace('_score', '_PRO_score')
                shutil.copy2(mesa_path, destino_final)
                final_id, final_link = sync_and_resolve_drive_file_id(destino_final, FOLDER_ID_3_CATALOGO_FINAL, creds)
                _queue_cell(sheet_row_num, col_dest_pro, str(destino_final))
                if final_id: _queue_cell(sheet_row_num, col_id_pro, final_id)
                if final_link: _queue_cell(sheet_row_num, col_link_pro, final_link)
                if final_id: _queue_cell(sheet_row_num, col_v_pro, f'=IMAGE("https://lh3.googleusercontent.com/d/{final_id}=s400")')
            _queue_cell(sheet_row_num, col_estado, 'APROBADO_OFICIAL')
            promovidas += 1
            print(f'   ✨ ID {rid}: APROBADO_OFICIAL en fila {sheet_row_num}')

    if batch_cells:
        sheet_maestro.batch_update(batch_cells, value_input_option='USER_ENTERED')

    print(f'🏆 Sincronización finalizada: {promovidas} fotos APROBADAS y {rechazadas_sync} marcadas para REINTENTO en {TAB_MAESTRO}.')
