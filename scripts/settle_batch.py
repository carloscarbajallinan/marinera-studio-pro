"""
Script de asentamiento y subida para el Lote 2 de Marinera Power.
Cumple con las Fases 2, 3 y 4 del Definition of Done (DoD).
"""

import os
import subprocess
import json
import re
from datetime import datetime

SPREADSHEET_ID = "1kRsCZ7ZpPxyxrSEkUrYRl3NHahrQQche90RKK2yedQ8"

BATCH_ITEMS = [
    {
        "id_reg": 21,
        "row_reg": 22,
        "cat": "Para ella / Accesorios / Escapulario para Mujer de Marinera",
        "orig_name": "1.1 Accesorios  Escapulario para Mujer de Marinera.jpg",
        "orig_id": "1cbu4sRw6NQZ2ZDLX6uPkAvGBYIjrbGfZ",
        "orig_link": "https://drive.google.com/file/d/1cbu4sRw6NQZ2ZDLX6uPkAvGBYIjrbGfZ/view",
        "pro_name": "1_1_Escapulario_Mujer_PRO_v2.jpg",
        "local_path": r"output\Lote_Prueba_Diario\1_1_Escapulario_Mujer_PRO_v2.jpg",
        "drive_folder_id": "1pAzP0RyT7CE9YxUHDzkA-Xb3Fag8YkAw",
        "obs": "Sujeto intacto fondo gris calido minimalista sombras de contacto",
        "control_row": 832,
        "pro_id": "1vxpf0zACFb3Y4puEk7qHJ_FpyqjZa0xi", # Ya subido exitosamente
        "pro_link": "https://drive.google.com/file/d/1vxpf0zACFb3Y4puEk7qHJ_FpyqjZa0xi/view"
    },
    {
        "id_reg": 22,
        "row_reg": 23,
        "cat": "Para ella / Accesorios / Aretes para Marinera",
        "orig_name": "1.1 aretes para marinera.jpg",
        "orig_id": "1mTcBmDz-V07AevtAPxwaqx_yCS6NH8vb",
        "orig_link": "https://drive.google.com/file/d/1mTcBmDz-V07AevtAPxwaqx_yCS6NH8vb/view",
        "pro_name": "1_1_aretes_para_marinera_PRO_v2.jpg",
        "local_path": r"output\Lote_Prueba_Diario\1_1_aretes_para_marinera_PRO_v2.jpg",
        "drive_folder_id": "1iHk0M9Nd3TxLBZFeEy10QaQfe1JjpDyk",
        "obs": "Sujeto intacto orfebreria preservada fondo #E5E1DE",
        "control_row": 834
    },
    {
        "id_reg": 23,
        "row_reg": 24,
        "cat": "Para ella / Accesorios / Mantos / Manto de Pava bordado",
        "orig_name": "2 Manto de Pava bordado.jpg",
        "orig_id": "1HHi34ac4a3aEaMhgbu1VNvyRHsOA6_ad",
        "orig_link": "https://drive.google.com/file/d/1HHi34ac4a3aEaMhgbu1VNvyRHsOA6_ad/view",
        "pro_name": "2_Manto_Pava_Bordado_PRO_v2.jpg",
        "local_path": r"output\Lote_Prueba_Diario\2_Manto_Pava_Bordado_PRO_v2.jpg",
        "drive_folder_id": "1g7XL098W2eU5eqhYemjpzJTAtQPwMqdx",
        "obs": "Sujeto intacto bordados en relieve preservados fondo #E5E1DE",
        "control_row": 840
    },
    {
        "id_reg": 24,
        "row_reg": 25,
        "cat": "Para ella / Accesorios / Pardos de Marinera / Pardos de Hilo",
        "orig_name": "2.2 Pardos de hilo.jpg",
        "orig_id": "1cP5JHPFpqn0_bGv8VgGyC9f1czHd5CKD",
        "orig_link": "https://drive.google.com/file/d/1cP5JHPFpqn0_bGv8VgGyC9f1czHd5CKD/view",
        "pro_name": "2_2_Pardos_de_hilo_PRO_v2.jpg",
        "local_path": r"output\Lote_Prueba_Diario\2_2_Pardos_de_hilo_PRO_v2.jpg",
        "drive_folder_id": "12fkES5ridQx74_jMCWO2CLVXrKKSM2h7",
        "obs": "Sujeto intacto cordon tradicional preservado fondo #E5E1DE",
        "control_row": 815
    },
    {
        "id_reg": 25,
        "row_reg": 26,
        "cat": "Para ella / Accesorios / Faja de Hilo para Marinera",
        "orig_name": "3.1 Faja de Hilo para Marinera.jpg",
        "orig_id": "1i_rR0DB1uERorgoX5l536RnxpkYN6lEO",
        "orig_link": "https://drive.google.com/file/d/1i_rR0DB1uERorgoX5l536RnxpkYN6lEO/view",
        "pro_name": "3_1_Faja_de_Hilo_PRO_v2.jpg",
        "local_path": r"output\Lote_Prueba_Diario\3_1_Faja_de_Hilo_PRO_v2.jpg",
        "drive_folder_id": "1rLHpaWFN6Qf4XeTC77WMb7-rp0vWctlg",
        "obs": "Sujeto intacto trama de hilo y calado preservados fondo #E5E1DE",
        "control_row": 819
    }
]

def check_local_images():
    ready = True
    for item in BATCH_ITEMS:
        full_p = os.path.join(os.getcwd(), item["local_path"])
        if os.path.exists(full_p):
            sz = os.path.getsize(full_p) / 1024
            print(f"[OK] Existe: {item['pro_name']} ({sz:.1f} KB)")
        else:
            print(f"[ERROR] No encontrado: {item['pro_name']}")
            ready = False
    return ready

def upload_images():
    for item in BATCH_ITEMS:
        if "pro_id" in item and item["pro_id"]:
            print(f"[SKIP] Ya subido previamente: {item['pro_name']} -> ID: {item['pro_id']}")
            continue
            
        full_p = os.path.join(os.getcwd(), item["local_path"])
        print(f"\nSubiendo {item['pro_name']} a carpeta Drive {item['drive_folder_id']}...")
        cmd = ["gdrive", "mutate", "upload", full_p, "--parent", item["drive_folder_id"]]
        res = subprocess.run(cmd, capture_output=True, text=True, shell=True)
        
        # Parse ID from stdout: Uploaded: 1_1_Escapulario_Mujer_PRO_v2.jpg (ID: 1vxpf0zACFb3Y4puEk7qHJ_FpyqjZa0xi)
        m = re.search(r'ID:\s*([a-zA-Z0-9_-]+)', res.stdout)
        if m:
            file_id = m.group(1)
            item["pro_id"] = file_id
            item["pro_link"] = f"https://drive.google.com/file/d/{file_id}/view"
            print(f"  -> Subido con éxito! ID: {file_id}")
        else:
            print("  -> Error: no se pudo parsear ID de salida.")
            print("  Stdout:", res.stdout)
            print("  Stderr:", res.stderr)
            raise RuntimeError(f"Fallo de subida en {item['pro_name']}")

def register_in_sheets():
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # 1. Filas para Registro_Imagenes_Creadas (filas 22 a 26)
    rows_to_append = []
    for item in BATCH_ITEMS:
        formula_orig = f'=IMAGE("https://lh3.googleusercontent.com/d/{item["orig_id"]}")'
        formula_pro = f'=IMAGE("https://lh3.googleusercontent.com/d/{item["pro_id"]}")'
        row = [
            str(item["id_reg"]),
            now_str,
            item["cat"],
            item["orig_name"],
            item["orig_link"],
            item["pro_name"],
            item["pro_id"],
            item["pro_link"],
            item["local_path"],
            "Antigravity Image Generator (Prompt Oficial #E5E1DE)",
            "E-Commerce 4K",
            "APROBADO_CATALOGO",
            item["obs"],
            formula_orig,
            formula_pro
        ]
        rows_to_append.append(row)
        
    batch_ops = [
        {
            "op": "write",
            "range": "Registro_Imagenes_Creadas!A22:O26",
            "data": rows_to_append
        }
    ]
    
    batch_json_path = os.path.join(os.getcwd(), "scripts", "batch_registro_lote2.json")
    with open(batch_json_path, "w", encoding="utf-8") as f:
        json.dump(batch_ops, f, ensure_ascii=False)
        
    print(f"\nEscribiendo filas 22-26 en Registro_Imagenes_Creadas...")
    cmd = ["gsheets", "mutate", "batch", SPREADSHEET_ID, "-f", batch_json_path]
    res = subprocess.run(cmd, capture_output=True, text=True, shell=True)
    print("Respuesta Registro_Imagenes_Creadas:", res.stdout)
    if res.returncode != 0:
        print("Error:", res.stderr)

    # 2. Vincular en Control_Total_Fotos
    control_ops = []
    for item in BATCH_ITEMS:
        c_row = item["control_row"]
        print(f"  Vinculando fila {c_row} en Control_Total_Fotos para {item['orig_name']}...")
        control_ops.append({
            "op": "write",
            "range": f"Control_Total_Fotos!F{c_row}:I{c_row}",
            "data": [["COMPLETADO", item["pro_name"], item["pro_id"], item["pro_link"]]]
        })
        # Asegurar fórmula en L
        pro_formula = f'=IMAGE("https://lh3.googleusercontent.com/d/{item["pro_id"]}")'
        control_ops.append({
            "op": "write",
            "range": f"Control_Total_Fotos!L{c_row}",
            "data": [[pro_formula]]
        })

    control_json_path = os.path.join(os.getcwd(), "scripts", "batch_control_lote2.json")
    with open(control_json_path, "w", encoding="utf-8") as f:
        json.dump(control_ops, f, ensure_ascii=False)
    print(f"Actualizando {len(control_ops)//2} filas en Control_Total_Fotos...")
    cmd_ctrl = ["gsheets", "mutate", "batch", SPREADSHEET_ID, "-f", control_json_path]
    res_ctrl = subprocess.run(cmd_ctrl, capture_output=True, text=True, shell=True)
    print("Respuesta Control_Total_Fotos:", res_ctrl.stdout)
    if res_ctrl.returncode != 0:
        print("Error:", res_ctrl.stderr)

if __name__ == "__main__":
    if check_local_images():
        upload_images()
        register_in_sheets()
        print("\n=== LOTE 2 COMPLETADO CON ÉXITO ===")
    else:
        print("\nError: faltan imágenes locales.")
