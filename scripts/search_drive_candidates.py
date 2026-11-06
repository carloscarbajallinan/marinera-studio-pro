import subprocess
import json

files = [
    ("1.1 Accesorios  Escapulario para Mujer de Marinera.jpg", "Escapulario"),
    ("1.1 aretes para marinera.jpg", "aretes"),
    ("2 Manto de Pava bordado.jpg", "Manto de Pava"),
    ("2.2 Pardos de hilo.jpg", "Pardos"),
    ("3.1 Faja de Hilo para Marinera.jpg", "Faja")
]

for filename, query in files:
    cmd = ['gdrive', 'readonly', 'search', '--name-contains', query, '--json']
    res = subprocess.run(cmd, capture_output=True, text=True, shell=True)
    try:
        data = json.loads(res.stdout)
        print(f"\nResultados para query='{query}' (Archivo: {filename}): {len(data)}")
        for d in data[:5]:
            print(f"  ID: {d.get('id')} | Name: {d.get('name')} | Parents: {d.get('parents')}")
    except Exception as e:
        print(f"Error for {query}: {e}")
        print("stdout:", res.stdout[:100])
