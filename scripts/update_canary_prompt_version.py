import subprocess, sys
sys.stdout.reconfigure(encoding='utf-8')

sheetId = '1kRsCZ7ZpPxyxrSEkUrYRl3NHahrQQche90RKK2yedQ8'
rows = [424, 422, 419, 29, 425]
for r in rows:
    cmd = f'gsheets.cmd mutate write {sheetId} "Control_Total_Drive_V2!AA{r}" "PROMPT_MAESTRO_V3_INDUSTRIAL"'
    subprocess.run(cmd, shell=True, check=True)
print("✅ Version_Prompt updated for all 5 Canary rows in Sheets.")
