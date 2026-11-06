import re
from pathlib import Path

# Mapeo de subcarpetas según docs/Mapeo_Maestro_Fotos_Originales_vs_Pro.md:
# Aretes para Marinera -> 1iHk0M9Nd3TxLBZFeEy10QaQfe1JjpDyk
# Escapulario para Mujer -> 1pAzP0RyT7CE9YxUHDzkA-Xb3Fag8YkAw
# Manto de Pava bordado -> 1g7XL098W2eU5eqhYemjpzJTAtQPwMqdx
# Pardos de Hilo -> 12fkES5ridQx74_jMCWO2CLVXrKKSM2h7
# Faja de Hilo para Marinera -> 1rLHpaWFN6Qf4XeTC77WMb7-rp0vWctlg
# Manto de Leche -> 1_urwXULEjVdVz40EtayD4tjBB63L-2e9
# Tocado Látex con Pedrería -> 1KIU09gVPWfEzPV_swmmMxM5yWyP2ZXZr
# Tocado con Peineta -> 1YFFOo4MtH4OdQub8BGdR_1o_x1dji4sV
# Juego de Collar y Aretes -> 10Ack0iTL6KisVXPbIKEMEgf8xdF89dHu

FOLDER_MAP = {
    "escapulario": {
        "cat": "Para ella / Accesorios / Escapulario para Mujer de Marinera",
        "drive_folder_id": "1pAzP0RyT7CE9YxUHDzkA-Xb3Fag8YkAw"
    },
    "aretes": {
        "cat": "Para ella / Accesorios / Aretes para Marinera",
        "drive_folder_id": "1iHk0M9Nd3TxLBZFeEy10QaQfe1JjpDyk"
    },
    "manto de pava": {
        "cat": "Para ella / Accesorios / Mantos / Manto de Pava bordado",
        "drive_folder_id": "1g7XL098W2eU5eqhYemjpzJTAtQPwMqdx"
    },
    "manto de leche": {
        "cat": "Para ella / Accesorios / Mantos / Manto de Leche",
        "drive_folder_id": "1_urwXULEjVdVz40EtayD4tjBB63L-2e9"
    },
    "pardos de hilo": {
        "cat": "Para ella / Accesorios / Pardos de Marinera / Pardos de Hilo",
        "drive_folder_id": "12fkES5ridQx74_jMCWO2CLVXrKKSM2h7"
    },
    "faja de hilo": {
        "cat": "Para ella / Accesorios / Faja de Hilo para Marinera",
        "drive_folder_id": "1rLHpaWFN6Qf4XeTC77WMb7-rp0vWctlg"
    },
    "tocado": {
        "cat": "Para ella / Accesorios / Tocados para Marinera / Tocado Látex con Pedrería",
        "drive_folder_id": "1KIU09gVPWfEzPV_swmmMxM5yWyP2ZXZr"
    },
    "collar": {
        "cat": "Para ella / Accesorios / Juego de Collar y Aretes para Marinera",
        "drive_folder_id": "10Ack0iTL6KisVXPbIKEMEgf8xdF89dHu"
    }
}

candidates = [
    "1.1 Accesorios  Escapulario para Mujer de Marinera.jpg",
    "1.1 aretes para marinera.jpg",
    "2 Manto de Pava bordado.jpg",
    "2.2 Pardos de hilo.jpg",
    "3.1 Faja de Hilo para Marinera.jpg"
]

src_dir = Path(r"C:\Users\LENOVO\Pictures\Marinera Power\fotos creadas")

print("Validación de lote de 5 imágenes:")
for f in candidates:
    p = src_dir / f
    print(f"- {f} | Existe: {p.exists()} | Tamaño: {p.stat().st_size/1024:.1f} KB")
    matched_cat = None
    matched_drive = None
    for k, v in FOLDER_MAP.items():
        if k in f.lower():
            matched_cat = v["cat"]
            matched_drive = v["drive_folder_id"]
            break
    print(f"  -> Categoría: {matched_cat} | Drive Folder ID: {matched_drive}")
