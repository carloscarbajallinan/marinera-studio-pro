import os
from pathlib import Path
from datetime import datetime

root = Path(r"C:\Users\LENOVO\Documents\Carlitos\IA\Antigravity\Profesionalización de catálogo\Cliente Marinera Power")

today_files = []
for p in root.rglob("*"):
    if p.is_file():
        mtime = datetime.fromtimestamp(p.stat().st_mtime)
        if mtime.date() == datetime.now().date():
            today_files.append((mtime, p.relative_to(root)))

today_files.sort(key=lambda x: x[0])
print(f"Total de archivos creados o modificados hoy en el proyecto: {len(today_files)}")
for t, p in today_files:
    print(f"  [{t.strftime('%H:%M:%S')}] {p}")
