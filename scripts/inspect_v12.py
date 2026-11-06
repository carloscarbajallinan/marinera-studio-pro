import json, sys
sys.stdout.reconfigure(encoding='utf-8')

with open(r'C:\Users\LENOVO\AppData\Local\Temp\colab_current_v12.ipynb', 'r', encoding='utf-8') as f:
    nb = json.load(f)

print(f"Total cells: {len(nb['cells'])}")
for i, c in enumerate(nb['cells']):
    first = c['source'][0].strip() if c['source'] else 'EMPTY'
    print(f"Cell {i} [{c['cell_type']}]: {first[:80]}")
