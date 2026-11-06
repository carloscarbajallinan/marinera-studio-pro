import subprocess
import json

SPREADSHEET_ID = "1kRsCZ7ZpPxyxrSEkUrYRl3NHahrQQche90RKK2yedQ8"

# 1. Aretes para Marinera 2 -> Fila 833
# 2. Pardos de Hilo 1 -> Fila 816
# 3. Manto de Leche 2 -> Fila 846
# 4. Manto de Leche 1 -> Fila 847

extra_links = [
    {
        "row": 833,
        "name_pro": "2_1_aretes_marinera_PRO_v2.jpg",
        "id_pro": "1prc92aNl0PEh0PZcoMtZwIp-oZWI2Qtu",
        "link_pro": "https://drive.google.com/file/d/1prc92aNl0PEh0PZcoMtZwIp-oZWI2Qtu/view"
    },
    {
        "row": 816,
        "name_pro": "2_1_Pardos_de_hilo_PRO_v2.jpg",
        "id_pro": "1UBSXB17tRakEPEO3obG3-IJ_uSTY-XHn",
        "link_pro": "https://drive.google.com/file/d/1UBSXB17tRakEPEO3obG3-IJ_uSTY-XHn/view"
    },
    {
        "row": 846,
        "name_pro": "2_2_MANTO_DE_LECHE_PRO_v2.jpg",
        "id_pro": "1vNkqHdCmydyQkr8TS7XGP7EE3PSlvbDx",
        "link_pro": "https://drive.google.com/file/d/1vNkqHdCmydyQkr8TS7XGP7EE3PSlvbDx/view"
    },
    {
        "row": 847,
        "name_pro": "2_1_MANTO_DE_LECHE_PRO_v2.jpg",
        "id_pro": "1mSa6YNMWkPp5qEZg3fxF84tDScZ7HOGu",
        "link_pro": "https://drive.google.com/file/d/1mSa6YNMWkPp5qEZg3fxF84tDScZ7HOGu/view"
    }
]

ops = []
for item in extra_links:
    r = item["row"]
    ops.append({
        "op": "write",
        "range": f"Control_Total_Fotos!F{r}:I{r}",
        "data": [["COMPLETADO", item["name_pro"], item["id_pro"], item["link_pro"]]]
    })
    ops.append({
        "op": "write",
        "range": f"Control_Total_Fotos!L{r}",
        "data": [[f'=IMAGE("https://lh3.googleusercontent.com/d/{item["id_pro"]}")']]
    })

with open("scripts/batch_extra_sync.json", "w", encoding="utf-8") as f:
    json.dump(ops, f, ensure_ascii=False)

cmd = ["gsheets", "mutate", "batch", SPREADSHEET_ID, "-f", "scripts/batch_extra_sync.json"]
res = subprocess.run(cmd, capture_output=True, text=True, shell=True)
print("Respuesta extra sync:", res.stdout)
