import subprocess
import json
from pathlib import Path

root = Path(r"C:\Users\LENOVO\Documents\Carlitos\IA\Antigravity\Profesionalización de catálogo\Cliente Marinera Power")

# 1. Leer Control_Total_Fotos completo
cmd = ["gsheets", "readonly", "read", "1kRsCZ7ZpPxyxrSEkUrYRl3NHahrQQche90RKK2yedQ8", "Control_Total_Fotos!A1:M870", "--json"]
res = subprocess.run(cmd, capture_output=True, text=True, shell=True)
if res.returncode == 0:
    data = json.loads(res.stdout)
    headers = data[0]
    catalog_rows = []
    for r in data[1:]:
        item = {}
        for i, h in enumerate(headers):
            val = r[i] if i < len(r) else ""
            item[h] = val
        catalog_rows.append(item)
    
    # 2. Guardar métricas y completados
    completed = [r for r in catalog_rows if r.get("Estado") == "COMPLETADO"]
    pending = [r for r in catalog_rows if r.get("Estado") != "COMPLETADO"]
    
    showcase_path = root / "output" / "full_catalog_showcase.json"
    with open(showcase_path, "w", encoding="utf-8") as f:
        json.dump(completed, f, indent=2, ensure_ascii=False)
        
    metrics_path = root / "output" / "metrics_summary.json"
    metrics = {
        "total": len(catalog_rows),
        "completed_pro": len(completed),
        "pending_virgin": len(pending),
        "completion_pct": round(len(completed) / len(catalog_rows) * 100, 1) if catalog_rows else 0
    }
    with open(metrics_path, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2)
        
    print(f"Exportados {len(completed)} productos PRO completados a {showcase_path.name}")
    print(f"Métricas generales: {metrics}")
else:
    print("Error leyendo Control_Total_Fotos:", res.stderr)
