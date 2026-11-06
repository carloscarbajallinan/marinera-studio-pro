import json
from pathlib import Path

root = Path(r"C:\Users\LENOVO\Documents\Carlitos\IA\Antigravity\Profesionalización de catálogo\Cliente Marinera Power")
output_dir = root / "output"

qa_data = json.load(open(output_dir / "test_cases_data.json", encoding="utf-8"))
showcase_data = json.load(open(output_dir / "full_catalog_showcase.json", encoding="utf-8"))

html_template = f"""<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Tablero Maestro & Control de Catálogo | MARINERA POWER</title>
  <script src="https://cdn.tailwindcss.com"></script>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Cinzel:wght@600;700;800;900&family=Plus+Jakarta+Sans:wght@400;500;600;700&display=swap" rel="stylesheet">
  <style>
    body {{ font-family: 'Plus Jakarta Sans', sans-serif; background-color: #0A0E17; color: #E2E8F0; }}
    .font-cinzel {{ font-family: 'Cinzel', serif; }}
    .gold-gradient {{
      background: linear-gradient(135deg, #FFF1BD 0%, #D4AF37 50%, #997300 100%);
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
    }}
    .active-nav {{
      background: linear-gradient(135deg, #D4AF37 0%, #AA820A 100%);
      color: #0A0E17;
      font-weight: 700;
    }}
    .badge-ok {{ background-color: rgba(16, 185, 129, 0.2); color: #34d399; border: 1px solid rgba(16, 185, 129, 0.4); }}
    .badge-error {{ background-color: rgba(239, 68, 68, 0.2); color: #f87171; border: 1px solid rgba(239, 68, 68, 0.4); }}
    
    .compare-container {{
      position: relative;
      overflow: hidden;
      width: 100%;
      height: 320px;
      border-radius: 0.75rem;
      background-color: #05070B;
    }}
    .compare-img {{
      position: absolute;
      top: 0;
      left: 0;
      width: 100%;
      height: 100%;
      object-fit: contain;
    }}
    .compare-overlay {{
      position: absolute;
      top: 0;
      left: 0;
      height: 100%;
      overflow: hidden;
      width: 50%;
      border-right: 2px solid #D4AF37;
    }}
    .compare-slider {{
      position: absolute;
      -webkit-appearance: none;
      appearance: none;
      width: 100%;
      height: 100%;
      background: transparent;
      outline: none;
      margin: 0;
      cursor: ew-resize;
      z-index: 20;
    }}
    .compare-slider::-webkit-slider-thumb {{
      -webkit-appearance: none;
      appearance: none;
      width: 24px;
      height: 24px;
      border-radius: 50%;
      background: #D4AF37;
      border: 3px solid #0A0E17;
      cursor: ew-resize;
      box-shadow: 0 0 10px rgba(212, 175, 55, 0.8);
    }}
  </style>
</head>
<body class="min-h-screen flex flex-col selection:bg-amber-400 selection:text-slate-950">

  <!-- Header -->
  <header class="bg-[#101622] border-b border-slate-800 sticky top-0 z-40 backdrop-blur-md bg-opacity-95 shadow-2xl px-6 py-4">
    <div class="max-w-7xl mx-auto flex flex-col lg:flex-row lg:items-center lg:justify-between gap-4">
      <div class="flex items-center space-x-4">
        <div class="w-12 h-12 rounded-xl bg-gradient-to-br from-[#D4AF37] via-amber-600 to-[#A31D1D] flex items-center justify-center font-cinzel font-bold text-[#101622] text-2xl shadow-lg border border-amber-300/40">
          MP
        </div>
        <div>
          <div class="flex items-center space-x-2">
            <h1 class="font-cinzel text-xl md:text-2xl font-bold tracking-wider gold-gradient">MARINERA POWER</h1>
            <span class="px-2.5 py-0.5 text-[11px] font-bold rounded-full bg-emerald-500/20 text-emerald-300 border border-emerald-500/30">MESA MAESTRA DE CONTROL</span>
          </div>
          <p class="text-xs text-slate-400 mt-0.5">Control de Calidad E-Commerce &bull; Auditoría Antes/Después &bull; Catálogo General PRO</p>
        </div>
      </div>

      <!-- Navigation Tabs (Las 3 Vistas) -->
      <div class="flex items-center bg-slate-900 p-1.5 rounded-xl border border-slate-800 space-x-1 overflow-x-auto">
        <button onclick="switchView('plan')" id="navBtn-plan" class="active-nav px-4 py-2 rounded-lg text-xs font-semibold transition flex items-center space-x-2 whitespace-nowrap">
          <span>📊 1. Avance & Plan</span>
        </button>
        <button onclick="switchView('qa')" id="navBtn-qa" class="px-4 py-2 rounded-lg text-xs font-semibold text-slate-300 hover:text-white transition flex items-center space-x-2 whitespace-nowrap">
          <span>🔍 2. Mesa QA (Antes/Después)</span>
        </button>
        <button onclick="switchView('showcase')" id="navBtn-showcase" class="px-4 py-2 rounded-lg text-xs font-semibold text-slate-300 hover:text-white transition flex items-center space-x-2 whitespace-nowrap">
          <span>🛍️ 3. Catálogo General PRO ({len(showcase_data)})</span>
        </button>
      </div>
    </div>
  </header>

  <!-- ==================== VISTA 1: AVANCE & PLAN DE TRABAJO ==================== -->
  <section id="view-plan" class="max-w-7xl mx-auto px-6 py-6 w-full flex-1">
    <div class="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
      <div class="bg-[#121927] p-5 rounded-2xl border border-slate-800 shadow">
        <span class="text-xs text-slate-400 font-medium">Universo Total Catálogo</span>
        <div class="text-3xl font-bold text-white mt-1">866</div>
        <p class="text-[11px] text-slate-500 mt-1">192 carpetas en Google Drive</p>
      </div>
      <div class="bg-[#121927] p-5 rounded-2xl border border-emerald-900/40 shadow">
        <span class="text-xs text-emerald-400 font-medium">Fotos PRO Validadas</span>
        <div class="text-3xl font-bold text-emerald-300 mt-1">{len(showcase_data)}</div>
        <p class="text-[11px] text-slate-500 mt-1">11.7% listas para Shopify</p>
      </div>
      <div class="bg-[#121927] p-5 rounded-2xl border border-amber-900/40 shadow">
        <span class="text-xs text-amber-400 font-medium">Pendientes Vírgenes (Colab)</span>
        <div class="text-3xl font-bold text-amber-300 mt-1">{866 - len(showcase_data)}</div>
        <p class="text-[11px] text-slate-500 mt-1">Por procesar en lotes de 15</p>
      </div>
      <div class="bg-[#121927] p-5 rounded-2xl border border-red-900/40 shadow">
        <span class="text-xs text-red-400 font-medium">En Subcarpeta Fallidas</span>
        <div class="text-3xl font-bold text-red-400 mt-1">15</div>
        <p class="text-[11px] text-slate-500 mt-1">Aisladas en ❌ Fallidas_QA</p>
      </div>
    </div>

    <div class="bg-[#121927] p-6 rounded-2xl border border-slate-800 mb-8 shadow">
      <div class="flex items-center justify-between mb-2">
        <span class="text-sm font-bold text-slate-200">Progreso Global de Profesionalización: 11.7%</span>
        <span class="text-xs text-amber-400 font-semibold">{len(showcase_data)} de 866 fotos completadas</span>
      </div>
      <div class="w-full bg-slate-900 h-3 rounded-full overflow-hidden border border-slate-800">
        <div class="bg-gradient-to-r from-amber-500 to-emerald-400 h-full rounded-full transition-all duration-500" style="width: 11.7%"></div>
      </div>
    </div>

    <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
      <div class="bg-[#121927] p-6 rounded-2xl border border-slate-800 shadow">
        <h3 class="text-base font-bold text-white font-cinzel mb-4">📁 Estructura Espejo en Google Drive</h3>
        <div class="space-y-3 text-xs">
          <div class="p-3 rounded-xl bg-slate-900/60 border border-slate-800 flex items-center justify-between">
            <span class="text-slate-300 font-medium">Ofertas (4 carpetas)</span>
            <span class="px-2 py-0.5 rounded bg-emerald-500/20 text-emerald-300 font-bold">100% Espejo Listo</span>
          </div>
          <div class="p-3 rounded-xl bg-slate-900/60 border border-slate-800 flex items-center justify-between">
            <span class="text-slate-300 font-medium">Para ensayos (6 carpetas)</span>
            <span class="px-2 py-0.5 rounded bg-emerald-500/20 text-emerald-300 font-bold">100% Espejo Listo</span>
          </div>
          <div class="p-3 rounded-xl bg-slate-900/60 border border-slate-800 flex items-center justify-between">
            <span class="text-slate-300 font-medium">Para él (9 carpetas)</span>
            <span class="px-2 py-0.5 rounded bg-emerald-500/20 text-emerald-300 font-bold">100% Espejo Listo</span>
          </div>
          <div class="p-3 rounded-xl bg-slate-900/60 border border-slate-800 flex items-center justify-between">
            <span class="text-slate-300 font-medium">Para ella (54 subcarpetas PRO)</span>
            <span class="px-2 py-0.5 rounded bg-amber-500/20 text-amber-300 font-bold">En Producción</span>
          </div>
        </div>
      </div>

      <div class="bg-[#121927] p-6 rounded-2xl border border-slate-800 shadow">
        <h3 class="text-base font-bold text-white font-cinzel mb-4">⚡ Plan de Ejecución en Google Colab</h3>
        <div class="space-y-3 text-xs text-slate-300">
          <div class="flex items-start space-x-3">
            <span class="w-6 h-6 rounded-full bg-amber-500/20 text-amber-400 font-bold flex items-center justify-center shrink-0">1</span>
            <p><strong>Pre-Check de Orientación:</strong> Auto-rotación sin pérdida con Pillow antes de llamar al prompt.</p>
          </div>
          <div class="flex items-start space-x-3">
            <span class="w-6 h-6 rounded-full bg-amber-500/20 text-amber-400 font-bold flex items-center justify-center shrink-0">2</span>
            <p><strong>Lotes por Oleadas (15 fotos):</strong> Throttling controlado en la nube para no consumir batería local.</p>
          </div>
          <div class="flex items-start space-x-3">
            <span class="w-6 h-6 rounded-full bg-amber-500/20 text-amber-400 font-bold flex items-center justify-center shrink-0">3</span>
            <p><strong>Post-Check Gemini Vision ($0):</strong> Detección de alucinaciones y guardado de fallidas en <code>❌ Fallidas_QA/</code>.</p>
          </div>
          <div class="flex items-start space-x-3">
            <span class="w-6 h-6 rounded-full bg-emerald-500/20 text-emerald-400 font-bold flex items-center justify-center shrink-0">4</span>
            <p><strong>Entrega Final para Shopify:</strong> Catálogo limpio en Drive listo para carga masiva.</p>
          </div>
        </div>
      </div>
    </div>
  </section>

  <!-- ==================== VISTA 2: MESA DE QA (ANTES / DESPUÉS FOTO POR FOTO) ==================== -->
  <section id="view-qa" class="max-w-7xl mx-auto px-6 py-6 w-full flex-1 hidden">
    <div class="bg-[#121927] p-4 rounded-2xl border border-slate-800 mb-6 shadow flex flex-col md:flex-row md:items-center justify-between gap-4">
      <div>
        <h2 class="text-base font-bold text-white font-cinzel">Auditoría Visual: Identificar y Marcar Fotos Incorrectas</h2>
        <p class="text-xs text-slate-400 mt-0.5">Compara el original con la versión PRO. Marca las fotos defectuosas para enviarlas a su subcarpeta de error.</p>
      </div>

      <div class="flex items-center space-x-3">
        <div class="flex items-center space-x-1 bg-slate-900 p-1 rounded-xl border border-slate-800 text-xs">
          <button onclick="setQaMode('slider')" id="btnQaSlider" class="px-2.5 py-1 rounded-lg bg-amber-500 text-slate-950 font-bold transition">Slider</button>
          <button onclick="setQaMode('sideBySide')" id="btnQaSide" class="px-2.5 py-1 rounded-lg text-slate-300 hover:text-white transition">Lado a Lado</button>
        </div>
        <button onclick="downloadAuditJSON()" class="px-3.5 py-1.5 rounded-xl text-xs font-semibold bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 transition">
          💾 Guardar QA JSON
        </button>
      </div>
    </div>

    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6" id="qaGrid"></div>
  </section>

  <!-- ==================== VISTA 3: CATÁLOGO GENERAL PRO (SHOWCASE COMPLETO) ==================== -->
  <section id="view-showcase" class="max-w-7xl mx-auto px-6 py-6 w-full flex-1 hidden">
    <div class="bg-[#121927] p-5 rounded-2xl border border-slate-800 mb-6 shadow flex flex-col md:flex-row md:items-center justify-between gap-4">
      <div>
        <h2 class="text-base font-bold text-white font-cinzel">Catálogo E-Commerce Oficial (Versiones PRO Validadas)</h2>
        <p class="text-xs text-slate-400 mt-0.5">Visualización limpia de todas las piezas que ya cuentan con fotografía PRO de catálogo ({len(showcase_data)} ítems).</p>
      </div>
      <div>
        <input type="text" id="showcaseSearch" oninput="filterShowcase()" placeholder="Buscar producto o carpeta..." 
               class="bg-slate-900 border border-slate-700 rounded-xl px-4 py-2 text-xs text-slate-200 focus:outline-none focus:border-amber-400 w-72">
      </div>
    </div>

    <div class="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 gap-4" id="showcaseGrid"></div>
  </section>

  <!-- Modal Rechazo -->
  <div id="rejectModal" class="fixed inset-0 bg-black/80 backdrop-blur-sm z-50 flex items-center justify-center p-4 hidden">
    <div class="bg-[#121927] border border-slate-700 rounded-2xl max-w-md w-full p-6 shadow-2xl">
      <h3 class="text-base font-bold text-red-300 font-cinzel">Marcar Imagen como Incorrecta</h3>
      <p class="text-xs text-slate-400 mt-1 mb-4">Selecciona el motivo del defecto para aislarla en la subcarpeta <code>❌ Fallidas_QA/</code>:</p>
      
      <div class="space-y-2 mb-5">
        <label class="flex items-center space-x-2.5 p-2.5 rounded-xl bg-slate-900/80 border border-slate-800 hover:border-amber-500/50 cursor-pointer">
          <input type="radio" name="rejectReason" value="Alucinación anatómica o deformación de tejido/joya" checked class="text-amber-500 focus:ring-0">
          <span class="text-xs text-slate-200">Alucinación anatómica / Deformación de tejido o joya</span>
        </label>
        <label class="flex items-center space-x-2.5 p-2.5 rounded-xl bg-slate-900/80 border border-slate-800 hover:border-amber-500/50 cursor-pointer">
          <input type="radio" name="rejectReason" value="Fondo no homogéneo o con manchas / no es #E5E1DE" class="text-amber-500 focus:ring-0">
          <span class="text-xs text-slate-200">Fondo sucio / no es gris cálido #E5E1DE</span>
        </label>
        <label class="flex items-center space-x-2.5 p-2.5 rounded-xl bg-slate-900/80 border border-slate-800 hover:border-amber-500/50 cursor-pointer">
          <input type="radio" name="rejectReason" value="Prenda recortada o pérdida de bordes/pies" class="text-amber-500 focus:ring-0">
          <span class="text-xs text-slate-200">Prenda recortada / pérdida de bordes o pies</span>
        </label>
        <label class="flex items-center space-x-2.5 p-2.5 rounded-xl bg-slate-900/80 border border-slate-800 hover:border-amber-500/50 cursor-pointer">
          <input type="radio" name="rejectReason" value="Orientación incorrecta (está volteada 90° o 180°)" class="text-amber-500 focus:ring-0">
          <span class="text-xs text-slate-200">Orientación incorrecta (está volteada 90° o 180°)</span>
        </label>
      </div>

      <div class="flex items-center justify-end space-x-3">
        <button onclick="closeRejectModal()" class="px-4 py-2 rounded-xl text-xs font-semibold text-slate-400 hover:text-white bg-slate-800 transition">Cancelar</button>
        <button onclick="confirmReject()" class="px-4 py-2 rounded-xl text-xs font-bold bg-red-600 hover:bg-red-500 text-white transition">Confirmar Rechazo</button>
      </div>
    </div>
  </div>

  <script>
    // DATOS INCRUSTADOS DIRECTAMENTE (Cero errores de CORS o archivo local)
    const qaItems = {json.dumps(qa_data, ensure_ascii=False)};
    const showcaseItems = {json.dumps(showcase_data, ensure_ascii=False)};
    
    let qaMode = 'slider';
    let selectedQaId = null;
    let pendingChanges = {{}};

    // Inicializar de inmediato al cargar la página
    window.addEventListener('DOMContentLoaded', () => {{
      renderQaCards();
      renderShowcaseCards();
    }});

    function switchView(viewName) {{
      ['plan', 'qa', 'showcase'].forEach(v => {{
        document.getElementById('view-' + v).classList.add('hidden');
        document.getElementById('navBtn-' + v).className = 'px-4 py-2 rounded-lg text-xs font-semibold text-slate-300 hover:text-white transition flex items-center space-x-2 whitespace-nowrap';
      }});
      document.getElementById('view-' + viewName).classList.remove('hidden');
      document.getElementById('navBtn-' + viewName).className = 'active-nav px-4 py-2 rounded-lg text-xs font-semibold transition flex items-center space-x-2 whitespace-nowrap';
    }}

    function setQaMode(mode) {{
      qaMode = mode;
      document.getElementById('btnQaSlider').className = mode === 'slider' 
        ? 'px-2.5 py-1 rounded-lg bg-amber-500 text-slate-950 font-bold transition'
        : 'px-2.5 py-1 rounded-lg text-slate-300 hover:text-white transition';
      document.getElementById('btnQaSide').className = mode === 'sideBySide' 
        ? 'px-2.5 py-1 rounded-lg bg-amber-500 text-slate-950 font-bold transition'
        : 'px-2.5 py-1 rounded-lg text-slate-300 hover:text-white transition';
      renderQaCards();
    }}

    function getOriginalUrl(item) {{
      if (item.local_orig_rel) return item.local_orig_rel;
      if (item.orig_id) return 'https://lh3.googleusercontent.com/d/' + item.orig_id;
      return 'https://placehold.co/600x600/101622/D4AF37?text=Original';
    }}

    function getProUrl(item) {{
      if (item.local_pro_rel) return item.local_pro_rel;
      if (item.pro_id && item.pro_id !== '-') return 'https://lh3.googleusercontent.com/d/' + item.pro_id;
      return 'https://placehold.co/600x600/101622/A31D1D?text=PRO';
    }}

    function renderQaCards() {{
      const grid = document.getElementById('qaGrid');
      grid.innerHTML = '';

      qaItems.forEach(item => {{
        const id = item.ID_Registro;
        const status = pendingChanges[id] ? pendingChanges[id].status : item.Estado_Validacion;
        const isApproved = status === 'APROBADO_CATALOGO';
        const origUrl = getOriginalUrl(item);
        const proUrl = getProUrl(item);

        const card = document.createElement('div');
        card.className = 'bg-[#121927] border border-slate-800 rounded-2xl overflow-hidden shadow-xl flex flex-col transition hover:border-slate-700';

        let imageViewerHtml = '';
        if (qaMode === 'slider') {{
          imageViewerHtml = `
            <div class="compare-container">
              <img src="${{proUrl}}" alt="PRO" class="compare-img" onerror="this.src='https://placehold.co/600x600/101622/A31D1D?text=PRO+en+Drive'">
              <div class="compare-overlay" id="overlay-${{id}}">
                <img src="${{origUrl}}" alt="Original" class="compare-img" style="width: 100%; max-width: none;" onerror="this.src='https://placehold.co/600x600/101622/D4AF37?text=Original+en+Drive'">
              </div>
              <input type="range" min="0" max="100" value="50" class="compare-slider" oninput="document.getElementById('overlay-${{id}}').style.width = this.value + '%'">
              <div class="absolute bottom-2 left-2 z-10 px-2 py-0.5 rounded bg-black/70 text-[10px] text-amber-300 font-bold border border-amber-400/30">ORIGINAL</div>
              <div class="absolute bottom-2 right-2 z-10 px-2 py-0.5 rounded bg-black/70 text-[10px] text-emerald-300 font-bold border border-emerald-400/30">VERSIÓN PRO</div>
            </div>
          `;
        }} else {{
          imageViewerHtml = `
            <div class="grid grid-cols-2 gap-1 bg-black/40 p-2 rounded-xl">
              <div class="relative">
                <img src="${{origUrl}}" alt="Original" class="w-full h-36 object-contain rounded-lg bg-black" onerror="this.src='https://placehold.co/600x600/101622/D4AF37?text=Original'">
                <span class="absolute bottom-1 left-1 px-1.5 py-0.5 rounded bg-black/70 text-[9px] text-amber-300 font-bold">Original</span>
              </div>
              <div class="relative">
                <img src="${{proUrl}}" alt="PRO" class="w-full h-36 object-contain rounded-lg bg-black" onerror="this.src='https://placehold.co/600x600/101622/A31D1D?text=PRO'">
                <span class="absolute bottom-1 left-1 px-1.5 py-0.5 rounded bg-black/70 text-[9px] text-emerald-300 font-bold">PRO</span>
              </div>
            </div>
          `;
        }}

        card.innerHTML = `
          <div class="p-3 bg-slate-900/60 border-b border-slate-800/80 flex items-center justify-between text-xs">
            <span class="font-bold text-slate-300 truncate">#${{id}} &bull; ${{item.Nombre_Archivo_Original}}</span>
            <span class="px-2 py-0.5 rounded-full text-[10px] font-bold ${{isApproved ? 'badge-ok' : 'badge-error'}} shrink-0">
              ${{isApproved ? 'APROBADO' : 'ERROR / RECHAZADO'}}
            </span>
          </div>

          <div class="p-4 flex-1 flex flex-col justify-between">
            ${{imageViewerHtml}}

            <div class="mt-3 space-y-1 text-[11px] text-slate-400">
              <div class="truncate text-slate-300"><strong class="text-slate-400">📁</strong> ${{item.Ubicacion_Categoria}}</div>
              <div class="p-2 rounded-lg bg-slate-900/80 border border-slate-800 mt-2 text-[11px] text-slate-300">
                ${{pendingChanges[id] ? pendingChanges[id].obs : item.Observaciones || 'Sin observaciones'}}
              </div>
            </div>

            <div class="mt-4 pt-3 border-t border-slate-800 flex items-center gap-2">
              <button onclick="approveQa('${{id}}')" class="flex-1 py-1.5 rounded-lg text-xs font-bold transition ${{isApproved ? 'bg-emerald-600/30 text-emerald-300 border border-emerald-500/40 cursor-default' : 'bg-emerald-600 hover:bg-emerald-500 text-white'}}">
                ✅ Aprobar
              </button>
              <button onclick="openRejectModal('${{id}}')" class="flex-1 py-1.5 rounded-lg text-xs font-bold transition ${{!isApproved ? 'bg-red-600/30 text-red-300 border border-red-500/40 cursor-default' : 'bg-red-600 hover:bg-red-500 text-white'}}">
                ❌ Marcar Mal
              </button>
            </div>
          </div>
        `;

        grid.appendChild(card);
      }});
    }}

    function renderShowcaseCards(filter = '') {{
      const grid = document.getElementById('showcaseGrid');
      grid.innerHTML = '';

      const itemsToRender = showcaseItems.filter(it => {{
        if (!filter) return true;
        const text = (it.Nombre_Foto_PRO + ' ' + it.Carpeta_Ruta_PRO).toLowerCase();
        return text.includes(filter.toLowerCase());
      }});

      itemsToRender.forEach(item => {{
        const idPro = item.ID_Foto_PRO;
        const imgUrl = idPro ? 'https://lh3.googleusercontent.com/d/' + idPro : 'https://placehold.co/400x400/101622/D4AF37?text=PRO';
        
        const card = document.createElement('div');
        card.className = 'bg-[#121927] border border-slate-800/80 rounded-xl overflow-hidden shadow hover:border-amber-500/40 transition flex flex-col';
        card.innerHTML = `
          <div class="aspect-square bg-black/60 relative overflow-hidden">
            <img src="${{imgUrl}}" alt="${{item.Nombre_Foto_PRO}}" class="w-full h-full object-cover" onerror="this.src='https://placehold.co/400x400/101622/D4AF37?text=Marinera+PRO'">
            <span class="absolute top-2 right-2 px-1.5 py-0.5 rounded bg-emerald-500/90 text-slate-950 font-bold text-[9px]">PRO</span>
          </div>
          <div class="p-2.5 flex-1 flex flex-col justify-between text-xs">
            <div>
              <p class="font-bold text-slate-200 truncate text-[11px]" title="${{item.Nombre_Foto_PRO}}">${{item.Nombre_Foto_PRO}}</p>
              <p class="text-[10px] text-slate-400 truncate mt-0.5" title="${{item.Carpeta_Ruta_PRO}}">${{item.Carpeta_Ruta_PRO.split('/').slice(-2).join('/')}}</p>
            </div>
            <a href="${{item.Link_Drive_PRO}}" target="_blank" class="mt-2 text-[10px] text-amber-400 hover:underline">Ver en Drive ↗</a>
          </div>
        `;
        grid.appendChild(card);
      }});
    }}

    function filterShowcase() {{
      const q = document.getElementById('showcaseSearch').value;
      renderShowcaseCards(q);
    }}

    function approveQa(id) {{
      pendingChanges[id] = {{ status: 'APROBADO_CATALOGO', obs: 'Aprobado formalmente en Mesa QA' }};
      renderQaCards();
    }}

    function openRejectModal(id) {{
      selectedQaId = id;
      document.getElementById('rejectModal').classList.remove('hidden');
    }}

    function closeRejectModal() {{
      selectedQaId = null;
      document.getElementById('rejectModal').classList.add('hidden');
    }}

    function confirmReject() {{
      if (!selectedQaId) return;
      const r = document.querySelector('input[name="rejectReason"]:checked');
      pendingChanges[selectedQaId] = {{
        status: 'ERROR_TEST_PROMPT',
        obs: r ? r.value : 'Rechazada en QA'
      }};
      closeRejectModal();
      renderQaCards();
    }}

    function downloadAuditJSON() {{
      const dataStr = "data:text/json;charset=utf-8," + encodeURIComponent(JSON.stringify(pendingChanges, null, 2));
      const a = document.createElement('a');
      a.setAttribute("href", dataStr);
      a.setAttribute("download", "auditoria_qa_cambios.json");
      document.body.appendChild(a);
      a.click();
      a.remove();
    }}
  </script>
</body>
</html>
"""

with open(output_dir / "dashboard_qa_catalogo.html", "w", encoding="utf-8") as f:
    f.write(html_template)

print("Dashboard maestro standalone generado con éxito.")
