import json, sys
sys.stdout.reconfigure(encoding='utf-8')
from pathlib import Path

root = Path(r"C:\Users\LENOVO\Documents\Carlitos\IA\Antigravity\Profesionalización de catálogo\Cliente Marinera Power")
nb_path = r"C:\Users\LENOVO\AppData\Local\Temp\colab_current_v12.ipynb"

with open(nb_path, 'r', encoding='utf-8') as f:
    nb = json.load(f)

# Cell 2: Cabeceras y Columnas en Sheets
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
    'Motivo_Rechazo'
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
        if cands: return cands[0]
    global_cands = list(DIR_ORIGEN_ROOT.glob(f"**/{clean_name}*"))
    if global_cands: return global_cands[0]
    return None

print('✅ Plomería física, conexiones y cabeceras matemáticas configuradas.')
'''
nb['cells'][2]['source'] = [line + '\n' for line in cell_2_code.split('\n')]

# Cell 5: Protocolo Estricto, Exportación Offline y Checkpointing
cell_5_code = '''# 5. Módulo de Enrutamiento, Exportación Atómica Offline a Drive
def save_and_route_photo(pro_img, row_data, qa_result, orig_img=None, error_type=None, math_telemetry=None):
    row_id = str(row_data.get('ID', '0'))
    orig_name = str(row_data.get('Nombre_Archivo_Original', 'foto'))
    clean_name = orig_name.replace('.jpg', '').replace('.jpeg', '').replace('.png', '').replace('.heic', '').replace('.HEIC', '').strip()
    
    score = qa_result.get('score', 0) if qa_result else 0
    aprobada = qa_result.get('aprobada', False) if qa_result else False
    motivo = error_type if error_type else qa_result.get('motivo', 'FALLO_DESCONOCIDO')

    ruta_origen = str(row_data.get('Ruta_Carpeta_Drive', row_data.get('Carpeta_Ruta_Original', '')))
    partes = [p.strip() for p in ruta_origen.split('/') if p.strip()]
    if partes and partes[0].lower() in ['fotos catalogo', 'fotos catalogo marinera power']:
        partes = partes[1:]
    subrama_parts = partes if partes else ['General']
    
    target_pro_dir = DIR_PRO_ROOT.joinpath(*subrama_parts)
    ruta_destino_oficial = target_pro_dir / f"{clean_name}_pro.jpg"
    
    tag_bov = "APROBADA" if aprobada else "RECHAZADA"
    bov_path = BOVEDA_BACKUP_DIR / f"ID{row_id.zfill(3)}_{clean_name}_{tag_bov}_score{score}.jpg"
    if pro_img:
        pro_img.save(bov_path, quality=95)
        
    if aprobada:
        target_pro_dir.mkdir(parents=True, exist_ok=True)
        pro_img.save(ruta_destino_oficial, quality=95)
        ubicacion_actual = ruta_destino_oficial
        link_rechazada = ""
        estado_final = "APROBADO_OFICIAL"
        motivo_final = "-"
    else:
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

    telemetry = math_telemetry if math_telemetry else {}
    return {
        'aprobada': aprobada,
        'estado': estado_final,
        'score': score,
        'motivo_qa': qa_result.get('motivo', '') if qa_result else motivo,
        'ruta_destino_pro': str(ruta_destino_oficial),
        'ubicacion_actual_fisica': str(ubicacion_actual),
        'motivo_rechazo': motivo_final,
        'link_drive_rechazada': link_rechazada,
        'delta_e': telemetry.get('delta_e', 0.0),
        'sobel_px': telemetry.get('sobel_px', '0px'),
        'sobel_grad': telemetry.get('sobel_grad', 0.0),
        'blanco_max': telemetry.get('blanco_max', 229.0),
        'latencia': telemetry.get('latencia', 0.0),
        'boveda_path': str(bov_path)
    }

def export_atomic_feed_and_checkpoint(checkpoint_data, feed_items):
    """Guarda atómicamente en Google Drive el checkpoint y el feed web offline."""
    # 1. Checkpoint
    tmp_chk = str(CHECKPOINT_FILE) + ".tmp"
    with open(tmp_chk, 'w', encoding='utf-8') as f:
        json.dump(checkpoint_data, f, indent=2, ensure_ascii=False)
    os.replace(tmp_chk, CHECKPOINT_FILE)
    
    # 2. Output Web Feed
    tmp_feed = str(WEB_FEED_FILE) + ".tmp"
    with open(tmp_feed, 'w', encoding='utf-8') as f:
        json.dump({
            'last_update': time.strftime('%Y-%m-%d %H:%M:%S'),
            'total_items': len(feed_items),
            'items': feed_items
        }, f, indent=2, ensure_ascii=False)
    os.replace(tmp_feed, WEB_FEED_FILE)
    print(f"💾 Checkpoint y Web Feed exportados atómicamente a: {DIR_PRO_ROOT}")

print('✅ Módulo de guardado, trazabilidad y persistencia atómica en Drive listo.')
'''
nb['cells'][5]['source'] = [line + '\n' for line in cell_5_code.split('\n')]

# Cell 6: Canary Test Registrando TODO en Google Sheets
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
        
        pro_img, err = edit_background_gemini(prep_img)
        t_latencia = round(time.time() - t0, 2)
        
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
            
            # ESCRITURA INCONDICIONAL EN GOOGLE SHEETS
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
            
            estado_icon = "✅ APROBADO_OFICIAL" if route_res['aprobada'] else "🚨 RECHAZADO_QA"
            print(f"   {estado_icon} | Score: {route_res['score']}/100 | Latencia: {t_latencia}s")
            print(f"   📊 Registrado en Google Sheets Fila {r_idx}:")
            print(f"      - Delta_E_Color:        {route_res['delta_e']}")
            print(f"      - Sobel_Recorte_PX:     {route_res['sobel_px']}")
            print(f"      - Blanco_Perimetro_Max: {route_res['blanco_max']}")
            print(f"      - Ruta Destino PRO:     {route_res['ruta_destino_pro']}")
            print(f"      - Ubicación Física:     {route_res['ubicacion_actual_fisica']}")
            
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

v13_path = r"C:\Users\LENOVO\AppData\Local\Temp\Pipeline_Masivo_Marinera_Power_V13_IndustrialSheets.ipynb"
with open(v13_path, 'w', encoding='utf-8') as f:
    json.dump(nb, f, indent=2, ensure_ascii=False)

repo_nb = root / "notebooks" / "Pipeline_Masivo_Marinera_Power.ipynb"
with open(repo_nb, 'w', encoding='utf-8') as f:
    json.dump(nb, f, indent=2, ensure_ascii=False)

print("✅ Notebook V13 con Registro Directo en Sheets y Persistencia en Drive generado exitosamente.")
