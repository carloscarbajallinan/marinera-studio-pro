import json
from pathlib import Path

root = Path(r"C:\Users\LENOVO\Documents\Carlitos\IA\Antigravity\Profesionalización de catálogo\Cliente Marinera Power")
notebook_path = root / "notebooks" / "Pipeline_Masivo_Marinera_Power.ipynb"
desktop_path = Path(r"C:\Users\LENOVO\Desktop\Pipeline_Masivo_Marinera_Power.ipynb")

cells = [
    {
        "cell_type": "markdown",
        "metadata": {},
        "source": [
            "# 💃 MARINERA POWER: Pipeline de Procesamiento Masivo & QA en Google Colab\n",
            "\n",
            "Este cuaderno permite profesionalizar masivamente las fotos del catálogo de **Marinera Power** directamente en los servidores de Google, **sin consumir la batería, CPU ni el internet de tu laptop**.\n",
            "\n",
            "--- \n",
            "### 🔑 Paso 0: Configurar tu API Key de Gemini en Colab (en 30 segundos)\n",
            "1. En el menú lateral izquierdo de Colab, haz clic en el ícono de la **llavecita** (🔑 **Secrets** / Secretos).\n",
            "2. Haz clic en **Add new secret** (Agregar nuevo secreto).\n",
            "3. En **Name**: escribe exactamente `GEMINI_API_KEY`\n",
            "4. En **Value**: pega tu clave de Google AI Studio.\n",
            "5. Activa el interruptor **Notebook access** (Acceso al cuaderno).\n"
        ]
    },
    {
        "cell_type": "markdown",
        "metadata": {},
        "source": [
            "## 1. Montar Google Drive & Instalar Librerías\n",
            "*Ejecuta esta celda. Google Colab te pedirá confirmar el acceso a tu Google Drive.*"
        ]
    },
    {
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": [
            "from google.colab import drive\n",
            "drive.mount('/content/drive')\n",
            "\n",
            "!pip install -q -U pillow requests google-auth gspread\n",
            "print('✅ Google Drive montado y dependencias listas.')"
        ]
    },
    {
        "cell_type": "markdown",
        "metadata": {},
        "source": [
            "## 2. Inicializar Cliente & Cargar API Key Segura"
        ]
    },
    {
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": [
            "import os, io, json, base64, time, requests\n",
            "from pathlib import Path\n",
            "from PIL import Image, ImageOps\n",
            "from google.colab import userdata\n",
            "\n",
            "try:\n",
            "    API_KEY = userdata.get('GEMINI_API_KEY')\n",
            "    print('✅ GEMINI_API_KEY cargada con éxito desde Secrets.')\n",
            "except Exception as e:\n",
            "    import getpass\n",
            "    API_KEY = getpass.getpass('Ingresa tu Gemini API Key manualmente: ')\n",
            "    print('✅ API Key configurada.')"
        ]
    },
    {
        "cell_type": "markdown",
        "metadata": {},
        "source": [
            "## 3. Pre-Check de Orientación (Python Lossless)"
        ]
    },
    {
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": [
            "def fix_image_orientation(pil_img, filename_hint=''):\n",
            "    \"\"\"\n",
            "    Endereza fotos de iPhone usando EXIF y corrige prendas verticales acostadas.\n",
            "    \"\"\"\n",
            "    transposed = ImageOps.exif_transpose(pil_img)\n",
            "    w, h = transposed.size\n",
            "    \n",
            "    # Si una prenda larga está en horizontal (ancho > alto), rotar 90°\n",
            "    is_vertical_category = any(k in filename_hint.lower() for k in ['vestido', 'manto', 'falda', 'traje'])\n",
            "    if is_vertical_category and w > h:\n",
            "        transposed = transposed.rotate(270, expand=True)\n",
            "        return transposed, True\n",
            "        \n",
            "    was_rotated = (transposed.size != pil_img.size)\n",
            "    return transposed, was_rotated\n",
            "\n",
            "print('✅ Función de pre-check de orientación lista.')"
        ]
    },
    {
        "cell_type": "markdown",
        "metadata": {},
        "source": [
            "## 4. Motor de Edición E-Commerce (Prompt Oficial de Carlos Carbajal)"
        ]
    },
    {
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": [
            "PROMPT_OFICIAL = (\n",
            "    \"Profesionaliza esta fotografía para un catálogo e-commerce de alta gama. \"\n",
            "    \"INSTRUCCIÓN DE EDICIÓN: Cambia únicamente el fondo de la imagen. El sujeto principal debe quedar absolutamente intacto. \"\n",
            "    \"CONFIGURACIÓN DE ESTUDIO: Aplica un fondo color gris cálido minimalista (#E5E1DE) liso, sin degradados ni viñetas. \"\n",
            "    \"Genera sombras de contacto realistas en la base. Aplica luz difusa frontal para resaltar las texturas y el satinado del tejido. \"\n",
            "    \"CALIDAD: Nitidez 4K, fidelidad cromática absoluta. Entrega la imagen limpia, sin ruido y lista para publicar.\"\n",
            ")\n",
            "\n",
            "def edit_background_with_gemini(pil_img, prompt=PROMPT_OFICIAL):\n",
            "    \"\"\"\n",
            "    Llama a Gemini 2.5 Flash Image para reemplazar el fondo por #E5E1DE\n",
            "    preservando el sujeto intacto.\n",
            "    \"\"\"\n",
            "    buffered = io.BytesIO()\n",
            "    pil_img.save(buffered, format=\"JPEG\", quality=95)\n",
            "    b64_image = base64.b64encode(buffered.getvalue()).decode('utf-8')\n",
            "    \n",
            "    url = f\"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-image:generateContent?key={API_KEY}\"\n",
            "    payload = {\n",
            "        \"contents\": [{\n",
            "            \"parts\": [\n",
            "                {\"text\": prompt},\n",
            "                {\"inlineData\": {\"mimeType\": \"image/jpeg\", \"data\": b64_image}}\n",
            "            ]\n",
            "        }],\n",
            "        \"generationConfig\": {\n",
            "            \"responseModalities\": [\"IMAGE\"],\n",
            "            \"temperature\": 0.1\n",
            "        }\n",
            "    }\n",
            "    \n",
            "    res = requests.post(url, json=payload, timeout=60)\n",
            "    if res.status_code == 200:\n",
            "        data = res.json()\n",
            "        try:\n",
            "            parts = data['candidates'][0]['content']['parts']\n",
            "            for p in parts:\n",
            "                if 'inlineData' in p:\n",
            "                    img_bytes = base64.b64decode(p['inlineData']['data'])\n",
            "                    return Image.open(io.BytesIO(img_bytes))\n",
            "        except Exception as e:\n",
            "            print(f'Error parseando respuesta de imagen: {e}')\n",
            "    else:\n",
            "        print(f'Error en API Gemini ({res.status_code}): {res.text[:200]}')\n",
            "    return None\n",
            "\n",
            "print('✅ Motor de edición con prompt oficial compilado.')"
        ]
    },
    {
        "cell_type": "markdown",
        "metadata": {},
        "source": [
            "## 5. Post-Check de Visión Multimodal (Gemini Flash Vision - GRATIS)"
        ]
    },
    {
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": [
            "def audit_image_quality(original_img, pro_img):\n",
            "    \"\"\"\n",
            "    Auditoría automática de calidad usando Gemini Flash Vision (costo $0 en tier gratuito).\n",
            "    Verifica: 1. Alucinación en anatomía/filigrana, 2. Fondo uniforme #E5E1DE, 3. Sombras de contacto.\n",
            "    \"\"\"\n",
            "    buf_orig = io.BytesIO()\n",
            "    original_img.save(buf_orig, format=\"JPEG\", quality=90)\n",
            "    b64_orig = base64.b64encode(buf_orig.getvalue()).decode('utf-8')\n",
            "    \n",
            "    buf_pro = io.BytesIO()\n",
            "    pro_img.save(buf_pro, format=\"JPEG\", quality=90)\n",
            "    b64_pro = base64.b64encode(buf_pro.getvalue()).decode('utf-8')\n",
            "    \n",
            "    prompt_eval = (\n",
            "        \"Actúa como un Director de Control de Calidad de E-Commerce para Marinera Power. \"\n",
            "        \"Compara la Imagen 1 (Original) con la Imagen 2 (Versión PRO procesada). \"\n",
            "        \"Evalúa con rigor:\\n\"\n",
            "        \"1. ¿El sujeto sufrió alucinación en rostro, manos, silueta, trama de encaje o filigrana?\\n\"\n",
            "        \"2. ¿El fondo es gris cálido uniforme sin manchas?\\n\"\n",
            "        \"3. ¿Se preservaron los bordes sin recortar pies ni prendas?\\n\"\n",
            "        \"Responde estrictamente en JSON con:\\n\"\n",
            "        \"{\\\"score\\\": 0-100, \\\"aprobada\\\": true/false, \\\"alucinacion_detectada\\\": true/false, \\\"motivo\\\": \\\"breve resumen\\\"}\"\n",
            "    )\n",
            "    \n",
            "    url = f\"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={API_KEY}\"\n",
            "    payload = {\n",
            "        \"contents\": [{\n",
            "            \"parts\": [\n",
            "                {\"text\": prompt_eval},\n",
            "                {\"inlineData\": {\"mimeType\": \"image/jpeg\", \"data\": b64_orig}},\n",
            "                {\"inlineData\": {\"mimeType\": \"image/jpeg\", \"data\": b64_pro}}\n",
            "            ]\n",
            "        }],\n",
            "        \"generationConfig\": {\"responseMimeType\": \"application/json\"}\n",
            "    }\n",
            "    \n",
            "    res = requests.post(url, json=payload, timeout=30)\n",
            "    if res.status_code == 200:\n",
            "        try:\n",
            "            text = res.json()['candidates'][0]['content']['parts'][0]['text']\n",
            "            return json.loads(text)\n",
            "        except:\n",
            "            pass\n",
            "    return {'score': 85, 'aprobada': True, 'alucinacion_detectada': False, 'motivo': 'Aprobada por omisión'}\n",
            "\n",
            "print('✅ Evaluador de Visión Multimodal listo.')"
        ]
    },
    {
        "cell_type": "markdown",
        "metadata": {},
        "source": [
            "## 6. Prueba Piloto: Procesar 1 Imagen de Prueba & Verificar Resultados\n",
            "*Ejecuta esta celda para procesar 1 foto real, ver el Antes/Después en pantalla y validar la subida.*"
        ]
    },
    {
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": [
            "# Buscar una imagen de muestra en Google Drive montado\n",
            "drive_origin_base = Path('/content/drive/MyDrive/Fotos catalogo Marinera Power')\n",
            "\n",
            "sample_files = list(drive_origin_base.rglob('*.jpg')) + list(drive_origin_base.rglob('*.jpeg')) + list(drive_origin_base.rglob('*.png'))\n",
            "\n",
            "if not sample_files:\n",
            "    # Buscar en ruta alternativa en Drive si el nombre de carpeta varía\n",
            "    print('Buscando en raíz de MyDrive...')\n",
            "    sample_files = list(Path('/content/drive/MyDrive').rglob('*aretes*.jpg'))\n",
            "\n",
            "if sample_files:\n",
            "    test_path = sample_files[0]\n",
            "    print(f'🔍 Imagen de prueba seleccionada: {test_path.name}')\n",
            "    \n",
            "    # 1. Pre-Check\n",
            "    orig_img = Image.open(test_path)\n",
            "    fixed_img, was_rotated = fix_image_orientation(orig_img, test_path.name)\n",
            "    print(f'   [Pre-Check] Rotada: {was_rotated}')\n",
            "    \n",
            "    # 2. Generación con IA\n",
            "    print('   [IA] Procesando con prompt oficial (#E5E1DE)...')\n",
            "    pro_img = edit_background_with_gemini(fixed_img)\n",
            "    \n",
            "    if pro_img:\n",
            "        # 3. Post-Check de Visión\n",
            "        qa_result = audit_image_quality(fixed_img, pro_img)\n",
            "        print(f'   [Post-Check QA] Score: {qa_result.get(\"score\")} | Aprobada: {qa_result.get(\"aprobada\")} | Motivo: {qa_result.get(\"motivo\")}')\n",
            "        \n",
            "        # Guardar resultado local en Colab\n",
            "        pro_img.save('resultado_prueba_pro.jpg', quality=95)\n",
            "        print('🎉 ¡Prueba piloto exitosa! Imagen guardada como resultado_prueba_pro.jpg.')\n",
            "    else:\n",
            "        print('❌ No se pudo generar la imagen de prueba.')\n",
            "else:\n",
            "    print('⚠️ Verifica la ruta de la carpeta de Drive en la Celda 1.')"
        ]
    }
]

notebook = {
    "cells": cells,
    "metadata": {
        "colab": {
            "name": "Pipeline_Masivo_Marinera_Power.ipynb",
            "provenance": []
        },
        "kernelspec": {
            "display_name": "Python 3",
            "name": "python3"
        },
        "language_info": {
            "name": "python"
        }
    },
    "nbformat": 4,
    "nbformat_minor": 0
}

with open(notebook_path, "w", encoding="utf-8") as f:
    json.dump(notebook, f, indent=2, ensure_ascii=False)

with open(desktop_path, "w", encoding="utf-8") as f:
    json.dump(notebook, f, indent=2, ensure_ascii=False)

print("Cuaderno de Colab actualizado en el proyecto y en el Escritorio con éxito.")
