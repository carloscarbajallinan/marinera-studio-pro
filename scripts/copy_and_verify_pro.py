import shutil
import os
from PIL import Image

brain_dir = r"C:\Users\LENOVO\.gemini\antigravity\brain\9fafa467-c0f1-4daa-8568-f84dce8c64ca"
dest_dir = r"C:\Users\LENOVO\Documents\Carlitos\IA\Antigravity\Profesionalización de catálogo\Cliente Marinera Power\output\Lote_Prueba_Diario"
os.makedirs(dest_dir, exist_ok=True)

file_mappings = [
    ("1_1_escapulario_mujer_pro_v2_1793902254994.jpg", "1_1_Escapulario_Mujer_PRO_v2.jpg"),
    ("1_1_aretes_para_marinera_pro_v2_1793902276539.jpg", "1_1_aretes_para_marinera_PRO_v2.jpg"),
    ("2_manto_pava_bordado_pro_v2_1793902275642.jpg", "2_Manto_Pava_Bordado_PRO_v2.jpg"),
    ("2_2_pardos_de_hilo_pro_v2_1793902272083.jpg", "2_2_Pardos_de_hilo_PRO_v2.jpg"),
    ("3_1_faja_de_hilo_pro_v2_1793902269316.jpg", "3_1_Faja_de_Hilo_PRO_v2.jpg")
]

print("Copiando y validando imágenes PRO...")
for src_name, dst_name in file_mappings:
    src_path = os.path.join(brain_dir, src_name)
    dst_path = os.path.join(dest_dir, dst_name)
    shutil.copy2(src_path, dst_path)
    im = Image.open(dst_path)
    sz_kb = os.path.getsize(dst_path) / 1024
    print(f"  [OK] {dst_name} -> {im.size[0]}x{im.size[1]} | {sz_kb:.1f} KB")

print("\nTodas las imágenes copiadas exitosamente a output/Lote_Prueba_Diario/")
