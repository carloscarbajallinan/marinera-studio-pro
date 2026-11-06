import json, sys
sys.stdout.reconfigure(encoding='utf-8')
from pathlib import Path

root = Path(r"C:\Users\LENOVO\Documents\Carlitos\IA\Antigravity\Profesionalización de catálogo\Cliente Marinera Power")
with open(root / "notebooks" / "Pipeline_Masivo_Marinera_Power.ipynb", 'r', encoding='utf-8') as f:
    nb = json.load(f)

for idx in [2, 4, 5, 6, 7]:
    src = "".join(nb['cells'][idx].get('source', []))
    print(f"=== CELL {idx} (Length: {len(src)} chars) ===")
    print(src[:600])
    print("...\n")
