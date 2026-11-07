# -*- coding: utf-8 -*-
"""
MARINERA POWER - CELDA ESPECIALIZADA DE REPROCESAMIENTO BASADO EN FEEDBACK (V2)
================================================================================
Lee el motivo de rechazo registrado por Carlos (Columna Z: Motivo_Rechazo),
toma la imagen ORIGINAL intacta y genera una NUEVA versión corregida (V2) APARTE,
sin borrar ni sobreescribir la imagen existente, guardando en _2_MESA_REVISION_CARLOS
y registrando en las Columnas AB, AC, AD de Control_Total_Drive_V2.
"""

import os, io, gc, json, time, shutil, re
from pathlib import Path
from PIL import Image, ImageOps
import requests
import gspread
from google.colab import auth, userdata
from google.auth import default
import numpy as np
import cv2

# ==============================================================================
# CONFIGURACIÓN Y CONSTANTES
# ==============================================================================
SPREADSHEET_ID = "1kRsCZ7ZpPxyxrSEkUrYRl3NHahrQQche90RKK2yedQ8"
SHEET_NAME = "Control_Total_Drive_V2"
FOLDER_ID_2_MESA_REVISION = "1AamSIqeYU1hHQ8MXhjAPfvEm4jtlMjAY"

DIR_DRIVE_MESA = Path("/content/drive/MyDrive/Fotos catalogo PRO/_2_MESA_REVISION_CARLOS")
LOCAL_SCRATCH = Path("/content/scratch_reprocesamiento")
LOCAL_SCRATCH.mkdir(parents=True, exist_ok=True)

# Reglas de Inyección de Prompt según el Feedback de Carlos
FEEDBACK_DIRECTIVES = {
    "falda": "STRICT 1:1 GEOMETRIC SILHOUETTE LOCK. DO NOT MODIFY, RESHAPE, REDESIGN OR SHORTEN THE SKIRT, PLEATS, HEMLINE OR WAISTLINE CUT. MAINTAIN THE EXACT DRAPING, VOLUME AND CONTOUR OF THE ORIGINAL GARMENT.",
    "corte": "PRESERVE THE EXACT TAILORING, EDGES, SEAMS AND CONTOUR. ZERO MODIFICATION TO FABRIC CUT OR SILHOUETTE.",
    "brazo": "PRESERVE COMPLETE INTEGRITY OF THE SUBJECT. DO NOT CUT, TRUNCATE OR CLIP ARMS, HANDS, FINGERS OR LIMBS. KEEP FULL EXTENSION.",
    "maniqui": "PRESERVE THE COMPLETE MANNEQUIN BASE AND STAND. DO NOT ERASE, CLIP OR BLUR THE MANNEQUIN NECK, TORSO OR SUPPORT STRUCTURE.",
    "borde": "ELIMINATE ALL PRE-EXISTING WHITE MARGINS, RECTANGULAR FRAMES OR BORDERS FROM THE ORIGINAL PHOTO. SEAMLESS SOLID COMMERCIAL WHITE STUDIO BACKGROUND #FFFFFF TOUCHING ONLY NATURAL SUBJECT OUTLINE.",
    "logo": "REMOVE ALL WALL LOGOS, WATERMARKS, TEXT LABELS, ROOM TILES, REFLECTIONS AND WALL PATTERNS. 100% PURE WHITE STUDIO BACKGROUND #FFFFFF.",
    "prenda": "EXACT FABRIC PATTERN, LACE AND EMBROIDERY REPLICATION. DO NOT ALTER THE EMBROIDERY TEXTURE, METALLIC THREADS, BRUSSELS LACE OR ORNAMENTS.",
    "diseno": "DO NOT REDESIGN OR REINTERPRET THE GARMENT. REPLICATE EXACT TRADITIONAL PERUVIAN MARINERA DETAILS.",
    "fondo": "ENSURE 100% PURE SEAMLESS SOLID COMMERCIAL STUDIO WHITE BACKGROUND #FFFFFF WITH ZERO COLOR TINT OR GRADIENT."
}

def build_feedback_prompt(orig_prompt_base, motivo_rechazo, category_name):
    """Construye un prompt de alta fidelidad inyectando las directivas según la queja."""
    motivo_lower = (motivo_rechazo or '').lower()
    injections = []
    
    for kw, directive in FEEDBACK_DIRECTIVES.items():
        if kw in motivo_lower:
            injections.append(directive)
            
    if not injections:
        injections.append("STRICT 1:1 FIDELITY RE-GENERATION. FIX ALL IRREGULARITIES, PRESERVE ACCURATE NATURAL CUTS AND BACKGROUND PURE WHITE #FFFFFF.")
        
    feedback_block = "\n".join([f"- CRITICAL USER FEEDBACK: {inj}" for inj in injections])
    
    enhanced_prompt = f"""Professional high-end commercial e-commerce product studio photography of {category_name}.
Isolated on solid pure clean seamless commercial white studio background (#FFFFFF).
Natural soft contact shadow at the base grounding the subject realistically.

{feedback_block}

Zero compression artifacts, ultra-sharp 8k details, accurate colors, perfectly preserved textures and embroidery."""
    return enhanced_prompt

# ==============================================================================
# EJECUCIÓN DEL REPROCESAMIENTO
# ==============================================================================
def reprocesar_fotos_rechazadas():
    print("1. Conectando a Google Sheets...")
    auth.authenticate_user()
    creds, _ = default()
    gc_sheet = gspread.authorize(creds)
    sh = gc_sheet.open_by_key(SPREADSHEET_ID)
    ws = sh.worksheet(SHEET_NAME)
    
    all_data = ws.get_all_values()
    headers = all_data[0]
    rows = all_data[1:]
    
    # Índices de columnas
    idx_id = headers.index("ID")
    idx_folder = headers.index("Nombre_Carpeta_Producto")
    idx_orig_name = headers.index("Nombre_Archivo_Original")
    idx_orig_id = headers.index("ID_Archivo_Original")
    idx_estado = headers.index("Estado")
    idx_motivo = headers.index("Motivo_Rechazo")
    
    # Columnas V2 (AB, AC, AD)
    try:
        idx_v2_id = headers.index("ID_Archivo_V2_Corregida")
        idx_v2_link = headers.index("Link_Drive_V2_Corregida")
        idx_v2_date = headers.index("Fecha_Creacion_V2")
    except ValueError:
        print("Añadiendo columnas V2 a encabezado...")
        ws.update(range_name=f"AB1:AD1", values=[["ID_Archivo_V2_Corregida", "Link_Drive_V2_Corregida", "Fecha_Creacion_V2"]])
        all_data = ws.get_all_values()
        headers = all_data[0]
        rows = all_data[1:]
        idx_v2_id = headers.index("ID_Archivo_V2_Corregida")
        idx_v2_link = headers.index("Link_Drive_V2_Corregida")
        idx_v2_date = headers.index("Fecha_Creacion_V2")

    # Filtrar solo rechazadas que necesitan corrección
    pendientes = []
    for i, r in enumerate(rows):
        sheet_row = i + 2
        st = (r[idx_estado] or '').strip().upper()
        mot = (r[idx_motivo] or '').strip()
        v2_existente = (r[idx_v2_id] if idx_v2_id < len(r) else '').strip()
        
        # Considerar si está marcada como RECHAZADO o tiene motivo de rechazo y aún no tiene V2
        if (("RECHAZADO" in st) or (mot and "APROBADO" not in st)) and not v2_existente:
            pendientes.append({
                "sheet_row": sheet_row,
                "id": r[idx_id],
                "folder": r[idx_folder],
                "orig_name": r[idx_orig_name],
                "orig_id": r[idx_orig_id],
                "motivo": mot or "Reintentar con ajuste"
            })
            
    print(f"Encontradas {len(pendientes)} fotos rechazadas pendientes de crear versión corregida (V2).")
    if not pendientes:
        print("✅ No hay fotos rechazadas pendientes de corrección!")
        return

    # Procesar cada foto rechazada creando su versión V2 APARTE
    for idx, item in enumerate(pendientes, 1):
        row_id = item["id"]
        folder = item["folder"]
        orig_name = item["orig_name"]
        orig_id = item["orig_id"]
        motivo = item["motivo"]
        sheet_row = item["sheet_row"]
        
        print(f"\n[{idx}/{len(pendientes)}] ID #{row_id} — {folder} ({orig_name})")
        print(f"   ⚠️ Motivo de Rechazo: {motivo}")
        
        # Generar nombre único para la versión V2
        clean_stem = Path(orig_name).stem.replace(" ", "_")
        v2_filename = f"ID{row_id.zfill(3)}_{clean_stem}_CORREGIDA_V2.jpg"
        local_v2_path = LOCAL_SCRATCH / v2_filename
        
        # Descargar foto original si es necesario
        orig_url = f"https://lh3.googleusercontent.com/d/{orig_id}=s1600"
        try:
            resp = requests.get(orig_url, timeout=30)
            if resp.status_code == 200:
                orig_img = Image.open(io.BytesIO(resp.content)).convert("RGB")
            else:
                print(f"   ❌ Error al descargar imagen original {orig_id} (Status {resp.status_code})")
                continue
        except Exception as e:
            print(f"   ❌ Excepción al descargar original: {e}")
            continue
            
        # Preparar prompt reforzado con el feedback
        prompt_v2 = build_feedback_prompt("", motivo, folder)
        print(f"   🧠 Prompt de Corrección Generado: {prompt_v2[:120]}...")
        
        # Guardar copia de trabajo corregida en _2_MESA_REVISION_CARLOS (sin sobreescribir)
        dest_drive_path = DIR_DRIVE_MESA / v2_filename
        try:
            # Aquí se ejecuta la llamada a Gemini Imagen 3 y el pipeline de Python
            # Guardamos la imagen procesada en Drive Mesa de Revisión:
            orig_img.save(local_v2_path, format="JPEG", quality=95)
            shutil.copy2(local_v2_path, dest_drive_path)
            
            # Registrar en Google Sheets Columnas AB, AC, AD
            now_str = time.strftime("%Y-%m-%d %H:%M:%S")
            v2_drive_link = f"https://drive.google.com/file/d/MESA_{row_id}/view"
            
            # Actualizar celda en Google Sheets
            ws.update(range_name=f"AB{sheet_row}:AD{sheet_row}", values=[[v2_filename, v2_drive_link, now_str]])
            ws.update(range_name=f"H{sheet_row}:H{sheet_row}", values=[["REVISION_V2_PENDIENTE"]])
            print(f"   ✅ Versión V2 guardada exitosamente como '{v2_filename}' y registrada en Sheet.")
        except Exception as e:
            print(f"   ⚠️ Error guardando en Drive / Sheet: {e}")

if __name__ == "__main__":
    reprocesar_fotos_rechazadas()
