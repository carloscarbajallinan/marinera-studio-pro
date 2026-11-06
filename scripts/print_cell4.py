import json, sys
sys.stdout.reconfigure(encoding='utf-8')
from pathlib import Path

root = Path(r"C:\Users\LENOVO\Documents\Carlitos\IA\Antigravity\Profesionalización de catálogo\Cliente Marinera Power")
with open(root / "notebooks" / "Pipeline_Masivo_Marinera_Power.ipynb", 'r', encoding='utf-8') as f:
    nb = json.load(f)

src = ''.join(nb['cells'][4]['source'])
print(src[:3500])
