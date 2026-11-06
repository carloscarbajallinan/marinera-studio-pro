import subprocess, json, sys
sys.stdout.reconfigure(encoding='utf-8')

PROMPT_JOYERIA_ACCESORIOS = "PROMPT_JOYERIA_ACCESORIOS"
PROMPT_MODA_MODELO = "PROMPT_MODA_MODELO"

def select_prompt_for_category_v2(subfolder_str, file_name=''):
    text = f"{subfolder_str} {file_name}".lower()
    
    # 1. Prioridad Absoluta: Prendas de Vestir y Danza Modelada
    # (Removido 'ensayo' porque es adjetivo de uso, no una prenda; añadido 'anaco')
    clothing_keywords = [
        'falda', 'faldas', 'blusa', 'blusas', 'vestido', 'vestidos',
        'traje', 'trajes', 'enague', 'enagues', 'enagua', 'enaguas',
        'pantalon', 'pantalones', 'camisa', 'camisas', 'chaleco',
        'poncho', 'polo', 'bobo', 'bobos', 'razo', 'anaco', 'anacos'
    ]
    if any(ck in text for ck in clothing_keywords):
        return PROMPT_MODA_MODELO, 'MODA_MODELO'
        
    # 2. Prioridad Secundaria: Accesorios y Joyería Aislada (Still Life / Fotoproducto)
    jewelry_keywords = [
        'accesorio', 'accesorios', 'arete', 'aretes', 'escapulario', 'escapularios',
        'collar', 'collares', 'filigrana', 'joya', 'joyas', 'joyeria', 'joyería',
        'prendedor', 'broche', 'tocado', 'sombrero', 'sombreros', 'faja', 'fajas'
    ]
    if any(jk in text for jk in jewelry_keywords):
        return PROMPT_JOYERIA_ACCESORIOS, 'JOYERIA_ACCESORIO'
        
    return PROMPT_MODA_MODELO, 'MODA_MODELO'

sheetId = '1kRsCZ7ZpPxyxrSEkUrYRl3NHahrQQche90RKK2yedQ8'
cmd = f'gsheets readonly read {sheetId} "Control_Total_Drive_V2!A1:H865" --json'
raw = subprocess.check_output(cmd, shell=True, text=True)
rows = json.loads(raw[raw.find('['):])[1:]

print("AUDITANDO CLASIFICACIÓN V2 SOBRE 863 FOTOS:")
joyeria_items = []
moda_items = []

for r in rows:
    folder = str(r[1]).strip()
    prod = str(r[2]).strip()
    filename = str(r[4]).strip()
    r_id = str(r[0]).strip()
    
    _, modo = select_prompt_for_category_v2(folder, filename)
    if modo == 'JOYERIA_ACCESORIO':
        joyeria_items.append((r_id, prod, folder))
    else:
        moda_items.append((r_id, prod, folder))

print(f"\nTotal MODA_MODELO:     {len(moda_items)}")
print(f"Total JOYERIA_ACCESORIO: {len(joyeria_items)}")

print("\n--- TODOS LOS PRODUCTOS CLASIFICADOS COMO JOYERIA_ACCESORIO ---")
unique_j_prods = {}
for r_id, prod, folder in joyeria_items:
    if prod not in unique_j_prods:
        unique_j_prods[prod] = (folder, 0)
    unique_j_prods[prod] = (folder, unique_j_prods[prod][1] + 1)

for p, (f, count) in sorted(unique_j_prods.items()):
    print(f"  • '{p}' ({count} fotos) | Folder: '{f}'")
