import json
import sys
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

creds_file = r'C:\Users\LENOVO\Documents\Carlitos\IA\Antigravity\Profesionalización de catálogo\Cliente Marinera Power\config\token.json'
with open(creds_file, 'r', encoding='utf-8') as f:
    data = json.load(f)

creds = Credentials.from_authorized_user_info(data)
if not creds.valid:
    creds.refresh(Request())
    with open(creds_file, 'w', encoding='utf-8') as f:
        f.write(creds.to_json())

service = build('sheets', 'v4', credentials=creds)

res = service.spreadsheets().get(
    spreadsheetId='1kRsCZ7ZpPxyxrSEkUrYRl3NHahrQQche90RKK2yedQ8',
    ranges=['Registro_Imagenes_Creadas!N17:O17'],
    fields='sheets(data(rowData(values(userEnteredValue,effectiveValue,formattedValue))))'
).execute()

print(json.dumps(res, indent=2))
