import os
from pathlib import Path

orig_dir = Path(r"C:\Users\LENOVO\Pictures\Marinera Power\fotos creadas")
files = list(orig_dir.iterdir())
print(f"Total archivos originales en Pictures/Marinera Power/fotos creadas: {len(files)}")

# Verificar que ninguno fue modificado hoy después de las 11:00 (o ver sus timestamps)
recent_mods = []
for f in files:
    mtime = f.stat().st_mtime
    # Chequear si alguno tiene sufijo PRO
    if "pro" in f.name.lower():
        recent_mods.append(f.name)

print(f"Archivos originales con 'pro' en el nombre: {len(recent_mods)} (deben ser solo los que ya existían originalmente)")
for r in recent_mods:
    print(" ", r)
