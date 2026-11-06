import subprocess
import json
from pathlib import Path

local_dir = Path(r"C:\Users\LENOVO\Pictures\Marinera Power\fotos creadas")
local_files = sorted([f.name for f in local_dir.iterdir() if f.is_file()])

cmd = ['gsheets', 'readonly', 'read', '1kRsCZ7ZpPxyxrSEkUrYRl3NHahrQQche90RKK2yedQ8', 'Registro_Imagenes_Creadas!A1:N40', '--json']
res = subprocess.run(cmd, capture_output=True, text=True, shell=True)
data = json.loads(res.stdout)
rows = data[1:]

registered_names = set()
for r in rows:
    # Col D is Nombre_Archivo_Original
    if len(r) > 3 and r[3]:
        registered_names.add(r[3].strip())
    # Col F is Nombre_Archivo_PRO
    if len(r) > 5 and r[5]:
        registered_names.add(r[5].strip())

print(f"Total fotos en 'fotos creadas': {len(local_files)}")
print(f"Total registros en Registro_Imagenes_Creadas: {len(rows)}")

unprocessed = [f for f in local_files if f not in registered_names]
print(f"Fotos no registradas aún en Registro_Imagenes_Creadas: {len(unprocessed)}")
print("\nPrimeras 20 fotos pendientes:")
for f in unprocessed[:20]:
    print(" ", f)
