# ==============================================================================
# PIPELINE MAESTRO INDUSTRIAL V4: MARINERA POWER CATALOGO PRO
# Plataforma: Google Colab (Python 3.10+)
# Modelo IA: gemini-2.5-flash-image (Invocación Multimodal Oficial)
# Integración: Google Sheets 'Control_Total_Drive_V2' + Google Drive FUSE
# ==============================================================================

import os
import io
import gc
import re
import time
import shutil
import random
import unicodedata
from datetime import datetime
from functools import wraps
from typing import Tuple, Dict, Any, Optional, List

import numpy as np
import cv2
from PIL import Image, ImageOps
import pillow_heif

# Servicios Google y SDK Gemini
from google.colab import drive, auth
import gspread
from gspread.utils import rowcol_to_a1
from google.auth import default
from google import genai
from google.genai import types
from google.genai.errors import APIError

# ------------------------------------------------------------------------------
# 1. PARÁMETROS GLOBALES Y BANDERAS DE SEGURIDAD
# ------------------------------------------------------------------------------
HABILITAR_BUCLE_MASIVO: bool = False  # False: 1 foto de prueba | True: corrida total (762 fotos)
VERSION_PROMPT: str = "v4.0_canary_adjusted_clean_floor_anti_zoomout"

# Entornos de almacenamiento
LOCAL_SCRATCH_DIR = "/content/local_scratch"
DRIVE_MOUNT_POINT = "/content/drive"
BASE_DIR = os.path.join(DRIVE_MOUNT_POINT, "MyDrive/Emprendimiento/Marinera power 2026")
ORIGEN_PATH = os.path.join(BASE_DIR, "Fotos catalogo")
DESTINO_PRO_PATH = os.path.join(BASE_DIR, "Fotos catalogo PRO")
DESTINO_ERROR_PATH = os.path.join(BASE_DIR, "_Fotos_Erroneas_y_Desalineadas")

# Google Sheets
SHEET_ID = "1kRsCZ7ZpPxyxrSEkUrYRl3NHahrQQche90RKK2yedQ8"
SHEET_TAB_NAME = "Control_Proceso"

# Constantes del Quality Gate Físico y Fisiológico
HEX_COLOR_OBJETIVO = "#E5E1DE"
RGB_OBJETIVO = (229, 225, 222)        # Ciclorama estándar oficial
DELTA_E_MAX_TOLERADO = 7.5            # Umbral CIELAB 1976
SOBEL_UMBRAL_MAX_BORDE = 25.0         # Nitidez máxima permitida en perímetro exterior
MAX_BLANCO_PERIMETRO_PX = 250         # Detección de franjas de Instagram
RATIO_BLANCO_PERIMETRO_MAX = 0.05     # Máximo 5% de blanco puro perimetral
MIN_OCUPACION_VERTICAL = 0.45         # Mínimo 45% de ocupación vertical (Anti-Zoomout Canary 5)
MIN_LIMPIEZA_SUELO_PIES = 95.0        # Mínimo 95% de limpieza en suelo (Anti-Manchas Canary 3)

pillow_heif.register_heif_opener()
os.makedirs(LOCAL_SCRATCH_DIR, exist_ok=True)


# ------------------------------------------------------------------------------
# 2. PREPROCESAMIENTO DETERMINISTA LANCZOS / EXIF
# ------------------------------------------------------------------------------
def prepare_image_for_inference(file_path: str, max_dim: int = 1920) -> Tuple[Image.Image, Tuple[int, int]]:
    """
    Normalización de orientación física EXIF, conversión RGB y redimensionamiento
    Lanczos con cota máxima de 1920px para proteger la memoria de Colab y prevenir
    payloads gigantes de cámaras de 48MP.
    Retorna: (imagen_redimensionada, dimensiones_originales_wh)
    """
    with Image.open(file_path) as raw:
        corrected = ImageOps.exif_transpose(raw)
        if corrected is None:
            corrected = raw
        rgb_img = corrected.convert("RGB")
        orig_dims = rgb_img.size
        
        w, h = orig_dims
        if max(w, h) > max_dim:
            scale = max_dim / max(w, h)
            new_w = int(round(w * scale))
            new_h = int(round(h * scale))
            final_img = rgb_img.resize((new_w, new_h), Image.Resampling.LANCZOS)
        else:
            final_img = rgb_img.copy()
            
        return final_img, orig_dims


def resolve_target_aspect_ratio(orig_w: int, orig_h: int) -> str:
    """Calcula el aspect ratio nativo más representativo para evitar deformaciones."""
    ratio = orig_w / orig_h
    supported = {
        "9:16": 9 / 16,  # 0.5625 (Vertical completo / Story)
        "3:4": 3 / 4,    # 0.7500 (Vertical de catálogo de moda)
        "1:1": 1.0,      # 1.0000 (Cuadrado de producto)
        "4:3": 4 / 3,    # 1.3333 (Horizontal estándar)
        "16:9": 16 / 9   # 1.7777 (Panorámico)
    }
    return min(supported.keys(), key=lambda k: abs(supported[k] - ratio))


# ------------------------------------------------------------------------------
# 3. PROMPT MAESTRO EN LENGUAJE NATURAL DIRECTO (AJUSTADO POR CANARY TEST)
# ------------------------------------------------------------------------------
def build_natural_language_prompt(aspect_ratio_str: str, es_reintento: bool = False, zoom_fallido: bool = False, suelo_sucio: bool = False) -> str:
    """
    Prompt directo en lenguaje natural claro. Incorpora las lecciones del Canary Test:
    - Falla 1: Fondo estrictamente uniforme en gris cálido #E5E1DE (RGB 229, 225, 222).
    - Falla 2: Prohibido encoger a la bailarina o hacer zoom-out; encuadre y pose original intactos.
    - Falla 3: Suelo impoluto, sin parches negros de suciedad ni halos oscuros bajo los pies.
    """
    prompt = (
        "Eres un retocador profesional de fotografía de moda y catálogo comercial de alta gama. "
        "Edita esta fotografía cambiando únicamente el fondo, bajo las siguientes instrucciones estrictas:\n\n"
        f"1. ENCUADRE Y ESCALA EXACTA (SIN ZOOM-OUT): Mantén la proporción y encuadre original en formato {aspect_ratio_str}. "
        "La persona u objeto debe permanecer exactamente en la misma posición, con el mismo tamaño de cuerpo "
        "y exactamente la misma pose original (brazos alzados, falda de marinera, pañuelo blanco en mano y pies descalzos intactos), "
        "sin alejar la toma, sin achicar a la persona y sin hacer zoom-out. La persona debe llenar verticalmente la imagen como en el original.\n"
        "2. FONDO DE ESTUDIO UNIFORME: Reemplaza todo el fondo y piso existente (madera, parquet, zócalos o salones de baile) "
        "por un fondo de estudio fotográfico ciclorama liso, mate y homogéneo en color gris cálido #E5E1DE (RGB 229, 225, 222), "
        "sin degradados, sin tonalidades amarillentas ni beige y sin esquinas oscuras.\n"
        "3. PISO IMPOLUTO Y SOMBRA SUAVE (SIN MANCHAS): El piso debe lucir totalmente limpio e impoluto. "
        "Genera únicamente una sombra de contacto suave, difusa y traslúcida justo debajo de los pies descalzos o base de apoyo. "
        "Está terminantemente prohibido generar manchas negras, parches oscuros quemados, halos grises o charcos de suciedad en el suelo.\n"
        "4. ILUMINACIÓN NEUTRA: Aplica luz difusa frontal de estudio calibrada a blanco neutro de luz día, "
        "eliminando cualquier dominante cálida o anaranjada proveniente del piso antiguo.\n"
        "5. PRESERVACIÓN TEXTIL Y ORFEBRE: Conserva íntegros los bordados en relieve del traje, la trama calada del pañuelo blanco "
        "y la filigrana tradicional de aretes y broches dorados (#D4AF37) y plateados, sin empastarlos ni suavizarlos."
    )
    if es_reintento:
        if zoom_fallido:
            prompt += (
                "\n\n¡CORRECCIÓN URGENTE POR REINTENTO (ANTI-ZOOMOUT)!: En el intento anterior la bailarina quedó achicada "
                "o la cámara se alejó dejando demasiado espacio vacío. Es OBLIGATORIO que el cuerpo de la bailarina conserve "
                "su tamaño original completo ocupando todo el marco vertical sin achicarse."
            )
        elif suelo_sucio:
            prompt += (
                "\n\n¡CORRECCIÓN URGENTE POR REINTENTO (PISO SUCIO)!: En el intento anterior aparecieron manchas oscuras o "
                "charcos negros bajo los pies. Deja el suelo COMPLETAMENTE LIMPIO en gris cálido #E5E1DE con solo una sombra sutil y traslúcida."
            )
        else:
            prompt += (
                "\n\n¡CORRECCIÓN POR REINTENTO!: Asegúrate de que el color del fondo sea exactamente el gris cálido uniforme #E5E1DE "
                "en toda la imagen, sin franjas residuales en las orillas y con el sujeto en su posición original exacta."
            )
    return prompt


# ------------------------------------------------------------------------------
# 4. MOTOR DE VALIDACIÓN FÍSICA Y FISIOLÓGICA (6 SCORES)
# ------------------------------------------------------------------------------
class QualityGateFisico:
    @staticmethod
    def rgb_to_lab(rgb_tuple: Tuple[int, int, int]) -> np.ndarray:
        img_rgb = np.uint8([[list(rgb_tuple)]])
        lab = cv2.cvtColor(img_rgb, cv2.COLOR_RGB2LAB)
        return lab[0, 0].astype(np.float64)

    @classmethod
    def segmentar_sujeto_cielab(cls, img_np: np.ndarray, delta_thresh: float = 12.0) -> Tuple[np.ndarray, Tuple[int, int, int, int], float]:
        """Segmenta al sujeto por diferencia cromática contra #E5E1DE y calcula ocupación vertical."""
        h, w, _ = img_np.shape
        img_lab = cv2.cvtColor(img_np, cv2.COLOR_RGB2LAB).astype(np.float64)
        target_lab = cls.rgb_to_lab(RGB_OBJETIVO)
        
        delta_map = np.sqrt(np.sum((img_lab - target_lab) ** 2, axis=-1))
        subject_mask = (delta_map > delta_thresh).astype(np.uint8)
        
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (7, 7))
        cleaned = cv2.morphologyEx(subject_mask, cv2.MORPH_OPEN, kernel)
        cleaned = cv2.morphologyEx(cleaned, cv2.MORPH_CLOSE, kernel)
        
        coords = np.argwhere(cleaned > 0)
        if len(coords) < 100:
            return cleaned, (0, 0, 0, 0), 0.0
            
        y_min, x_min = coords.min(axis=0)
        y_max, x_max = coords.max(axis=0)
        ratio_altura = float((y_max - y_min) / h)
        return cleaned, (int(y_min), int(y_max), int(x_min), int(x_max)), round(ratio_altura, 3)

    @classmethod
    def evaluar_limpieza_suelo(cls, img_np: np.ndarray, bbox: Tuple[int, int, int, int]) -> float:
        """
        [Score 5 - Limpieza_Suelo_Pies]: Evalúa la zona inferior de apoyo en busca de manchas oscuras o quemadas.
        Un suelo limpio tiene L* >= 60. Píxeles con L* < 45 o RGB < 100 indican manchas de suciedad o halos negros.
        Retorna porcentaje de limpieza (0.0 a 100.0%).
        """
        h, w, _ = img_np.shape
        y_min, y_max, x_min, x_max = bbox
        
        # Analizar franja del piso: desde la base del sujeto (y_max) hacia el fondo de la imagen
        floor_top = max(0, y_max - int(h * 0.08))
        floor_bottom = h
        floor_left = max(0, x_min - int(w * 0.10))
        floor_right = min(w, x_max + int(w * 0.10))
        
        floor_roi = img_np[floor_top:floor_bottom, floor_left:floor_right]
        if floor_roi.size == 0:
            return 100.0
            
        floor_lab = cv2.cvtColor(floor_roi, cv2.COLOR_RGB2LAB)
        l_channel = floor_lab[:, :, 0]
        
        # En escala OpenCV: L va de 0 a 255. L* < 45 equivale a L_cv < 114.
        dirty_pixels = np.sum(l_channel < 114)
        total_pixels = floor_roi.shape[0] * floor_roi.shape[1]
        
        ratio_sucio = float(dirty_pixels / total_pixels)
        score_limpieza = max(0.0, min(100.0, (1.0 - ratio_sucio) * 100.0))
        return round(score_limpieza, 2)

    @classmethod
    def validar_imagen(cls, pil_img: Image.Image, aspect_ratio_str: str) -> Tuple[bool, Dict[str, Any], Optional[str]]:
        img_np = np.array(pil_img.convert("RGB"))
        h, w, _ = img_np.shape
        
        # 1. Delta E en esquinas
        patch_size = max(10, min(30, h // 10, w // 10))
        c_tl = img_np[0:patch_size, 0:patch_size]
        c_tr = img_np[0:patch_size, w - patch_size:w]
        c_bl = img_np[h - patch_size:h, 0:patch_size]
        c_br = img_np[h - patch_size:h, w - patch_size:w]
        
        corner_pixels = np.concatenate([c_tl.reshape(-1, 3), c_tr.reshape(-1, 3), 
                                        c_bl.reshape(-1, 3), c_br.reshape(-1, 3)], axis=0)
        avg_corner_rgb = tuple(np.median(corner_pixels, axis=0).astype(int))
        target_lab = cls.rgb_to_lab(RGB_OBJETIVO)
        sample_lab = cls.rgb_to_lab(avg_corner_rgb)
        delta_e = float(np.sqrt(np.sum((target_lab - sample_lab) ** 2)))

        # 2. Análisis Sobel perimetral
        gray = cv2.cvtColor(img_np, cv2.COLOR_RGB2GRAY)
        sobel_x = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=3)
        sobel_y = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=3)
        mag_sobel = np.hypot(sobel_x, sobel_y)
        
        b = 10
        border_mask = np.zeros((h, w), dtype=bool)
        border_mask[0:b, :] = True
        border_mask[h-b:h, :] = True
        border_mask[:, 0:b] = True
        border_mask[:, w-b:w] = True
        sobel_perimetro_mean = float(np.mean(mag_sobel[border_mask]))

        # 3. Pureza de Blanco perimetral (Franjas Instagram)
        border_rgb = img_np[border_mask]
        pure_white_pixels = np.all(border_rgb >= MAX_BLANCO_PERIMETRO_PX, axis=-1)
        ratio_blanco_perimetro = float(np.mean(pure_white_pixels))

        # 4 y 5. Ocupación Fisiológica y Limpieza de Suelo
        _, bbox, ratio_altura = cls.segmentar_sujeto_cielab(img_np)
        limpieza_suelo = cls.evaluar_limpieza_suelo(img_np, bbox)

        metrics = {
            "Delta_E_Color": round(delta_e, 2),
            "Sobel_Recorte_PX": round(sobel_perimetro_mean, 2),
            "Blanco_Perimetro_Max": round(ratio_blanco_perimetro * 100, 2),
            "Ocupacion_Sujeto_Ratio": ratio_altura,
            "Limpieza_Suelo_Pies": limpieza_suelo,
            "Corner_RGB_Medio": str(avg_corner_rgb)
        }

        # REGLAS DE CALIFICACIÓN DETERMINISTAS
        es_foto_vertical = aspect_ratio_str in ["9:16", "3:4"] or (w / h <= 0.85)
        if es_foto_vertical and ratio_altura < MIN_OCUPACION_VERTICAL:
            return False, metrics, f"RECHAZO_QC: ESCALA_ENCOGIDA_ZOOM_OUT (Ocupación {ratio_altura:.1%} < {MIN_OCUPACION_VERTICAL*100}%)"
            
        if limpieza_suelo < MIN_LIMPIEZA_SUELO_PIES:
            return False, metrics, f"RECHAZO_QC: MANCHAS_SUELO_PIES (Limpieza {limpieza_suelo}% < {MIN_LIMPIEZA_SUELO_PIES}%)"

        if delta_e > DELTA_E_MAX_TOLERADO:
            return False, metrics, f"RECHAZO_QC: DELTA_E_FONDO ({delta_e:.2f} > {DELTA_E_MAX_TOLERADO})"
            
        if sobel_perimetro_mean > SOBEL_UMBRAL_MAX_BORDE:
            return False, metrics, f"RECHAZO_QC: SOBEL_BORDE ({sobel_perimetro_mean:.2f} > {SOBEL_UMBRAL_MAX_BORDE})"
            
        if ratio_blanco_perimetro > RATIO_BLANCO_PERIMETRO_MAX:
            return False, metrics, f"RECHAZO_QC: FRANJA_BLANCA_INSTAGRAM ({ratio_blanco_perimetro*100:.1f}% > {RATIO_BLANCO_PERIMETRO_MAX*100}%)"

        return True, metrics, None


# ------------------------------------------------------------------------------
# 5. GESTIÓN DE GOOGLE SHEETS CON MAPEO CANÓNICO DE LOS 6 SCORES
# ------------------------------------------------------------------------------
def canonical_key(text: str) -> str:
    norm = unicodedata.normalize('NFKD', str(text)).encode('ASCII', 'ignore').decode('utf-8')
    return re.sub(r'[^a-zA-Z0-9]', '', norm).lower()

ALIAS_MAP: Dict[str, str] = {
    # Estado e Intentos
    "estado": "estado_proceso", "estadoproceso": "estado_proceso", "status": "estado_proceso",
    "intentos": "intentos", "reintentos": "intentos",
    # Enlaces y Fechas
    "urldrivepro": "url_drive_pro", "linkpro": "url_drive_pro",
    "fechaproceso": "fecha_proceso", "fecha": "fecha_proceso",
    # LOS 6 SCORES OFICIALES
    "deltaecolor": "delta_e_color", "deltae": "delta_e_color",
    "sobelrecortepx": "sobel_recorte_px", "sobel": "sobel_recorte_px",
    "blancoperimetromax": "blanco_perimetro_max", "blancoperimetro": "blanco_perimetro_max",
    "ocupacionsujetoratio": "ocupacion_sujeto_ratio", "ocupacionsujeto": "ocupacion_sujeto_ratio",
    "limpiezasuelopies": "limpieza_suelo_pies", "limpiezapiso": "limpieza_suelo_pies",
    "latenciaseg": "latencia_seg", "latencia": "latencia_seg",
    # Datos de control
    "versionprompt": "version_prompt",
    "rutadestinopro": "ruta_destino_pro",
    "ubicacionactualfisica": "ubicacion_actual_fisica",
    "motivorechazo": "motivo_rechazo", "error": "motivo_rechazo"
}

def retry_api_with_backoff(max_retries: int = 4, base_delay: float = 2.0):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            delay = base_delay
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    err_msg = str(e)
                    is_rate_limit = "429" in err_msg or "Quota exceeded" in err_msg
                    if attempt == max_retries - 1 or not is_rate_limit:
                        raise
                    jitter = random.uniform(0.5, 1.5)
                    sleep_time = (delay * (2 ** attempt)) + jitter
                    print(f"    [!] Cuota en Sheets API. Esperando {sleep_time:.2f}s...")
                    time.sleep(sleep_time)
        return wrapper
    return decorator


class DynamicSheetManager:
    def __init__(self, sheet_id: str, tab_name: str):
        self.sheet_id = sheet_id
        self.tab_name = tab_name
        self.sheet = None
        self.canonical_col_map: Dict[str, int] = {}
        self.init_services()

    @retry_api_with_backoff()
    def init_services(self):
        auth.authenticate_user()
        creds, _ = default()
        gc_client = gspread.authorize(creds)
        spreadsheet = gc_client.open_by_key(self.sheet_id)
        try:
            self.sheet = spreadsheet.worksheet(self.tab_name)
        except gspread.WorksheetNotFound:
            self.sheet = spreadsheet.get_worksheet(0)
            
        headers = self.sheet.row_values(1)
        self.canonical_col_map = {}
        for idx, h in enumerate(headers, start=1):
            raw_canon = canonical_key(h)
            resolved = ALIAS_MAP.get(raw_canon, raw_canon)
            self.canonical_col_map[resolved] = idx
        print(f"[✓] Google Sheets 'Control_Total_Drive_V2' mapeado con {len(self.canonical_col_map)} columnas.")

    @retry_api_with_backoff()
    def read_pending_rows(self) -> List[Dict[str, Any]]:
        records = self.sheet.get_all_records()
        pending = []
        for idx, row in enumerate(records, start=2):
            estado = str(row.get("Estado_Proceso", "")).strip().upper()
            if estado not in ["APROBADO_PRO", "RECHAZADA"]:
                row["_row_num"] = idx
                pending.append(row)
        return pending

    @retry_api_with_backoff()
    def update_row_audit(self, row_num: int, audit_data: Dict[str, Any]):
        cell_updates = []
        for raw_key, value in audit_data.items():
            canon = canonical_key(raw_key)
            resolved = ALIAS_MAP.get(canon, canon)
            if resolved in self.canonical_col_map:
                col_idx = self.canonical_col_map[resolved]
                a1 = rowcol_to_a1(row_num, col_idx)
                cell_updates.append({"range": a1, "values": [[value]]})
                
        if cell_updates:
            self.sheet.batch_update(cell_updates)


# ------------------------------------------------------------------------------
# 6. INVOCACIÓN MULTIMODAL GEMINI 2.5 FLASH IMAGE
# ------------------------------------------------------------------------------
def call_gemini_multimodal_image(client: genai.Client, pil_img: Image.Image, prompt_text: str) -> Image.Image:
    buf = io.BytesIO()
    pil_img.save(buf, format="JPEG", quality=95)
    image_bytes = buf.getvalue()

    image_part = types.Part.from_bytes(data=image_bytes, mime_type="image/jpeg")

    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash-image",
            contents=[image_part, prompt_text],
            config=types.GenerateContentConfig(
                response_modalities=["IMAGE"],
                temperature=0.2
            )
        )
    except APIError as api_err:
        code = getattr(api_err, "code", None)
        message = str(api_err)
        if code == 429 or "RESOURCE_EXHAUSTED" in message:
            raise PermissionError(f"RateLimit 429: {message}")
        elif code == 400 or "INVALID_ARGUMENT" in message:
            raise ValueError(f"Payload Corrupto 400: {message}")
        else:
            raise RuntimeError(f"API Error ({code}): {message}")

    candidates = getattr(response, "candidates", [])
    if not candidates:
        raise RuntimeError("La API no devolvió candidatos en la respuesta.")
    
    parts = getattr(candidates[0].content, "parts", [])
    for part in parts:
        if getattr(part, "inline_data", None) and part.inline_data.data:
            return Image.open(io.BytesIO(part.inline_data.data))
            
    raise RuntimeError("No se encontró bitmap de imagen en la respuesta multimodal.")


# ------------------------------------------------------------------------------
# 7. DOBLE FASE DE PERSISTENCIA Y PURGA LOCAL ATÓMICA
# ------------------------------------------------------------------------------
def persist_and_sync_bitmap(pil_img: Image.Image, filename: str, drive_target_folder: str) -> str:
    """Fase 1: NVMe local | Fase 2: Drive FUSE | Fase 3: os.sync() | Fase 4: Purga scratch."""
    local_path = os.path.join(LOCAL_SCRATCH_DIR, filename)
    pil_img.save(local_path, format="JPEG", quality=95, optimize=True)
    
    os.makedirs(drive_target_folder, exist_ok=True)
    drive_dest_path = os.path.join(drive_target_folder, filename)
    shutil.copy2(local_path, drive_dest_path)
    
    try:
        os.sync()
    except AttributeError:
        pass
        
    try:
        if os.path.exists(local_path):
            os.remove(local_path)
    except Exception as e:
        print(f"    [!] Advertencia al purgar local ({filename}): {e}")

    return drive_dest_path


# ------------------------------------------------------------------------------
# 8. BUCLE PRINCIPAL DE PROCESAMIENTO RESILIENTE
# ------------------------------------------------------------------------------
def ejecutar_pipeline_marinera():
    print("=== INICIANDO PIPELINE MARINERA POWER V4 (CANARY-CALIBRATED) ===")
    
    if not os.path.exists(DRIVE_MOUNT_POINT):
        drive.mount(DRIVE_MOUNT_POINT)
        
    os.makedirs(DESTINO_PRO_PATH, exist_ok=True)
    os.makedirs(DESTINO_ERROR_PATH, exist_ok=True)

    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY no configurada en las variables de entorno.")
    ai_client = genai.Client(api_key=api_key)

    sheet_mgr = DynamicSheetManager(SHEET_ID, SHEET_TAB_NAME)
    pending_items = sheet_mgr.read_pending_rows()
    print(f"Total fotos pendientes encontradas en Sheets: {len(pending_items)}")

    if not HABILITAR_BUCLE_MASIVO:
        print(">>> AVISO DE SEGURIDAD: HABILITAR_BUCLE_MASIVO = False. Modo unitario (1 foto).")
        pending_items = pending_items[:1]

    for item in pending_items:
        row_num = item["_row_num"]
        file_name = item.get("Nombre_Archivo") or item.get("Archivo", "")
        subfolder = item.get("Carpeta_Origen", "")
        base_name = os.path.splitext(file_name)[0]
        
        full_input_path = os.path.join(ORIGEN_PATH, subfolder, file_name)
        if not os.path.exists(full_input_path):
            print(f"[-] Archivo físico ausente: {full_input_path}")
            sheet_mgr.update_row_audit(row_num, {
                "Estado_Proceso": "ERROR_NO_EXISTE",
                "Motivo_Rechazo": "Archivo físico ausente en Google Drive",
                "Fecha_Proceso": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            })
            continue

        print(f"\n[+] Procesando: {file_name} (Fila {row_num}) en '{subfolder}'")
        
        # Preprocesamiento seguro Lanczos 1920px
        input_image, orig_dims = prepare_image_for_inference(full_input_path, max_dim=1920)
        orig_w, orig_h = orig_dims
        aspect_ratio_str = resolve_target_aspect_ratio(orig_w, orig_h)
        print(f"    Aspect Ratio: {aspect_ratio_str} | Original: {orig_w}x{orig_h} -> Downscale Lanczos: {input_image.size}")

        intentos = 0
        aprobado = False
        final_metrics = {}
        motivo_fallo = None
        latencia_total = 0.0
        saved_paths_per_attempt = {}
        zoom_detectado = False
        suelo_sucio_detectado = False

        # REGLA OPERATIVA INNEGOCIABLE: MÁXIMO 1 REINTENTO (2 EJECUCIONES EN TOTAL)
        while intentos < 2 and not aprobado:
            intentos += 1
            es_reintento = (intentos == 2)
            prompt = build_natural_language_prompt(
                aspect_ratio_str, 
                es_reintento=es_reintento, 
                zoom_fallido=zoom_detectado,
                suelo_sucio=suelo_sucio_detectado
            )
            
            t0 = time.time()
            output_image = None
            try:
                # 1. Invocación IA
                output_image = call_gemini_multimodal_image(ai_client, input_image, prompt)
                latencia = time.time() - t0
                latencia_total += latencia
                
                # 2. Quality Gate Físico y Fisiológico (Obtención de los 6 Scores)
                valido, metrics, error_msg = QualityGateFisico.validar_imagen(output_image, aspect_ratio_str)
                metrics["Latencia_Seg"] = round(latencia, 2)
                final_metrics = metrics
                
                attempt_filename = f"{base_name}_intento_{intentos}.jpg"
                
                # 3. Persistencia Total (Cero Bitmaps descartados en memoria)
                if valido:
                    aprobado = True
                    motivo_fallo = None
                    target_folder = os.path.join(DESTINO_PRO_PATH, subfolder)
                    drive_saved = persist_and_sync_bitmap(output_image, f"{base_name}_pro.jpg", target_folder)
                    saved_paths_per_attempt[intentos] = drive_saved
                    print(f"    -> Intento {intentos}: APROBADO [Delta_E={metrics['Delta_E_Color']}, Ocupación={metrics['Ocupacion_Sujeto_Ratio']:.1%}, Limpieza={metrics['Limpieza_Suelo_Pies']}%]")
                else:
                    motivo_fallo = error_msg
                    zoom_detectado = "ZOOM_OUT" in str(error_msg)
                    suelo_sucio_detectado = "MANCHAS_SUELO" in str(error_msg)
                    target_err_folder = os.path.join(DESTINO_ERROR_PATH, subfolder)
                    drive_saved = persist_and_sync_bitmap(output_image, f"FAIL_{attempt_filename}", target_err_folder)
                    saved_paths_per_attempt[intentos] = drive_saved
                    print(f"    -> Intento {intentos}: RECHAZADO por Quality Gate. {error_msg}")

            except PermissionError as p_err:
                latencia_total += (time.time() - t0)
                motivo_fallo = str(p_err)
                print(f"    [!] {motivo_fallo}. Pausa de 15s por Rate Limit...")
                time.sleep(15.0)
            except ValueError as v_err:
                latencia_total += (time.time() - t0)
                motivo_fallo = str(v_err)
                print(f"    [-] {motivo_fallo}. Abortando reintentos.")
                break
            except Exception as e:
                latencia_total += (time.time() - t0)
                motivo_fallo = f"Excepción API: {str(e)}"
                print(f"    -> Intento {intentos}: Error de ejecución: {motivo_fallo}")

            time.sleep(5.0)  # Throttling preventivo de cuota

        # ----------------------------------------------------------------------
        # PERSISTENCIA TOTAL Y ASENTAMIENTO EN GOOGLE SHEETS
        # ----------------------------------------------------------------------
        status_final = "APROBADO_PRO" if aprobado else "RECHAZADA"
        ultima_ruta_drive = saved_paths_per_attempt.get(intentos, "")
        
        if not ultima_ruta_drive:
            target_err_folder = os.path.join(DESTINO_ERROR_PATH, subfolder)
            os.makedirs(target_err_folder, exist_ok=True)
            ultima_ruta_drive = os.path.join(target_err_folder, f"NO_RENDER_{file_name}")
            shutil.copy2(full_input_path, ultima_ruta_drive)
            os.sync()

        audit_payload = {
            "Estado_Proceso": status_final,
            "URL_Drive_Pro": f"file://{ultima_ruta_drive}",
            "Fecha_Proceso": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "Intentos": intentos,
            # LOS 6 SCORES EXACTOS COMPUTADOS POR PYTHON
            "Delta_E_Color": final_metrics.get("Delta_E_Color", "N/A"),
            "Sobel_Recorte_PX": final_metrics.get("Sobel_Recorte_PX", "N/A"),
            "Blanco_Perimetro_Max": final_metrics.get("Blanco_Perimetro_Max", "N/A"),
            "Ocupacion_Sujeto_Ratio": final_metrics.get("Ocupacion_Sujeto_Ratio", "N/A"),
            "Limpieza_Suelo_Pies": final_metrics.get("Limpieza_Suelo_Pies", "N/A"),
            "Latencia_Seg": round(latencia_total, 2),
            # Metadata de auditoría
            "Version_Prompt": VERSION_PROMPT,
            "Ruta_Destino_PRO": ultima_ruta_drive,
            "Ubicacion_Actual_Fisica": full_input_path,
            "Motivo_Rechazo": motivo_fallo if not aprobado else ""
        }
        
        sheet_mgr.update_row_audit(row_num, audit_payload)
        print(f"[✓] Fila {row_num} asentada en Sheets con estado: {status_final}")
        print(f"    Scores: Delta_E={audit_payload['Delta_E_Color']} | Ocupación={audit_payload['Ocupacion_Sujeto_Ratio']} | Suelo={audit_payload['Limpieza_Suelo_Pies']}% | Latencia={audit_payload['Latencia_Seg']}s")

        # Limpieza estricta de memoria RAM/VRAM
        del input_image
        if output_image is not None:
            del output_image
        gc.collect()

    print("\n=== EJECUCIÓN DEL PIPELINE V4 FINALIZADA ===")


if __name__ == "__main__":
    ejecutar_pipeline_marinera()
