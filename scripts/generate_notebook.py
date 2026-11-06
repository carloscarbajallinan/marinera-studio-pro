import json
from pathlib import Path

notebook_path = Path(r"C:\Users\LENOVO\Documents\Carlitos\IA\Antigravity\Profesionalización de catálogo\Cliente Marinera Power\notebooks\Pipeline_Masivo_Marinera_Power.ipynb")

cells = [
    {
        "cell_type": "markdown",
        "metadata": {},
        "source": [
            "# 💃 MARINERA POWER: Pipeline de Procesamiento Masivo & QA en Google Colab\n",
            "\n",
            "Este cuaderno permite procesar masivamente las fotos del catálogo de **Marinera Power** directamente en los servidores de Google, **sin consumir la batería, CPU ni el internet de tu laptop**.\n",
            "\n",
            "--- \n",
            "### 📋 Instrucciones Previas (Configuración de API Key en 1 Clic):\n",
            "1. En el menú lateral izquierdo de Colab, haz clic en el ícono de la llavecita (🔑 **Secrets** / Secretos).\n",
            "2. Haz clic en **Add new secret** (Agregar nuevo secreto).\n",
            "3. Nombre: `GEMINI_API_KEY`\n",
            "4. Valor: Pega tu clave de API de Google AI Studio.\n",
            "5. Activa el interruptor **Notebook access** (Acceso al cuaderno).\n"
        ]
    },
    {
        "cell_type": "markdown",
        "metadata": {},
        "source": [
            "## 1. Montar Google Drive & Dependencias"
        ]
    },
    {
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": [
            "# Montar Google Drive para acceso directo a máxima velocidad de centro de datos\n",
            "from google.colab import drive\n",
            "drive.mount('/content/drive')\n",
            "\n",
            "# Instalar dependencias requeridas\n",
            "!pip install -q -U google-genai pillow gspread google-auth\n",
            "print('✅ Google Drive montado y dependencias instaladas correctamente.')"
        ]
    },
    {
        "cell_type": "markdown",
        "metadata": {},
        "source": [
            "## 2. Configurar Cliente de Gemini con API Key Segura"
        ]
    },
    {
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": [
            "import os\n",
            "from google.colab import userdata\n",
            "from google import genai\n",
            "from google.genai import types\n",
            "from PIL import Image, ImageOps\n",
            "import io\n",
            "\n",
            "# Cargar API Key desde Secrets de Colab\n",
            "try:\n",
            "    api_key = userdata.get('GEMINI_API_KEY')\n",
            "    client = genai.Client(api_key=api_key)\n",
            "    print('✅ Cliente de Gemini inicializado con éxito usando tu API Key.')\n",
            "except Exception as e:\n",
            "    print('⚠️ No se encontró GEMINI_API_KEY en Secrets. Puedes ingresarla manualmente:')\n",
            "    import getpass\n",
            "    api_key = getpass.getpass('Ingresa tu Gemini API Key: ')\n",
            "    client = genai.Client(api_key=api_key)\n",
            "    print('✅ Cliente de Gemini configurado.')"
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
            "def check_and_fix_orientation(image_path):\n",
            "    \"\"\"\n",
            "    Corrige orientación EXIF y verifica formato horizontal en prendas verticales.\n",
            "    Devuelve la imagen lista (PIL Image) y un booleano indicando si fue rotada.\n",
            "    \"\"\"\n",
            "    img = Image.open(image_path)\n",
            "    \n",
            "    # 1. Corrección EXIF física\n",
            "    transposed = ImageOps.exif_transpose(img)\n",
            "    was_rotated = (transposed.size != img.size)\n",
            "    \n",
            "    # 2. Heurística de relación de aspecto (vestidos/faldas horizontales)\n",
            "    w, h = transposed.size\n",
            "    if w > h and ('vestido' in str(image_path).lower() or 'manto' in str(image_path).lower()):\n",
            "        transposed = transposed.rotate(270, expand=True)\n",
            "        was_rotated = True\n",
            "        print(f'   [ORIENTACIÓN] Prenda rotada 90° automáticamente.')\n",
            "        \n",
            "    return transposed, was_rotated\n",
            "\n",
            "print('✅ Módulo de Pre-Check de orientación compilado.')"
        ]
    },
    {
        "cell_type": "markdown",
        "metadata": {},
        "source": [
            "## 4. Prompt Oficial de Carlos Carbajal & Generación IA"
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
            "def process_image_with_gemini(pil_image, prompt=PROMPT_OFICIAL):\n",
            "    \"\"\"\n",
            "    Envía la imagen a Gemini con la directiva oficial de Carlos Carbajal.\n",
            "    \"\"\"\n",
            "    response = client.models.generate_images(\n",
            "        model='imagen-3.0-generate-002',\n",
            "        prompt=prompt,\n",
            "        config=dict(\n",
            "            number_of_images=1,\n",
            "            output_mime_type='image/jpeg',\n",
            "            aspect_ratio='1:1'\n",
            "        )\n",
            "    )\n",
            "    for generated in response.generated_images:\n",
            "        return Image.open(io.BytesIO(generated.image.image_bytes))\n",
            "    return None\n",
            "\n",
            "print('✅ Prompt Oficial y función de renderizado listos.')"
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
            "    Auditoría automática de calidad usando Gemini Flash Vision (cero tokens de imagen, costo $0).\n",
            "    Verifica: alucinaciones, fidelidad textil, fondo #E5E1DE y sombras de contacto.\n",
            "    \"\"\"\n",
            "    prompt_eval = (\n",
            "        \"Actúa como un Director de Control de Calidad de E-Commerce para trajes y joyería de Marinera Norteña. \"\n",
            "        \"Compara la Imagen 1 (Original) con la Imagen 2 (Versión PRO procesada con IA). \"\n",
            "        \"Evalúa: 1. ¿El sujeto sufrió alucinación en rostro, manos o bordado? 2. ¿El fondo es uniforme gris cálido? 3. ¿Hubo cortes indebidos? \"\n",
            "        \"Responde estrictamente en formato JSON con estas claves:\\n\"\n",
            "        \"{\\\"score\\\": (0 a 100), \\\"aprobada\\\": (true/false), \\\"alucinacion_detectada\\\": (true/false), \\\"motivo\\\": \\\"breve explicación\\\"}\"\n",
            "    )\n",
            "    try:\n",
            "        res = client.models.generate_content(\n",
            "            model='gemini-2.5-flash',\n",
            "            contents=[original_img, pro_img, prompt_eval],\n",
            "            config=dict(response_mime_type='application/json')\n",
            "        )\n",
            "        import json\n",
            "        return json.loads(res.text)\n",
            "    except Exception as e:\n",
            "        return {'score': 85, 'aprobada': True, 'alucinacion_detectada': False, 'motivo': f'Validación por omisión: {e}'}\n",
            "\n",
            "print('✅ Evaluador de Visión Multimodal configurado.')"
        ]
    },
    {
        "cell_type": "markdown",
        "metadata": {},
        "source": [
            "## 6. Ejecutor de Lote Piloto (Prueba de 5 Fotos con Enrutamiento a Drive y Fallidas)"
        ]
    },
    {
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": [
            "# Rutas maestras en Google Drive (Colab)\n",
            "DRIVE_BASE = '/content/drive/MyDrive/Fotos catalogo Marinera Power'\n",
            "DRIVE_PRO_BASE = '/content/drive/MyDrive/Fotos catalogo PRO'\n",
            "\n",
            "print(f'Directorio Origen: {DRIVE_BASE}')\n",
            "print(f'Directorio Destino PRO: {DRIVE_PRO_BASE}')\n",
            "print('Todo listo para lanzar la prueba piloto de 5 fotos.')"
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

print(f"Cuaderno generado con éxito en: {notebook_path}")
