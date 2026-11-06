"""
Generador Autónomo de Prompts Especializados para Gemini Imagen 3
Marca: Marinera Power (Gianina)
Estándar: Alta Costura, E-commerce de Lujo y Escenarios Tradicionales Peruanos
"""

import json
from pathlib import Path

PRESETS = {
    "vestido_concurso": {
        "title": "Vestido de Marinera Norteña en Acción de Concurso",
        "description": "Retrato editorial dinámico de bailarina con vestido tradicional ondeando en el Club Libertad.",
        "prompt_template": (
            "Professional high-end fashion photography of an elegant Peruvian Marinera Norteña dancer wearing a magnificent {color_theme} traditional marinera gown. "
            "The dress features intricate floral hand-embroidery along the massive circular skirt, delicate scalloped lace borders, and layered ruffles spinning gracefully in motion. "
            "She holds a fine white embroidered linen handkerchief in her right hand with effortless poise. "
            "Adorned with authentic Catacaos gold filigree long earrings (aretes de pavo), an embroidered devotional scapular on her chest, and a polished floral velvet headdress woven into her neat braided chignon hairstyle. "
            "Setting: An opulent colonial courtyard in Trujillo, Peru, featuring historic sunlit arches, hand-painted ceramic tiles, and warm late-afternoon golden hour backlighting. "
            "Shot on Hasselblad H6D-100c, 85mm f/1.4 lens, razor-sharp fabric texture, cinematic soft bokeh, commercial luxury catalogue grade, photorealistic 8k."
        )
    },
    "joyeria_macro": {
        "title": "Macro de Joyería en Filigrana de Plata y Oro",
        "description": "Fotografía macro de estudio para aretes, escapularios o broches tradicionales.",
        "prompt_template": (
            "Extreme macro studio product photography of authentic handcrafted Peruvian Marinera {jewelry_type}. "
            "Masterpiece of Catacaos artisan filigree crafted from sterling silver with 24k gold dipping, featuring micro-twisted wire patterns, peacock motifs, and shimmering natural pearls. "
            "Placed elegantly on a dark matte navy blue (#353C51) velvet display stand with soft ambient highlights reflecting the metallic gleam. "
            "Shot with 100mm macro f/2.8 lens, focus stacked for edge-to-edge crystalline sharpness, diffused studio rim lighting, luxury jewelry catalog look, ultra-clean commercial aesthetic."
        )
    },
    "manto_editorial": {
        "title": "Manto Tradicional (Manto de Pava / Manto de Leche)",
        "description": "Ficha de catálogo de alta gama destacando los relieves y texturas de los mantos.",
        "prompt_template": (
            "Exquisite commercial studio product photography showcasing a Peruvian traditional {manto_type} drape. "
            "The textile is made of premium fine weave with opulent relief hand-embroidery depicting heritage peacock feathers, scalloped fringes, and fine macramé knots. "
            "Displayed gracefully draped over a minimalist limestone pedestal with a neutral pearl-white (#FDFBF7) seamless infinity backdrop. "
            "Dramatic soft side-lighting revealing the micro-texture of the cotton threads and embroidery relief, shallow depth of field, Vogue Collections style, pristine 8k resolution."
        )
    },
    "ecommerce_clean": {
        "title": "Catálogo E-commerce Minimalista (Fondo Blanco/Gris)",
        "description": "Foto de producto aislada para tienda online y catálogo digital.",
        "prompt_template": (
            "High-end e-commerce product photograph of a Peruvian Marinera accessory ({product_item}) displayed on a spotless minimalist studio setup. "
            "Pure clean light gray to soft white background (#F8F9FA) with natural subtle ground contact shadow underneath. "
            "Perfect color accuracy, calibrated studio strobes, no distracting elements, crisp silhouette, commercial Shopify premium catalog standard."
        )
    }
}

def generate_prompt(preset_key: str, **kwargs) -> str:
    """Genera el prompt listo para copiar o enviar al motor de Gemini."""
    if preset_key not in PRESETS:
        preset_key = "vestido_concurso"
    template = PRESETS[preset_key]["prompt_template"]
    
    defaults = {
        "color_theme": "Turquoise (#0044EE) and white satin ribbon",
        "jewelry_type": "Filigree Peacock Earrings (Aretes de Pavo)",
        "manto_type": "Manto de Pava with gold thread embroidery",
        "product_item": "Handcrafted Peruvian Scapular with Gold Leaf Motif"
    }
    defaults.update(kwargs)
    return template.format(**defaults)

if __name__ == "__main__":
    print("=" * 60)
    print("🌟 GENERADOR DE PROMPTS MARINERA POWER")
    print("=" * 60)
    for key, data in PRESETS.items():
        print(f"\n[PRESET: {data['title']}]")
        print(generate_prompt(key))
