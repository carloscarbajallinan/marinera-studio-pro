import json, sys
sys.stdout.reconfigure(encoding='utf-8')
from pathlib import Path

root = Path(r"C:\Users\LENOVO\Documents\Carlitos\IA\Antigravity\Profesionalización de catálogo\Cliente Marinera Power")
with open(root / 'scripts' / 'drive_origin_tree.json', 'r', encoding='utf-8') as f:
    orig = json.load(f)

print(f"Total orig files: {len(orig['files'])}")
for f in orig['files']:
    if 'aretes' in f['folder_path'].lower():
        print(f"Aretes: {f['name']} | ID: {f['id']} | Folder: {f['folder_path']}")
