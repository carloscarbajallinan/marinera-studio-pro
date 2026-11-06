import json, sys
sys.stdout.reconfigure(encoding='utf-8')
from pathlib import Path

root = Path(r"C:\Users\LENOVO\Documents\Carlitos\IA\Antigravity\Profesionalización de catálogo\Cliente Marinera Power")
with open(root / "notebooks" / "Pipeline_Masivo_Marinera_Power.ipynb", 'r', encoding='utf-8') as f:
    nb = json.load(f)

src5 = ''.join(nb['cells'][5]['source'])
print("=== CELL 5 ===")
print(src5)

src6 = ''.join(nb['cells'][6]['source'])
print("=== CELL 6 ===")
print(src6[:2000])
