import subprocess, json, sys
sys.stdout.reconfigure(encoding='utf-8')

sheetId = '1kRsCZ7ZpPxyxrSEkUrYRl3NHahrQQche90RKK2yedQ8'
cmd = f'gsheets readonly read {sheetId} "Control_Total_Drive_V2!A1:G5" --json'
raw = subprocess.check_output(cmd, shell=True, text=True)
rows = json.loads(raw[raw.find('['):])
for r in rows:
    print(r)
