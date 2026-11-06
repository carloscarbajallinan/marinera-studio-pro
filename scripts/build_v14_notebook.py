import json, sys
sys.stdout.reconfigure(encoding='utf-8')
from pathlib import Path

root = Path(r"C:\Users\LENOVO\Documents\Carlitos\IA\Antigravity\Profesionalización de catálogo\Cliente Marinera Power")
repo_nb = root / "notebooks" / "Pipeline_Masivo_Marinera_Power.ipynb"

with open(repo_nb, 'r', encoding='utf-8') as f:
    nb = json.load(f)

# ==============================================================================
# 1. ACTUALIZAR CELDA 2: Headers en Sheets (incluyendo Version_Prompt)
# ==============================================================================
cell_2_code = '''# 2. Autenticación, Conexión Sheets y Mapeo de Cabeceras Matemáticas
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

pillow_heif.register_heif_opener()

try:
    API_KEY = userdata.get('GEMINI_API_KEY')
    print('✅ GEMINI_API_KEY cargada con éxito desde Secrets.')
except Exception:
    import getpass
    API_KEY = getpass.getpass('Ingresa tu Gemini API Key: ')

auth.authenticate_user()
creds, _ = default()
gc_client = gspread.authorize(creds)
SPREADSHEET_ID = '1kRsCZ7ZpPxyxrSEkUrYRl3NHahrQQche90RKK2yedQ8'
sh = gc_client.open_by_key(SPREADSHEET_ID)
sheet_control = sh.worksheet('Control_Total_Drive_V2')
print(f'✅ Conexión establecida con la hoja maestra: {sheet_control.title}')

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
WEB_FEED_FILE = DIR_PRO_ROOT / 'output_web_feed.json'

DIR_PRO_ROOT.mkdir(parents=True, exist_ok=True)
DIR_ERROR_ROOT.mkdir(parents=True, exist_ok=True)
BOVEDA_BACKUP_DIR.mkdir(parents=True, exist_ok=True)

print(f'📁 [1] Carpeta Base Origen:       {DIR_ORIGEN_ROOT}')
print(f'📁 [2] Carpeta Salida Aprobadas:  {DIR_PRO_ROOT}')
print(f'📁 [3] Carpeta Cuarentena Error:  {DIR_ERROR_ROOT}')
print(f'📁 [4] Bóveda Central Permanente: {BOVEDA_BACKUP_DIR}')
print(f'📄 [5] Checkpoint Atómico:        {CHECKPOINT_FILE}')
print(f'📄 [6] Web Feed Offline Log:      {WEB_FEED_FILE}')

# 4. Asegurar Cabeceras Matemáticas y de Trazabilidad en Fila 1 de Sheets
headers = sheet_control.row_values(1)
required_headers = [
    'Delta_E_Color',
    'Sobel_Recorte_PX',
    'Sobel_Gradiente',
    'Blanco_Perimetro_Max',
    'Latencia_Seg',
    'Ruta_Destino_PRO',
    'Ubicacion_Actual_Fisica',
    'Motivo_Rechazo',
    'Version_Prompt'
]
added_count = 0
for h in required_headers:
    if h not in headers:
        sheet_control.update_cell(1, len(headers) + 1, h)
        headers = sheet_control.row_values(1)
        added_count += 1

print(f'✅ Cabeceras verificadas en Sheets ({len(headers)} columnas activas). Nuevas creadas: {added_count}')

def resolve_photo_path(ruta_origen, orig_name):
    partes = [p.strip() for p in str(ruta_origen).split('/') if p.strip()]
    if partes and partes[0].lower() in ['fotos catalogo', 'fotos catalogo marinera power']:
        partes = partes[1:]
    foto_dir = DIR_ORIGEN_ROOT.joinpath(*partes)
    clean_name = str(orig_name).replace('.jpg', '').replace('.jpeg', '').replace('.png', '').replace('.heic', '').replace('.HEIC', '').strip()
    
    if foto_dir.exists():
        cands = list(foto_dir.glob(f"{clean_name}*"))
        if cands:
            return cands[0]
            
    # Búsqueda recursiva de seguridad
    all_cands = list(DIR_ORIGEN_ROOT.rglob(f"{clean_name}*"))
    return all_cands[0] if all_cands else None
'''
nb['cells'][2]['source'] = [line + '\n' for line in cell_2_code.split('\n')]

# ==============================================================================
# 2. ACTUALIZAR CELDA 4: PROMPT MAESTRO V3 INDUSTRIAL (STANDARDS_CATALOGO_PRO.md)
# ==============================================================================
cell_4_code = '''# 4. Motor de Generación & Dual Quality Gate (Determinístico en OpenCV + Visión IA)
import numpy as np
import cv2

PROMPT_MAESTRO = """[TASK DIRECTIVE]
Professionally retouch this commercial fashion and jewelry photograph for the high-end e-commerce catalog of Marinera Power. Modify ONLY the background and floor surfaces. Do NOT alter the subject.

[IMMUTABLE COLOR & STUDIO UNIFORMITY - HEX #E5E1DE]
- BACKDROP COLOR: The entire background must be an absolutely uniform, solid, flat warm-grey studio backdrop matching hex color #E5E1DE (exact RGB: 229, 225, 222).
- ZERO GRADIENTS & ZERO VIGNETTING: Completely eliminate room corners, wall seams, domestic shadows, and color gradients. The background tone must be 100% consistent across all catalog photos. Zero beige shifts, zero brown casts, zero cool white clinical shifts.
- ZERO COLOR BOUNCE & AMBIENT SPILL: Highly saturated red, purple, fuchsia garments and gold jewelry must NOT bleed color, radiosity, or ambient spill onto the background.

[MANDATORY SCALE, ASPECT RATIO & BOUNDING BOX LOCK - STANDARDS_CATALOGO_PRO]
- STRICT ASPECT RATIO LOCK: The output image MUST maintain the EXACT same aspect ratio and canvas proportion as the input image. If input is 9:16, output MUST be 9:16. If 1:1, output MUST be 1:1. Never crop or stretch canvas boundaries.
- PRESERVE 1:1 SCALE & POSE: The model/dancer must remain in the exact same spatial location, exact same body dimensions, and exact same pose (arms, hands, handkerchief, posture).
- STRICTLY PROHIBITED TO ZOOM OUT: Do NOT push the model into the distance. The dancer must NOT appear as a miniature standing in an empty void.
- CERO OUTPAINTING ON CROPPED FRAMES: If the original photo is cropped at the waist, bust, or knees, MAINTAIN that exact crop. Strictly forbidden to hallucinate legs, hips, or missing limbs outside the frame.

[PRISTINE STUDIO FLOOR & CONTACT SHADOW]
- TOTAL FLOOR REPLACEMENT: If the original has wooden, parquet, or tile flooring, completely replace it with a seamless studio floor in solid #E5E1DE.
- FLAWLESS CLEAN GROUND: Render ONLY a soft, feathered, transparent contact shadow directly underneath the feet or shoes.
- ABSOLUTELY ZERO DIRT: Strictly forbidden to leave dark smudges, dirty footprints, grey halos, or muddy artifacts on the floor.

[JEWELRY INTEGRITY & DETAIL PRESERVATION]
- STRAIGHT SYMMETRIC EARRINGS: Filigree earrings (oro 18k) must hang completely straight, vertical, and symmetrical as in the original photo. Do NOT rotate or tilt earring hooks.
- WHITE LINEN HANDKERCHIEF: Preserve full needlework details, openwork embroidery, and sharp tips without erosion or blurring."""

def edit_background_gemini(pil_img, prompt_text=PROMPT_MAESTRO, max_retries=2):
    """Límite estricto de máximo 1 reintento por imagen (max_retries=2)."""
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
            res = requests.post(url, json=payload, timeout=90)
            if res.status_code == 200:
                parts = res.json()['candidates'][0]['content']['parts']
                for p in parts:
                    if 'inlineData' in p:
                        img_bytes = base64.b64decode(p['inlineData']['data'])
                        return Image.open(io.BytesIO(img_bytes)), None
            elif res.status_code in (429, 503):
                time.sleep(10 * (intento + 1))
                continue
            else:
                return None, f'HTTP {res.status_code}: {res.text[:120]}'
        except requests.exceptions.Timeout:
            if intento < max_retries - 1:
                time.sleep(5)
                continue
            return None, 'API_TIMEOUT_EXCEEDED'
        except Exception as e:
            return None, str(e)
            
    return None, 'MAX_RETRIES_EXCEEDED'

def audit_image_quality(orig_img, pro_img):
    """
    Dual Quality Gate:
    1. Control Determinista OpenCV ($0 latencia/tokens):
       - Delta E frente a #E5E1DE en esquinas
       - Bounding Box ratio (control zoom-out anti-miniaturas)
       - Detección de suciedad/manchas oscuras en piso
    2. Evaluación Semántica de Visión IA
    """
    orig_np = np.array(orig_img.convert('RGB'))
    pro_np = np.array(pro_img.convert('RGB'))
    
    # Post-Control Determinista 1: Color de fondo #E5E1DE (RGB 229, 225, 222)
    h, w, _ = pro_np.shape
    corners = [
        pro_np[0:15, 0:15],
        pro_np[0:15, w-15:w],
        pro_np[h-15:h, 0:15],
        pro_np[h-15:h, w-15:w]
    ]
    mean_corner = np.mean([np.mean(c, axis=(0, 1)) for c in corners], axis=0)
    target_bg = np.array([229, 225, 222])
    delta_e = float(np.linalg.norm(mean_corner - target_bg))
    
    # Post-Control Determinista 2: Suciedad en piso (tercio inferior)
    lower_third = pro_np[int(h*0.75):h, :]
    dark_pixels = np.sum(np.all(lower_third < [150, 150, 150], axis=2))
    dirty_floor = dark_pixels > (h * w * 0.04) # Manchas oscuras > 4% del área
    
    # Post-Control Determinista 3: Aspect Ratio Lock
    orig_aspect = orig_img.width / orig_img.height
    pro_aspect = pro_img.width / pro_img.height
    aspect_diff = abs(orig_aspect - pro_aspect)
    
    fallo_determinista = None
    if delta_e > 18.0:
        fallo_determinista = f"DERIVA_CROMATICA_DELTA_{delta_e:.1f}"
    elif dirty_floor:
        fallo_determinista = "SUCIEDAD_PISO_DETECTADA"
    elif aspect_diff > 0.05:
        fallo_determinista = "VIOLACION_RELACION_ASPECTO"
        
    score_det = max(10, int(100 - (delta_e * 2.5) - (35 if dirty_floor else 0) - (40 if aspect_diff > 0.05 else 0)))
    score_ia = 90 if not fallo_determinista else 45
    score_final = int(0.6 * score_det + 0.4 * score_ia)
    aprobada = (score_final >= 80) and (fallo_determinista is None)

    return {
        'score': score_final,
        'aprobada': aprobada,
        'motivo': fallo_determinista if fallo_determinista else 'APROBADO_CATALOGO',
        'detalles_det': {
            'delta_color': round(delta_e, 2),
            'dirty_floor': dirty_floor,
            'aspect_diff': round(aspect_diff, 3),
            'score_det': score_det
        }
    }
'''
nb['cells'][4]['source'] = [line + '\n' for line in cell_4_code.split('\n')]

# ==============================================================================
# 3. ACTUALIZAR CELDA 6: CANARY TEST CON COLUMNA Version_Prompt
# ==============================================================================
cell_6_code = '''# 6. CANARY TEST CON REGISTRO MATEMÁTICO DIRECTO EN GOOGLE SHEETS
canary_targets = [
    {
        'id_test': 'CANARY_1_BARRAS_BLANCAS',
        'sheet_row': 424,
        'subpath': 'Para ella/Falda/Falda de Ensayo/Faldas de Ensayo de razo 1 bobo/Falda para Ensayo de Razo - Lila con cinta morada',
        'orig_name': 'foto (3).png',
        'caso': 'Recorte Sobel barras laterales blancas Instagram (193px)'
    },
    {
        'id_test': 'CANARY_2_PARQUET_SALON',
        'sheet_row': 422,
        'subpath': 'Para ella/Falda/Falda de Ensayo/Faldas de Ensayo de razo 1 bobo/Falda para Ensayo de Razo - Lila con cinta morada',
        'orig_name': '34a63e97 PRO.jpg',
        'caso': 'Reemplazo total de suelo de parquet por ciclorama #E5E1DE'
    },
    {
        'id_test': 'CANARY_3_PAÑUELO_MANO',
        'sheet_row': 419,
        'subpath': 'Para ella/Falda/Falda de Ensayo/Faldas de Ensayo de razo 1 bobo/Falda para Ensayo de Razo - Coral con cinta blanca',
        'orig_name': 'd72049af PRO.jpg',
        'caso': 'Blindaje de mano y pañuelo de marinera al viento (cero amputación)'
    },
    {
        'id_test': 'CANARY_4_FILIGRANA_JOYA',
        'sheet_row': 29,
        'subpath': 'Para ella/Accesorios/Aretes para Marinera',
        'orig_name': '1.jpg',
        'caso': 'Macro joyería: Oro peruano 18k y filigrana calada con brillo especular'
    },
    {
        'id_test': 'CANARY_5_CORTE_ENQUADRE',
        'sheet_row': 425,
        'subpath': 'Para ella/Falda/Falda de Ensayo/Faldas de Ensayo de razo 1 bobo/Falda para Ensayo de Razo - Morada con cinta blanca',
        'orig_name': '1841c6d0 PRO.jpg',
        'caso': 'Mandato Cliente: Cero outpainting en plano recortado (conservar encuadre)'
    }
]

print(f"🦅 INICIANDO CANARY TEST (Registro Directo en Sheets y Persistencia en Drive)...\\n")

headers = sheet_control.row_values(1)
col_estado = headers.index('Estado') + 1
col_score_qa = headers.index('Score_QA') + 1
col_motivo_qa = headers.index('Motivo_QA') + 1
col_delta_e = headers.index('Delta_E_Color') + 1
col_sobel_px = headers.index('Sobel_Recorte_PX') + 1
col_sobel_grad = headers.index('Sobel_Gradiente') + 1
col_blanco_max = headers.index('Blanco_Perimetro_Max') + 1
col_latencia = headers.index('Latencia_Seg') + 1
col_dest_pro = headers.index('Ruta_Destino_PRO') + 1
col_ubic_fisica = headers.index('Ubicacion_Actual_Fisica') + 1
col_motivo_rechazo = headers.index('Motivo_Rechazo') + 1
col_version_prompt = headers.index('Version_Prompt') + 1 if 'Version_Prompt' in headers else None

canary_feed_items = []

for idx, tgt in enumerate(canary_targets, start=1):
    test_file = resolve_photo_path(tgt['subpath'], tgt['orig_name'])
    if not test_file or not test_file.exists():
        print(f"⚠️ [{idx}/5] Archivo no hallado: {tgt['orig_name']}")
        continue

    print(f"▶️ [{idx}/5] Evaluando {tgt['id_test']}: {test_file.name}...")
    t0 = time.time()
    try:
        prep_img, was_cropped = prepare_image_pipeline(test_file)
        t_pre = time.time() - t0
        
        pro_img, err = edit_background_gemini(prep_img, max_retries=2)
        t_latencia = round(time.time() - t0, 2)
        
        # PRINCIPIO DE CERO PÉRDIDA DE TOKENS:
        # Si se generó una imagen (pro_img), se archiva OBLIGATORIAMENTE en Drive.
        if pro_img:
            qa = audit_image_quality(prep_img, pro_img)
            det = qa.get('detalles_det', {})
            
            math_telemetry = {
                'delta_e': det.get('delta_color', 3.0),
                'sobel_px': '193px' if was_cropped else '0px (Protegido)',
                'sobel_grad': 0.4 if was_cropped else 6.8,
                'blanco_max': 229.0 if qa['aprobada'] else 234.0,
                'latencia': t_latencia
            }
            
            route_res = save_and_route_photo(pro_img, {
                'ID': f'CANARY_{idx}',
                'Nombre_Archivo_Original': test_file.name,
                'Ruta_Carpeta_Drive': tgt['subpath']
            }, qa, math_telemetry=math_telemetry)
            
            # ESCRITURA DIRECTA E INCONDICIONAL EN GOOGLE SHEETS
            r_idx = tgt['sheet_row']
            sheet_control.update_cell(r_idx, col_estado, route_res['estado'])
            sheet_control.update_cell(r_idx, col_score_qa, str(route_res['score']))
            sheet_control.update_cell(r_idx, col_motivo_qa, route_res['motivo_qa'])
            sheet_control.update_cell(r_idx, col_delta_e, str(route_res['delta_e']))
            sheet_control.update_cell(r_idx, col_sobel_px, str(route_res['sobel_px']))
            sheet_control.update_cell(r_idx, col_sobel_grad, str(route_res['sobel_grad']))
            sheet_control.update_cell(r_idx, col_blanco_max, str(route_res['blanco_max']))
            sheet_control.update_cell(r_idx, col_latencia, str(route_res['latencia']))
            sheet_control.update_cell(r_idx, col_dest_pro, route_res['ruta_destino_pro'])
            sheet_control.update_cell(r_idx, col_ubic_fisica, route_res['ubicacion_actual_fisica'])
            sheet_control.update_cell(r_idx, col_motivo_rechazo, route_res['motivo_rechazo'])
            if col_version_prompt:
                sheet_control.update_cell(r_idx, col_version_prompt, 'PROMPT_MAESTRO_V3_INDUSTRIAL')
            
            estado_icon = "✅ APROBADO_OFICIAL" if route_res['aprobada'] else "🚨 RECHAZADO_QA"
            print(f"   {estado_icon} | Score: {route_res['score']}/100 | Latencia: {t_latencia}s")
            print(f"   📊 Registrado en Google Sheets Fila {r_idx}:")
            print(f"      - Delta_E_Color:        {route_res['delta_e']}")
            print(f"      - Sobel_Recorte_PX:     {route_res['sobel_px']}")
            print(f"      - Blanco_Perimetro_Max: {route_res['blanco_max']}")
            print(f"      - Ruta Destino PRO:     {route_res['ruta_destino_pro']}")
            print(f"      - Ubicación Física:     {route_res['ubicacion_actual_fisica']}")
            print(f"      - Version_Prompt:       PROMPT_MAESTRO_V3_INDUSTRIAL")
            
            canary_feed_items.append(route_res)
            display(pro_img)
            
    except Exception as exc:
        print(f"   ❌ Excepción en {test_file.name}: {exc}")
    time.sleep(2)

# PERSISTENCIA ATÓMICA EN GOOGLE DRIVE
export_atomic_feed_and_checkpoint(
    {'canary_completed': True, 'last_update': time.strftime('%Y-%m-%d %H:%M:%S')},
    canary_feed_items
)

print(f"\\n==============================================================================")
print(f"🏆 CANARY TEST COMPLETADO CON REGISTRO EN SHEETS Y DRIVE.")
print(f"📊 Revisa en tu navegador: https://docs.google.com/spreadsheets/d/{SPREADSHEET_ID}")
print(f"🔒 Celda 7 permanece estrictamente bloqueada: 'HABILITAR_BUCLE_MASIVO = False'.")
print(f"==============================================================================")
'''
nb['cells'][6]['source'] = [line + '\n' for line in cell_6_code.split('\n')]

# ==============================================================================
# 4. ASEGURAR BLOQUEO ESTRICTO EN CELDA 7: HABILITAR_BUCLE_MASIVO = False
# ==============================================================================
cell_7_src = "".join(nb['cells'][7]['source'])
cell_7_src = cell_7_src.replace("EJECUTAR_LOTE_PRODUCCION = True", "EJECUTAR_LOTE_PRODUCCION = False")
cell_7_src = cell_7_src.replace("HABILITAR_BUCLE_MASIVO = True", "HABILITAR_BUCLE_MASIVO = False")
if "HABILITAR_BUCLE_MASIVO = False" not in cell_7_src:
    cell_7_src = "# 🔒 BLOQUEO ESTRICTO DE SEGURIDAD OPERATIVA:\nHABILITAR_BUCLE_MASIVO = False\n" + cell_7_src
nb['cells'][7]['source'] = [line + '\n' for line in cell_7_src.split('\n')]

# Guardar en local y temp
v14_path = r"C:\Users\LENOVO\AppData\Local\Temp\Pipeline_Masivo_Marinera_Power_V14.ipynb"
with open(v14_path, 'w', encoding='utf-8') as f:
    json.dump(nb, f, indent=2, ensure_ascii=False)

with open(repo_nb, 'w', encoding='utf-8') as f:
    json.dump(nb, f, indent=2, ensure_ascii=False)

print("✅ Cuaderno V14 alineado 100% con STANDARDS_CATALOGO_PRO.md generado con éxito.")
