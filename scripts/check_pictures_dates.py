from pathlib import Path
from datetime import datetime

orig_dir = Path(r"C:\Users\LENOVO\Pictures\Marinera Power\fotos creadas")
files = list(orig_dir.iterdir())
times = [datetime.fromtimestamp(f.stat().st_mtime) for f in files]
max_time = max(times)
min_time = min(times)
print(f"Rango de fechas de tus fotos originales en Pictures: {min_time} hasta {max_time}")
today_files = [f for f in files if datetime.fromtimestamp(f.stat().st_mtime).date() == datetime.now().date()]
print(f"Total de archivos en Pictures modificados hoy: {len(today_files)}")
