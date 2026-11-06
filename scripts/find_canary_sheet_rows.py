import subprocess, json, sys
sys.stdout.reconfigure(encoding='utf-8')

sheetId = '1kRsCZ7ZpPxyxrSEkUrYRl3NHahrQQche90RKK2yedQ8'
cmd = f'gsheets readonly read {sheetId} "Control_Total_Drive_V2!A1:Z800" --json'
raw = subprocess.check_output(cmd, shell=True, text=True)
rows = json.loads(raw[raw.find('['):])

canaries = [
    ('CANARY_1', 'foto (3)'),
    ('CANARY_2', '34a63e97'),
    ('CANARY_3', 'd72049af'),
    ('CANARY_4', 'aretes'),
    ('CANARY_5', '1841c6d0')
]

print(f"Total rows in sheet: {len(rows)}")
for r_idx, r in enumerate(rows, start=1):
    r_id = r[0] if len(r) > 0 else ''
    r_folder = r[1] if len(r) > 1 else ''
    r_name = r[4] if len(r) > 4 else ''
    
    for c_id, c_pattern in canaries:
        if c_id == 'CANARY_4':
            if 'aretes' in r_folder.lower() and (r_name == '1' or r_name.startswith('1.')):
                print(f"Row {r_idx}: {c_id} -> ID={r_id} | Name={r_name} | Folder={r_folder}")
        else:
            if c_pattern in r_name:
                print(f"Row {r_idx}: {c_id} -> ID={r_id} | Name={r_name} | Folder={r_folder}")
