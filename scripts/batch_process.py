"""
Script ejecutor para procesar en lote las fotos de Marinera Power.
Lee directamente desde la carpeta de fotos creadas y exporta a output.
"""

import os
import sys
from pathlib import Path

# Agregar raiz al PYTHONPATH
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from engine.processor import batch_process_folder

def main():
    source_folder = r"C:\Users\LENOVO\Pictures\Marinera Power\fotos creadas"
    target_folder = str(PROJECT_ROOT / "output")
    
    print("=" * 65)
    print("MARINERA POWER - PROFESIONALIZADOR POR LOTES")
    print(f"Origen:  {source_folder}")
    print(f"Destino: {target_folder}")
    print("=" * 65)
    
    if not os.path.exists(source_folder):
        print(f"Error: La carpeta de origen no existe: {source_folder}")
        return
        
    batch_process_folder(
        input_folder=source_folder,
        output_folder=target_folder,
        preset="editorial",
        ratio="1:1",
        max_files=None,
        skip_existing=True
    )

if __name__ == "__main__":
    main()
