import json, sys
sys.stdout.reconfigure(encoding='utf-8')
from pathlib import Path

root = Path(r"C:\Users\LENOVO\Documents\Carlitos\IA\Antigravity\Profesionalización de catálogo\Cliente Marinera Power")
with open(root / "notebooks" / "Pipeline_Masivo_Marinera_Power.ipynb", 'r', encoding='utf-8') as f:
    nb = json.load(f)

for i, c in enumerate(nb['cells']):
    src = "".join(c.get('source', []))
    lines = [l.strip() for l in src.split('\n') if l.strip()]
    first = lines[0] if lines else "EMPTY"
    print(f"Cell {i} ({c.get('cell_type')}): {first[:80]}")
