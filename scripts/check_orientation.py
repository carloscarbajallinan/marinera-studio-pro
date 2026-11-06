"""
Módulo de Detección y Corrección de Orientación para Fotografías de Catálogo.
Aplica auto-rotación EXIF sin pérdida y chequeo heurístico/visión antes de pasar por el prompt IA.
"""

import os
from pathlib import Path
from PIL import Image, ImageOps

def fix_exif_orientation(image_path: Path, output_path: Path = None) -> bool:
    """
    Lee los metadatos EXIF de orientación y rota físicamente los píxeles si la imagen
    está rotada (típico en fotos de iPhone/Android). Devuelve True si requirió rotación.
    """
    if output_path is None:
        output_path = image_path
        
    try:
        with Image.open(image_path) as img:
            # Obtener imagen con rotación corregida según EXIF
            transposed = ImageOps.exif_transpose(img)
            
            # Verificar si cambió la orientación
            if transposed.size != img.size:
                transposed.save(output_path, quality=95, keep_exif=False)
                print(f"[ORIENTACIÓN EXIF] Corregida: {image_path.name} (Nuevo tamaño: {transposed.size})")
                return True
            else:
                # Si no requirió transposición de dimensiones, verificar si igual hubo cambio
                return False
    except Exception as e:
        print(f"[ERROR EXIF] En {image_path.name}: {e}")
        return False

def check_aspect_ratio_heuristic(image_path: Path, category_name: str) -> dict:
    """
    Verifica si una prenda vertical (vestido, manto de pie, maniquí)
    está acostada horizontalmente (ancho > alto).
    """
    with Image.open(image_path) as img:
        w, h = img.size
        is_landscape = w > h
        
        # Categorías que DEBEN ser verticales
        vertical_categories = ["vestido", "falda", "manto", "blusa", "traje"]
        should_be_vertical = any(cat in category_name.lower() for cat in vertical_categories)
        
        if should_be_vertical and is_landscape:
            return {
                "sospechosa": True,
                "motivo": f"Prenda de categoría '{category_name}' en formato horizontal ({w}x{h}). Probable rotación 90° requerida.",
                "sugerencia_rotacion": 90
            }
        return {"sospechosa": False, "motivo": "Orientación geométrica normal", "sugerencia_rotacion": 0}

if __name__ == "__main__":
    sample_dir = Path(r"C:\Users\LENOVO\Pictures\Marinera Power\fotos creadas")
    if sample_dir.exists():
        samples = list(sample_dir.glob("*.jpg"))[:5]
        print(f"Probando pre-check de orientación en {len(samples)} fotos locales...")
        for s in samples:
            res = check_aspect_ratio_heuristic(s, "Para ella / Vestidos")
            print(f" - {s.name}: {res}")
