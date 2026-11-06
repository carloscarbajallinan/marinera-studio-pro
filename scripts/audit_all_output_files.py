import os
from pathlib import Path

output_root = Path(r"C:\Users\LENOVO\Documents\Carlitos\IA\Antigravity\Profesionalización de catálogo\Cliente Marinera Power\output")

all_files = list(output_root.rglob("*"))
file_list = [f for f in all_files if f.is_file()]

print(f"Total archivos en output: {len(file_list)}")

# 1. Archivos con ERROR_TEST en el nombre
error_test_files = [f for f in file_list if "error_test" in f.name.lower() or "error" in f.name.lower()]
print(f"\nArchivos con 'ERROR_TEST' en el nombre ({len(error_test_files)}):")
for f in error_test_files:
    print(f"  - {f.relative_to(output_root)}")

# 2. Archivos en output/Lote_Prueba_Diario
lote_prueba = output_root / "Lote_Prueba_Diario"
if lote_prueba.exists():
    lp_files = list(lote_prueba.glob("*"))
    print(f"\nArchivos en Lote_Prueba_Diario ({len(lp_files)}):")
    for f in lp_files:
        print(f"  - {f.name}")

# 3. Otros archivos en output/ que terminen en _PRO_1x1.jpg o similares del batch local antiguo
other_batch_files = [f for f in file_list if ("_pro_1x1" in f.name.lower() or "_pro_4x5" in f.name.lower()) and f not in error_test_files]
print(f"\nOtros archivos generados por filtros locales/Pillow (_PRO_1x1) ({len(other_batch_files)}):")
for f in other_batch_files[:15]:
    print(f"  - {f.relative_to(output_root)}")
if len(other_batch_files) > 15:
    print(f"  ... y {len(other_batch_files) - 15} más")
