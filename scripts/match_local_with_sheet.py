import subprocess
import json
from pathlib import Path

local_dir = Path(r"C:\Users\LENOVO\Pictures\Marinera Power\fotos creadas")
local_files = [f.name for f in local_dir.iterdir() if f.is_file()]

cmd = ['gsheets', 'readonly', 'read', '1kRsCZ7ZpPxyxrSEkUrYRl3NHahrQQche90RKK2yedQ8', 'Control_Total_Fotos!A1:J867', '--json']
res = subprocess.run(cmd, capture_output=True, text=True, shell=True)
data = json.loads(res.stdout)
rows = data[1:]

print(f"Total fotos locales en 'fotos creadas': {len(local_files)}")
print(f"Muestra fotos locales (primeras 15):")
for f in local_files[:15]:
    print(" ", f)

# Ver cómo se llaman los archivos en Control_Total_Fotos
print("\nMuestra nombres de archivo en Control_Total_Fotos (Col C):")
for r in rows[:15]:
    print(" ", r[0], "|", r[1], "|", r[2])

print("\nBuscando si los nombres de 'fotos creadas' coinciden con Col C o Col B:")
matched = []
for f in local_files:
    for r in rows:
        # Check if f matches Col C or parts of Col B
        if f.lower() == r[2].lower() or f.lower().startswith(r[2].lower() + " ") or r[2].lower() in f.lower():
            matched.append((f, r[0], r[1], r[2], r[3], r[5]))
            break

print(f"Total coincidencias preliminares: {len(matched)}")
for m in matched[:20]:
    print(" ", m)
