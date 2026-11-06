import subprocess
import json

cmd = ['gsheets', 'readonly', 'read', '1kRsCZ7ZpPxyxrSEkUrYRl3NHahrQQche90RKK2yedQ8', 'Control_Total_Fotos!A1:D867', '--json']
res = subprocess.run(cmd, capture_output=True, text=True, shell=True)
try:
    data = json.loads(res.stdout)
except Exception as e:
    print("Error parsing json:", e)
    print("STDOUT:", res.stdout[:200])
    print("STDERR:", res.stderr)
    exit(1)

keywords = ["2.1 aretes", "2.1 MANTO", "2.2 MANTO", "2.1 Pardos", "Manto de Leche", "Aretes para"]
matches = []
for idx, row in enumerate(data, start=1):
    row_str = " | ".join(row)
    for kw in keywords:
        if kw.lower() in row_str.lower():
            matches.append((idx, kw, row_str))
            break

print("Found matches:", len(matches))
for m in matches[:15]:
    print(f"Row {m[0]}: {m[2]}")
