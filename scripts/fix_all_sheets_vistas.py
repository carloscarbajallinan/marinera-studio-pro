import subprocess
import json
import re

SPREADSHEET_ID = "1kRsCZ7ZpPxyxrSEkUrYRl3NHahrQQche90RKK2yedQ8"

print("1. Leyendo datos de Registro_Imagenes_Creadas...")
cmd = ["gsheets", "readonly", "read", SPREADSHEET_ID, "Registro_Imagenes_Creadas!A1:M25", "--json"]
res = subprocess.run(cmd, capture_output=True, text=True, shell=True)
try:
    reg_data = json.loads(res.stdout)
except Exception as e:
    print("Error reading Registro_Imagenes_Creadas:", e)
    print("Output:", res.stdout[:200])
    exit(1)

print(f"Total filas leídas en Registro_Imagenes_Creadas: {len(reg_data)}")

# Columnas en Registro_Imagenes_Creadas:
# Col E (index 4): Link_Drive_Original
# Col G (index 6): ID_Drive_PRO
# Col H (index 7): Link_Drive_PRO

def extract_drive_id(link_or_id):
    if not link_or_id or link_or_id.strip() == "-" or link_or_id.strip() == "":
        return None
    link_or_id = link_or_id.strip()
    match = re.search(r'/d/([a-zA-Z0-9_-]+)', link_or_id)
    if match:
        return match.group(1)
    if re.match(r'^[a-zA-Z0-9_-]{20,}$', link_or_id):
        return link_or_id
    return None

batch_ops = []

# Filas de Registro_Imagenes_Creadas (fila 2 en adelante)
for idx, row in enumerate(reg_data[1:], start=2):
    orig_link = row[4] if len(row) > 4 else ""
    pro_id = row[6] if len(row) > 6 else ""
    pro_link = row[7] if len(row) > 7 else ""
    
    orig_id = extract_drive_id(orig_link)
    final_pro_id = extract_drive_id(pro_id) or extract_drive_id(pro_link)
    
    orig_formula = f'=IMAGE("https://lh3.googleusercontent.com/d/{orig_id}")' if orig_id else ""
    pro_formula = f'=IMAGE("https://lh3.googleusercontent.com/d/{final_pro_id}")' if final_pro_id else ""
    
    batch_ops.append({
        "op": "write",
        "range": f"Registro_Imagenes_Creadas!N{idx}:O{idx}",
        "data": [[orig_formula, pro_formula]]
    })

print(f"Generadas {len(batch_ops)} operaciones para Registro_Imagenes_Creadas.")

# Ahora para Control_Total_Fotos
print("\n2. Leyendo datos de Control_Total_Fotos...")
cmd_total = ["gsheets", "readonly", "read", SPREADSHEET_ID, "Control_Total_Fotos!A1:J867", "--json"]
res_total = subprocess.run(cmd_total, capture_output=True, text=True, shell=True)
total_data = json.loads(res_total.stdout)

print(f"Total filas leídas en Control_Total_Fotos: {len(total_data)}")

# Col D (index 3): ID_Archivo_Original
# Col H (index 7): ID_Foto_PRO
# Queremos escribir en K (Vista_Original) y L (Vista_PRO)
# En es_ES, usando fórmulas con comillas limpias:
# Para K: =SI(ESBLANCO(D2);"";IMAGE("https://lh3.googleusercontent.com/d/"&D2)) o directamente el ID fijo
# O mejor aún: generamos la fórmula fija con comillas o la fórmula relativa correcta:
control_batch = []
for idx, row in enumerate(total_data[1:], start=2):
    orig_id = row[3].strip() if len(row) > 3 and row[3] else None
    pro_id = row[7].strip() if len(row) > 7 and row[7] and row[7] != "-" else None
    
    # En la fórmula de Google Sheets en español:
    # Si ponemos el enlace directo exacto cuando existe el ID:
    orig_formula = f'=IMAGE("https://lh3.googleusercontent.com/d/{orig_id}")' if orig_id else ""
    pro_formula = f'=IMAGE("https://lh3.googleusercontent.com/d/{pro_id}")' if pro_id else ""
    
    control_batch.append([orig_formula, pro_formula])

batch_ops.append({
    "op": "write",
    "range": f"Control_Total_Fotos!K2:L{len(control_batch) + 1}",
    "data": control_batch
})

print(f"Generado bloque para Control_Total_Fotos ({len(control_batch)} filas).")

# Guardar batch.json
with open("C:/Users/LENOVO/Documents/Carlitos/IA/Antigravity/Profesionalización de catálogo/Cliente Marinera Power/scripts/batch_vistas.json", "w", encoding="utf-8") as f:
    json.dump(batch_ops, f)

print("batch_vistas.json guardado con éxito. Ejecutando gsheets mutate batch...")
