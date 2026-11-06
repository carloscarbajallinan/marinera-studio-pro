import subprocess
import json

cmd = ['gsheets', 'readonly', 'read', '1kRsCZ7ZpPxyxrSEkUrYRl3NHahrQQche90RKK2yedQ8', 'Control_Total_Fotos!A1:J867', '--json']
res = subprocess.run(cmd, capture_output=True, text=True, shell=True)
data = json.loads(res.stdout)
rows = data[1:]

target_ids = {
    '1T0z_DfDEmrr6H9wbiNGfg5RmBg8MneYX': '2.1 aretes marinera',
    '1mtiG5AJj24HzoSuvu_amXKo-Por54CLq': '2.1 aretes para marinera',
    '1MQdfxQoWrRHOsGsAFd6_jziGKoqmyw24': '2.1 MANTO DE LECHE',
    '1Hf2Y6MLDWayEHFl46aRAZm52z0NOb8PP': '2.2 MANTO DE LECHE',
    '1t2jde5a9D55KbOwpqelT-MX-Z8LK4Jvv': '2.1 Pardos de hilo'
}

found = 0
for idx, r in enumerate(rows, start=2):
    orig_id = r[3].strip() if len(r)>3 else ''
    if orig_id in target_ids:
        found += 1
        print(f"Fila {idx}: ID={r[0]} | Cat={r[1]} | Nom={r[2]} | ID_Drive={orig_id} | Estado={r[5]} | ProID={r[7] if len(r)>7 else ''}")

print(f"Total encontrados: {found} de {len(target_ids)}")
