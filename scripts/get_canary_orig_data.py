import json, sys
sys.stdout.reconfigure(encoding='utf-8')
from pathlib import Path

root = Path(r"C:\Users\LENOVO\Documents\Carlitos\IA\Antigravity\Profesionalización de catálogo\Cliente Marinera Power")
with open(root / 'scripts' / 'drive_origin_tree.json', 'r', encoding='utf-8') as f:
    orig_tree = json.load(f)

canaries = [
    ('CANARY_1', 'foto (3)'),
    ('CANARY_2', '34a63e97'),
    ('CANARY_3', 'd72049af'),
    ('CANARY_4', '1'),
    ('CANARY_5', '1841c6d0')
]

for tag, prefix in canaries:
    matches = [f for f in orig_tree['files'] if f['name'].startswith(prefix)]
    print(f"=== {tag} ({prefix}) ===")
    for m in matches[:2]:
        print(f"  Name: {m['name']}")
        print(f"  ID: {m['id']}")
        print(f"  Folder: {m['folder_path']}")
