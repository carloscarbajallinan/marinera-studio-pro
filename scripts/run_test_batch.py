import sys
from pathlib import Path
from PIL import Image

PROJECT_ROOT = Path(r"C:\Users\LENOVO\Documents\Carlitos\IA\Antigravity\Profesionalización de catálogo\Cliente Marinera Power")
sys.path.insert(0, str(PROJECT_ROOT))

from engine.processor import professionalize_single_image

src_dir = Path(r"C:\Users\LENOVO\Pictures\Marinera Power\fotos creadas")
out_dir = PROJECT_ROOT / "output" / "Lote_Prueba_Diario"
out_dir.mkdir(parents=True, exist_ok=True)

test_files = [
    ("2.1 aretes marinera.jpg", "Aretes Filigrana Norteña"),
    ("2.1 aretes para marinera.jpg", "Aretes Tradicionales Catacaos"),
    ("2.1 MANTO DE LECHE.jpg", "Manto de Leche Bordado"),
    ("2.2 MANTO DE LECHE.jpg", "Manto de Leche Relieve"),
    ("2.1 Pardos de hilo.jpg", "Pardos de Hilo Tradicionales")
]

results = []
print("Iniciando procesamiento de 5 imágenes de prueba...")

for idx, (filename, desc) in enumerate(test_files, start=11):
    src_path = src_dir / filename
    if not src_path.exists():
        print(f"Error: {filename} no encontrado.")
        continue
    
    stem_clean = filename.replace(" ", "_").replace(".jpg", "").replace(".", "_")
    target_name = f"{stem_clean}_PRO_1x1.jpg"
    target_path = out_dir / target_name
    
    out = professionalize_single_image(
        input_path=str(src_path),
        output_path=str(target_path),
        preset="editorial",
        ratio="1:1",
        add_badge=True
    )
    
    im = Image.open(out)
    print(f"[{idx}] OK: {filename} -> {target_name} ({im.size[0]}x{im.size[1]})")
    results.append({
        "id": idx,
        "filename": filename,
        "target_name": target_name,
        "target_path": str(target_path),
        "desc": desc,
        "size": f"{im.size[0]}x{im.size[1]}"
    })

print(f"\nFinalizado: {len(results)} fotos procesadas exitosamente en: {out_dir}")
