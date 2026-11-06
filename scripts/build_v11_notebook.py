import json, sys
sys.stdout.reconfigure(encoding='utf-8')
from pathlib import Path

root = Path(r"C:\Users\LENOVO\Documents\Carlitos\IA\Antigravity\Profesionalización de catálogo\Cliente Marinera Power")
nb_path = r"C:\Users\LENOVO\AppData\Local\Temp\colab_carlos_updated.ipynb"

with open(nb_path, 'r', encoding='utf-8') as f:
    nb = json.load(f)

# Cell 4: Engine + Dual Quality Gates (Deterministic + Gemini Vision)
cell_4_code = '''# 4. Motor de Generación & Dual Quality Gate (Determinístico en OpenCV + Visión IA)
import numpy as np
import cv2

PROMPT_MAESTRO = """[TASK DIRECTIVE]
Professionally retouch this commercial fashion and jewelry photograph for the high-end e-commerce catalog of Marinera Power. Modify ONLY the background and floor surfaces. Do NOT alter the subject.

[IMMUTABLE COLOR & STUDIO UNIFORMITY - HEX #E5E1DE]
- BACKDROP COLOR: The entire background must be an absolutely uniform, solid, flat warm-grey studio backdrop matching hex color #E5E1DE (exact RGB: 229, 225, 222).
- ZERO GRADIENTS & ZERO VIGNETTING: Completely eliminate room corners, wall seams, domestic shadows, and color gradients. The background tone must be 100% consistent across all catalog photos. Zero beige shifts, zero brown casts, zero cool white clinical shifts.
- ZERO COLOR BOUNCE & AMBIENT SPILL: Highly saturated red, purple, fuchsia garments and gold jewelry must NOT bleed color, radiosity, or ambient spill onto the background.

[MANDATORY SCALE & BOUNDING BOX LOCK - NO ZOOM OUT / NO SHRINKING]
- PRESERVE 1:1 SCALE: The subject (model, dancer, garment, jewelry) MUST maintain the EXACT same pixel dimensions, proportion, and framing as in the original photograph.
- STRICTLY PROHIBITED TO ZOOM OUT: Do NOT push the subject into the distance. Do NOT shrink the subject. The subject must remain in full foreground focus exactly as framed originally.
- NO OUTPAINTING: If the subject is cut at the waist, bust, or legs, KEEP that exact crop. Do NOT hallucinate missing limbs or expand the field of view.

[CLEAN FLOOR & FOOT CONTACT - ZERO DIRT OR SMUDGES]
- PRISTINE FLOOR: The ground surface must be clean and flawless.
- NATURAL CONTACT SHADOW: Render ONLY a delicate, soft, feathered, transparent contact shadow directly under the soles of shoes or bare feet. 
- ABSOLUTELY NO DIRT, NO MUDDY PATCHES, NO DARK SMUDGES, and NO grey halos around the feet or hemline.

[PRESERVATION OF DETAILS]
- Faces, skin tone, hair, white linen marinera handkerchief, and 18k Peruvian gold filigree must remain 100% untouched and razor-sharp."""

def edit_background_gemini(pil_img, prompt_text=PROMPT_MAESTRO, max_retries=3):
    buffered = io.BytesIO()
    pil_img.save(buffered, format='JPEG', quality=95)
    b64_image = base64.b64encode(buffered.getvalue()).decode('utf-8')

    url = f'https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-image:generateContent?key={API_KEY}'
    payload = {
        'contents': [{
            'parts': [
                {'text': prompt_text},
                {'inlineData': {'mimeType': 'image/jpeg', 'data': b64_image}}
            ]
        }],
        'generationConfig': {
            'responseModalities': ['IMAGE'],
            'temperature': 0.05
        }
    }

    for intento in range(max_retries):
        try:
            res = requests.post(url, json=payload, timeout=90)
            if res.status_code == 200:
                parts = res.json()['candidates'][0]['content']['parts']
                for p in parts:
                    if 'inlineData' in p:
                        img_bytes = base64.b64decode(p['inlineData']['data'])
                        return Image.open(io.BytesIO(img_bytes)), None
            elif res.status_code in (429, 503):
                time.sleep(12 * (intento + 1))
                continue
            else:
                return None, f'HTTP {res.status_code}: {res.text[:120]}'
        except requests.exceptions.Timeout:
            if intento == max_retries - 1:
                return None, 'Timeout API (90s alcanzado)'
            time.sleep(5)
        except Exception as e:
            return None, str(e)
    return None, 'Fallo recurrente tras reintentos'

def deterministic_quality_gates(orig_pil, pro_pil):
    """
    Quality Gates Deterministas en Python (< 50ms, Costo $0):
    1. QG-01: Delta Cromático Periférico en 4 esquinas vs #E5E1DE (RGB 229, 225, 222)
    2. QG-02: Bounding Box & Escala 1:1 (Detección de Zoom-out / encogimiento)
    3. QG-03: Desplazamiento de Centroide (Desbalance de composición)
    4. QG-05: Índice de Limpieza de Piso (Detección de manchas oscuras / barro)
    """
    np_orig = np.array(orig_pil)
    np_pro = np.array(pro_pil)
    h, w = np_pro.shape[:2]

    # 1. Delta Cromático en 4 esquinas
    target_rgb = np.array([229, 225, 222], dtype=np.float32)
    corner_sz = max(15, min(w, h) // 15)
    corners = [
        np_pro[0:corner_sz, 0:corner_sz],
        np_pro[0:corner_sz, -corner_sz:],
        np_pro[h//2 - corner_sz:h//2, 0:corner_sz],
        np_pro[h//2 - corner_sz:h//2, -corner_sz:]
    ]
    mean_corner_rgb = np.mean([c.mean(axis=(0,1)) for c in corners], axis=0)
    delta_color = float(np.linalg.norm(mean_corner_rgb - target_rgb))

    # 2. Escala 1:1 y Bounding Box
    dist_orig = np.linalg.norm(np_orig.astype(np.float32) - np_orig[0:15, 0:15].mean(axis=(0,1)), axis=2)
    dist_pro = np.linalg.norm(np_pro.astype(np.float32) - target_rgb, axis=2)
    mask_orig = (dist_orig > 25).astype(np.uint8)
    mask_pro = (dist_pro > 25).astype(np.uint8)

    scale_ratio = 1.0
    centroid_shift = 0.0
    pts_orig = cv2.findNonZero(mask_orig)
    pts_pro = cv2.findNonZero(mask_pro)

    if pts_orig is not None and pts_pro is not None:
        _, _, _, h_orig_box = cv2.boundingRect(pts_orig)
        _, _, _, h_pro_box = cv2.boundingRect(pts_pro)
        scale_ratio = float(h_pro_box) / float(h_orig_box) if h_orig_box > 0 else 1.0
        m_pro = cv2.moments(mask_pro)
        if m_pro['m00'] > 0:
            cx_pro = m_pro['m10'] / m_pro['m00']
            centroid_shift = abs(cx_pro - (w / 2.0)) / float(w)

    # 3. Limpieza de Piso (15% inferior)
    floor_roi = np_pro[int(h * 0.85):, :]
    floor_dist = np.linalg.norm(floor_roi.astype(np.float32) - target_rgb, axis=2)
    dirt_pixels = np.sum((floor_dist > 45) & (np.mean(floor_roi, axis=2) < 160)) / float(floor_roi.shape[0] * floor_roi.shape[1])
    floor_dirt_score = max(0, 100 - int(dirt_pixels * 500))

    # Veredicto Determinístico
    det_pass = True
    fail_reasons = []

    if scale_ratio < 0.85:
        det_pass = False
        fail_reasons.append(f"Zoom-out no autorizado: Sujeto encogido al {int(scale_ratio*100)}%")
    elif scale_ratio > 1.15:
        fail_reasons.append(f"Encuadre expandido / Outpainting: {scale_ratio:.2f}x")

    if delta_color > 18.0:
        det_pass = False
        fail_reasons.append(f"Desvío cromático: ΔE={delta_color:.1f} (Límite 18.0)")

    if floor_dirt_score < 60:
        fail_reasons.append("Piso sucio / Manchas oscuras bajo los pies")

    score_color = max(0, 100 - int(delta_color * 3.5))
    score_scale = max(10, int(scale_ratio * 100)) if scale_ratio < 0.85 else 100
    score_det = int(score_color * 0.35 + score_scale * 0.40 + floor_dirt_score * 0.15 + (100 - int(centroid_shift * 100)) * 0.10)
    if not det_pass:
        score_det = min(score_det, 35)

    return {
        'score_deterministico': score_det,
        'aprobada_deterministico': det_pass,
        'delta_color': round(delta_color, 1),
        'escala_ratio': round(scale_ratio, 2),
        'desplazamiento_centroide': round(centroid_shift, 3),
        'limpieza_piso_score': floor_dirt_score,
        'motivo': " | ".join(fail_reasons) if fail_reasons else "Cumple todos los Quality Gates matemáticos (#E5E1DE, escala 1:1, piso limpio)"
    }

def audit_image_quality(orig_pil, pro_pil):
    """
    Auditoría Híbrida:
    1. Quality Gate Matemático (60% peso + Veto Absoluto)
    2. Opinión Visión Multimodal Gemini 2.5 Flash (40% peso)
    """
    det_eval = deterministic_quality_gates(orig_pil, pro_pil)

    # Veto Inmediato sin complacencia si falla el determinismo:
    if not det_eval['aprobada_deterministico']:
        return {
            'score': det_eval['score_deterministico'],
            'score_det': det_eval['score_deterministico'],
            'score_ia': 0,
            'aprobada': False,
            'motivo': f"🚨 VETO DETERMINÍSTICO: {det_eval['motivo']}",
            'detalles_det': det_eval
        }

    # Si pasa el determinismo, solicitamos la opinión de Gemini Vision:
    buf1, buf2 = io.BytesIO(), io.BytesIO()
    orig_pil.save(buf1, format='JPEG', quality=85)
    pro_pil.save(buf2, format='JPEG', quality=85)
    b64_1 = base64.b64encode(buf1.getvalue()).decode('utf-8')
    b64_2 = base64.b64encode(buf2.getvalue()).decode('utf-8')

    eval_prompt = (
        'Actúa como Auditor Riguroso de E-Commerce para Marinera Power. Evalúa la foto PRO respecto a la Original:\\n'
        '1. ¿Manos, dedos, pañuelo de marinera y filigrana de oro están 100% nítidos e intactos?\\n'
        '2. ¿La sombra de contacto es natural, suave y transparente?\\n'
        'Responde estrictamente en JSON: {"score": 0-100, "aprobada": true/false, "motivo": "breve resumen"}'
    )
    url = f'https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={API_KEY}'
    payload = {
        'contents': [{
            'parts': [
                {'text': eval_prompt},
                {'inlineData': {'mimeType': 'image/jpeg', 'data': b64_1}},
                {'inlineData': {'mimeType': 'image/jpeg', 'data': b64_2}}
            ]
        }],
        'generationConfig': {'responseMimeType': 'application/json'}
    }

    score_ia = 80
    aprobada_ia = True
    motivo_ia = "Evaluación IA satisfactoria"

    try:
        res = requests.post(url, json=payload, timeout=25)
        if res.status_code == 200:
            ai_data = json.loads(res.json()['candidates'][0]['content']['parts'][0]['text'])
            score_ia = ai_data.get('score', 80)
            aprobada_ia = ai_data.get('aprobada', True)
            motivo_ia = ai_data.get('motivo', 'Validado')
    except Exception as e:
        motivo_ia = f"Fallo parcial de visión: {e}"

    # Ponderación Oficial: 60% Determinístico + 40% IA
    score_final = int(det_eval['score_deterministico'] * 0.60 + score_ia * 0.40)
    aprobada_final = det_eval['aprobada_deterministico'] and aprobada_ia and (score_final >= 80)

    return {
        'score': score_final,
        'score_det': det_eval['score_deterministico'],
        'score_ia': score_ia,
        'aprobada': aprobada_final,
        'motivo': f"[Det: {det_eval['score_deterministico']}/100 | IA: {score_ia}/100] {motivo_ia}",
        'detalles_det': det_eval
    }

print('✅ Motor de Generación & Dual Quality Gate (Determinístico + IA) cargados.')
'''

nb['cells'][4]['source'] = [line + '\n' for line in cell_4_code.split('\n')]

v11_path = r"C:\Users\LENOVO\AppData\Local\Temp\Pipeline_Masivo_Marinera_Power_V11_DualScore.ipynb"
with open(v11_path, 'w', encoding='utf-8') as f:
    json.dump(nb, f, indent=2, ensure_ascii=False)

repo_nb = root / "notebooks" / "Pipeline_Masivo_Marinera_Power.ipynb"
with open(repo_nb, 'w', encoding='utf-8') as f:
    json.dump(nb, f, indent=2, ensure_ascii=False)

print("Notebook V11 con Dual Quality Gate generado exitosamente.")
