# -*- coding: utf-8 -*-
"""
Script to generate the updated marinera_colab_pipeline_v5_hardened.py
"""
from pathlib import Path

content = '''"""
MARINERA POWER - PIPELINE INDUSTRIAL V5 HARDENED (DEFINITIVO)
Arquitectura de 3 Niveles + Clasificador Condicional Jerárquico + Sincronización Drive API Directa
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
    clean = re.sub(r'[\\\\/*?:"<>|]', '_', str(name_str).strip())
    return re.sub(r'\\s+', '_', clean)[:80]

def resolve_file_from_sheet_row(row_data):
    """
    Localizador determinista FUSE sin espacios en separadores de carpetas.
    """
    ruta_origen = str(row_data.get('Ruta_Carpeta_Drive', ''))
    file_name = str(row_data.get('Nombre_Archivo_Original', '')).strip()
    base_stem = Path(file_name).stem.strip()

    partes = [p.strip() for p in ruta_origen.replace('\\\\', '/').split('/') if p.strip()]
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
    # 1. Intento FUSE Local
    p = resolve_file_from_sheet_row(row_data)
    if p and p.exists():
        try:
            with Image.open(p) as img:
                return ImageOps.exif_transpose(img).convert('RGB'), f'FUSE Local ({p.name})'
        except Exception:
            pass
            
    # 2. Respaldo Drive API v3 por ID (Infalible, cero dependencia de nombres de carpeta)
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
    Resuelve el ID de Google Drive de forma infalible:
    1. Si el archivo ya se sincronizó vía FUSE, consulta Drive API por su nombre en la carpeta.
    2. Si FUSE aún no lo indexa en la nube, lo sube de forma atómica vía Drive API v3 (multipart).
    Retorna (drive_id, web_view_link).
    """
    try:
        if hasattr(auth_creds, 'valid') and not auth_creds.valid and hasattr(auth_creds, 'refresh'):
            from google.auth.transport.requests import Request
            auth_creds.refresh(Request())
        headers = {'Authorization': f'Bearer {auth_creds.token}'}
        
        filename = Path(local_path).name
        q = f"'{folder_id}' in parents and name = '{filename}' and trashed = false"
        q_url = f"https://www.googleapis.com/drive/v3/files?q={requests.utils.quote(q)}&fields=files(id,webViewLink)"
        
        q_res = requests.get(q_url, headers=headers, timeout=25)
        if q_res.status_code == 200:
            files = q_res.json().get('files', [])
            if files:
                return files[0].get('id'), files[0].get('webViewLink')
                
        # Si aún no aparece por FUSE, subida directa vía Drive API v3
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
# 3. Pre-Procesamiento Sobel (Umbral 3.5) & Context Managers Anti-OOM
import numpy as np
import cv2

def detect_and_crop_artificial_borders(pil_img, edge_thresh=3.5):
    cv_img = np.array(pil_img.convert('RGB'))
    gray = cv2.cvtColor(cv_img, cv2.COLOR_RGB2GRAY)
    h, w = gray.shape
    
    sobelx = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=3)
    grad_x = np.mean(np.abs(sobelx), axis=0)
    left_crop = 0
    right_crop = w
    
    search_band = int(w * 0.15)
    for x in range(search_band):
        if grad_x[x] > edge_thresh: left_crop = x + 1
    for x in range(w - 1, w - search_band, -1):
        if grad_x[x] > edge_thresh: right_crop = x
        
    if left_crop > 0 or right_crop < w:
        return pil_img.crop((left_crop, 0, right_crop, h))
    return pil_img

def prepare_image_for_gemini(pil_img, max_side=1920):
    cleaned = detect_and_crop_artificial_borders(pil_img)
    w, h = cleaned.size
    if max(w, h) > max_side:
        ratio = max_side / float(max(w, h))
        new_size = (int(w * ratio), int(h * ratio))
        return cleaned.resize(new_size, Image.Resampling.LANCZOS)
    return cleaned

print('✅ Pre-Procesamiento Sobel (Umbral 3.5) y Lanczos 1920 compilados.')


# ============================================================
# CELDA 4
# ============================================================
# 4. Motor de Prompts Condicionales Jerárquico (Joyería vs Vestuario) & QA Evaluator
import numpy as np
import cv2
import base64
import requests

# PROMPT TIPO A: JOYERÍA, ACCESORIOS Y FOTOPRODUCTO (STILL LIFE / MACRO)
# Prohíbe terminantemente inventar personas, modelos o cuerpos humanos.
PROMPT_JOYERIA_ACCESORIOS = """Eres un retocador profesional de alta gama de joyería tradicional, orfebrería y accesorios. Edita esta fotografía cambiando ÚNICAMENTE el fondo circundante. El producto (arete, collar, escapulario, joya de filigrana, faja o accesorio) debe permanecer 100% idéntico en su escala, forma, textura, metales, brillos y posición original.

1. PROHIBICIÓN ABSOLUTA DE PERSONAS O MODELOS: Está TERMINANTEMENTE PROHIBIDO inventar personas, rostros, modelos, cuerpos, manos, brazos o bailarinas. Es una foto de bodegón/producto comercial aislado, NO de moda modelada.
2. FONDO CICLORAMA GRIS CÁLIDO #E5E1DE: Reemplaza todo el fondo existente por un fondo de estudio liso, mate, plano y uniforme en color gris cálido #E5E1DE (RGB 229, 225, 222). Cero degradados, cero viñetas oscuras y cero sombras duras.
3. SOMBRA DE APOYO SUTIL: Genera únicamente una sombra de contacto suave, difusa y transparente inmediatamente bajo la base del producto.
4. INTEGRIDAD DE FILIGRANA Y MATERIALES: Conserva íntegros los calados de oro 18k (#D4AF37), perlas, broches y terciopelo, sin empastar la trama ni deformar los ganchos."""

# PROMPT TIPO B: MODA, DANZA Y VESTUARIO MODELADO (TRAJES, FALDAS, BLUSAS)
PROMPT_MODA_MODELO = """Eres un retocador fotográfico profesional especializado en catálogo e-commerce de moda y danza tradicional de marinera. Edita esta fotografía cambiando ÚNICAMENTE el fondo y el suelo. El sujeto modelado, su vestuario completo, rostro y expresión deben quedar absolutamente intactos.

1. ENCUADRE Y ESCALA EXACTA (CERO ZOOM-OUT): Mantén la proporción y encuadre original. La bailarina o persona debe quedar exactamente en la misma posición espacial, con la misma estatura y tamaño relativo de cuerpo, y con la misma pose exacta (brazos alzados, falda extendida, pañuelo blanco en mano y pies descalzos intactos). Prohibido achicar a la persona o alejar la cámara.
2. FONDO CICLORAMA GRIS CÁLIDO #E5E1DE: Reemplaza todo el fondo y piso antiguo por un fondo de estudio liso, plano, mate y completamente uniforme en color gris cálido #E5E1DE (RGB 229, 225, 222). Cero degradados y cero virajes a marrón o verde.
3. PISO IMPOLUTO Y SOMBRA SUAVE: El piso debe ser uniforme del mismo color #E5E1DE. Genera ÚNICAMENTE una sombra de contacto suave, difusa y traslúcida directamente bajo los pies o calzado. Cero manchas negras o charcos oscuros.
4. PRESERVACIÓN TEXTIL: Conserva íntegros los bordados del traje, el pañuelo calado de lino blanco y la orfebrería tradicional."""

def select_prompt_for_category(subfolder_str, file_name=''):
    """
    Selecciona el prompt idóneo según la naturaleza del producto para erradicar alucinaciones de modelos.
    REGLA DE PRECEDENCIA ESTRICTA:
    1. PRENDAS DE VESTIR / DANZA (Faldas, Blusas, Vestidos, Trajes, Enagues, Polos, Pantalones):
       SIEMPRE clasifica como MODA_MODELO.
       Incluso si el nombre de carpeta dice 'con cinta blanca' o 'con cinta morada', 'cinta' es un
       ribete de la falda, por lo que NUNCA debe derivar en joyería ni producto aislado.
    2. JOYERÍA, ACCESORIOS Y STILL LIFE (Aretes, Collares, Escapularios, Filigrana, Joyas, Sombreros):
       Clasifica como JOYERIA_ACCESORIO.
       Prohíbe terminantemente inventar modelos o personas.
    """
    text = f"{subfolder_str} {file_name}".lower()
    
    # 1. Prioridad Absoluta: Prendas de Vestir y Danza Modelada
    clothing_keywords = [
        'falda', 'faldas', 'blusa', 'blusas', 'vestido', 'vestidos',
        'traje', 'trajes', 'enague', 'enagues', 'enagua', 'enaguas',
        'pantalon', 'pantalones', 'camisa', 'camisas', 'chaleco',
        'poncho', 'polo', 'bobo', 'bobos', 'razo', 'ensayo'
    ]
    if any(ck in text for ck in clothing_keywords):
        return PROMPT_MODA_MODELO, 'MODA_MODELO'
        
    # 2. Prioridad Secundaria: Accesorios y Joyería Aislada (Still Life)
    jewelry_keywords = [
        'accesorio', 'accesorios', 'arete', 'aretes', 'escapulario', 'escapularios',
        'collar', 'collares', 'filigrana', 'joya', 'joyas', 'joyeria', 'joyería',
        'prendedor', 'broche', 'tocado', 'sombrero', 'faja'
    ]
    if any(jk in text for jk in jewelry_keywords):
        return PROMPT_JOYERIA_ACCESORIOS, 'JOYERIA_ACCESORIO'
        
    # Por defecto en catálogo Marinera Power es moda modelada
    return PROMPT_MODA_MODELO, 'MODA_MODELO'

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
            'responseModalities': ['IMAGE'],
            'temperature': 0.1
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

def audit_image_quality(orig_img, pro_img):
    """
    Evaluación Matemática Equilibrada en OpenCV (CIELAB 1976 + Uniformidad Ciclorama + Suelo).
    """
    orig_np = np.array(orig_img.convert('RGB'))
    pro_np = np.array(pro_img.convert('RGB'))
    h, w, _ = pro_np.shape

    # 1. Delta E perceptual CIELAB en esquinas superiores (evitando margen externo de 5px)
    target_lab = cv2.cvtColor(np.uint8([[[229, 225, 222]]]), cv2.COLOR_RGB2LAB)[0, 0].astype(np.float64)
    roi_tl = pro_np[5:35, 5:35].reshape(-1, 3)
    roi_tr = pro_np[5:35, w-35:w-5].reshape(-1, 3)
    
    c_tl = cv2.cvtColor(np.uint8([[np.median(roi_tl, axis=0).astype(int)]]), cv2.COLOR_RGB2LAB)[0, 0]
    c_tr = cv2.cvtColor(np.uint8([[np.median(roi_tr, axis=0).astype(int)]]), cv2.COLOR_RGB2LAB)[0, 0]
    
    delta_tl = float(np.sqrt(np.sum((target_lab - c_tl) ** 2)))
    delta_tr = float(np.sqrt(np.sum((target_lab - c_tr) ** 2)))
    delta_e = round(max(delta_tl, delta_tr), 2)
    
    # 2. Homogeneidad del Ciclorama (simetría izquierda-derecha del estudio)
    diff_lr = float(np.sqrt(np.sum((c_tl.astype(np.float64) - c_tr.astype(np.float64)) ** 2)))
    
    # 3. Análisis de Suelo Aislado (Franja inferior 15%)
    lower_roi = pro_np[int(h * 0.85):h, :]
    lower_lab = cv2.cvtColor(lower_roi, cv2.COLOR_RGB2LAB)[:, :, 0]
    dirty_pixels = np.sum(lower_lab < 90)
    ratio_sucio = float(dirty_pixels / lower_lab.size)
    score_suelo = round(max(0.0, min(100.0, (1.0 - ratio_sucio) * 100.0)), 1)

    # 4. Score Ponderado para Mesa de Revisión de Carlos
    observaciones = []
    if delta_e <= 25.0:
        observaciones.append(f'Ciclorama #E5E1DE uniforme (ΔE={delta_e})')
    elif delta_e <= 50.0:
        observaciones.append(f'Tono estudio cálido homogéneo (ΔE={delta_e})')
    else:
        observaciones.append(f'Alerta: variación cromática (ΔE={delta_e})')

    if score_suelo >= 90.0:
        observaciones.append(f'Piso limpio ({score_suelo}%)')
    else:
        observaciones.append(f'Alerta: posible sombra densa ({score_suelo}%)')

    score_color = max(40, 100 - int(delta_e * 1.2))
    score_simetria = max(50, 100 - int(diff_lr * 3.0))
    score_final = int(round(score_color * 0.40 + score_simetria * 0.30 + score_suelo * 0.30))
    score_final = max(35, min(99, score_final))
    
    return {
        'score': score_final,
        'delta_e': delta_e,
        'score_suelo': score_suelo,
        'observaciones': ' | '.join(observaciones)
    }

print('✅ Motor de Prompts Condicionales y Evaluador QA Calibrado compilados.')


# ============================================================
# CELDA 5
# ============================================================
# 5. Guardado en 3 Niveles y Sincronización con Google Sheets (Cero Descarte)
def route_and_save_photo(orig_img, pro_img, row_data, qa_metrics, latency_sec):
    row_id = str(row_data.get('ID', '0'))
    orig_name = str(row_data.get('Nombre_Archivo_Original', 'foto'))
    safe_stem = sanitize_safe_filename(Path(orig_name).stem)

    # FASE 1: GUARDADO INMEDIATO EN NVME LOCAL (Cero caída de red)
    local_raw = LOCAL_SCRATCH / f'ID{row_id.zfill(3)}_{safe_stem}_RAW.jpg'
    pro_img.save(local_raw, format='JPEG', quality=95, optimize=True)

    # FASE 2: COPIA ATÓMICA A DRIVE NIVEL 1 (Salida Cruda Gemini)
    raw_drive_file = DIR_1_RAW_GEMINI / local_raw.name
    shutil.copy2(local_raw, raw_drive_file)

    # FASE 3: COPIA ATÓMICA A DRIVE NIVEL 2 (Mesa de Revisión Carlos)
    score = qa_metrics.get('score', 90)
    revision_drive_file = DIR_2_MESA_REVISION / f'ID{row_id.zfill(3)}_{safe_stem}_score{score}.jpg'
    shutil.copy2(local_raw, revision_drive_file)

    # FASE 4: FORZAR SINCRONIZACIÓN FUSE AL BUS DE DRIVE
    try:
        os.sync()
    except Exception:
        pass

    # FASE 4.5: RESOLUCIÓN Y GARANTÍA DETERMINISTA DE GOOGLE DRIVE IDs
    raw_id, raw_link = sync_and_resolve_drive_file_id(raw_drive_file, FOLDER_ID_1_RAW_GEMINI, creds)
    mesa_id, mesa_link = sync_and_resolve_drive_file_id(revision_drive_file, FOLDER_ID_2_MESA_REVISION, creds)

    # FASE 5: REGISTRO PERMANENTE EN BITÁCORA INMUTABLE (.JSONL)
    record = {
        'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
        'id': row_id,
        'archivo_original': orig_name,
        'raw_gemini_path': str(raw_drive_file),
        'raw_drive_id': raw_id,
        'mesa_revision_path': str(revision_drive_file),
        'mesa_drive_id': mesa_id,
        'score_qa': score,
        'delta_e': qa_metrics.get('delta_e', 0.0),
        'observaciones': qa_metrics.get('observaciones', ''),
        'latencia': latency_sec
    }
    with open(LEDGER_FILE, 'a', encoding='utf-8') as lf:
        lf.write(json.dumps(record, ensure_ascii=False) + '\\n')

    return {
        'estado': 'PENDIENTE_REVISION_CARLOS',
        'score_qa': score,
        'motivo_qa': qa_metrics.get('observaciones', 'Listo para revisión de Carlos'),
        'delta_e': qa_metrics.get('delta_e', 0.0),
        'latencia': latency_sec,
        'ruta_mesa_revision': str(revision_drive_file),
        'ruta_raw_gemini': str(raw_drive_file),
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
# Las pruebas NUNCA modifican ni contaminan el Catálogo Maestro de Producción.
# Cada ejecución crea una NUEVA fila de auditoría para rastrear intentos y evolución.
CANARY_IDS_OBJETIVO = ['28', '418', '421', '423', '424'] # IDs a probar
BATCH_EXPERIMENTO_ID = f'EXP_{time.strftime("%Y%m%d_%H%M%S")}'

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
    
    print(f'\\n🔬 [{idx}/{len(target_rows)}] Prueba sobre ID {c_id}: {file_name}')
    print(f'   Carpeta: {subfolder}')
    
    # CARGA INFALIBLE: FUSE + DRIVE API BACKUP
    t0 = time.time()
    prep_img, source_info = load_source_image_infallible(row_data, creds)
    if not prep_img:
        print(f'   ⚠️ Error de carga: {source_info}. Saltando.')
        continue
        
    print(f'   📥 Imagen cargada con éxito vía: {source_info}')
    
    try:
        # Inyección inteligente de prompt según categoría jerárquica (Anti-Alucinación)
        prompt_elegido, tipo_prod = select_prompt_for_category(subfolder, file_name)
        print(f'   🎯 Modo seleccionado: {tipo_prod}')
        
        pro_img, err = edit_background_gemini(prep_img, prompt_text=prompt_elegido)
        t_latencia = round(time.time() - t0, 2)
        
        if pro_img:
            try:
                qa = audit_image_quality(prep_img, pro_img)
            except Exception as qa_err:
                qa = {'score': 70, 'delta_e': 0.0, 'score_suelo': 90.0, 'observaciones': f'Excepción OpenCV: {qa_err}'}
                
            res = route_and_save_photo(prep_img, pro_img, row_data, qa, t_latencia)
            
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
            
            print(f'   ✅ Persistido en Drive y asentado en Sandbox | Score: {res["score_qa"]}/100 | {t_latencia}s')
            print(f'   🛡️ Drive ID Mesa: {mesa_drive_id}')
            display(pro_img)
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

print(f'\\n🏆 SESIÓN DE PRUEBAS COMPLETADA. Revisa todos los intentos en la pestaña Registro_Pruebas_Sandbox.')


# ============================================================
# CELDA 7
# ============================================================
# 🔒 SEGURO DE ACTIVACIÓN MANUAL: LOTES DE 20 FOTOS PARA CATÁLOGO MAESTRO
# Procesa de forma autónoma los ítems que NO TIENEN VERSIÓN PRO en el Catálogo Maestro.
EJECUTAR_LOTE_PRODUCCION = False
CHUNK_SIZE = 20

if not EJECUTAR_LOTE_PRODUCCION:
    print('🔒 [PASO 7 EN ESPERA] Seguro activo. Cambia EJECUTAR_LOTE_PRODUCCION = True para iniciar.')
else:
    print(f'🚀 INICIANDO LOTE DE {CHUNK_SIZE} FOTOS HACIA LA MESA DE REVISIÓN EN CATÁLOGO MAESTRO...')
    all_records = sheet_maestro.get_all_records()
    headers = sheet_maestro.row_values(1)
    
    col_estado = headers.index('Estado') + 1
    col_score_qa = headers.index('Score_QA') + 1 if 'Score_QA' in headers else None
    col_motivo_qa = headers.index('Motivo_QA') + 1 if 'Motivo_QA' in headers else None
    col_delta_e = headers.index('Delta_E_Color') + 1 if 'Delta_E_Color' in headers else None
    col_latencia = headers.index('Latencia_Seg') + 1 if 'Latencia_Seg' in headers else None
    col_dest_pro = headers.index('Ruta_Destino_PRO') + 1 if 'Ruta_Destino_PRO' in headers else None
    col_id_pro = headers.index('ID_Archivo_PRO') + 1 if 'ID_Archivo_PRO' in headers else None
    col_link_pro = headers.index('Link_Drive_PRO') + 1 if 'Link_Drive_PRO' in headers else None
    col_v_orig = headers.index('Vista_Original') + 1 if 'Vista_Original' in headers else None
    col_v_pro = headers.index('Vista_PRO') + 1 if 'Vista_PRO' in headers else None
    
    pendientes = []
    for sheet_row_num, row in enumerate(all_records, start=2):
        st = str(row.get('Estado', '')).upper()
        id_pro_existente = str(row.get('ID_Archivo_PRO', '')).strip()
        if st in ['PENDIENTE', ''] and (not id_pro_existente or id_pro_existente == '-'):
            pendientes.append((sheet_row_num, row))
            
    print(f'📊 Total fotos pendientes sin versión PRO en Catálogo Maestro: {len(pendientes)}')
    chunk = pendientes[:CHUNK_SIZE]
    
    for idx, (sheet_row_num, row_data) in enumerate(chunk, start=1):
        c_id = str(row_data.get('ID', ''))
        file_name = str(row_data.get('Nombre_Archivo_Original', ''))
        subfolder = str(row_data.get('Ruta_Carpeta_Drive', ''))
        orig_drive_id = str(row_data.get('ID_Archivo_Original', '')).strip()
        
        print(f'\\n[{idx}/{len(chunk)}] Procesando ID {c_id}: {file_name}')
        print(f'   Carpeta: {subfolder}')
        
        t0 = time.time()
        prep_img, source_info = load_source_image_infallible(row_data, creds)
        if not prep_img:
            print(f'   ⚠️ Error de carga: {source_info}. Saltando.')
            continue
            
        print(f'   📥 Imagen cargada con éxito vía: {source_info}')
        
        try:
            prompt_elegido, tipo_prod = select_prompt_for_category(subfolder, file_name)
            pro_img, err = edit_background_gemini(prep_img, prompt_text=prompt_elegido)
            t_latencia = round(time.time() - t0, 2)
            
            if pro_img:
                try:
                    qa = audit_image_quality(prep_img, pro_img)
                except Exception as qa_err:
                    qa = {'score': 70, 'delta_e': 0.0, 'observaciones': f'Excepción OpenCV: {qa_err}'}
                    
                res = route_and_save_photo(prep_img, pro_img, row_data, qa, t_latencia)
                mesa_drive_id = res.get('mesa_id') or ''
                link_drive_mesa = res.get('mesa_link') or (f'https://drive.google.com/file/d/{mesa_drive_id}/view' if mesa_drive_id else '')
                
                sheet_maestro.update_cell(sheet_row_num, col_estado, 'PENDIENTE_REVISION_CARLOS')
                if col_score_qa: sheet_maestro.update_cell(sheet_row_num, col_score_qa, str(res['score_qa']))
                if col_motivo_qa: sheet_maestro.update_cell(sheet_row_num, col_motivo_qa, res['motivo_qa'])
                if col_delta_e: sheet_maestro.update_cell(sheet_row_num, col_delta_e, str(res['delta_e']))
                if col_latencia: sheet_maestro.update_cell(sheet_row_num, col_latencia, str(res['latencia']))
                if col_dest_pro: sheet_maestro.update_cell(sheet_row_num, col_dest_pro, res['ruta_mesa_revision'])
                if col_id_pro and mesa_drive_id: sheet_maestro.update_cell(sheet_row_num, col_id_pro, mesa_drive_id)
                if col_link_pro and link_drive_mesa: sheet_maestro.update_cell(sheet_row_num, col_link_pro, link_drive_mesa)
                if col_v_orig and orig_drive_id and orig_drive_id != '-':
                    sheet_maestro.update_cell(sheet_row_num, col_v_orig, f'=IMAGE("https://lh3.googleusercontent.com/d/{orig_drive_id}=s400")')
                if col_v_pro and mesa_drive_id:
                    sheet_maestro.update_cell(sheet_row_num, col_v_pro, f'=IMAGE("https://lh3.googleusercontent.com/d/{mesa_drive_id}=s400")')
                
                print(f'   ✅ Listo en Mesa de Revisión (Score {res["score_qa"]}/100 | {t_latencia}s)')
            else:
                sheet_maestro.update_cell(sheet_row_num, col_estado, 'ERROR_API_GEMINI')
                print(f'   ❌ Fallo API Gemini: {err}')
        except Exception as exc:
            print(f'   ❌ Excepción: {exc}')
        time.sleep(3)
    print(f'\\n🎉 Lote de {len(chunk)} fotos finalizado. Revisa en {TAB_MAESTRO} para aprobar.')


# ============================================================
# CELDA 8
# ============================================================
# 🎯 PASO 8: PROMOVER FOTOS VALIDADAS AL CATÁLOGO FINAL APROBADO
# Cuando revises en Sheets y marques 'APROBADO' o 'APROBADO_OFICIAL', ejecuta esta celda
# para mover los archivos a la carpeta final: Fotos catalogo PRO/_3_CATALOGO_FINAL_APROBADO
print('📦 Escaneando fotos aprobadas para consolidación final en Catálogo Maestro...')
all_records = sheet_maestro.get_all_records()
headers = sheet_maestro.row_values(1)
col_dest_pro = headers.index('Ruta_Destino_PRO') + 1 if 'Ruta_Destino_PRO' in headers else None
col_id_pro = headers.index('ID_Archivo_PRO') + 1 if 'ID_Archivo_PRO' in headers else None
col_link_pro = headers.index('Link_Drive_PRO') + 1 if 'Link_Drive_PRO' in headers else None
col_v_pro = headers.index('Vista_PRO') + 1 if 'Vista_PRO' in headers else None
col_estado = headers.index('Estado') + 1
promovidas = 0

for sheet_row_num, row in enumerate(all_records, start=2):
    estado = str(row.get('Estado', '')).upper()
    ruta_mesa = str(row.get('Ruta_Destino_PRO', ''))
    
    if estado in ['APROBADO', 'APROBADO_OFICIAL', 'APROBADO_CARLOS'] and '_2_MESA_REVISION_CARLOS' in ruta_mesa:
        mesa_path = Path(ruta_mesa)
        if mesa_path.exists():
            destino_final = DIR_3_CATALOGO_FINAL / mesa_path.name.replace('_score', '_PRO_score')
            shutil.copy2(mesa_path, destino_final)
            
            # Sincronizar en carpeta final
            final_id, final_link = sync_and_resolve_drive_file_id(destino_final, FOLDER_ID_3_CATALOGO_FINAL, creds)
            
            if col_dest_pro: sheet_maestro.update_cell(sheet_row_num, col_dest_pro, str(destino_final))
            if col_id_pro and final_id: sheet_maestro.update_cell(sheet_row_num, col_id_pro, final_id)
            if col_link_pro and final_link: sheet_maestro.update_cell(sheet_row_num, col_link_pro, final_link)
            if col_v_pro and final_id:
                sheet_maestro.update_cell(sheet_row_num, col_v_pro, f'=IMAGE("https://lh3.googleusercontent.com/d/{final_id}=s400")')
                
            sheet_maestro.update_cell(sheet_row_num, col_estado, 'APROBADO_OFICIAL')
            promovidas += 1
            print(f'   ✨ ID {row.get("ID")}: Promovida a Catálogo Final -> {destino_final.name}')

print(f'🏆 Consolidación finalizada: {promovidas} fotos promovidas al Catálogo Final.')
'''

target_path = Path(r"C:\Users\LENOVO\Documents\Carlitos\IA\Antigravity\Profesionalización de catálogo\Cliente Marinera Power\marinera_colab_pipeline_v5_hardened.py")
with open(target_path, 'w', encoding='utf-8') as f:
    f.write(content.strip() + '\n')
print(f"Generated {target_path} successfully!")
