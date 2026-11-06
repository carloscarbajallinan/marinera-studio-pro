import subprocess
import json
from pathlib import Path

root = Path(r"C:\Users\LENOVO\Documents\Carlitos\IA\Antigravity\Profesionalización de catálogo\Cliente Marinera Power")
cmd = ["gsheets", "readonly", "read", "1kRsCZ7ZpPxyxrSEkUrYRl3NHahrQQche90RKK2yedQ8", "Registro_Imagenes_Creadas!A1:O26", "--json"]
res = subprocess.run(cmd, capture_output=True, text=True, shell=True)
if res.returncode != 0:
    print("Error running gsheets:", res.stderr)
    exit(1)

data = json.loads(res.stdout)
headers = data[0]
rows = []
for r in data[1:]:
    item = {}
    for i, h in enumerate(headers):
        val = r[i] if i < len(r) else ""
        item[h.strip("﻿")] = val
    
    # Extraer ID original si viene en el link
    orig_link = item.get("Link_Drive_Original", "")
    orig_id = ""
    if "/d/" in orig_link:
        orig_id = orig_link.split("/d/")[1].split("/")[0]
    item["orig_id"] = orig_id
    item["pro_id"] = item.get("ID_Drive_PRO", "")
    
    rows.append(item)

out_file = root / "output" / "test_cases_data.json"
with open(out_file, "w", encoding="utf-8") as f:
    json.dump(rows, f, indent=2, ensure_ascii=False)

print(f"Exportados {len(rows)} casos reales a {out_file.name}")
