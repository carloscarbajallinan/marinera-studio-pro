import shutil
import os
import json
from pathlib import Path

root = Path(r"C:\Users\LENOVO\Documents\Carlitos\IA\Antigravity\Profesionalización de catálogo\Cliente Marinera Power")
output_dir = root / "output"
cache_orig = output_dir / "preview_cache" / "orig"
cache_pro = output_dir / "preview_cache" / "pro"
cache_orig.mkdir(parents=True, exist_ok=True)
cache_pro.mkdir(parents=True, exist_ok=True)

cases_file = output_dir / "test_cases_data.json"
cases = json.load(open(cases_file, encoding="utf-8"))

copied_orig = 0
copied_pro = 0

for c in cases:
    orig_name = c["Nombre_Archivo_Original"]
    pro_name = c["Nombre_Archivo_PRO"]
    
    # Origen
    src_orig = Path(r"C:\Users\LENOVO\Pictures\Marinera Power\fotos creadas") / orig_name
    if src_orig.exists():
        shutil.copy2(src_orig, cache_orig / orig_name)
        c["local_orig_rel"] = f"preview_cache/orig/{orig_name}"
        copied_orig += 1
    else:
        c["local_orig_rel"] = ""
        
    # PRO
    src_pro_v2 = output_dir / "Lote_Prueba_Diario" / pro_name
    src_pro_err = output_dir / "fallidas" / "pruebas_prompt_erroneo" / pro_name
    if src_pro_v2.exists():
        shutil.copy2(src_pro_v2, cache_pro / pro_name)
        c["local_pro_rel"] = f"preview_cache/pro/{pro_name}"
        copied_pro += 1
    elif src_pro_err.exists():
        shutil.copy2(src_pro_err, cache_pro / pro_name)
        c["local_pro_rel"] = f"preview_cache/pro/{pro_name}"
        copied_pro += 1
    else:
        c["local_pro_rel"] = ""

with open(cases_file, "w", encoding="utf-8") as f:
    json.dump(cases, f, indent=2, ensure_ascii=False)

print(f"Copiados en preview_cache: {copied_orig} originales y {copied_pro} PRO.")
