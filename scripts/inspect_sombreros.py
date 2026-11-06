import subprocess, json, sys
sys.stdout.reconfigure(encoding='utf-8')

sheetId = '1kRsCZ7ZpPxyxrSEkUrYRl3NHahrQQche90RKK2yedQ8'
cmd = f'gsheets readonly read {sheetId} "Control_Total_Drive_V2!A1:H865" --json'
raw = subprocess.check_output(cmd, shell=True, text=True)
rows = json.loads(raw[raw.find('['):])[1:]

for r in rows:
    folder = str(r[1]).strip()
    if 'sombrero' in folder.lower():
        product = str(r[2]).strip()
        filename = str(r[4]).strip()
        r_id = str(r[0]).strip()
        print(f"ID {r_id} | Product: '{product}' | File: '{filename}' | Folder: '{folder}'")
