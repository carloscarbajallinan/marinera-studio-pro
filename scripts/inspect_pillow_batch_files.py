import os
from pathlib import Path
from datetime import datetime

output_dir = Path(r"C:\Users\LENOVO\Documents\Carlitos\IA\Antigravity\Profesionalización de catálogo\Cliente Marinera Power\output")

# Archivos directamente en la raíz de output/ (no en subcarpetas)
root_files = [f for f in output_dir.iterdir() if f.is_file()]

print(f"Total archivos en la raíz de output: {len(root_files)}")

# Inspeccionar timestamps y tipos
timestamps = set()
categories = {}
samples = []

for f in root_files:
    mtime = datetime.fromtimestamp(f.stat().st_mtime).strftime("%Y-%m-%d %H:%M")
    timestamps.add(mtime)
    
    # Categorizar por nombre
    name_lower = f.name.lower()
    cat = "Otros / Generales"
    if "aretes" in name_lower:
        cat = "Aretes de Filigrana"
    elif "escapulario" in name_lower:
        cat = "Escapularios"
    elif "manto" in name_lower:
        cat = "Mantos (Pava / Leche / Gasa)"
    elif "pardo" in name_lower:
        cat = "Pardos (Hilo / Lana)"
    elif "faja" in name_lower:
        cat = "Fajas de Hilo"
    elif "tocado" in name_lower or "peineta" in name_lower:
        cat = "Tocados & Peinetas"
    elif "collar" in name_lower:
        cat = "Collares & Juegos"
    elif "foto" in name_lower or "img" in name_lower or "whatsapp" in name_lower:
        cat = "Fotos Generales / Modelos"
        
    categories[cat] = categories.get(cat, 0) + 1

print("\nFechas de modificación encontradas:")
for t in sorted(timestamps):
    print(" ", t)

print("\nDistribución por tipo de producto:")
for cat, count in sorted(categories.items(), key=lambda x: -x[1]):
    print(f"  - {cat}: {count} archivos")

print("\nMuestra de archivos representativos:")
for f in sorted(root_files, key=lambda x: x.name)[:20]:
    sz_kb = f.stat().st_size / 1024
    print(f"  • {f.name} ({sz_kb:.1f} KB)")
