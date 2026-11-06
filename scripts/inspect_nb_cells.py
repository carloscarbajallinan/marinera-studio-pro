import json
import sys
sys.stdout.reconfigure(encoding='utf-8')

nb_path = r'C:\Users\LENOVO\Documents\Carlitos\IA\Antigravity\Profesionalización de catálogo\Cliente Marinera Power\notebooks\Pipeline_Masivo_Marinera_Power.ipynb'
with open(nb_path, 'r', encoding='utf-8') as f:
    nb = json.load(f)

print(f'Total cells: {len(nb["cells"])}')
for i, c in enumerate(nb['cells']):
    first_line = c['source'][0].strip() if c['source'] else 'EMPTY'
    print(f'Cell {i} ({c["cell_type"]}): {first_line[:80]}')
