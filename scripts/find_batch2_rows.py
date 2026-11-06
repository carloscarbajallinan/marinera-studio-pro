import subprocess
import json

SPREADSHEET_ID = "1kRsCZ7ZpPxyxrSEkUrYRl3NHahrQQche90RKK2yedQ8"
cmd = ["gsheets", "readonly", "read", SPREADSHEET_ID, "Control_Total_Fotos!A1:D867", "--json"]
res = subprocess.run(cmd, capture_output=True, text=True, shell=True)
data = json.loads(res.stdout)

target_ids = {
    "1cbu4sRw6NQZ2ZDLX6uPkAvGBYIjrbGfZ": "1.1 Accesorios  Escapulario para Mujer de Marinera.jpg",
    "1mTcBmDz-V07AevtAPxwaqx_yCS6NH8vb": "1.1 aretes para marinera.jpg",
    "1HHi34ac4a3aEaMhgbu1VNvyRHsOA6_ad": "2 Manto de Pava bordado.jpg",
    "1cP5JHPFpqn0_bGv8VgGyC9f1czHd5CKD": "2.2 Pardos de hilo.jpg",
    "1i_rR0DB1uERorgoX5l536RnxpkYN6lEO": "3.1 Faja de Hilo para Marinera.jpg"
}

print("Buscando por ID original:")
for idx, r in enumerate(data[1:], start=2):
    orig_id = r[3].strip() if len(r) > 3 and r[3] else ""
    if orig_id in target_ids:
        print(f"Fila {idx}: ID={r[0]} | Cat={r[1]} | Nom={r[2]} | OrigID={orig_id}")

print("\nBuscando por coincidencias en nombre/categoría:")
for idx, r in enumerate(data[1:], start=2):
    r_text = " ".join([str(x) for x in r]).lower()
    for tid, name in target_ids.items():
        if "escapulario" in name.lower() and "escapulario" in r_text and ("1" in r[2] or "mujer" in r_text):
            print(f"Match Escapulario: Fila {idx}: ID={r[0]} | Nom={r[2]} | ID_Drive={r[3] if len(r)>3 else ''}")
            break
