import subprocess
import json
from pathlib import Path

local_dir = Path(r"C:\Users\LENOVO\Pictures\Marinera Power\fotos creadas")
local_files = sorted([f for f in local_dir.iterdir() if f.is_file()], key=lambda x: x.name)

# Leer Registro_Imagenes_Creadas
cmd = ['gsheets', 'readonly', 'read', '1kRsCZ7ZpPxyxrSEkUrYRl3NHahrQQche90RKK2yedQ8', 'Registro_Imagenes_Creadas!A1:N30', '--json']
res = subprocess.run(cmd, capture_output=True, text=True, shell=True)
data = json.loads(res.stdout)
rows = data[1:]

processed_orig_names = set()
for r in rows:
    # Si fue aprobado
    if len(r) > 11 and r[11] == "APROBADO_CATALOGO":
        processed_orig_names.add(r[3].strip())

print(f"Total fotos aprobadas actualmente: {len(processed_orig_names)}")
for p in processed_orig_names:
    print("  Aprobada:", p)

candidates = []
for f in local_files:
    if f.name not in processed_orig_names:
        candidates.append(f)

print(f"\nCandidatos pendientes: {len(candidates)}")
print("Siguientes 15 candidatos:")
for idx, c in enumerate(candidates[:15], 1):
    print(f"{idx}. {c.name} ({c.stat().st_size / 1024:.1f} KB)")
