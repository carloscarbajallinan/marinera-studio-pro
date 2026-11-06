import shutil
import os
from pathlib import Path

project_root = Path(r"C:\Users\LENOVO\Documents\Carlitos\IA\Antigravity\Profesionalización de catálogo\Cliente Marinera Power")
output_dir = project_root / "output"

fallidas_dir = output_dir / "fallidas"
fallidas_prompts = fallidas_dir / "pruebas_prompt_erroneo"
fallidas_pillow = fallidas_dir / "legacy_local_pillow"

fallidas_prompts.mkdir(parents=True, exist_ok=True)
fallidas_pillow.mkdir(parents=True, exist_ok=True)

# 1. Mover los 15 archivos ERROR_TEST
count_prompt_errors = 0
for f in list(output_dir.rglob("*")):
    if f.is_file() and "error_test" in f.name.lower():
        dest = fallidas_prompts / f.name
        # Si ya existe con el mismo nombre, agregar prefijo o sobrescribir
        if dest.exists():
            dest = fallidas_prompts / f"{f.parent.name}_{f.name}"
        shutil.move(str(f), str(dest))
        count_prompt_errors += 1
        print(f"[MOVIDO PROMPT] {f.name} -> fallidas/pruebas_prompt_erroneo/")

# 2. Mover los archivos de Pillow sueltos en la raíz de output/
count_pillow = 0
for f in list(output_dir.iterdir()):
    if f.is_file() and f.suffix.lower() in [".jpg", ".jpeg", ".png", ".webp"]:
        dest = fallidas_pillow / f.name
        shutil.move(str(f), str(dest))
        count_pillow += 1
        print(f"[MOVIDO PILLOW] {f.name} -> fallidas/legacy_local_pillow/")

print(f"\nTotal movidos a fallidas/pruebas_prompt_erroneo: {count_prompt_errors}")
print(f"Total movidos a fallidas/legacy_local_pillow: {count_pillow}")

# 3. Limpiar subcarpetas vacías en Para ella_Pro si quedaron vacías
for root, dirs, files in os.walk(output_dir / "Para ella_Pro", topdown=False):
    for d in dirs:
        dir_p = Path(root) / d
        try:
            if not any(dir_p.iterdir()):
                dir_p.rmdir()
                print(f"[CLEANUP] Carpeta vacía eliminada: {dir_p.name}")
        except Exception:
            pass
