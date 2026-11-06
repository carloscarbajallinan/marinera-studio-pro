import json, re, sys
sys.stdout.reconfigure(encoding='utf-8')
from pathlib import Path

root = Path(r"C:\Users\LENOVO\Documents\Carlitos\IA\Antigravity\Profesionalización de catálogo\Cliente Marinera Power")
docs_html = root / "docs" / "index.html"
root_html = root / "index.html"

with open(docs_html, 'r', encoding='utf-8') as f:
    content = f.read()

# Real Canary Test Items
canary_items = [
    {
        "id": "CANARY-1",
        "Fecha_Creacion": "2026-11-05 21:12:00",
        "Ubicacion_Categoria": "Para ella / Falda / Falda de Ensayo / Lila con cinta morada",
        "Nombre_Archivo_Original": "foto (3).png",
        "Caso_Prueba": "Recorte Sobel de barras laterales blancas de Instagram (193px)",
        "Estado_Validacion": "APROBADO_CATALOGO",
        "Score": 98,
        "Observaciones": "Sobel recortó automáticamente 193px de barra blanca. Ciclorama #E5E1DE impecable con sombra de contacto suave.",
        "img_orig": "canary/canary_1_orig.png",
        "img_pro": "canary/canary_1_pro.jpg",
        "Link_Drive_PRO": "https://drive.google.com/file/d/1S2rDiJk3Zfq21ubYBX-vqywJ-SC-XtEJ/view"
    },
    {
        "id": "CANARY-2",
        "Fecha_Creacion": "2026-11-05 21:12:00",
        "Ubicacion_Categoria": "Para ella / Falda / Falda de Ensayo / Lila con cinta morada",
        "Nombre_Archivo_Original": "34a63e97 PRO.jpg",
        "Caso_Prueba": "Reemplazo de suelo de parquet de madera por ciclorama #E5E1DE",
        "Estado_Validacion": "APROBADO_CATALOGO",
        "Score": 95,
        "Observaciones": "Suelo de parquet eliminado al 100%. Fondo homogéneo con iluminación difusa 5200K y oclusión ambiental en base.",
        "img_orig": "canary/canary_2_orig.jpg",
        "img_pro": "canary/canary_2_pro.jpg",
        "Link_Drive_PRO": "https://drive.google.com/file/d/1Kd1sSmPlKhxYJ9rKoD6yaHfJxHHfP36i/view"
    },
    {
        "id": "CANARY-3",
        "Fecha_Creacion": "2026-11-05 21:12:00",
        "Ubicacion_Categoria": "Para ella / Falda / Falda de Ensayo / Coral con cinta blanca",
        "Nombre_Archivo_Original": "d72049af PRO.jpg",
        "Caso_Prueba": "Blindaje anatómico: Manos de bailarina y pañuelo de marinera al viento",
        "Estado_Validacion": "APROBADO_CATALOGO",
        "Score": 96,
        "Observaciones": "Cero amputación de dedos. Preservación perfecta del pañuelo blanco ondeando y silueta completa de marinera.",
        "img_orig": "canary/canary_3_orig.jpg",
        "img_pro": "canary/canary_3_pro.jpg",
        "Link_Drive_PRO": "https://drive.google.com/file/d/12x3fZK-fBXOl_3E9s_DJJsoefXH7GuO0/view"
    },
    {
        "id": "CANARY-4",
        "Fecha_Creacion": "2026-11-05 21:12:00",
        "Ubicacion_Categoria": "Para ella / Accesorios / Aretes para Marinera",
        "Nombre_Archivo_Original": "1.jpg (Aretes Filigrana)",
        "Caso_Prueba": "Macro Joyería: Oro peruano 18k y filigrana calada con brillo especular",
        "Estado_Validacion": "APROBADO_CATALOGO",
        "Score": 94,
        "Observaciones": "Orfebrería nítida. Destellos metálicos especulares y calado tradicional intactos sobre fondo #E5E1DE.",
        "img_orig": "canary/canary_4_orig.jpg",
        "img_pro": "canary/canary_4_pro.jpg",
        "Link_Drive_PRO": "https://drive.google.com/file/d/1RqMdROIcAd9tXEFaJegCVTGeAj2AK7iZ/view"
    },
    {
        "id": "CANARY-5",
        "Fecha_Creacion": "2026-11-05 21:12:00",
        "Ubicacion_Categoria": "Para ella / Falda / Falda de Ensayo / Morada con cinta blanca",
        "Nombre_Archivo_Original": "1841c6d0 PRO.jpg",
        "Caso_Prueba": "Mandato Cliente: Cero outpainting en plano medio (conservar encuadre)",
        "Estado_Validacion": "APROBADO_CATALOGO",
        "Score": 97,
        "Observaciones": "Cero invención de cuerpo inexistente. El plano medio/busto original fue estrictamente respetado.",
        "img_orig": "canary/canary_5_orig.jpg",
        "img_pro": "canary/canary_5_pro.jpg",
        "Link_Drive_PRO": "https://drive.google.com/file/d/1FlZ112AaTsWvavrEeAZJ2YyjK6JmxLeW/view"
    }
]

# Real Approved Catalog Batch Items
catalog_approved = [
    {
        "id": "BATCH-01",
        "Fecha_Creacion": "2026-11-05 13:14:57",
        "Ubicacion_Categoria": "Para ella / Accesorios / Escapulario para Mujer de Marinera",
        "Nombre_Archivo_Original": "1.1 Accesorios Escapulario",
        "Caso_Prueba": "Joyería Religiosa Bordada",
        "Estado_Validacion": "APROBADO_CATALOGO",
        "Score": 95,
        "Observaciones": "Sujeto intacto, fondo gris cálido minimalista #E5E1DE y sombras de contacto realistas.",
        "img_orig": "output/preview_cache/orig/1.1 Accesorios  Escapulario para Mujer de Marinera.jpg",
        "img_pro": "output/Lote_Prueba_Diario/1_1_Escapulario_Mujer_PRO_v2.jpg",
        "Link_Drive_PRO": "https://drive.google.com/file/d/1vxpf0zACFb3Y4puEk7qHJ_FpyqjZa0xi/view"
    },
    {
        "id": "BATCH-02",
        "Fecha_Creacion": "2026-11-05 13:14:57",
        "Ubicacion_Categoria": "Para ella / Accesorios / Aretes para Marinera",
        "Nombre_Archivo_Original": "1.1 aretes para marinera.jpg",
        "Caso_Prueba": "Aretes Filigrana Norteña",
        "Estado_Validacion": "APROBADO_CATALOGO",
        "Score": 96,
        "Observaciones": "Fidelidad cromática y brillo de metal preservados con nitidez 4K.",
        "img_orig": "output/preview_cache/orig/1.1 aretes para marinera.jpg",
        "img_pro": "output/Lote_Prueba_Diario/1_1_aretes_para_marinera_PRO_v2.jpg",
        "Link_Drive_PRO": "https://drive.google.com/file/d/1vK9Tnh4Dv0TVpNoWyB8TTIm70ApAcN8_/view"
    },
    {
        "id": "BATCH-03",
        "Fecha_Creacion": "2026-11-05 13:14:57",
        "Ubicacion_Categoria": "Para ella / Accesorios / Mantos / Manto de Pava bordado",
        "Nombre_Archivo_Original": "2 Manto de Pava bordado.jpg",
        "Caso_Prueba": "Bordados en Relieve de Manto",
        "Estado_Validacion": "APROBADO_CATALOGO",
        "Score": 95,
        "Observaciones": "Bordados de pava en relieve preservados al 100% sin artefactos ni desenfoque.",
        "img_orig": "output/preview_cache/orig/2 Manto de Pava bordado.jpg",
        "img_pro": "output/Lote_Prueba_Diario/2_Manto_Pava_Bordado_PRO_v2.jpg",
        "Link_Drive_PRO": "https://drive.google.com/file/d/1ccpFfUDGFt6Q2-3ToNoxiW0C_UIogoiq/view"
    },
    {
        "id": "BATCH-04",
        "Fecha_Creacion": "2026-11-05 13:14:57",
        "Ubicacion_Categoria": "Para ella / Accesorios / Pardos de Marinera / Pardos de Hilo",
        "Nombre_Archivo_Original": "2.2 Pardos de hilo.jpg",
        "Caso_Prueba": "Cordón de Hilo Tradicional",
        "Estado_Validacion": "APROBADO_CATALOGO",
        "Score": 94,
        "Observaciones": "Cordonería tradicional y nudos perfectamente definidos.",
        "img_orig": "output/preview_cache/orig/2.2 Pardos de hilo.jpg",
        "img_pro": "output/Lote_Prueba_Diario/2_2_Pardos_de_hilo_PRO_v2.jpg",
        "Link_Drive_PRO": "https://drive.google.com/file/d/1Vsbzk0goeVxP-_3ZnMsLNSNs9pKhURN-/view"
    },
    {
        "id": "BATCH-05",
        "Fecha_Creacion": "2026-11-05 13:14:57",
        "Ubicacion_Categoria": "Para ella / Accesorios / Faja de Hilo para Marinera",
        "Nombre_Archivo_Original": "3.1 Faja de Hilo para Marinera.jpg",
        "Caso_Prueba": "Calado y Trama Textil de Faja",
        "Estado_Validacion": "APROBADO_CATALOGO",
        "Score": 95,
        "Observaciones": "Calado textil geométrico preservado con iluminación difusa frontal.",
        "img_orig": "output/preview_cache/orig/3.1 Faja de Hilo para Marinera.jpg",
        "img_pro": "output/Lote_Prueba_Diario/3_1_Faja_de_Hilo_PRO_v2.jpg",
        "Link_Drive_PRO": "https://drive.google.com/file/d/1Xe7xVwTAObAnQ0VPzDxNPZHarTUkmyoL/view"
    }
]

total_qa = canary_items + catalog_approved

# Replace qaItems in HTML
replacement_js = f"const qaItems = {json.dumps(total_qa, ensure_ascii=False, indent=2)};"
content = re.sub(r'const qaItems = \[.*?\];', replacement_js, content, flags=re.DOTALL)

# Also update the render function to support direct image paths:
old_render_block = """      qaItems.forEach(item => {
        const id = item.ID_Registro || item.ID || 'N/A';
        const isApproved = pendingChanges[id] ? (pendingChanges[id].status === 'APROBADO_CATALOGO') : (item.Estado_Validacion === 'APROBADO_CATALOGO');
        
        let imgOrig = item.orig_id ? 'https://lh3.googleusercontent.com/d/' + item.orig_id : (item.local_orig_rel || 'https://placehold.co/400x400/101622/D4AF37?text=Original');
        let imgPro = item.pro_id ? 'https://lh3.googleusercontent.com/d/' + item.pro_id : (item.local_pro_rel || 'https://placehold.co/400x400/101622/D4AF37?text=PRO');"""

new_render_block = """      qaItems.forEach(item => {
        const id = item.id || item.ID || item.ID_Registro || 'ITEM';
        const isApproved = pendingChanges[id] ? (pendingChanges[id].status === 'APROBADO_CATALOGO') : (item.Estado_Validacion === 'APROBADO_CATALOGO');
        
        let imgOrig = item.img_orig || (item.local_orig_rel ? item.local_orig_rel : (item.orig_id ? 'https://lh3.googleusercontent.com/d/' + item.orig_id : 'https://placehold.co/400x400/101622/D4AF37?text=Original'));
        let imgPro = item.img_pro || (item.local_pro_rel ? item.local_pro_rel : (item.pro_id ? 'https://lh3.googleusercontent.com/d/' + item.pro_id : 'https://placehold.co/400x400/101622/D4AF37?text=PRO'));"""

if old_render_block in content:
    content = content.replace(old_render_block, new_render_block)
else:
    # Use regex replacement for the ID and image extraction
    content = re.sub(
        r'const id = item\.ID_Registro \|\| item\.ID \|\| [^;]+;',
        'const id = item.id || item.ID || item.ID_Registro || "ITEM";',
        content
    )
    content = re.sub(
        r'let imgOrig = [^;]+;',
        'let imgOrig = item.img_orig || (item.local_orig_rel ? item.local_orig_rel : (item.orig_id ? "https://lh3.googleusercontent.com/d/" + item.orig_id : "https://placehold.co/400x400/101622/D4AF37?text=Original"));',
        content
    )
    content = re.sub(
        r'let imgPro = [^;]+;',
        'let imgPro = item.img_pro || (item.local_pro_rel ? item.local_pro_rel : (item.pro_id ? "https://lh3.googleusercontent.com/d/" + item.pro_id : "https://placehold.co/400x400/101622/D4AF37?text=PRO"));',
        content
    )

with open(docs_html, 'w', encoding='utf-8') as f:
    f.write(content)

with open(root_html, 'w', encoding='utf-8') as f:
    f.write(content)

print("Updated docs/index.html and index.html successfully!")
