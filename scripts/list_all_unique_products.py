import subprocess, json, sys
sys.stdout.reconfigure(encoding='utf-8')

sheetId = '1kRsCZ7ZpPxyxrSEkUrYRl3NHahrQQche90RKK2yedQ8'
cmd = f'gsheets readonly read {sheetId} "Control_Total_Drive_V2!A1:E865" --json'
raw = subprocess.check_output(cmd, shell=True, text=True)
rows = json.loads(raw[raw.find('['):])[1:]

products = {}
for r in rows:
    folder = str(r[1]).strip()
    prod = str(r[2]).strip()
    if prod not in products:
        products[prod] = {'folder': folder, 'count': 0, 'sample_id': r[0]}
    products[prod]['count'] += 1

print(f"Total productos únicos: {len(products)}")
for p, d in sorted(products.items()):
    print(f"• '{p}' ({d['count']} fotos) | ID: {d['sample_id']} | Folder: {d['folder']}")
