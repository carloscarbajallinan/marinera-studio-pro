import subprocess
import json

cmd = ['gsheets', 'readonly', 'read', '1kRsCZ7ZpPxyxrSEkUrYRl3NHahrQQche90RKK2yedQ8', 'Control_Total_Fotos!A1:J867', '--json']
res = subprocess.run(cmd, capture_output=True, text=True, shell=True)
data = json.loads(res.stdout)
headers = data[0]
rows = data[1:]

stats = {}
for r in rows:
    status = r[5] if len(r) > 5 and r[5] else 'VACIO'
    stats[status] = stats.get(status, 0) + 1

print('Estados en Control_Total_Fotos:', stats)

completed = [r for r in rows if len(r) > 5 and r[5] == 'COMPLETADO']
print(f'Total COMPLETADOS: {len(completed)}')
for c in completed:
    print(' ', c[0], c[1], c[2], c[6] if len(c)>6 else '', c[7] if len(c)>7 else '')
