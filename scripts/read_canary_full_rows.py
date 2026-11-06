import subprocess, sys
sys.stdout.reconfigure(encoding='utf-8')

sheetId = '1kRsCZ7ZpPxyxrSEkUrYRl3NHahrQQche90RKK2yedQ8'
rows = [424, 422, 419, 29, 425]

for r in rows:
    res = subprocess.run(f'gsheets.cmd readonly read {sheetId} "Control_Total_Drive_V2!A{r}:AA{r}"', shell=True, capture_output=True, text=True)
    print(f"=== ROW {r} ===")
    print(res.stdout.strip())
