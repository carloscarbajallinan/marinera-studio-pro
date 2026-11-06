import json, sys
sys.stdout.reconfigure(encoding='utf-8')

with open(r'C:\Users\LENOVO\AppData\Local\Temp\colab_latest_run.ipynb', 'r', encoding='utf-8') as f:
    nb = json.load(f)

print(f"Total cells: {len(nb['cells'])}")
for i, cell in enumerate(nb['cells']):
    title = cell['source'][0].strip() if cell['source'] else 'EMPTY'
    print(f"\n--- Cell {i} [{cell['cell_type']}] ---")
    print(f"Source preview: {title[:80]}")
    outputs = cell.get('outputs', [])
    print(f"Outputs count: {len(outputs)}")
    for out in outputs:
        if 'text' in out:
            print("TEXT OUTPUT:")
            print("".join(out['text'])[:500])
        elif 'data' in out:
            print("DATA OUTPUT: image or HTML displayed")
