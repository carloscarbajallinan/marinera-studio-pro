import json, sys
sys.stdout.reconfigure(encoding='utf-8')

with open(r'C:\Users\LENOVO\AppData\Local\Temp\colab_carlos_updated.ipynb', 'r', encoding='utf-8') as f:
    nb = json.load(f)

print("=== CELL 7 FULL CODE ===")
print("".join(nb['cells'][7]['source']))
