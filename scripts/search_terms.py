import subprocess
import json

cmd = ['gsheets', 'readonly', 'read', '1kRsCZ7ZpPxyxrSEkUrYRl3NHahrQQche90RKK2yedQ8', 'Control_Total_Fotos!A1:J867', '--json']
res = subprocess.run(cmd, capture_output=True, text=True, shell=True)
data = json.loads(res.stdout)
rows = data[1:]

terms = ["aretes", "manto", "pardo", "leche"]

for idx, r in enumerate(rows, start=2):
    row_text = " ".join([str(x) for x in r]).lower()
    for t in terms:
        if t in row_text:
            print(f"Fila {idx}: ID={r[0]} | Cat={r[1]} | Nom={r[2]} | ID_Drive={r[3] if len(r)>3 else ''} | Estado={r[5] if len(r)>5 else ''}")
            break
