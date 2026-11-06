import json, sys
sys.stdout.reconfigure(encoding='utf-8')

with open(r'C:\Users\LENOVO\AppData\Local\Temp\colab_carlos_updated.ipynb', 'r', encoding='utf-8') as f:
    nb = json.load(f)

print(f"Total cells: {len(nb['cells'])}")
for i, cell in enumerate(nb['cells']):
    first_lines = "".join(cell['source'][:3]).strip()
    print(f"\n==================== CELL {i} [{cell['cell_type']}] ====================")
    print(f"Preview: {first_lines[:120]}")

print("\n\n>>> DETAILED CONTENT OF CELL 4 & 5 & 6:")
for idx in [4, 5]:
    if idx < len(nb['cells']):
        print(f"\n--- CELL {idx} ---")
        print("".join(nb['cells'][idx]['source']))
