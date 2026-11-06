# ==============================================================================
# PIPELINE MAESTRO INDUSTRIAL V3 (BLINDADO FINAL): MARINERA POWER CATALOGO PRO
# Plataforma: Google Colab (Python 3.10+) | Modelo: gemini-2.5-flash-image
# ==============================================================================

import os
import io
import gc
import re
import time
import math
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
# 1. CONFIGURACIÓN, RUTAS Y BANDERAS DE SEGURIDAD
# ------------------------------------------------------------------------------
HABILITAR_BUCLE_MASIVO: bool = False  # True: corrida masiva (762 fotos) | False: prueba unitaria
VERSION_PROMPT: str = "v3.0_multimodal_anti_zoomout_physiological"

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

# Tolerancias Quality Gate Físico y Fisiológico
HEX_COLOR_OBJETIVO = "#E5E1DE"
RGB_OBJETIVO = (229, 225, 222)      # #E5E1DE
DELTA_E_MAX_TOLERADO = 7.5          # Tolerancia CIELAB 1976 en ciclorama
SOBEL_UMBRAL_MAX_BORDE = 25.0       # Gradiente perimetral máximo (líneas parásitas)
MAX_BLANCO_PERIMETRO_PX = 250       # Intensidad RGB para detectar franjas blancas
RATIO_BLANCO_PERIMETRO_MAX = 0.05   # Máximo 5% de blanco puro perimetral permitido
MIN_OCUPACION_VERTICAL = 0.45       # [QG-R2-02]: Mínimo 45% de altura en fotos verticales

pillow_heif.register_heif_opener()
os.makedirs(LOCAL_SCRATCH_DIR, exist_ok=True)


# ------------------------------------------------------------------------------
# 2. PREPROCESAMIENTO DETERMINISTA LANCZOS / EXIF [QG-R2-01]
# ------------------------------------------------------------------------------
def prepare_image_for_inference(file_path: str, max_dim: int = 1920) -> Tuple[Image.Image, Tuple[int, int]]:
    """
    [QG-R2-01]: Carga robusta, transposición EXIF de orientación física,
    normalización a RGB y redimensionamiento Lanczos con cota de 1920px.
    Previene desbordamiento de memoria VRAM/RAM y consumo de cuota por fotos de 48MP.
    Retorna: (imagen_preparada_pil, dimensiones_originales_wh)
    """
    with Image.open(file_path) as raw:
        corrected = ImageOps.exif_transpose(raw)
        if corrected is None:
            corrected = raw
        rgb_img = corrected.convert("RGB")
        orig_dims = rgb_img.size  # (orig_w, orig_h)
        
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
    """Calcula el aspect ratio nativo óptimo para preservar proporciones."""
    ratio = orig_w / orig_h
    supported = {
        "9:16": 9 / 16,  # 0.5625
        "3:4": 3 / 4,    # 0.7500
        "1:1": 1.0,      # 1.0000
        "4:3": 4 / 3,    # 1.3333
        "16:9": 16 / 9   # 1.7777
    }
    return min(supported.keys(), key=lambda k: abs(supported[k] - ratio))


def build_natural_language_prompt(aspect_ratio_str: str, es_reintento: bool = False, zoom_out_fallido: bool = False) -> str:
    """Prompt fotográfico directo en lenguaje natural sin tecnicismos matemáticos confusos."""
    prompt = (
        "Eres un retocador profesional de fotografía de moda y catálogo comercial. "
        "Edita esta fotografía cambiando únicamente el fondo, bajo las siguientes instrucciones estrictas:\n\n"
        f"1. ENCUADRE Y ESCALA EXACTA: Mantén la proporción y encuadre original en formato {aspect_ratio_str}. "
        "La persona u objeto debe permanecer exactamente en la misma posición, con el mismo tamaño de cuerpo "
        "y exactamente la misma pose original (brazos, falda, pañuelo, manos y pies intactos), "
        "sin alejar la toma, sin achicar a la persona y sin hacer zoom-out.\n"
        "2. FONDO DE ESTUDIO LISO: Reemplaza todo el fondo y piso existente (madera, parquet, zócalos o salones de baile) "
        "por un fondo de estudio fotográfico liso, mate y uniforme en color gris cálido #E5E1DE continuo de pared a piso.\n"
        "3. ANCLAJE AL SUELO Y SOMBRAS: Genera sombras de contacto suaves y naturales justo debajo de los pies o base "
        "para que el sujeto quede firmemente plantado en el piso y no parezca estar flotando.\n"
        "4. ILUMINACIÓN: Aplica luz frontal suave y difusa de estudio fotográfico con balance de blancos neutro (luz día), "
        "eliminando cualquier reflejo amarillento o anaranjado residual.\n"
        "5. PRESERVACIÓN TEXTIL Y ORFEBRE: Conserva íntegros los bordados del vestido, la trama calada del pañuelo blanco "
        "y los detalles finos de los aretes y joyas de filigrana dorada y plateada, sin deformarlos ni empastarlos."
    )
    if es_reintento:
        if zoom_out_fallido:
            prompt += (
                "\n\n¡ADVERTENCIA CRÍTICA DE REINTENTO POR ZOOM-OUT!: En el intento anterior achicaste a la persona "
                "o alejaste la cámara dejando demasiado espacio vacío. ES OBLIGATORIO mantener a la bailarina en primer plano "
                "con su tamaño corporal original idéntico, ocupando toda la altura de la imagen sin encogerla."
            )
        else:
            prompt += (
                "\n\nATENCIÓN ESPECIAL POR REINTENTO: En el intento anterior hubo desvío en el color del fondo "
                "o artefactos en los bordes. Asegúrate de que el fondo sea completamente uniforme en gris cálido #E5E1DE "
                "sin franjas blancas en las orillas y con el sujeto exactamente en su posición original."
            )
    return prompt


# ------------------------------------------------------------------------------
# 3. NORMALIZACIÓN CANÓNICA DE COLUMNAS CON ALIAS [QG-R2-03]
# ------------------------------------------------------------------------------
def canonical_key(text: str) -> str:
    """Normaliza un texto a formato canónico sin tildes, espacios ni caracteres especiales."""
    norm = unicodedata.normalize('NFKD', str(text)).encode('ASCII', 'ignore').decode('utf-8')
    return re.sub(r'[^a-zA-Z0-9]', '', norm).lower()

# Diccionario exhaustivo de alias para tolerar variaciones en el Google Sheet
ALIAS_MAP: Dict[str, str] = {
    # Estado
    "estado": "estado_proceso", "estadoproceso": "estado_proceso", "status": "estado_proceso",
    # Enlace PRO
    "urldrivepro": "url_drive_pro", "linkpro": "url_drive_pro", "rutadrivepro": "url_drive_pro",
    # Fecha
    "fechaproceso": "fecha_proceso", "fecha": "fecha_proceso", "timestamp": "fecha_proceso",
    # Intentos
    "intentos": "intentos", "reintentos": "intentos", "numintentos": "intentos",
    # Delta E
    "deltaecolor": "delta_e_color", "deltae": "delta_e_color", "deltacolor": "delta_e_color",
    # Sobel
    "sobelrecortepx": "sobel_recorte_px", "sobel": "sobel_recorte_px", "sobelborde": "sobel_recorte_px",
    # Blanco Perímetro
    "blancoperimetromax": "blanco_perimetro_max", "blancoperimetro": "blanco_perimetro_max", "purezaperimetro": "blanco_perimetro_max",
    # Ocupación Fisiológica Sujeto [QG-R2-02]
    "ocupacionsujeto": "ocupacion_sujeto_ratio", "ratioalturasujeto": "ocupacion_sujeto_ratio", "ocupacionvertical": "ocupacion_sujeto_ratio",
    # Latencia
    "latenciaseg": "latencia_seg", "latencia": "latencia_seg", "duracionseg": "latencia_seg",
    # Versión Prompt
    "versionprompt": "version_prompt", "promptversion": "version_prompt",
    # Ruta Destino PRO
    "rutadestinopro": "ruta_destino_pro", "destinopro": "ruta_destino_pro",
    # Ubicación Física
    "ubicacionactualfisica": "ubicacion_actual_fisica", "rutaorigen": "ubicacion_actual_fisica", "rutafisica": "ubicacion_actual_fisica",
    # Motivo Rechazo
    "motivorechazo": "motivo_rechazo", "error": "motivo_rechazo", "fallo": "motivo_rechazo"
}

def retry_api_with_backoff(max_retries: int = 4, base_delay: float = 2.0):
    """Decorador con backoff exponencial y jitter para cuotas en Google Sheets API."""
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
    """[QG-R2-03]: Administrador dinámico con resolución canónica de columnas por alias."""
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
        print(f"[✓] Sheets inicializado con {len(self.canonical_col_map)} columnas canónicas mapeadas.")

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
        """Actualiza audit_data mapeando llaves canónicas a índices reales de columnas."""
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
# 4. QUALITY GATE FÍSICO Y FISIOLÓGICO DETERMINISTA [QG-R2-02]
# ------------------------------------------------------------------------------
class QualityGateFisico:
    @staticmethod
    def rgb_to_lab(rgb_tuple: Tuple[int, int, int]) -> np.ndarray:
        img_rgb = np.uint8([[list(rgb_tuple)]])
        lab = cv2.cvtColor(img_rgb, cv2.COLOR_RGB2LAB)
        return lab[0, 0].astype(np.float64)

    @classmethod
    def calcular_ocupacion_sujeto(cls, img_np: np.ndarray, delta_thresh: float = 12.0) -> Tuple[float, Tuple[int, int, int, int]]:
        """
        [QG-R2-02]: Segmenta al sujeto mediante distancia cromática contra #E5E1DE en CIELAB.
        Calcula la Ocupación Vertical del Sujeto = (y_max - y_min) / frame_h.
        Aplica limpieza morfológica para descartar sombras difusas y partículas aisladas.
        """
        h, w, _ = img_np.shape
        img_lab = cv2.cvtColor(img_np, cv2.COLOR_RGB2LAB).astype(np.float64)
        target_lab = cls.rgb_to_lab(RGB_OBJETIVO)
        
        # Mapa euclidiano de distancia cromática al ciclorama
        delta_map = np.sqrt(np.sum((img_lab - target_lab) ** 2, axis=-1))
        subject_mask = (delta_map > delta_thresh).astype(np.uint8)
        
        # Filtro morfológico para aislar cuerpo sólido
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (7, 7))
        cleaned = cv2.morphologyEx(subject_mask, cv2.MORPH_OPEN, kernel)
        cleaned = cv2.morphologyEx(cleaned, cv2.MORPH_CLOSE, kernel)
        
        coords = np.argwhere(cleaned > 0)
        if len(coords) < 100:  # Sujeto no detectado o fondo uniforme
            return 0.0, (0, 0, 0, 0)
            
        y_min, x_min = coords.min(axis=0)
        y_max, x_max = coords.max(axis=0)
        
        subject_height = y_max - y_min
        ratio_altura = float(subject_height / h)
        return round(ratio_altura, 3), (int(y_min), int(y_max), int(x_min), int(x_max))

    @classmethod
    def validar_imagen(cls, pil_img: Image.Image, aspect_ratio_str: str) -> Tuple[bool, Dict[str, Any], Optional[str]]:
        img_np = np.array(pil_img.convert("RGB"))
        h, w, _ = img_np.shape
        
        # 1. Delta E en esquinas exteriores
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

        # 2. Análisis Sobel en perímetro exterior (10px)
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

        # 4. [QG-R2-02]: Ocupación Vertical del Sujeto (Fisiológica Anti-Zoomout)
        ratio_altura_sujeto, bbox_sujeto = cls.calcular_ocupacion_sujeto(img_np)

        metrics = {
            "Delta_E_Color": round(delta_e, 2),
            "Sobel_Recorte_PX": round(sobel_perimetro_mean, 2),
            "Blanco_Perimetro_Max": round(ratio_blanco_perimetro * 100, 2),
            "Ocupacion_Sujeto_Ratio": ratio_altura_sujeto,
            "Corner_RGB_Medio": str(avg_corner_rgb),
            "BBox_Sujeto": str(bbox_sujeto)
        }

        # REGLA FISIOLÓGICA ANTI-ZOOMOUT EN FOTOS VERTICALES
        es_foto_vertical = aspect_ratio_str in ["9:16", "3:4"] or (w / h <= 0.85)
        if es_foto_vertical and ratio_altura_sujeto < MIN_OCUPACION_VERTICAL:
            return False, metrics, f"RECHAZO_QC: ESCALA_ENCOGIDA_ZOOM_OUT (Ocupación {ratio_altura_sujeto:.1%} < {MIN_OCUPACION_VERTICAL*100}%)"

        if delta_e > DELTA_E_MAX_TOLERADO:
            return False, metrics, f"RECHAZO_QC: Delta_E fondo ({delta_e:.2f} > {DELTA_E_MAX_TOLERADO})"
        if sobel_perimetro_mean > SOBEL_UMBRAL_MAX_BORDE:
            return False, metrics, f"RECHAZO_QC: Sobel borde perimetral ({sobel_perimetro_mean:.2f} > {SOBEL_UMBRAL_MAX_BORDE})"
        if ratio_blanco_perimetro > RATIO_BLANCO_PERIMETRO_MAX:
            return False, metrics, f"RECHAZO_QC: Franja blanca residual ({ratio_blanco_perimetro*100:.1f}% > {RATIO_BLANCO_PERIMETRO_MAX*100}%)"

        return True, metrics, None


# ------------------------------------------------------------------------------
# 5. INVOCACIÓN MULTIMODAL CON GEMINI 2.5 FLASH IMAGE
# ------------------------------------------------------------------------------
def call_gemini_multimodal_image(client: genai.Client, pil_img: Image.Image, prompt_text: str) -> Image.Image:
    """Invocación directa de generate_content con response_modalities=['IMAGE']."""
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
# 6. PERSISTENCIA SEGURA Y PURGA DE SCRATCH LOCAL [QG-R2-04]
# ------------------------------------------------------------------------------
def persist_and_sync_bitmap(pil_img: Image.Image, filename: str, drive_target_folder: str) -> str:
    """
    1. Escribe en scratch NVMe local (/content/local_scratch/).
    2. Copia a Google Drive FUSE con shutil.copy2().
    3. Ejecuta os.sync() a nivel de kernel para evitar archivos de 0 bytes.
    4. Purga el archivo temporal de NVMe local [QG-R2-04].
    """
    local_path = os.path.join(LOCAL_SCRATCH_DIR, filename)
    pil_img.save(local_path, format="JPEG", quality=95, optimize=True)
    
    os.makedirs(drive_target_folder, exist_ok=True)
    drive_dest_path = os.path.join(drive_target_folder, filename)
    shutil.copy2(local_path, drive_dest_path)
    
    # Sincronización obligatoria a bajo nivel
    try:
        os.sync()
    except AttributeError:
        pass
        
    # [QG-R2-04]: Purga inmediata de scratch local
    try:
        if os.path.exists(local_path):
            os.remove(local_path)
    except Exception as e:
        print(f"    [!] Advertencia purga local ({filename}): {e}")

    return drive_dest_path


# ------------------------------------------------------------------------------
# 7. BUCLE PRINCIPAL DE PROCESAMIENTO RESILIENTE
# ------------------------------------------------------------------------------
def ejecutar_pipeline_marinera():
    print("=== INICIANDO PIPELINE MARINERA POWER CATALOGO PRO V3 ===")
    
    if not os.path.exists(DRIVE_MOUNT_POINT):
        drive.mount(DRIVE_MOUNT_POINT)
        
    os.makedirs(DESTINO_PRO_PATH, exist_ok=True)
    os.makedirs(DESTINO_ERROR_PATH, exist_ok=True)

    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY no configurada en el entorno.")
    ai_client = genai.Client(api_key=api_key)

    sheet_mgr = DynamicSheetManager(SHEET_ID, SHEET_TAB_NAME)
    pending_items = sheet_mgr.read_pending_rows()
    print(f"Total fotos pendientes en Sheets: {len(pending_items)}")

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
                "Motivo_Rechazo": "Archivo ausente en ruta física de Drive",
                "Fecha_Proceso": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            })
            continue

        print(f"\n[+] Procesando: {file_name} (Fila {row_num}) en '{subfolder}'")
        
        # [QG-R2-01]: Preprocesamiento determinista Lanczos / EXIF
        input_image, orig_dims = prepare_image_for_inference(full_input_path, max_dim=1920)
        orig_w, orig_h = orig_dims
        aspect_ratio_str = resolve_target_aspect_ratio(orig_w, orig_h)
        print(f"    Aspect Ratio: {aspect_ratio_str} | Original: {orig_w}x{orig_h} -> Procesado: {input_image.size}")

        intentos = 0
        aprobado = False
        final_metrics = {}
        motivo_fallo = None
        latencia_total = 0.0
        saved_paths_per_attempt = {}
        zoom_out_detectado = False

        # MÁXIMO 1 REINTENTO (2 intentos totales)
        while intentos < 2 and not aprobado:
            intentos += 1
            es_reintento = (intentos == 2)
            prompt = build_natural_language_prompt(
                aspect_ratio_str, 
                es_reintento=es_reintento, 
                zoom_out_fallido=zoom_out_detectado
            )
            
            t0 = time.time()
            output_image = None
            try:
                # LLAMADA MULTIMODAL A GEMINI
                output_image = call_gemini_multimodal_image(ai_client, input_image, prompt)
                latencia = time.time() - t0
                latencia_total += latencia
                
                # VALIDACIÓN FÍSICA Y FISIOLÓGICA DETERMINISTA [QG-R2-02]
                valido, metrics, error_msg = QualityGateFisico.validar_imagen(output_image, aspect_ratio_str)
                final_metrics = metrics
                
                attempt_filename = f"{base_name}_intento_{intentos}.jpg"
                if valido:
                    aprobado = True
                    motivo_fallo = None
                    target_folder = os.path.join(DESTINO_PRO_PATH, subfolder)
                    drive_saved = persist_and_sync_bitmap(output_image, f"{base_name}_pro.jpg", target_folder)
                    saved_paths_per_attempt[intentos] = drive_saved
                    print(f"    -> Intento {intentos}: APROBADO (Delta_E={metrics['Delta_E_Color']}, Ocupación={metrics['Ocupacion_Sujeto_Ratio']:.1%})")
                else:
                    motivo_fallo = error_msg
                    zoom_out_detectado = "ZOOM_OUT" in str(error_msg)
                    # Persistencia obligatoria de render fallido en árbol de error
                    target_err_folder = os.path.join(DESTINO_ERROR_PATH, subfolder)
                    drive_saved = persist_and_sync_bitmap(output_image, f"FAIL_{attempt_filename}", target_err_folder)
                    saved_paths_per_attempt[intentos] = drive_saved
                    print(f"    -> Intento {intentos}: RECHAZADO por Quality Gate. {error_msg}")

            except PermissionError as p_err:
                latencia_total += (time.time() - t0)
                motivo_fallo = str(p_err)
                print(f"    [!] {motivo_fallo}. Esperando 15s...")
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

            # Throttling preventivo
            time.sleep(5.0)

        # ----------------------------------------------------------------------
        # AUDITORÍA EN GOOGLE SHEETS [QG-R2-03]
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
            "Delta_E_Color": final_metrics.get("Delta_E_Color", "N/A"),
            "Sobel_Recorte_PX": final_metrics.get("Sobel_Recorte_PX", "N/A"),
            "Blanco_Perimetro_Max": final_metrics.get("Blanco_Perimetro_Max", "N/A"),
            "Ocupacion_Sujeto_Ratio": final_metrics.get("Ocupacion_Sujeto_Ratio", "N/A"),
            "Latencia_Seg": round(latencia_total, 2),
            "Version_Prompt": VERSION_PROMPT,
            "Ruta_Destino_PRO": ultima_ruta_drive,
            "Ubicacion_Actual_Fisica": full_input_path,
            "Motivo_Rechazo": motivo_fallo if not aprobado else ""
        }
        
        sheet_mgr.update_row_audit(row_num, audit_payload)
        print(f"[✓] Fila {row_num} asentada en Sheets con estado: {status_final} (Ocupación: {audit_payload['Ocupacion_Sujeto_Ratio']})")

        # Liberación explícita de descriptores y memoria RAM/VRAM
        del input_image
        if output_image is not None:
            del output_image
        gc.collect()

    print("\n=== PIPELINE V3 FINALIZADO EXITOSAMENTE ===")


if __name__ == "__main__":
    ejecutar_pipeline_marinera()
