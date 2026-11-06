import json, re, sys
sys.stdout.reconfigure(encoding='utf-8')
from pathlib import Path

root = Path(r"C:\Users\LENOVO\Documents\Carlitos\IA\Antigravity\Profesionalización de catálogo\Cliente Marinera Power")
py_script = root / "marinera_colab_pipeline_v5_hardened.py"
nb_target = root / "notebooks" / "Pipeline_Masivo_Marinera_Power.ipynb"

with open(py_script, 'r', encoding='utf-8') as f:
    text = f.read()

# Split by '# ============================================================\n# CELDA '
pattern = r'# ============================================================\s*\n# CELDA \d+\s*\n# ============================================================\s*\n'
raw_chunks = re.split(pattern, text)

# The first chunk before Celda 1 is module docstring
header_doc = raw_chunks[0].strip().replace('"""', '').strip()
cells = []

# Cell 0: Markdown overview
md_intro = f"""# 🏛️ MARINERA POWER: Pipeline Industrial Definitivo (Arquitectura en 3 Niveles)
### Retoque Fotográfico E-Commerce de Alta Fidelidad con Gemini 2.5 Flash & OpenCV

**Garantías del Pipeline:**
1. **Cero Pérdida de Inversión:** Toda imagen devuelta por Gemini se persiste atómicamente en NVMe local y Google Drive antes de cualquier análisis.
2. **Arquitectura de 3 Niveles:** `_1_RAW_GEMINI` (crudo inalterado) ➡️ `_2_MESA_REVISION_CARLOS` (con score) ➡️ `_3_CATALOGO_FINAL_APROBADO` (visto bueno).
3. **Clasificador Jerárquico Condicional Anti-Alucinación:**
   - **MODA_MODELO:** Prioridad máxima para indumentaria (faldas, blusas, vestidos, trajes, enagues). Conserva modelos 1:1 sin alucinaciones de escala. Los ribetes ("con cinta blanca") jamás se confunden con joyería.
   - **JOYERIA_ACCESORIO:** Bodegón macro (aretes, collares, filigrana). Prohíbe terminantemente inventar humanos o bailarinas.
4. **Sincronización Directa Google Drive API v3:** Resuelve el File ID real en la nube sin depender del retardo de sincronización de FUSE.
5. **Aislamiento Total de Pruebas:** Los tests se auditan exclusivamente en `Registro_Pruebas_Sandbox`. El Catálogo Maestro `Control_Total_Drive_V2` permanece limpio y protegido.
"""

cells.append({
    "cell_type": "markdown",
    "metadata": {},
    "source": [line + '\n' for line in md_intro.splitlines()]
})

for i, code_body in enumerate(raw_chunks[1:], start=1):
    clean_lines = [line + '\n' for line in code_body.strip().splitlines()]
    cells.append({
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": clean_lines
    })

nb_json = {
    "nbformat": 4,
    "nbformat_minor": 0,
    "metadata": {
        "colab": {
            "name": "Pipeline_Masivo_Marinera_Power.ipynb",
            "provenance": []
        },
        "kernelspec": {
            "name": "python3",
            "display_name": "Python 3"
        },
        "language_info": {
            "name": "python"
        }
    },
    "cells": cells
}

with open(nb_target, 'w', encoding='utf-8') as f:
    json.dump(nb_json, f, indent=2, ensure_ascii=False)

print(f"Compiled {nb_target} successfully with {len(cells)} cells!")
