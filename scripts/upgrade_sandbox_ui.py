import re
from pathlib import Path

repo_dir = Path(r"C:\Users\LENOVO\Documents\Carlitos\IA\Antigravity\Profesionalización de catálogo\Cliente Marinera Power")

for html_file in [repo_dir / "index.html", repo_dir / "docs" / "index.html"]:
    if not html_file.exists():
        continue
    content = html_file.read_text(encoding="utf-8")

    # 1. Add Batch Filter UI in view-sandbox
    old_banner = '''      <!-- BANNER EXPLICATIVO SANDBOX -->
      <div class="bg-amber-950/20 border border-amber-500/30 rounded-xl p-4 flex items-start space-x-3">
        <span class="text-xl">🧪</span>
        <div>
          <h3 class="text-sm font-bold text-amber-300">Entorno de Pruebas y Experimentos de Pipeline</h3>
          <p class="text-xs text-slate-300 mt-0.5">
            Esta mesa se alimenta directamente de la pestaña <strong class="text-amber-200">Registro_Pruebas_Sandbox</strong> en Google Sheets.
            Cada ejecución del Canary Test o prueba unitaria en Colab genera una fila nueva (append-only) para evaluar evolución sin tocar el inventario de producción.
          </p>
        </div>
      </div>

      <!-- GRID DE TARJETAS SANDBOX CON SLIDERS -->
      <div id="sandboxCardsGrid" class="grid grid-cols-1 md:grid-cols-2 gap-6">'''

    new_banner = '''      <!-- BANNER EXPLICATIVO SANDBOX -->
      <div class="bg-amber-950/20 border border-amber-500/30 rounded-xl p-4 flex items-start space-x-3">
        <span class="text-xl">🧪</span>
        <div>
          <h3 class="text-sm font-bold text-amber-300">Entorno de Pruebas y Experimentos de Pipeline</h3>
          <p class="text-xs text-slate-300 mt-0.5">
            Esta mesa se alimenta en vivo de la pestaña <a href="https://docs.google.com/spreadsheets/d/1kRsCZ7ZpPxyxrSEkUrYRl3NHahrQQche90RKK2yedQ8/edit#gid=1349722500" target="_blank" class="text-amber-300 underline font-semibold">Registro_Pruebas_Sandbox (Google Sheets)</a>.
            Cada ejecución en Colab agrega una fila de auditoría sin tocar el inventario maestro de 863 fotos de producción.
          </p>
        </div>
      </div>

      <!-- BARRA DE FILTRO POR SESIÓN / LOTE EN SANDBOX -->
      <div class="bg-[#121927] border border-slate-800 rounded-xl p-4 flex flex-col sm:flex-row gap-3 items-stretch sm:items-center justify-between">
        <div class="flex items-center space-x-2 flex-wrap gap-y-2">
          <span class="text-xs text-slate-400 font-semibold uppercase tracking-wider">Filtrar Lote:</span>
          <div id="sandboxBatchPills" class="flex flex-wrap gap-1.5">
            <!-- Píldoras de lote generadas dinámicamente -->
          </div>
        </div>
        <div class="flex items-center space-x-2 self-end sm:self-auto">
          <span class="text-xs text-slate-400">Orden:</span>
          <select id="sandboxSortSelect" onchange="setSandboxSort(this.value)" class="bg-slate-900 border border-slate-700 text-xs text-slate-200 rounded-lg px-2.5 py-1.5 focus:outline-none focus:border-amber-400">
            <option value="NEWEST" selected>Más recientes primero (Último Lote arriba)</option>
            <option value="OLDEST">Cronológico (Primer Lote arriba)</option>
            <option value="SCORE">Mayor Score QA</option>
          </select>
        </div>
      </div>

      <!-- GRID DE TARJETAS SANDBOX CON SLIDERS -->
      <div id="sandboxCardsGrid" class="grid grid-cols-1 md:grid-cols-2 gap-6">'''

    # Normalize line endings before replacing
    content_norm = content.replace("\r\n", "\n")
    old_banner_norm = old_banner.replace("\r\n", "\n")
    new_banner_norm = new_banner.replace("\r\n", "\n")

    if old_banner_norm in content_norm:
        content_norm = content_norm.replace(old_banner_norm, new_banner_norm)
        print(f"Banner replaced in {html_file.name}")
    else:
        print(f"Banner pattern not matched in {html_file.name}")

    # 2. Add JavaScript state & functions for Batch Filtering & Sorting
    js_marker = "let currentTab = 'sandbox';"
    new_js_state = """let currentTab = 'sandbox';
    let sandboxFilterBatch = 'ALL';
    let sandboxSortOrder = 'NEWEST';"""

    if js_marker in content_norm:
        content_norm = content_norm.replace(js_marker, new_js_state)

    # Replace renderSandboxCards implementation
    old_render_sb = re.search(r'function renderSandboxCards\(\)\s*\{[\s\S]*?grid\.appendChild\(card\);\s*setupCardSlider\(`sb-slider-\$\{idx\}`\);\s*\}\);\s*\}', content_norm)
    
    new_render_sb = """function renderSandboxBatchPills() {
      const container = document.getElementById('sandboxBatchPills');
      if (!container) return;
      container.innerHTML = '';

      const batches = ['ALL'];
      sandboxItems.forEach(item => {
        const b = item.Test_Batch_ID || 'DESCONOCIDO';
        if (!batches.includes(b)) batches.push(b);
      });

      batches.forEach(b => {
        const count = b === 'ALL' ? sandboxItems.length : sandboxItems.filter(i => (i.Test_Batch_ID || '') === b).length;
        const btn = document.createElement('button');
        const isActive = sandboxFilterBatch === b;
        btn.className = isActive 
          ? 'px-3 py-1 rounded-lg text-xs font-semibold bg-amber-400 text-slate-950 transition shadow-sm'
          : 'px-3 py-1 rounded-lg text-xs font-semibold bg-slate-800 text-slate-300 hover:bg-slate-700 transition';
        
        let label = b;
        if (b === 'ALL') label = `Todos los Lotes (${count})`;
        else if (b.includes('EXP')) label = `🌟 Última Corrida: ${b.replace('EXP_', '')} (${count})`;
        else if (b.includes('BATCH1')) label = `Corrida 1: BATCH1 (${count})`;
        else label = `${b} (${count})`;
        
        btn.textContent = label;
        btn.onclick = () => {
          sandboxFilterBatch = b;
          renderSandboxBatchPills();
          renderSandboxCards();
        };
        container.appendChild(btn);
      });
    }

    function setSandboxSort(order) {
      sandboxSortOrder = order;
      renderSandboxCards();
    }

    function renderSandboxCards() {
      renderSandboxBatchPills();
      const grid = document.getElementById('sandboxCardsGrid');
      if (!grid) return;
      grid.innerHTML = '';

      let items = [...sandboxItems];
      if (sandboxFilterBatch !== 'ALL') {
        items = items.filter(item => (item.Test_Batch_ID || '') === sandboxFilterBatch);
      }

      if (sandboxSortOrder === 'NEWEST') {
        items.reverse();
      } else if (sandboxSortOrder === 'SCORE') {
        items.sort((a, b) => Number(b.Score_QA_Final || 0) - Number(a.Score_QA_Final || 0));
      }

      if (items.length === 0) {
        grid.innerHTML = `
          <div class="col-span-2 p-12 text-center text-slate-500 bg-[#121927] border border-slate-800 rounded-2xl">
            <p class="text-lg">No hay pruebas registradas en este lote.</p>
          </div>
        `;
        return;
      }

      items.forEach((item, idx) => {
        const idCat = item.ID_Catalogo || item.id || '28';
        const intNum = item.Intento_Num || (idx + 1);
        const batchId = item.Test_Batch_ID || 'CANARY';
        const mode = item.Modo_Prompt || 'MODA_MODELO';
        const resVisual = item.Resultado_Visual || 'EXITO';
        const score = item.Score_QA_Final || item.score_qa || 50;
        const delta = item.Delta_E_Color || 0.0;
        const suelo = item.Score_Suelo_Pies || '100%';
        const lat = item.Latencia_Seg || 8.0;
        const obs = item.Observaciones_Tecnicas || '';

        const driveMesaId = extractDriveId(item.ID_Drive_Mesa) || extractDriveId(item.Link_Drive_Mesa) || extractDriveId(item.Vista_PRO_Test);
        const origProd = prodItems.find(p => String(p.ID) === String(idCat));
        const origId = extractDriveId(item.Vista_Original) || (origProd ? extractDriveId(origProd.ID_Archivo_Original) : '') || extractDriveId(item.orig_drive_id) || '1FbJY50m7dM-QBZ81pQfK4jRFazy3BX4m';
        const origUrl = origId ? `https://lh3.googleusercontent.com/d/${origId}=s600` : 'https://placehold.co/600x600/121927/D4AF37?text=Original';
        const proUrl = driveMesaId ? `https://lh3.googleusercontent.com/d/${driveMesaId}=s600` : (resVisual.includes('ERROR') ? 'https://placehold.co/600x600/1e293b/ef4444?text=Error+API+Gemini' : origUrl);

        let badgeClass = 'badge-ok';
        if (resVisual.includes('ALERTA')) badgeClass = 'badge-error';
        else if (resVisual.includes('ERROR')) badgeClass = 'badge-warn';

        const isLatestBatch = batchId.includes('EXP');
        const card = document.createElement('div');
        card.className = `bg-[#121927] border ${isLatestBatch ? 'border-amber-500/40' : 'border-slate-800'} rounded-2xl p-5 flex flex-col space-y-4 shadow-xl hover:border-slate-700 transition`;
        card.innerHTML = `
          <div class="flex items-center justify-between">
            <div class="flex items-center space-x-2">
              <span class="px-2 py-0.5 rounded text-[11px] font-bold bg-amber-400 text-slate-950 font-cinzel">ID #${idCat}</span>
              <span class="px-2 py-0.5 rounded text-[10px] font-mono ${isLatestBatch ? 'bg-amber-400/20 text-amber-300 border border-amber-400/40 font-bold' : 'bg-slate-800 text-slate-400'}">${batchId}</span>
              <span class="text-xs text-slate-400 font-mono">Intento #${intNum}</span>
            </div>
            <span class="px-2.5 py-0.5 rounded-full text-[11px] font-semibold ${badgeClass}">${resVisual}</span>
          </div>

          <div>
            <p class="text-xs text-slate-400 truncate">${item.Categoria_Ruta || 'Marinera Power'}</p>
            <p class="text-sm font-bold text-white truncate">${item.Nombre_Archivo_Original || 'foto'} <span class="text-xs text-amber-300 font-normal">(${mode})</span></p>
          </div>

          <!-- Interactive Slider Container -->
          <div class="compare-container" id="sb-slider-${idx}">
            <img src="${proUrl}" alt="PRO" class="compare-img">
            <div class="compare-overlay" style="width: 50%;">
              <img src="${origUrl}" alt="Original" class="compare-img" style="width: 100%; height: 100%; object-fit: contain;">
            </div>
            <div class="compare-slider-handle" style="left: 50%;">
              <svg class="w-3.5 h-3.5 text-slate-900" fill="currentColor" viewBox="0 0 20 20"><path fill-rule="evenodd" d="M10 3a1 1 0 01.707.293l3 3a1 1 0 01-1.414 1.414L11 6.414V13.586l1.293-1.293a1 1 0 011.414 1.414l-3 3a1 1 0 01-1.414 0l-3-3a1 1 0 111.414-1.414L9 13.586V6.414L7.707 7.707a1 1 0 01-1.414-1.414l3-3A1 1 0 0110 3z" clip-rule="evenodd" transform="rotate(90 10 10)"/></svg>
            </div>
            <div class="absolute bottom-2 left-2 px-2 py-0.5 rounded text-[10px] bg-slate-950/80 text-amber-300 font-mono">Original</div>
            <div class="absolute bottom-2 right-2 px-2 py-0.5 rounded text-[10px] bg-slate-950/80 text-emerald-400 font-mono">PRO Gemini</div>
          </div>

          <!-- Métricas OpenCV -->
          <div class="grid grid-cols-4 gap-2 bg-slate-900/60 p-2.5 rounded-xl border border-slate-800/80 text-center text-xs">
            <div>
              <span class="text-[10px] text-slate-500 block">Score QA</span>
              <span class="font-bold ${score >= 75 ? 'text-emerald-400' : (score > 0 ? 'text-rose-400' : 'text-slate-500')}">${score > 0 ? score + '/100' : 'N/A'}</span>
            </div>
            <div>
              <span class="text-[10px] text-slate-500 block">ΔE Color</span>
              <span class="font-bold text-slate-300">${delta}</span>
            </div>
            <div>
              <span class="text-[10px] text-slate-500 block">Piso Limpio</span>
              <span class="font-bold text-slate-300">${suelo}</span>
            </div>
            <div>
              <span class="text-[10px] text-slate-500 block">Latencia</span>
              <span class="font-bold text-indigo-400">${lat}s</span>
            </div>
          </div>

          <!-- Observaciones Técnicas -->
          <p class="text-xs text-slate-300 bg-slate-950/40 p-2.5 rounded-lg border border-slate-800/60 leading-relaxed">
            <span class="text-amber-400 font-semibold">Diagnóstico:</span> ${obs || 'Procesado correctamente.'}
          </p>

          <div class="flex items-center justify-between pt-1">
            <span class="text-[10px] text-slate-500">${item.Timestamp || ''}</span>
            <button onclick="openModalCompare('${idCat}', '${origUrl}', '${proUrl}', '${resVisual}', '${score}', '${delta}', '${item.Link_Drive_Mesa || '#' }')" class="px-3 py-1.5 rounded-lg text-xs font-semibold bg-amber-500/10 text-amber-300 hover:bg-amber-500/20 border border-amber-500/30 transition">
              Pantalla Completa
            </button>
          </div>
        `;
        grid.appendChild(card);
        setupCardSlider(`sb-slider-${idx}`);
      });
    }"""

    if old_render_sb:
        content_norm = content_norm[:old_render_sb.start()] + new_render_sb + content_norm[old_render_sb.end():]
        print(f"renderSandboxCards replaced in {html_file.name}")
    else:
        print(f"old_render_sb regex not matched in {html_file.name}")

    html_file.write_text(content_norm, encoding="utf-8")
    print(f"Saved {html_file.name} successfully!")
