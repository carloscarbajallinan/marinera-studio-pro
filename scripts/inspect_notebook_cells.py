import json
import sys
sys.stdout.reconfigure(encoding='utf-8')

with open(r'C:\Users\LENOVO\AppData\Local\Temp\colab_inspect.ipynb', 'r', encoding='utf-8') as f:
    nb = json.load(f)

print(f"Total cells: {len(nb['cells'])}")
for i, cell in enumerate(nb['cells']):
    first_line = cell['source'][0] if cell['source'] else 'EMPTY'
    print(f"Cell {i} [{cell['cell_type']}]: {first_line.strip()[:80]}")
    if 'outputs' in cell and cell['outputs']:
        for out in cell['outputs']:
            if 'text' in out:
                txt = "".join(out['text'])
                print(f"   OUTPUT: {txt[:100]}...")
