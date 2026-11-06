"""
Motor de Procesamiento y Profesionalización de Imágenes
Marca: Marinera Power (Gianina)
Tecnología: Python Pillow (PIL)
"""

import os
import sys
from pathlib import Path
from PIL import Image, ImageEnhance, ImageFilter, ImageOps, ImageDraw, ImageFont

# Dimensiones estándar según Brand Book
ASPECT_RATIOS = {
    "1:1": (1080, 1080),      # Instagram Feed
    "4:5": (1080, 1350),      # Instagram Retrato
    "9:16": (1080, 1920),     # Stories / Reels / TikTok
    "3:4": (1200, 1600),      # Catálogo E-commerce Web
}

def apply_preset_filters(image: Image.Image, preset: str = "editorial") -> Image.Image:
    """Aplica curvas de ajuste de color y enfoque según el estilo seleccionado."""
    # Convertir a RGB si está en RGBA o modo paleta
    if image.mode != "RGB":
        image = image.convert("RGB")
        
    if preset == "ecommerce":
        # Máxima nitidez y claridad para ficha técnica
        enhancer = ImageEnhance.Sharpness(image)
        image = enhancer.enhance(1.4)
        enhancer = ImageEnhance.Contrast(image)
        image = enhancer.enhance(1.15)
        enhancer = ImageEnhance.Brightness(image)
        image = enhancer.enhance(1.05)
        
    elif preset == "editorial":
        # Calidez norteña, tonos dorados suaves y contraste elegante
        enhancer = ImageEnhance.Color(image)
        image = enhancer.enhance(1.2)
        enhancer = ImageEnhance.Contrast(image)
        image = enhancer.enhance(1.1)
        enhancer = ImageEnhance.Sharpness(image)
        image = enhancer.enhance(1.25)
        
    elif preset == "vibrance":
        # Resalte de faldas turquesa (#0044EE) y rojos vivos
        enhancer = ImageEnhance.Color(image)
        image = enhancer.enhance(1.35)
        enhancer = ImageEnhance.Contrast(image)
        image = enhancer.enhance(1.2)
        enhancer = ImageEnhance.Sharpness(image)
        image = enhancer.enhance(1.3)
        
    return image

def fit_to_aspect_ratio(image: Image.Image, target_ratio: str = "1:1", pad_color: tuple = (250, 250, 252)) -> Image.Image:
    """Ajusta la imagen a la proporción deseada sin recortar información vital, agregando marco de estudio."""
    if target_ratio not in ASPECT_RATIOS:
        target_ratio = "1:1"
        
    target_w, target_h = ASPECT_RATIOS[target_ratio]
    orig_w, orig_h = image.size
    
    # Calcular escala de contención
    scale = min(target_w / orig_w, target_h / orig_h)
    new_w = int(orig_w * scale)
    new_h = int(orig_h * scale)
    
    resized = image.resize((new_w, new_h), Image.Resampling.LANCZOS)
    
    # Crear lienzo de destino con fondo neutro de alta gama
    canvas = Image.new("RGB", (target_w, target_h), pad_color)
    pos_x = (target_w - new_w) // 2
    pos_y = (target_h - new_h) // 2
    
    canvas.paste(resized, (pos_x, pos_y))
    return canvas

def add_marinera_brand_badge(image: Image.Image, opacity: float = 0.85) -> Image.Image:
    """Agrega el sello distintivo de 'MARINERA POWER' en la esquina inferior."""
    w, h = image.size
    overlay = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    
    # Dimensiones relativas del badge
    badge_w = int(w * 0.38)
    badge_h = int(h * 0.055)
    margin = int(w * 0.04)
    
    box_x1 = w - badge_w - margin
    box_y1 = h - badge_h - margin
    box_x2 = w - margin
    box_y2 = h - margin
    
    # Fondo elegante azul marino (#353C51) con borde dorado (#D4AF37)
    draw.rounded_rectangle([box_x1, box_y1, box_x2, box_y2], radius=10, fill=(53, 60, 81, int(220 * opacity)), outline=(212, 175, 55, int(255 * opacity)), width=2)
    
    # Texto
    text = "MARINERA POWER"
    subtext = "COLECCIÓN OFICIAL"
    
    # Intentar usar fuente básica predeterminada si no hay truetype
    try:
        font_main = ImageFont.load_default()
    except Exception:
        font_main = None
        
    text_x = box_x1 + 16
    text_y = box_y1 + 8
    draw.text((text_x, text_y), f"{text} | {subtext}", fill=(253, 251, 247, 240), font=font_main)
    
    # Combinar overlay con la imagen original
    image = image.convert("RGBA")
    combined = Image.alpha_composite(image, overlay)
    return combined.convert("RGB")

def professionalize_single_image(input_path: str, output_path: str, preset: str = "editorial", ratio: str = "1:1", add_badge: bool = True) -> str:
    """Procesa una imagen individual con el flujo completo."""
    img = Image.open(input_path)
    # 1. Aplicar filtros de realce y color grading
    img = apply_preset_filters(img, preset=preset)
    # 2. Ajustar al aspect ratio deseado
    img = fit_to_aspect_ratio(img, target_ratio=ratio)
    # 3. Aplicar badge de marca si se requiere
    if add_badge:
        img = add_marinera_brand_badge(img)
    # 4. Guardar resultado
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    img.save(output_path, quality=95)
    return output_path

def batch_process_folder(input_folder: str, output_folder: str, preset: str = "editorial", ratio: str = "1:1", max_files: int = None, skip_existing: bool = True):
    """Procesa una carpeta completa de imágenes en lote."""
    valid_extensions = {".jpg", ".jpeg", ".png", ".webp"}
    input_p = Path(input_folder)
    output_p = Path(output_folder)
    output_p.mkdir(parents=True, exist_ok=True)
    
    files = [f for f in input_p.iterdir() if f.suffix.lower() in valid_extensions]
    total_found = len(files)
    target_files = files if (max_files is None or max_files <= 0) else files[:max_files]
    
    print(f"[INFO] Se encontraron {total_found} imágenes en '{input_folder}'. Procesando {len(target_files)}...")
    
    count = 0
    skipped = 0
    for i, f in enumerate(target_files, 1):
        out_file = output_p / f"{f.stem}_PRO_{ratio.replace(':', 'x')}.jpg"
        if skip_existing and out_file.exists():
            skipped += 1
            continue
        try:
            professionalize_single_image(str(f), str(out_file), preset=preset, ratio=ratio)
            print(f"  [{i}/{len(target_files)}] [OK] {f.name} -> {out_file.name}")
            count += 1
        except Exception as e:
            print(f"  [{i}/{len(target_files)}] [ERROR] en {f.name}: {e}")
            
    print(f"\n[FIN] Lote finalizado: {count} nuevas imágenes procesadas, {skipped} omitidas (ya existían) en '{output_folder}'.")

if __name__ == "__main__":
    # Test simple de verificación
    print("Módulo de procesamiento cargado con éxito.")
