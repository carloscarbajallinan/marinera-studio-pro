import json, sys
sys.stdout.reconfigure(encoding='utf-8')
from pathlib import Path

# Load V8 as base
v8_path = r"C:\Users\LENOVO\AppData\Local\Temp\Pipeline_Masivo_Marinera_Power_V8_Deterministic.ipynb"
with open(v8_path, 'r', encoding='utf-8') as f:
    nb = json.load(f)

# Cell 0: Header Markdown
nb['cells'][0]['source'] = [
    "# 🏛️ MARINERA POWER: Pipeline Industrial Definitivo & Control Humano (Lotes de 20)\n",
    "\n",
    "Pipeline oficial de profesionalización de catálogo para **Marinera Power**.\n",
    "- **Fondo de Estudio:** Gris cálido `#E5E1DE` con sombra de contacto y luz difusa 5200K.\n",
    "- **Pre-procesamiento:** Corrección EXIF + Detección de bordes Sobel (umbral 3.5) + Redimensionamiento Lanczos a 1920px.\n",
    "- **Control Humano (Human-in-the-Loop):** Procesamiento en **lotes de 20 fotos** para revisión y feedback de Carlos Carbajal.\n",
    "- **Respaldo Doble:** Enrutamiento en espejo a carpetas PRO / Erróneas + Bóveda Central permanente.\n",
    "- **Tablero Web en Vivo:** https://carloscarbajallinan.github.io/marinera-studio-pro/\n"
]

# Cell 2: Autenticación, Conexión Sheets y Auto-Detección de Rutas en Drive
# Incorporamos la función resolve_photo_path con partes_limpias y búsqueda insensible
cell_2_code = '''# 2. Autenticación, Conexión Sheets y Auto-Detección de Rutas en Drive
import os, io, gc, json, base64, time, requests, shutil
from pathlib import Path
import cv2
import numpy as np
from PIL import Image, ImageOps
from google.colab import userdata, auth
from IPython.display import display, Image as IPImage
import gspread
from google.auth import default

# 1. Cargar API Key
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

# 3. Auto-detección de la ruta exacta en Google Drive
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

print(f'📁 Ruta Origen detectada:  {DIR_ORIGEN_ROOT}')
print(f'📁 Ruta PRO detectada:     {DIR_PRO_ROOT}')
print(f'📁 Ruta Erróneas en Drive: {DIR_ERROR_ROOT}')
print(f'📁 Bóveda de Respaldo:     {BOVEDA_BACKUP_DIR}')

# 4. Resolvedor Robusto Linux (partes_limpias + búsqueda insensible)
def resolve_photo_path(ruta_origen, orig_name):
    """
    Localiza la foto física en Google Drive de forma ultra-robusta.
    Limpia espacios en rutas tipo Linux y realiza búsqueda insensible a extensiones.
    """
    partes = [p.strip() for p in str(ruta_origen).split('/') if p.strip()]
    if partes and partes[0].lower() in ['fotos catalogo', 'fotos catalogo marinera power']:
        partes = partes[1:]
        
    foto_dir = DIR_ORIGEN_ROOT.joinpath(*partes)
    
    clean_name = str(orig_name).replace('.jpg', '').replace('.jpeg', '').replace('.png', '').replace('.heic', '').replace('.HEIC', '').strip()
    
    # 1. Búsqueda directa en la subcarpeta del producto
    if foto_dir.exists():
        cands = list(foto_dir.glob(f"{clean_name}*"))
        if cands:
            return cands[0]
            
    # 2. Fallback global insensible en todo el árbol de origen
    global_cands = list(DIR_ORIGEN_ROOT.glob(f"**/{clean_name}*"))
    if global_cands:
        return global_cands[0]
        
    return None

print('✅ Resolvedor de rutas Linux y búsqueda insensible compilado.')
'''

nb['cells'][2]['source'] = [line + '\n' for line in cell_2_code.split('\n')]

# Cell 6: Canary Test (Actualizado para usar resolve_photo_path y mostrar imágenes claras)
cell_6_code = '''# 6. CANARY TEST DETERMINISTA (5 Casos Críticos de Fuego)
canary_targets = [
    {
        'id_test': 'CANARY_1_BARRAS_BLANCAS',
        'subpath': 'Para ella/Falda/Falda de Ensayo/Faldas de Ensayo de razo 1 bobo/Falda para Ensayo de Razo - Lila con cinta morada',
        'orig_name': 'foto (3).png',
        'caso': 'Recorte Sobel de barras laterales blancas de Instagram (193px)'
    },
    {
        'id_test': 'CANARY_2_PARQUET_SALON',
        'subpath': 'Para ella/Falda/Falda de Ensayo/Faldas de Ensayo de razo 1 bobo/Falda para Ensayo de Razo - Lila con cinta morada',
        'orig_name': '34a63e97 PRO.jpg',
        'caso': 'Reemplazo total de suelo de parquet por ciclorama #E5E1DE con oclusión'
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

print(f"🦅 INICIANDO CANARY TEST DETERMINISTA (Ruta Base: {DIR_ORIGEN_ROOT})...\\n")
canary_results = []

for idx, tgt in enumerate(canary_targets, start=1):
    test_file = resolve_photo_path(tgt['subpath'], tgt['orig_name'])
    
    if not test_file or not test_file.exists():
        print(f"⚠️ [{idx}/5] No se localizó archivo para {tgt['id_test']}: {tgt['orig_name']}")
        continue

    print(f"▶️ [{idx}/5] Evaluando {tgt['id_test']}: {test_file.name}...")
    print(f"   🎯 Caso a probar: {tgt['caso']}")
    
    t0 = time.time()
    try:
        prep_img, was_cropped = prepare_image_pipeline(test_file)
        pro_img, err = edit_background_gemini(prep_img)
        
        if pro_img:
            qa = audit_image_quality(prep_img, pro_img)
            final_p, bov_p, aprobada = save_and_route_photo(pro_img, {
                'ID': f'CANARY_{idx}',
                'Nombre_Archivo_Original': test_file.name,
                'Ruta_Carpeta_Drive': tgt['subpath']
            }, qa)
            t_tot = time.time() - t0
            
            print(f"   ✅ Score QA: {qa.get('score')}/100 | Aprobada: {aprobada} | Total: {t_tot:.1f}s (Sobel Crop: {was_cropped})")
            print(f"   📝 Motivo QA: {qa.get('motivo')}")
            print(f"   📁 Guardada en: {final_p}")
            canary_results.append({'test': tgt['id_test'], 'score': qa.get('score'), 'aprobada': aprobada, 'file': test_file.name})
            display(pro_img)
        else:
            print(f"   ❌ Fallo API: {err}")
    except Exception as exc:
        print(f"   ❌ Error procesando {test_file.name}: {exc}")
    time.sleep(3)

aprobadas = sum(1 for c in canary_results if c.get('aprobada'))
print(f"\\n🏆 RESUMEN CANARY TEST: {aprobadas}/{len(canary_results)} Aprobadas.")
if aprobadas >= 4:
    print("🚀 ¡CANARY TEST SUPERADO CON ÉXITO! Las fotos cumplen todos los Quality Gates del Red Team.")
'''

nb['cells'][6]['source'] = [line + '\n' for line in cell_6_code.split('\n')]

# Cell 7: Bucle Masivo en Lotes de 20 con Seguro de Ejecución y Logging a Sheet
cell_7_code = '''# ==============================================================================
# 🎯 PASO 7: PROCESAMIENTO EN LOTES DE 20 FOTOS (HUMAN-IN-THE-LOOP)
# ==============================================================================
# 🔒 SEGURO DE ACTIVACIÓN MANUAL:
# Para ejecutar el Lote 1 (20 fotos), cambia esta variable a True:
EJECUTAR_LOTE_PRODUCCION = False

CHUNK_SIZE = 20  # Lote estricto de 20 fotos solicitado por Carlos Carbajal

if not EJECUTAR_LOTE_PRODUCCION:
    print("🔒 [PASO 7 EN ESPERA] Seguro de activación manual activo.")
    print("👉 Este paso NO se ejecutará al pulsar 'Ejecutar todo'.")
    print(f"👉 Para procesar el siguiente lote de {CHUNK_SIZE} fotos:")
    print("   1. Cambia arriba: EJECUTAR_LOTE_PRODUCCION = True")
    print("   2. Presiona únicamente el botón Play de esta celda.")
else:
    print(f"🚀 INICIANDO LOTE DE {CHUNK_SIZE} FOTOS (Mesa de Control Oficial)...")
    
    # 1. Cargar datos de la pestaña oficial: Control_Total_Drive_V2
    sheet_data = sheet_control.get_all_records()
    headers = sheet_control.row_values(1)
    
    # Column indices (1-based for gspread)
    col_estado_idx = headers.index('Estado') + 1 if 'Estado' in headers else 8
    
    # Asegurar columnas para feedback de Carlos
    if 'Feedback_Carlos' not in headers:
        sheet_control.update_cell(1, len(headers) + 1, 'Feedback_Carlos')
        sheet_control.update_cell(1, len(headers) + 2, 'Detalle_Error_Carlos')
        headers = sheet_control.row_values(1)
        
    col_feedback_idx = headers.index('Feedback_Carlos') + 1
    col_detalle_idx = headers.index('Detalle_Error_Carlos') + 1
    
    # 2. Cargar Checkpoint
    checkpoint = load_checkpoint()
    processed_set = set(checkpoint.get('processed_ids', []))
    print(f"📦 Fotos ya aseguradas en checkpoint previo: {len(processed_set)}")
    
    # 3. Filtrar pendientes
    pendientes = []
    for idx, row in enumerate(sheet_data, start=2):
        row_id = str(row.get('ID', ''))
        estado = str(row.get('Estado', '')).upper()
        if row_id and (row_id not in processed_set) and ('PRO_VERIFICADO' not in estado):
            pendientes.append((idx, row))
            
    print(f"📊 Total fotos pendientes en catálogo: {len(pendientes)}")
    chunk_to_process = pendientes[:CHUNK_SIZE]
    print(f"🎯 Procesando lote de {len(chunk_to_process)} fotos ahora...\\n")
    
    exitosas_chunk = 0
    rechazadas_chunk = 0
    
    for i, (row_idx, row_data) in enumerate(chunk_to_process, start=1):
        row_id = str(row_data.get('ID', '0'))
        orig_name = str(row_data.get('Nombre_Archivo_Original', ''))
        ruta_origen = str(row_data.get('Ruta_Carpeta_Drive', row_data.get('Carpeta_Ruta_Original', '')))
        
        print(f"[{i}/{len(chunk_to_process)}] Foto ID {row_id}: {orig_name}")
        
        # Localización ultra-robusta
        foto_path = resolve_photo_path(ruta_origen, orig_name)
        if not foto_path or not foto_path.exists():
            print(f"   ⚠️ Archivo físico no hallado en Drive. Saltando.")
            continue
            
        t0 = time.time()
        try:
            # Pre-procesamiento Sobel
            prep_img, was_cropped = prepare_image_pipeline(foto_path)
            
            # Generación IA
            pro_img, err = edit_background_gemini(prep_img)
            
            if pro_img:
                # Auditoría de Calidad
                qa = audit_image_quality(prep_img, pro_img)
                final_path, bov_path, aprobada = save_and_route_photo(pro_img, row_data, qa)
                
                # Registro en Sheet
                nuevo_estado = 'PRO_PENDIENTE_FEEDBACK_CARLOS' if aprobada else 'FALLIDA_QA'
                sheet_control.update_cell(row_idx, col_estado_idx, nuevo_estado)
                
                if aprobada:
                    exitosas_chunk += 1
                    print(f"   ✅ Aprobada QA (Score {qa.get('score')}/100) -> Guardada en PRO y Bóveda")
                else:
                    rechazadas_chunk += 1
                    print(f"   ⚠️ Rechazada QA (Score {qa.get('score')}/100) -> Guardada en Carpeta Erróneas")
                    
                display(pro_img)
            else:
                sheet_control.update_cell(row_idx, col_estado_idx, 'ERROR_GENERACION_API')
                print(f"   ❌ Fallo API Gemini: {err}")
                
        except Exception as exc:
            print(f"   ❌ Excepción aislada en ID {row_id}: {exc}")
        finally:
            gc.collect()
            
        processed_set.add(row_id)
        save_checkpoint(list(processed_set))
        time.sleep(3)
        
    print(f"\\n==============================================================================")
    print(f"🎉 LOTE DE {len(chunk_to_process)} FOTOS COMPLETADO!")
    print(f"📊 Resumen: {exitosas_chunk} aprobadas por QA | {rechazadas_chunk} en carpeta erróneas")
    print(f"📁 Todas las fotos tienen copia de seguridad en: _BOVEDA_HISTORIAL_BACKUP")
    print(f"🌐 Tablero de Control Web: https://carloscarbajallinan.github.io/marinera-studio-pro/")
    print(f"📋 Hoja Oficial en Sheets: {sheet_control.title}")
    print(f"👉 Asigna tu feedback (APROBADO_CARLOS / CORREGIR_CARLOS) en el Tablero o Sheet")
    print(f"   antes de correr el siguiente lote.")
    print(f"==============================================================================")
'''

nb['cells'][7]['source'] = [line + '\n' for line in cell_7_code.split('\n')]

# Save V10 notebook
v10_path = r"C:\Users\LENOVO\AppData\Local\Temp\Pipeline_Masivo_Marinera_Power_V10.ipynb"
with open(v10_path, 'w', encoding='utf-8') as f:
    json.dump(nb, f, indent=2, ensure_ascii=False)

# Copy to repo and desktop
repo_nb = r"C:\Users\LENOVO\Documents\Carlitos\IA\Antigravity\Profesionalización de catálogo\Cliente Marinera Power\notebooks\Pipeline_Masivo_Marinera_Power.ipynb"
desktop_nb = r"C:\Users\LENOVO\Desktop\Pipeline_Masivo_Marinera_Power.ipynb"

with open(repo_nb, 'w', encoding='utf-8') as f:
    json.dump(nb, f, indent=2, ensure_ascii=False)

with open(desktop_nb, 'w', encoding='utf-8') as f:
    json.dump(nb, f, indent=2, ensure_ascii=False)

print("✅ Notebook V10 creado exitosamente en Temp, Repo y Desktop.")
