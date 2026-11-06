import json, sys
sys.stdout.reconfigure(encoding='utf-8')
with open(r'C:\Users\LENOVO\AppData\Local\Temp\colab_inspect.ipynb', 'r', encoding='utf-8') as f:
    nb = json.load(f)

print('=== CELL 2 ===')
print(''.join(nb['cells'][2]['source']))
print('\n=== CELL 5 ===')
print(''.join(nb['cells'][5]['source']))
print('\n=== CELL 6 ===')
print(''.join(nb['cells'][6]['source']))
