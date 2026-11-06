import json, re, sys
sys.stdout.reconfigure(encoding='utf-8')
from pathlib import Path

root = Path(r"C:\Users\LENOVO\Documents\Carlitos\IA\Antigravity\Profesionalización de catálogo\Cliente Marinera Power")
docs_html = root / "docs" / "index.html"
root_html = root / "index.html"

with open(docs_html, 'r', encoding='utf-8') as f:
    content = f.read()

# Enhanced Items with Dual Scoring: Deterministic (Math) vs AI (Vision)
qa_items_dual = [
    {
        "id": "CANARY-1",
        "Fecha_Creacion": "2026-11-05 21:12:00",
        "Ubicacion_Categoria": "Para ella / Falda / Falda de Ensayo / Lila con cinta morada",
        "Nombre_Archivo_Original": "foto (3).png",
        "Caso_Prueba": "Recorte Sobel barras blancas Instagram (193px)",
        "Estado_Validacion": "APROBADO_CATALOGO",
        "Score_Final": 98,
        "Score_Det": 100,
        "Score_IA": 96,
        "Det_Details": {
            "delta_color": "ΔE 3.2 (OK)",
            "escala": "1:1 Exacta",
            "piso": "100% Impoluto",
            "sobel": "Recorte 193px ejecutado"
        },
        "IA_Details": "Ciclorama uniforme #E5E1DE sin viñeteo. Sombras de contacto sutiles.",
        "Observaciones": "Filtro Sobel recortó 193px de barra lateral. Ciclorama y textura de razo lila 100% preservados.",
        "img_orig": "canary/canary_1_orig.png",
        "img_pro": "canary/canary_1_pro.jpg",
        "Link_Drive_PRO": "https://drive.google.com/file/d/1S2rDiJk3Zfq21ubYBX-vqywJ-SC-XtEJ/view"
    },
    {
        "id": "CANARY-2",
        "Fecha_Creacion": "2026-11-05 21:12:00",
        "Ubicacion_Categoria": "Para ella / Falda / Falda de Ensayo / Lila con cinta morada",
        "Nombre_Archivo_Original": "34a63e97 PRO.jpg",
        "Caso_Prueba": "Reemplazo de suelo de parquet por ciclorama #E5E1DE",
        "Estado_Validacion": "VETADO_DETERMINISMO",
        "Score_Final": 25,
        "Score_Det": 25,
        "Score_IA": 85,
        "Det_Details": {
            "delta_color": "ΔE 26.8 (FAIL - Marrón)",
            "escala": "FAIL: Encogida al 30% (Zoom-Out)",
            "piso": "FAIL: Manchas oscuras en piso",
            "sobel": "N/A"
        },
        "IA_Details": "Evaluador complaciente no midió escala ni suciedad (Corregido en V2).",
        "Observaciones": "VETADO POR AUDITORÍA: La modelo fue encogida al 30% violando escala 1:1 y el fondo viró a marrón #9B8F86.",
        "img_orig": "canary/canary_2_orig.jpg",
        "img_pro": "canary/canary_2_pro.jpg",
        "Link_Drive_PRO": "https://drive.google.com/file/d/1Kd1sSmPlKhxYJ9rKoD6yaHfJxHHfP36i/view"
    },
    {
        "id": "CANARY-3",
        "Fecha_Creacion": "2026-11-05 21:12:00",
        "Ubicacion_Categoria": "Para ella / Falda / Falda de Ensayo / Coral con cinta blanca",
        "Nombre_Archivo_Original": "d72049af PRO.jpg",
        "Caso_Prueba": "Blindaje anatómico: Manos y pañuelo al viento",
        "Estado_Validacion": "APROBADO_CATALOGO",
        "Score_Final": 96,
        "Score_Det": 96,
        "Score_IA": 96,
        "Det_Details": {
            "delta_color": "ΔE 4.1 (OK)",
            "escala": "1:1 Exacta",
            "piso": "100% Impoluto",
            "sobel": "Sin bordes artificiales"
        },
        "IA_Details": "Cero amputación de dedos. Preservación perfecta del pañuelo blanco ondeando.",
        "Observaciones": "Silueta de bailarina intacta, dedos completos y pañuelo de lino ondeando con máxima nitidez.",
        "img_orig": "canary/canary_3_orig.jpg",
        "img_pro": "canary/canary_3_pro.jpg",
        "Link_Drive_PRO": "https://drive.google.com/file/d/12x3fZK-fBXOl_3E9s_DJJsoefXH7GuO0/view"
    },
    {
        "id": "CANARY-4",
        "Fecha_Creacion": "2026-11-05 21:12:00",
        "Ubicacion_Categoria": "Para ella / Accesorios / Aretes para Marinera",
        "Nombre_Archivo_Original": "1.jpg (Aretes Filigrana)",
        "Caso_Prueba": "Macro Joyería: Oro 18k y filigrana calada",
        "Estado_Validacion": "APROBADO_CATALOGO",
        "Score_Final": 95,
        "Score_Det": 97,
        "Score_IA": 94,
        "Det_Details": {
            "delta_color": "ΔE 2.8 (OK)",
            "escala": "1:1 Macro Exacto",
            "piso": "N/A (Joyería)",
            "sobel": "Sin barras"
        },
        "IA_Details": "Destellos especulares metálicos e hilos de oro de 18k preservados sin desenfoque.",
        "Observaciones": "Orfebrería nítida. Destellos metálicos especulares y calado tradicional intactos sobre fondo #E5E1DE.",
        "img_orig": "canary/canary_4_orig.jpg",
        "img_pro": "canary/canary_4_pro.jpg",
        "Link_Drive_PRO": "https://drive.google.com/file/d/1RqMdROIcAd9tXEFaJegCVTGeAj2AK7iZ/view"
    },
    {
        "id": "CANARY-5",
        "Fecha_Creacion": "2026-11-05 21:12:00",
        "Ubicacion_Categoria": "Para ella / Falda / Falda de Ensayo / Morada con cinta blanca",
        "Nombre_Archivo_Original": "1841c6d0 PRO.jpg",
        "Caso_Prueba": "Mandato Cliente: Cero outpainting en plano medio",
        "Estado_Validacion": "APROBADO_CATALOGO",
        "Score_Final": 97,
        "Score_Det": 98,
        "Score_IA": 96,
        "Det_Details": {
            "delta_color": "ΔE 3.0 (OK)",
            "escala": "1:1 Plano Medio Intacto",
            "piso": "N/A (Toma recortada)",
            "sobel": "Sin barras"
        },
        "IA_Details": "Cero alucinación de extremidades faltantes. Encuadre original respetado.",
        "Observaciones": "Cero invención de cuerpo inexistente. El plano medio/busto original fue estrictamente respetado.",
        "img_orig": "canary/canary_5_orig.jpg",
        "img_pro": "canary/canary_5_pro.jpg",
        "Link_Drive_PRO": "https://drive.google.com/file/d/1FlZ112AaTsWvavrEeAZJ2YyjK6JmxLeW/view"
    }
]

# Update the qaItems JSON in the HTML
replacement_js = f"const qaItems = {json.dumps(qa_items_dual, ensure_ascii=False, indent=2)};"
content = re.sub(r'const qaItems = \[.*?\];', replacement_js, content, flags=re.DOTALL)

# Now update the renderQaCards function to render the DUAL SCORECARD
dual_render_function = """    function renderQaCards() {
      const grid = document.getElementById('qaGrid');
      grid.innerHTML = '';

      qaItems.forEach(item => {
        const id = item.id || item.ID || 'ITEM';
        const status = pendingChanges[id] ? pendingChanges[id].status : item.Estado_Validacion;
        const isApproved = status === 'APROBADO_CATALOGO';
        const isVetoed = status === 'VETADO_DETERMINISMO';
        
        const origUrl = item.img_orig || getOriginalUrl(item);
        const proUrl = item.img_pro || getProUrl(item);

        const card = document.createElement('div');
        card.className = 'bg-[#121927] border ' + (isVetoed ? 'border-rose-700/80' : 'border-slate-800') + ' rounded-2xl overflow-hidden shadow-2xl flex flex-col transition hover:border-slate-700';

        let imageViewerHtml = '';
        if (qaMode === 'slider') {
          imageViewerHtml = `
            <div class="compare-container">
              <img src="${proUrl}" alt="PRO" class="compare-img" onerror="this.src='https://placehold.co/600x600/101622/A31D1D?text=PRO+en+Drive'">
              <div class="compare-overlay" id="overlay-${id}">
                <img src="${origUrl}" alt="Original" class="compare-img" style="width: 100%; max-width: none;" onerror="this.src='https://placehold.co/600x600/101622/D4AF37?text=Original+en+Drive'">
              </div>
              <input type="range" min="0" max="100" value="50" class="compare-slider" oninput="document.getElementById('overlay-${id}').style.width = this.value + '%'">
              <div class="absolute bottom-2 left-2 z-10 px-2 py-0.5 rounded bg-black/75 text-[10px] text-amber-300 font-bold border border-amber-400/30">ORIGINAL</div>
              <div class="absolute bottom-2 right-2 z-10 px-2 py-0.5 rounded bg-black/75 text-[10px] text-emerald-300 font-bold border border-emerald-400/30">VERSIÓN PRO</div>
            </div>
          `;
        } else {
          imageViewerHtml = `
            <div class="grid grid-cols-2 gap-2 bg-black/40 p-2 rounded-xl">
              <div class="relative">
                <img src="${origUrl}" alt="Original" class="w-full h-44 object-contain rounded-lg bg-black" onerror="this.src='https://placehold.co/600x600/101622/D4AF37?text=Original'">
                <span class="absolute bottom-1.5 left-1.5 px-1.5 py-0.5 rounded bg-black/75 text-[9px] text-amber-300 font-bold border border-amber-400/30">Original</span>
              </div>
              <div class="relative">
                <img src="${proUrl}" alt="PRO" class="w-full h-44 object-contain rounded-lg bg-black" onerror="this.src='https://placehold.co/600x600/101622/A31D1D?text=PRO'">
                <span class="absolute bottom-1.5 left-1.5 px-1.5 py-0.5 rounded bg-black/75 text-[9px] text-emerald-300 font-bold border border-emerald-400/30">PRO</span>
              </div>
            </div>
          `;
        }

        const scoreFinal = item.Score_Final || 85;
        const scoreDet = item.Score_Det || 85;
        const scoreIA = item.Score_IA || 85;

        let badgeClass = 'badge-ok';
        let badgeText = 'APROBADO';
        if (isVetoed) {
          badgeClass = 'bg-rose-500/20 text-rose-300 border border-rose-500/40';
          badgeText = '🚨 VETADO POR DETERMINISMO';
        } else if (!isApproved) {
          badgeClass = 'badge-error';
          badgeText = 'ERROR / RECHAZADO';
        }

        card.innerHTML = `
          <div class="p-3.5 bg-slate-900/80 border-b border-slate-800 flex items-center justify-between text-xs">
            <div>
              <span class="font-bold text-amber-400 font-cinzel text-sm">#${id}</span>
              <span class="text-slate-300 ml-1 truncate font-medium">&bull; ${item.Nombre_Archivo_Original}</span>
            </div>
            <span class="px-2.5 py-1 rounded-full text-[10px] font-bold ${badgeClass} shrink-0">
              ${badgeText}
            </span>
          </div>

          <div class="p-4 flex-1 flex flex-col justify-between">
            ${imageViewerHtml}

            <!-- PANEL DE DOBLE AUDITORÍA: DETERMINÍSTICO VS IA -->
            <div class="mt-4 p-3 rounded-xl bg-slate-950/80 border border-slate-800 space-y-2.5">
              <div class="flex items-center justify-between text-xs border-b border-slate-800/80 pb-1.5">
                <span class="font-bold text-slate-300">⚖️ Score Final Ponderado:</span>
                <span class="font-bold text-sm ${scoreFinal >= 80 ? 'text-emerald-400' : 'text-rose-400'}">${scoreFinal}/100</span>
              </div>

              <!-- 1. Medidor Determinístico (Matemático) -->
              <div>
                <div class="flex items-center justify-between text-[11px] mb-1">
                  <span class="text-indigo-300 font-bold flex items-center gap-1">📐 Control Determinista (OpenCV / $0):</span>
                  <span class="font-bold ${scoreDet >= 80 ? 'text-indigo-400' : 'text-rose-400'}">${scoreDet}/100</span>
                </div>
                <div class="w-full h-1.5 bg-slate-800 rounded-full overflow-hidden">
                  <div class="h-full ${scoreDet >= 80 ? 'bg-indigo-500' : 'bg-rose-500'}" style="width: ${scoreDet}%"></div>
                </div>
                <div class="grid grid-cols-2 gap-1 mt-1.5 text-[9px] text-slate-400 font-mono">
                  <span>🎨 Color: <strong class="text-slate-200">${item.Det_Details ? item.Det_Details.delta_color : 'N/A'}</strong></span>
                  <span>📏 Escala: <strong class="text-slate-200">${item.Det_Details ? item.Det_Details.escala : 'N/A'}</strong></span>
                  <span>🧹 Piso: <strong class="text-slate-200">${item.Det_Details ? item.Det_Details.piso : 'N/A'}</strong></span>
                  <span>✂️ Borde: <strong class="text-slate-200">${item.Det_Details ? item.Det_Details.sobel : 'N/A'}</strong></span>
                </div>
              </div>

              <!-- 2. Medidor IA (Gemini Vision) -->
              <div class="pt-1.5 border-t border-slate-800/60">
                <div class="flex items-center justify-between text-[11px] mb-1">
                  <span class="text-amber-300 font-bold flex items-center gap-1">🤖 Opinión IA (Gemini Vision):</span>
                  <span class="font-bold ${scoreIA >= 80 ? 'text-amber-400' : 'text-rose-400'}">${scoreIA}/100</span>
                </div>
                <div class="w-full h-1.5 bg-slate-800 rounded-full overflow-hidden">
                  <div class="h-full ${scoreIA >= 80 ? 'bg-amber-500' : 'bg-rose-500'}" style="width: ${scoreIA}%"></div>
                </div>
                <p class="text-[10px] text-slate-400 mt-1 italic">${item.IA_Details || 'Validación de textura y joyería'}</p>
              </div>
            </div>

            <!-- Caso y Observaciones -->
            <div class="mt-3 space-y-1 text-[11px] text-slate-400">
              <div class="truncate text-slate-300"><strong class="text-amber-400">📁</strong> ${item.Ubicacion_Categoria}</div>
              <div class="p-2.5 rounded-lg bg-slate-900/90 border border-slate-800 mt-1.5 text-[11px] text-slate-300">
                ${pendingChanges[id] ? pendingChanges[id].obs : item.Observaciones || 'Sin observaciones'}
              </div>
            </div>

            <!-- Botones de Feedback Humano -->
            <div class="mt-4 pt-3 border-t border-slate-800 flex items-center gap-2">
              <button onclick="approveQa('${id}')" class="flex-1 py-2 rounded-lg text-xs font-bold transition ${isApproved ? 'bg-emerald-600/30 text-emerald-300 border border-emerald-500/40 cursor-default' : 'bg-emerald-600 hover:bg-emerald-500 text-white shadow-lg'}">
                ✅ Aprobar
              </button>
              <button onclick="openRejectModal('${id}')" class="flex-1 py-2 rounded-lg text-xs font-bold transition ${(!isApproved || isVetoed) ? 'bg-rose-600/30 text-rose-300 border border-rose-500/40 cursor-default' : 'bg-rose-600 hover:bg-rose-500 text-white shadow-lg'}">
                ❌ Marcar Mal
              </button>
            </div>
          </div>
        `;

        grid.appendChild(card);
      });
    }"""

# Replace the old renderQaCards function
content = re.sub(r'function renderQaCards\(\)\s*\{.*?function renderShowcaseCards', dual_render_function + "\n\n    function renderShowcaseCards", content, flags=re.DOTALL)

with open(docs_html, 'w', encoding='utf-8') as f:
    f.write(content)

with open(root_html, 'w', encoding='utf-8') as f:
    f.write(content)

print("docs/index.html and index.html upgraded with Dual Scorecard successfully!")
