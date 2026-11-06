import subprocess, json, sys
sys.stdout.reconfigure(encoding='utf-8')

PROMPT_JOYERIA_ACCESORIOS = "PROMPT_JOYERIA_ACCESORIOS"
PROMPT_MODA_MODELO = "PROMPT_MODA_MODELO"

def select_prompt_for_category(subfolder_str, file_name=''):
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
        
    return PROMPT_MODA_MODELO, 'MODA_MODELO'

sheetId = '1kRsCZ7ZpPxyxrSEkUrYRl3NHahrQQche90RKK2yedQ8'
cmd = f'gsheets readonly read {sheetId} "Control_Total_Drive_V2!A1:H865" --json'
print("1. Leyendo las 863 filas del Catálogo Maestro desde Google Sheets...")
raw = subprocess.check_output(cmd, shell=True, text=True)
rows = json.loads(raw[raw.find('['):])

headers = rows[0]
data_rows = rows[1:]
print(f"✅ Total registros leídos en Catálogo Maestro: {len(data_rows)}")

CANARY_IDS_OBJETIVO = ['28', '418', '421', '423', '424']

print("\n" + "="*80)
print("2. SIMULACIÓN DETALLADA SOBRE LAS 5 FOTOS DEL CANARY TEST")
print("="*80)

canary_found = []
for idx, r in enumerate(data_rows, start=2):
    r_id = str(r[0]).strip()
    if r_id in CANARY_IDS_OBJETIVO:
        folder = str(r[1]).strip()
        product = str(r[2]).strip()
        filename = str(r[4]).strip()
        orig_drive_id = str(r[5]).strip()
        estado = str(r[7]).strip()
        
        prompt_text, modo = select_prompt_for_category(folder, filename)
        
        canary_found.append({
            'sheet_row': idx,
            'id': r_id,
            'filename': filename,
            'product': product,
            'folder': folder,
            'orig_drive_id': orig_drive_id,
            'modo': modo
        })

for c in sorted(canary_found, key=lambda x: CANARY_IDS_OBJETIVO.index(x['id'])):
    is_correct = (c['id'] == '28' and c['modo'] == 'JOYERIA_ACCESORIO') or (c['id'] != '28' and c['modo'] == 'MODA_MODELO')
    status_icon = "✅ CORRECTO" if is_correct else "❌ ERROR"
    print(f"\n🔹 ID {c['id']} (Fila {c['sheet_row']} en Sheet):")
    print(f"   Archivo:        {c['filename']}")
    print(f"   Producto:       {c['product']}")
    print(f"   Carpeta:        {c['folder']}")
    print(f"   Drive File ID:  {c['orig_drive_id']}")
    print(f"   Modo Asignado:  {status_icon} -> {c['modo']}")

print("\n" + "="*80)
print("3. SIMULACIÓN Y AUDITORÍA DE CLASIFICACIÓN EN TODO EL CATÁLOGO (863 FOTOS)")
print("="*80)

moda_count = 0
joyeria_count = 0
categories_summary = {}

for r in data_rows:
    folder = str(r[1]).strip()
    product = str(r[2]).strip()
    filename = str(r[4]).strip()
    
    _, modo = select_prompt_for_category(folder, filename)
    if modo == 'MODA_MODELO':
        moda_count += 1
    else:
        joyeria_count += 1
        
    parts = [p.strip() for p in folder.split('/') if p.strip()]
    top_folder = parts[2] if len(parts) > 2 else (parts[1] if len(parts) > 1 else folder)
    
    if top_folder not in categories_summary:
        categories_summary[top_folder] = {'MODA_MODELO': 0, 'JOYERIA_ACCESORIO': 0, 'samples': []}
    categories_summary[top_folder][modo] += 1
    if len(categories_summary[top_folder]['samples']) < 2:
        categories_summary[top_folder]['samples'].append((product, modo))

print(f"\n📊 RESUMEN GLOBAL (863 FOTOS):")
print(f"   Total Fotos Moda Modelada (MODA_MODELO):      {moda_count} fotos ({round(moda_count/len(data_rows)*100, 1)}%)")
print(f"   Total Fotos Joyería / Bodegón (JOYERIA_ACC):  {joyeria_count} fotos ({round(joyeria_count/len(data_rows)*100, 1)}%)")

print("\n📁 DESGLOSE POR SUBCARPETAS DEL CATÁLOGO:")
for cat, d in sorted(categories_summary.items()):
    print(f"\n   📂 Subcarpeta: [{cat}]")
    print(f"      MODA_MODELO: {d['MODA_MODELO']} | JOYERIA_ACCESORIO: {d['JOYERIA_ACCESORIO']}")
    for s_prod, s_modo in d['samples']:
        print(f"      • Muestra: '{s_prod[:45]}' -> {s_modo}")
