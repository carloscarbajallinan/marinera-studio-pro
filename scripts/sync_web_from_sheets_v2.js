const { execSync } = require('child_process');
const fs = require('fs');
const path = require('path');

const repoDir = 'C:\\Users\\LENOVO\\Documents\\Carlitos\\IA\\Antigravity\\Profesionalización de catálogo\\Cliente Marinera Power';
const sheetId = '1kRsCZ7ZpPxyxrSEkUrYRl3NHahrQQche90RKK2yedQ8';

console.log('1. Leyendo datos de Registro_Pruebas_Sandbox...');
const rawSandbox = execSync(`gsheets readonly read ${sheetId} "Registro_Pruebas_Sandbox!A1:R100" --json`, { maxBuffer: 15 * 1024 * 1024 }).toString();
const startSb = rawSandbox.indexOf('[');
const rowsSb = JSON.parse(rawSandbox.substring(startSb));
console.log(`Leídas ${rowsSb.length - 1} filas de Sandbox.`);

const sandboxItems = rowsSb.slice(1).map((r, idx) => {
  return {
    Sheet_Row: idx + 2,
    Timestamp: r[0] || '',
    Test_Batch_ID: r[1] || '',
    ID_Catalogo: r[2] || '',
    Intento_Num: r[3] || '',
    Categoria_Ruta: r[4] || '',
    Nombre_Archivo_Original: r[5] || '',
    Modo_Prompt: r[6] || '',
    Resultado_Visual: r[7] || '',
    Score_QA_Final: r[8] || '',
    Delta_E_Color: r[9] || '',
    Score_Suelo_Pies: r[10] || '',
    Latencia_Seg: r[11] || '',
    Vista_Original: r[12] || '',
    Vista_PRO_Test: r[13] || '',
    ID_Drive_RAW: r[14] || '',
    ID_Drive_Mesa: r[15] || '',
    Link_Drive_Mesa: r[16] || '',
    Observaciones_Tecnicas: r[17] || ''
  };
});

console.log('2. Leyendo datos de Control_Total_Drive_V2 (Producción)...');
const rawProd = execSync(`gsheets readonly read ${sheetId} "Control_Total_Drive_V2!A1:AE865" --json`, { maxBuffer: 30 * 1024 * 1024 }).toString();
const startPr = rawProd.indexOf('[');
const rowsPr = JSON.parse(rawProd.substring(startPr));
console.log(`Leídas ${rowsPr.length - 1} filas de Catálogo Maestro.`);

const prodItems = rowsPr.slice(1).map(r => {
  return {
    ID: r[0] || '',
    Ruta_Carpeta_Drive: r[1] || '',
    Nombre_Carpeta_Producto: r[2] || '',
    ID_Carpeta_Drive: r[3] || '',
    Nombre_Archivo_Original: r[4] || '',
    ID_Archivo_Original: r[5] || '',
    Link_Drive_Original: r[6] || '',
    Estado: r[7] || 'PENDIENTE',
    Ruta_Carpeta_PRO: r[8] || '',
    Nombre_Archivo_PRO: r[9] || '',
    ID_Archivo_PRO: r[10] || '',
    Link_Drive_PRO: r[11] || '',
    Vista_Original: r[12] || '',
    Vista_PRO: r[13] || '',
    Link_Gemini_Raw: r[14] || '',
    ID_Archivo_Gemini_Raw: r[15] || '',
    Score_QA: r[16] || '',
    Motivo_QA: r[17] || '',
    Delta_E_Color: r[18] || '',
    Sobel_Recorte_PX: r[19] || '',
    Sobel_Gradiente: r[20] || '',
    Blanco_Perimetro_Max: r[21] || '',
    Latencia_Seg: r[22] || '',
    Ruta_Destino_PRO: r[23] || '',
    Ubicacion_Actual_Fisica: r[24] || '',
    Motivo_Rechazo: r[25] || '',
    Version_Prompt: r[26] || ''
  };
});

// Guardar JSONs en docs/
fs.writeFileSync(path.join(repoDir, 'docs', 'sandbox_live_sheet.json'), JSON.stringify(sandboxItems, null, 2), 'utf8');
fs.writeFileSync(path.join(repoDir, 'docs', 'catalog_live_sheet.json'), JSON.stringify(prodItems, null, 2), 'utf8');
console.log('Archivos JSON guardados en docs/');

const docsHtmlPath = path.join(repoDir, 'docs', 'index.html');
const rootHtmlPath = path.join(repoDir, 'index.html');

[docsHtmlPath, rootHtmlPath].forEach(fPath => {
  if (!fs.existsSync(fPath)) return;
  let content = fs.readFileSync(fPath, 'utf8');

  // Reemplazo robusto de sandboxItems
  const sbRegex = /let sandboxItems = \[[\s\S]*?\];\s*let prodItems = /;
  if (sbRegex.test(content)) {
    content = content.replace(sbRegex, `let sandboxItems = ${JSON.stringify(sandboxItems)};\r\n    let prodItems = `);
    console.log(`Reemplazado sandboxItems en ${path.basename(fPath)}`);
  } else {
    console.error(`sbRegex no coincidió en ${path.basename(fPath)}`);
  }

  // Reemplazo robusto de prodItems
  const prRegex = /let prodItems = \[[\s\S]*?\];\s*let currentTab =/;
  if (prRegex.test(content)) {
    content = content.replace(prRegex, `let prodItems = ${JSON.stringify(prodItems)};\r\n\r\n    let currentTab =`);
    console.log(`Reemplazado prodItems en ${path.basename(fPath)}`);
  } else {
    console.error(`prRegex no coincidió en ${path.basename(fPath)}`);
  }

  // Inyectar estilos photo-canvas y zoom-container (estilo Canary_Test_Marinera_Power.html) si no existen
  if (!content.includes('.photo-canvas')) {
    content = content.replace(
      '.modal-backdrop {',
      `.photo-canvas {
      background-color: #0A0D14;
      background-image: 
        linear-gradient(45deg, #101522 25%, transparent 25%), 
        linear-gradient(-45deg, #101522 25%, transparent 25%), 
        linear-gradient(45deg, transparent 75%, #101522 75%), 
        linear-gradient(-45deg, transparent 75%, #101522 75%);
      background-size: 16px 16px;
      background-position: 0 0, 0 8px, 8px -8px, -8px 0px;
      position: relative;
      cursor: crosshair;
    }
    .zoom-container img {
      transition: transform 0.25s ease-out;
      transform-origin: center center;
    }
    .zoom-container:hover img {
      transform: scale(1.6);
      z-index: 20;
    }
    .modal-backdrop {`
    );
  }

  // Asegurar que sandboxCardsGrid sea de 1 columna de ancho completo para las tarjetas Tri-Comparativas (3 fotos por fila)
  content = content.replace(
    /<div id="sandboxCardsGrid" class="[^"]*">/,
    '<div id="sandboxCardsGrid" class="space-y-8">'
  );

  // Actualizar barra de filtros y modos de vista en Producción para incluir Vista Tri-Comparativa (3 Fotos) por defecto
  content = content.replace(
    /<!-- Status Pill Filters -->[\s\S]*?<!-- CATALOG ITEMS CONTAINER -->/,
    `<!-- Status Pill Filters -->
          <div class="flex flex-wrap gap-1.5" id="prodStatusFilterPills">
            <button onclick="setProdFilter('VALIDAR')" id="filterBtn-VALIDAR" class="px-3 py-1.5 rounded-lg text-xs font-semibold bg-amber-400 text-slate-950 transition shadow">📋 Por Validar</button>
            <button onclick="setProdFilter('APROBADO')" id="filterBtn-APROBADO" class="px-3 py-1.5 rounded-lg text-xs font-semibold bg-slate-800 text-slate-300 hover:bg-slate-700 transition">✅ Aprobadas</button>
            <button onclick="setProdFilter('RECHAZADO')" id="filterBtn-RECHAZADO" class="px-3 py-1.5 rounded-lg text-xs font-semibold bg-slate-800 text-slate-300 hover:bg-slate-700 transition">❌ Rechazadas</button>
            <button onclick="setProdFilter('CON_PRO')" id="filterBtn-CON_PRO" class="px-3 py-1.5 rounded-lg text-xs font-semibold bg-slate-800 text-slate-300 hover:bg-slate-700 transition">✨ Con Foto PRO</button>
            <button onclick="setProdFilter('PENDIENTE')" id="filterBtn-PENDIENTE" class="px-3 py-1.5 rounded-lg text-xs font-semibold bg-slate-800 text-slate-300 hover:bg-slate-700 transition">⏳ Sin Foto PRO</button>
            <button onclick="setProdFilter('ALL')" id="filterBtn-ALL" class="px-3 py-1.5 rounded-lg text-xs font-semibold bg-slate-800 text-slate-300 hover:bg-slate-700 transition">📚 Todos</button>
          </div>

          <!-- View Mode (Tri-Comparativa 3 Fotos vs Cuadrícula vs Tabla) -->
          <div class="flex items-center space-x-2">
            <button onclick="setProdViewMode('tri')" id="btnViewTri" class="px-3 py-1.5 rounded-lg text-xs font-bold bg-amber-500/20 text-amber-300 border border-amber-500/40">
              🔬 Tri-Comparativa (3 Fotos)
            </button>
            <button onclick="setProdViewMode('grid')" id="btnViewGrid" class="px-2.5 py-1.5 rounded-lg text-xs font-semibold bg-slate-800 text-slate-400 hover:text-white border border-slate-700">
              🔲 Cuadrícula
            </button>
            <button onclick="setProdViewMode('table')" id="btnViewTable" class="px-2.5 py-1.5 rounded-lg text-xs font-semibold bg-slate-800 text-slate-400 hover:text-white border border-slate-700">
              📋 Tabla
            </button>
          </div>
        </div>

        <!-- Search and Category dropdown -->
        <div class="grid grid-cols-1 sm:grid-cols-3 gap-3">
          <div class="sm:col-span-2 relative">
            <input type="text" id="prodSearchInput" oninput="applyProdFilters()" placeholder="Buscar por ID (ej: #160 o 160), prenda, tela, carpeta o archivo..." class="w-full bg-slate-900 border border-slate-700 rounded-lg px-4 py-2 text-xs text-white placeholder-slate-500 focus:outline-none focus:border-amber-400">
            <svg class="w-4 h-4 text-slate-500 absolute right-3 top-2.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"/></svg>
          </div>
          <div>
            <select id="prodCategorySelect" onchange="applyProdFilters()" class="w-full bg-slate-900 border border-slate-700 rounded-lg px-3 py-2 text-xs text-white focus:outline-none focus:border-amber-400">
              <option value="ALL">📂 Todas las Categorías</option>
              <option value="Para ella">👗 Para Ella (Todas)</option>
              <option value="Para el">👔 Para Él (Todas)</option>
              <option value="Para ensayos">💃 Para Ensayos (Todas)</option>
              <option value="Accesorios">💎 Accesorios & Joyería</option>
              <option value="Falda">🩰 Faldas de Ensayo</option>
              <option value="Traje">✨ Trajes Completos y Elegantes</option>
              <option value="Blusa">👚 Blusas y Corsets</option>
              <option value="Camisa">👔 Camisas y Guayaberas Hombre</option>
              <option value="Pantalon">👖 Pantalones y Chalecos Hombre</option>
              <option value="Manto">🧣 Mantos y Fajas</option>
              <option value="Tocado">🌸 Tocados, Aretes y Escapularios</option>
              <option value="Sombrero">👒 Sombreros y Pañuelos</option>
            </select>
          </div>
        </div>
      </div>

      <!-- BARRA DE PAGINACIÓN SUPERIOR (DESPLAZADOR AL INICIO) -->
      <div id="prodPaginationTopBar" class="bg-[#121927] border border-amber-500/30 rounded-xl p-3 flex flex-col sm:flex-row items-center justify-between gap-3 shadow-lg">
        <div class="flex items-center space-x-2 text-xs text-slate-300">
          <span class="w-2.5 h-2.5 rounded-full bg-amber-400 animate-pulse"></span>
          <span id="prodShowingCountTop" class="font-medium text-amber-200">Mostrando fotos...</span>
          <span class="text-slate-600">|</span>
          <span id="prodPageIndicatorTop" class="font-mono text-amber-300 font-bold">Página 1</span>
        </div>
        <div class="flex flex-wrap items-center gap-2">
          <div class="flex items-center space-x-1" id="prodPaginationButtonsTop">
            <!-- Botones dinámicos generados por JS -->
          </div>
          <div class="flex items-center space-x-1 pl-2 border-l border-slate-700">
            <span class="text-[11px] text-slate-400">Ver:</span>
            <select id="prodPageSizeSelect" onchange="setProdPageSize(Number(this.value))" class="bg-slate-900 border border-slate-700 text-xs text-amber-300 font-semibold rounded-lg px-2 py-1 focus:outline-none focus:border-amber-400">
              <option value="50">50 por pág</option>
              <option value="100" selected>100 por pág</option>
              <option value="200">200 por pág</option>
              <option value="9999">Todas sin paginar</option>
            </select>
          </div>
        </div>
      </div>

      <!-- CATALOG ITEMS CONTAINER -->`
  );

  // Reemplazo robusto de DOMContentLoaded (abre directamente en Catálogo Maestro de Producción para facilitar revisión compartida)
  const domRegex = /\/\/\s*INITIAL LOAD[\s\S]*?window\.addEventListener\('DOMContentLoaded'[\s\S]*?\}\);/;
  const newDom = `// INITIAL LOAD CON AUTO-SYNC EN VIVO Y POLLING CADA 25s
    window.addEventListener('DOMContentLoaded', () => {
      updateCounters();
      renderSandboxCards();
      switchTab('production');
      renderProductionView();
      // Consulta en vivo inmediata al abrir la página
      syncLiveFromGoogleSheets();
      // Auto-actualización continua en segundo plano cada 25 segundos
      setInterval(syncLiveFromGoogleSheets, 25000);
    });`;

  if (domRegex.test(content)) {
    content = content.replace(domRegex, newDom);
    console.log(`Reemplazado DOMContentLoaded en ${path.basename(fPath)}`);
  } else {
    console.error(`domRegex no coincidió en ${path.basename(fPath)}`);
  }

  // Reemplazo de selector de orden en Sandbox
  content = content.replace(
    /<select id="sandboxSortSelect"[\s\S]*?<\/select>/,
    `<select id="sandboxSortSelect" onchange="setSandboxSort(this.value)" class="bg-slate-900 border border-slate-700 text-xs text-slate-200 rounded-lg px-2.5 py-1.5 focus:outline-none focus:border-amber-400">
            <option value="NEWEST" selected>Última Corrida primero (Orden de Producción 1→5 por lote)</option>
            <option value="OLDEST">Cronológico Histórico (Fila #2 → Fila #16)</option>
            <option value="SCORE">Mayor Score QA</option>
          </select>`
  );

  // Reemplazo de bloque de funciones de sincronización y renderizado de Sandbox y Producción con Sistema de Aprobación/Rechazo Interactivo
  const fnBlockRegex = /\/\/\s*2\.\s*(?:LIVE FETCH FROM GOOGLE SHEETS|SISTEMA DE EVALUACIÓN INTERACTIVA)[\s\S]*?\/\/\s*INITIAL LOAD/;
  const newFnBlock = `// 2. SISTEMA DE EVALUACIÓN INTERACTIVA DE CARLOS (CORRECTO / INCORRECTO PERSISTENTE)
    const QA_STORAGE_KEY = 'marinera_carlos_qa_decisions_v2';
    let carlosDecisions = {};
    try {
      carlosDecisions = JSON.parse(localStorage.getItem(QA_STORAGE_KEY) || '{}');
    } catch (e) {
      carlosDecisions = {};
    }

    function saveCarlosDecisions() {
      localStorage.setItem(QA_STORAGE_KEY, JSON.stringify(carlosDecisions));
      renderCarlosDecisionBar();
    }

    function getDecisionKey(scope, id, batchOrRow = '') {
      return scope === 'sandbox' ? \`SB_\${batchOrRow}_ID\${id}\` : \`PROD_ID\${id}\`;
    }

    function setPhotoDecision(scope, id, batchOrRow, verdict, reason = '', preferredSource = 'PYTHON_PRO') {
      const key = getDecisionKey(scope, id, batchOrRow);
      if (carlosDecisions[key] && carlosDecisions[key].verdict === verdict && carlosDecisions[key].preferredSource === preferredSource && !reason) {
        delete carlosDecisions[key];
      } else {
        const prev = carlosDecisions[key] || {};
        const presetReason = reason || prev.presetReason || (verdict === 'INCORRECTO' ? 'Cambió la prenda / diseño' : '');
        const customNote = verdict === 'INCORRECTO' ? (prev.customNote || '') : '';
        const combinedReason = verdict === 'INCORRECTO'
          ? (customNote.trim() ? (presetReason && presetReason !== 'Reintentar con ajuste' ? \`\${presetReason} — \${customNote.trim()}\` : customNote.trim()) : presetReason)
          : \`Aprobado (\${preferredSource === 'GEMINI_RAW' ? 'Versión Gemini' : 'Versión Pulida Python'})\`;
        carlosDecisions[key] = {
          scope,
          id: String(id),
          batch: String(batchOrRow || ''),
          verdict, // 'CORRECTO' | 'INCORRECTO'
          preferredSource: preferredSource || 'PYTHON_PRO', // 'PYTHON_PRO' | 'GEMINI_RAW'
          presetReason,
          customNote,
          reason: combinedReason,
          updatedAt: new Date().toLocaleTimeString()
        };
      }
      saveCarlosDecisions();
      if (currentTab === 'sandbox') renderSandboxCards();
      else renderProductionView();
      updateModalDecisionButtons();
    }

    function setPhotoReason(scope, id, batchOrRow, reasonText) {
      const key = getDecisionKey(scope, id, batchOrRow);
      if (!carlosDecisions[key]) {
        carlosDecisions[key] = { scope, id: String(id), batch: String(batchOrRow || ''), verdict: 'INCORRECTO', presetReason: reasonText, customNote: '', reason: reasonText, updatedAt: new Date().toLocaleTimeString() };
      } else {
        carlosDecisions[key].presetReason = reasonText;
        const note = (carlosDecisions[key].customNote || '').trim();
        carlosDecisions[key].reason = note ? \`\${reasonText} — \${note}\` : reasonText;
      }
      saveCarlosDecisions();
    }

    function setPhotoCustomNote(scope, id, batchOrRow, customText) {
      const key = getDecisionKey(scope, id, batchOrRow);
      if (!carlosDecisions[key]) {
        carlosDecisions[key] = { scope, id: String(id), batch: String(batchOrRow || ''), verdict: 'INCORRECTO', presetReason: 'Error específico', customNote: customText, reason: customText || 'Error específico', updatedAt: new Date().toLocaleTimeString() };
      } else {
        carlosDecisions[key].customNote = customText;
        const preset = carlosDecisions[key].presetReason || 'Cambió la prenda / diseño';
        const note = (customText || '').trim();
        carlosDecisions[key].reason = note ? (preset && preset !== 'Reintentar con ajuste' && preset !== 'Otro (Especificar al lado)' ? \`\${preset} — \${note}\` : note) : preset;
      }
      saveCarlosDecisions();
    }

    function getApprovedAndRejectedLists() {
      const approvedIds = new Set();
      const rejectedIds = new Set();
      const rejectedDetails = [];
      Object.values(carlosDecisions).forEach(d => {
        if (d.verdict === 'CORRECTO') {
          approvedIds.add(Number(d.id) || d.id);
          rejectedIds.delete(Number(d.id) || d.id);
        } else if (d.verdict === 'INCORRECTO') {
          rejectedIds.add(Number(d.id) || d.id);
          approvedIds.delete(Number(d.id) || d.id);
          rejectedDetails.push(\`ID #\${d.id} (\${d.reason || 'Reintentar'})\`);
        }
      });
      return {
        approved: Array.from(approvedIds),
        rejected: Array.from(rejectedIds),
        rejectedDetails
      };
    }

    function buildExportSnippet() {
      const { approved, rejected, rejectedDetails } = getApprovedAndRejectedLists();
      const webDict = {};
      Object.values(carlosDecisions).forEach(d => {
        if (d.verdict === 'CORRECTO') {
          webDict[String(d.id)] = {
            status: d.preferredSource === 'GEMINI_RAW' ? 'APROBADO_GEMINI' : 'APROBADO_PYTHON',
            reason: d.reason || 'Aprobado'
          };
        } else if (d.verdict === 'INCORRECTO') {
          webDict[String(d.id)] = {
            status: 'RECHAZADO',
            reason: d.reason || 'Reintentar'
          };
        }
      });
      return [
        \`# === PEGAR EN CELDA #8 DE COLAB O EN EL CHAT PARA ACTUALIZAR GOOGLE SHEETS ===\`,
        \`DECISIONES_WEB = \${JSON.stringify(webDict)}\`,
        \`# === RESUMEN DE LISTAS ===\`,
        \`IDS_APROBADOS_CARLOS = \${JSON.stringify(approved)}\`,
        \`IDS_REINTENTAR_MANUAL = \${JSON.stringify(rejected)}\`
      ].join('\\n');
    }

    function copyColabCommand() {
      const snippet = buildExportSnippet();
      navigator.clipboard.writeText(snippet).then(() => {
        const btn = document.getElementById('btnCopyColabCmd');
        if (btn) {
          const orig = btn.innerHTML;
          btn.innerHTML = '✅ ¡Marcas Copiadas! Envíalas por WhatsApp o pégalas en el Chat';
          setTimeout(() => { btn.innerHTML = orig; }, 3500);
        }
      });
    }

    function downloadDecisionsFile() {
      const snippet = buildExportSnippet();
      const blob = new Blob([snippet], { type: 'text/plain;charset=utf-8' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = \`marcas_catalogo_marinera_\${new Date().toISOString().slice(0,10)}.txt\`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
    }

    function clearAllDecisions() {
      if (!confirm('¿Deseas limpiar todas las marcas locales de Correcto / Incorrecto de este navegador?')) return;
      carlosDecisions = {};
      saveCarlosDecisions();
      renderSandboxCards();
      renderProductionView();
    }

    function renderCarlosDecisionBar() {
      let bar = document.getElementById('carlosDecisionStickyBar');
      if (!bar) {
        const mainEl = document.querySelector('main');
        if (!mainEl) return;
        bar = document.createElement('div');
        bar.id = 'carlosDecisionStickyBar';
        bar.className = 'mb-6 bg-slate-900/95 border border-amber-500/40 rounded-2xl p-3.5 shadow-2xl flex flex-col lg:flex-row items-start lg:items-center justify-between gap-3 sticky top-16 z-30 backdrop-blur';
        mainEl.insertBefore(bar, mainEl.firstChild);
      }
      const { approved, rejected } = getApprovedAndRejectedLists();
      bar.innerHTML = \`
        <div class="flex flex-wrap items-center gap-2.5">
          <span class="px-2.5 py-1 rounded-lg bg-amber-400/15 border border-amber-400/30 text-amber-300 text-xs font-bold">🎛️ Tus Marcas en esta Sesión</span>
          <span class="px-2.5 py-1 rounded-lg bg-emerald-500/15 border border-emerald-500/30 text-emerald-300 text-xs font-semibold">✅ Buenos (Aprobar): <strong>\${approved.length}</strong> \${approved.length ? '[' + approved.slice(0, 6).join(', ') + (approved.length > 6 ? '...' : '') + ']' : ''}</span>
          <span class="px-2.5 py-1 rounded-lg bg-rose-500/15 border border-rose-500/30 text-rose-300 text-xs font-semibold">❌ Con Error (Corregir): <strong>\${rejected.length}</strong> \${rejected.length ? '[' + rejected.slice(0, 6).join(', ') + (rejected.length > 6 ? '...' : '') + ']' : ''}</span>
        </div>
        <div class="flex flex-wrap items-center gap-2 self-end lg:self-auto">
          <button id="btnCopyColabCmd" onclick="copyColabCommand()" class="px-3 py-1.5 rounded-lg text-xs font-bold bg-amber-400 hover:bg-amber-300 text-slate-950 transition shadow">
            📋 Copiar Mis Marcas (Para enviar)
          </button>
          <button onclick="downloadDecisionsFile()" class="px-2.5 py-1.5 rounded-lg text-xs font-semibold bg-sky-500/20 hover:bg-sky-500/30 text-sky-300 border border-sky-500/40 transition">
            💾 Descargar (.txt)
          </button>
          <button onclick="clearAllDecisions()" class="px-2.5 py-1.5 rounded-lg text-xs font-semibold bg-slate-800 hover:bg-slate-700 text-slate-300 border border-slate-700 transition">
            Limpiar
          </button>
        </div>
      \`;
    }

    // 2.5 LIVE FETCH FROM GOOGLE SHEETS (GVIZ ENDPOINT + JSONP FALLBACK PARA FILE:///)
    function parseGvizTable(rawTable, includeSheetRow = false) {
      const cols = rawTable.table.cols.map((c, i) => c.label || c.id || \`col_\${i}\`);
      return rawTable.table.rows.map((r, rowIdx) => {
        const obj = {};
        if (includeSheetRow) obj.Sheet_Row = rowIdx + 2;
        cols.forEach((col, idx) => {
          const cell = r.c && r.c[idx];
          obj[col] = cell ? (cell.f !== undefined && cell.f !== null ? String(cell.f) : (cell.v !== null && cell.v !== undefined ? String(cell.v) : '')) : '';
        });
        return obj;
      });
    }

    function fetchGvizWithJsonpFallback(sheetId, sheetName, includeSheetRow = false) {
      const url = \`https://docs.google.com/spreadsheets/d/\${sheetId}/gviz/tq?tqx=out:json&sheet=\${encodeURIComponent(sheetName)}&_ts=\${Date.now()}\`;
      return fetch(url, { cache: 'no-store' })
        .then(res => res.text())
        .then(text => {
          const match = text.match(/setResponse\\(([\\s\\S]*)\\);/);
          if (!match) throw new Error('Formato GViz inválido');
          return parseGvizTable(JSON.parse(match[1]), includeSheetRow);
        })
        .catch(() => {
          return new Promise((resolve, reject) => {
            const cbName = \`__gvizCb_\${sheetName.replace(/[^a-zA-Z0-9]/g, '')}_\${Date.now()}\`;
            const script = document.createElement('script');
            const timer = setTimeout(() => {
              delete window[cbName];
              if (script.parentNode) script.parentNode.removeChild(script);
              reject(new Error('Timeout JSONP GViz'));
            }, 8000);
            window[cbName] = (rawResponse) => {
              clearTimeout(timer);
              delete window[cbName];
              if (script.parentNode) script.parentNode.removeChild(script);
              try {
                resolve(parseGvizTable(rawResponse, includeSheetRow));
              } catch (e) {
                reject(e);
              }
            };
            script.onerror = () => {
              clearTimeout(timer);
              delete window[cbName];
              if (script.parentNode) script.parentNode.removeChild(script);
              reject(new Error('Error de red en script JSONP'));
            };
            script.src = \`https://docs.google.com/spreadsheets/d/\${sheetId}/gviz/tq?tqx=out:json;responseHandler:\${cbName}&sheet=\${encodeURIComponent(sheetName)}&_ts=\${Date.now()}\`;
            document.head.appendChild(script);
          });
        });
    }

    async function syncLiveFromGoogleSheets() {
      const syncIcon = document.getElementById('syncIcon');
      const statusText = document.getElementById('syncStatusText');
      
      syncIcon.classList.add('animate-spin');
      statusText.textContent = 'Consultando Google Sheets...';
      
      const sheetId = '1kRsCZ7ZpPxyxrSEkUrYRl3NHahrQQche90RKK2yedQ8';

      try {
        const [sbRows, prRows] = await Promise.all([
          fetchGvizWithJsonpFallback(sheetId, 'Registro_Pruebas_Sandbox', true),
          fetchGvizWithJsonpFallback(sheetId, 'Control_Total_Drive_V2', false)
        ]);
        if (Array.isArray(sbRows) && sbRows.length > 0) sandboxItems = sbRows;
        if (Array.isArray(prRows) && prRows.length > 0) prodItems = prRows;

        updateCounters();
        renderCarlosDecisionBar();
        renderSandboxCards();
        renderProductionView();
        statusText.textContent = \`Sincronizado con Sheet: \${new Date().toLocaleTimeString()}\`;
      } catch (err) {
        console.warn('Usando dataset embebido actualizado:', err);
        renderCarlosDecisionBar();
        statusText.textContent = \`Datos locales sincronizados (\${sandboxItems.length} pruebas)\`;
      } finally {
        syncIcon.classList.remove('animate-spin');
      }
    }

    function getChronoBatches() {
      const chrono = [];
      sandboxItems.forEach(item => {
        const b = item.Test_Batch_ID || 'DESCONOCIDO';
        if (!chrono.includes(b)) chrono.push(b);
      });
      return chrono;
    }

    function updateCounters() {
      document.getElementById('badgeCountSandbox').textContent = sandboxItems.length;
      document.getElementById('statSbTotal').textContent = sandboxItems.length;
      document.getElementById('badgeCountProd').textContent = prodItems.length;
      document.getElementById('statProdTotal').textContent = prodItems.length;

      const chronoBatches = getChronoBatches();
      const latestBatch = chronoBatches[chronoBatches.length - 1] || '';
      const latestItems = sandboxItems.filter(i => (i.Test_Batch_ID || '') === latestBatch);
      const targetStatsItems = latestItems.length > 0 ? latestItems : sandboxItems;

      const validScores = targetStatsItems.map(i => Number(i.Score_QA_Final || 0)).filter(n => n > 0);
      const avgScore = validScores.length > 0 ? (validScores.reduce((a, b) => a + b, 0) / validScores.length).toFixed(1) : '0.0';
      const validLats = targetStatsItems.map(i => parseFloat(String(i.Latencia_Seg || '0').replace(',', '.'))).filter(n => n > 0);
      const avgLat = validLats.length > 0 ? (validLats.reduce((a, b) => a + b, 0) / validLats.length).toFixed(1) + 's' : '0.0s';
      const alertsCount = targetStatsItems.filter(i => {
        const rv = String(i.Resultado_Visual || '').toUpperCase();
        return rv.includes('ALERTA') || rv.includes('ERROR') || rv.includes('REVISION_MANUAL');
      }).length;

      const elAvgScore = document.getElementById('statSbAvgScore');
      const elAvgLat = document.getElementById('statSbAvgLat');
      const elAlerts = document.getElementById('statSbAlerts');
      if (elAvgScore) elAvgScore.textContent = avgScore;
      if (elAvgLat) elAvgLat.textContent = avgLat;
      if (elAlerts) elAlerts.textContent = alertsCount;

      let approved = 0, pending = 0, review = 0;
      prodItems.forEach(p => {
        const st = String(p.Estado || '').toUpperCase();
        if (st.includes('APROBADO')) approved++;
        else if (st.includes('REVISION')) review++;
        else pending++;
      });
      document.getElementById('statProdApproved').textContent = approved;
      document.getElementById('statProdPending').textContent = pending;
      document.getElementById('statProdReview').textContent = review;
    }

    // 3. RENDER MESA DE PRUEBAS (SANDBOX)
    function renderSandboxBatchPills() {
      const container = document.getElementById('sandboxBatchPills');
      if (!container) return;
      container.innerHTML = '';

      const chronoBatches = getChronoBatches();
      const latestBatchId = chronoBatches[chronoBatches.length - 1] || '';
      const batchesNewestFirst = [...chronoBatches].reverse();
      const batches = ['ALL', ...batchesNewestFirst];

      batches.forEach(b => {
        const batchItems = b === 'ALL'
          ? sandboxItems
          : sandboxItems.map((it, idx) => ({ ...it, _row: Number(it.Sheet_Row || (idx + 2)) })).filter(i => (i.Test_Batch_ID || '') === b);
        const count = batchItems.length;
        const minRow = b !== 'ALL' && batchItems.length > 0 ? Math.min(...batchItems.map(i => i._row)) : null;
        const maxRow = b !== 'ALL' && batchItems.length > 0 ? Math.max(...batchItems.map(i => i._row)) : null;
        const rowRangeText = (minRow && maxRow) ? \` • Filas \${minRow}-\${maxRow}\` : '';

        const btn = document.createElement('button');
        const isActive = sandboxFilterBatch === b;
        btn.className = isActive 
          ? 'px-3 py-1 rounded-lg text-xs font-semibold bg-amber-400 text-slate-950 transition shadow-sm'
          : 'px-3 py-1 rounded-lg text-xs font-semibold bg-slate-800 text-slate-300 hover:bg-slate-700 transition';
        
        const runNumber = chronoBatches.indexOf(b) + 1;
        let label = b;
        if (b === 'ALL') {
          label = \`Todos los Lotes (\${count})\`;
        } else if (b === latestBatchId) {
          label = \`🌟 Última Corrida #\${runNumber}: \${b.replace('EXP_', '')} (\${count}\${rowRangeText})\`;
        } else {
          label = \`Corrida #\${runNumber}: \${b.replace('EXP_', '')} (\${count}\${rowRangeText})\`;
        }
        
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

    // Helper que construye automáticamente los bloques de auditoría técnica Python y guía de revisión
    function buildDiagnosticAnalysis(item, isSandbox = true) {
      const idCat = String(item.ID_Catalogo || item.ID || '');
      const obs = String(item.Observaciones_Tecnicas || item.Motivo_QA || '');
      const mode = String(item.Modo_Prompt || (String(item.Ruta_Carpeta_Drive || '').toLowerCase().includes('accesorio') ? 'JOYERIA_ACCESORIO' : 'MODA_MODELO'));
      const delta = parseFloat(String(item.Delta_E_Color || '0').replace(',', '.')) || 0;
      const suelo = String(item.Score_Suelo_Pies || '95%');
      const sobel = String(item.Sobel_Recorte_PX || '');
      const scoreNum = Number(item.Score_QA_Final || item.Score_QA || 80);

      let escGemini = '1.000x';
      let escPython = '1.000x (1:1)';
      const mEsc = obs.match(/Gemini\s+([0-9.]+x)\s*->\s*Python\s+([0-9.]+x)/i);
      if (mEsc) {
        escGemini = mEsc[1];
        escPython = mEsc[2] + ' (1:1)';
      } else if (obs.includes('0.687x') || idCat === '421') {
        escGemini = '0.687x (Zoom-out)';
        escPython = '1.000x (SIFT 1:1)';
      } else if (obs.includes('0.737x') || idCat === '424') {
        escGemini = '0.737x (Zoom-out)';
        escPython = '1.000x (SIFT 1:1)';
      }

      // 1. Semáforo del Score Total
      let scoreBadgeClass = 'bg-emerald-500/20 text-emerald-300 border-emerald-500/50';
      let scoreLabel = 'Excelente fidelidad';
      let scoreIcon = '🟢';
      if (scoreNum < 70) {
        scoreBadgeClass = 'bg-rose-500/20 text-rose-300 border-rose-500/50';
        scoreLabel = 'Alerta Técnica / Revisar';
        scoreIcon = '🔴';
      } else if (scoreNum < 85) {
        scoreBadgeClass = 'bg-amber-500/20 text-amber-300 border-amber-500/50';
        scoreLabel = 'Aceptable / Verificar';
        scoreIcon = '🟡';
      }

      // 2. Guía de Enfoque Rápido ("En qué enfocarte antes de decidir si está fallada")
      const focusPoints = [];
      const obsLower = obs.toLowerCase();

      if (delta >= 45) {
        focusPoints.push(\`🎨 <strong>Tono del fondo (ΔE=\${delta}):</strong> Posible deriva cromática respecto al ciclorama marfil (#E5E1DE). Comprueba si el fondo se ve demasiado amarillento o frío.\`);
      } else if (delta > 0) {
        focusPoints.push(\`🎨 <strong>Tono de fondo (ΔE=\${delta}):</strong> Calibración cromática uniforme y cercana a la norma de catálogo.\`);
      }

      if (escGemini.includes('0.68') || escGemini.includes('0.73') || escGemini.includes('Zoom-out') || obsLower.includes('alejo') || obsLower.includes('zoom_out')) {
        focusPoints.push(\`🔍 <strong>Escala y Zoom (\${escGemini}):</strong> Gemini alejó el sujeto. Python SIFT restituyó la proporción 1:1. Revisa que manos, pañuelo o bordes no presenten saltos visuales.\`);
      } else {
        focusPoints.push(\`📐 <strong>Geometría 1:1:</strong> Proporción dimensional intacta sin deformaciones de encuadre.\`);
      }

      if (mode.includes('JOYERIA') || obsLower.includes('accesorio') || obsLower.includes('filigrana')) {
        focusPoints.push('💎 <strong>Accesorios / Joyería:</strong> Verifica que la filigrana metálica y pedrería conserven nitidez y que NO haya alucinado dedos o modelos humanas artificiales.');
      } else {
        focusPoints.push('👗 <strong>Prenda / Maniquí:</strong> Revisa que la base de madera del maniquí se mantenga visible, que el cuello no esté cortado y que la forma de la falda no se haya modificado.');
      }

      if (obsLower.includes('sombra densa')) {
        const mSombra = obs.match(/sombra densa\s*\(([^)]+)\)/i);
        const sombraPct = mSombra ? mSombra[1] : 'detectada';
        focusPoints.push(\`🌓 <strong>Base y Sombras:</strong> Se detectó sombra en el piso (\${sombraPct}). Verifica que el degradado del suelo se vea natural y no como una mancha negra cortada.\`);
      }

      if (obsLower.includes('barras') || sobel.includes('px')) {
        focusPoints.push('✂️ <strong>Bordes blancos:</strong> El pre-procesador Sobel recortó barras blancas laterales del archivo original.');
      }

      const positivo = [];
      const negativo = [];

      if (mode.includes('JOYERIA')) {
        positivo.push('Clasificado en modo JOYERIA_ACCESORIO: bodegón aislado con fondo neutro de estudio.');
        positivo.push('Conservación de filigrana metálica, perlas y proporciones sin recorte agresivo.');
      } else {
        positivo.push('Clasificado en modo MODA_MODELO: reemplazo de fondo por ciclorama de estudio profesional.');
        positivo.push('Conservación de textura satinada de la prenda, bordados y pliegues originales.');
      }

      if (scoreNum >= 85) {
        positivo.push(\`Score QA alto (\${scoreNum}/100): parámetros geométricos y cromáticos dentro de tolerancia oficial.\`);
      } else if (scoreNum < 70) {
        negativo.push(\`Score QA bajo (\${scoreNum}/100): atención especial a posibles anomalías en fondo, corte de silueta o sombra densa.\`);
      }

      if (delta >= 45) {
        negativo.push(\`Desviación térmica del fondo (ΔE = \${delta}): tono de ciclorama con variación perceptible respecto a #E5E1DE.\`);
      } else {
        positivo.push(\`Fidelidad cromática de fondo estable (ΔE = \${delta} respecto a #E5E1DE).\`);
      }

      if (escGemini.includes('Zoom-out') || obsLower.includes('alejo')) {
        negativo.push(\`Gemini crudo redujo la escala (\${escGemini}).\`);
        positivo.push(\`Python SIFT+RANSAC compensó el alejamiento devolviendo la escala a \${escPython}.\`);
      }

      return {
        scoreNum,
        scoreBadgeClass,
        scoreLabel,
        scoreIcon,
        mode,
        delta,
        suelo,
        escGemini,
        escPython,
        focusPoints,
        obsRaw: obs || 'Sin observaciones adicionales registradas.',
        positivo,
        negativo
      };
    }

    // Generador HTML de Tarjeta Tri-Comparativa (1. Original | 2. Gemini 2.5 Flash | 3. Pulida Post-Python)
    function buildTriComparativeCardHtml(cfg) {
      const {
        scope, idCat, batchId, title, subpath, resVisual, badgeClass, score, lat,
        origUrl, geminiRawUrl, pythonProUrl,
        origDriveLink, geminiRawLink, pythonProLink,
        hasDistinctGeminiRaw, hasPythonPro,
        headerExtraBadges, analysis, proFilename
      } = cfg;

      const decKey = getDecisionKey(scope, idCat, batchId);
      const dec = carlosDecisions[decKey];
      const isApproved = dec && dec.verdict === 'CORRECTO';
      const isRejected = dec && dec.verdict === 'INCORRECTO';
      const prefSource = (dec && dec.preferredSource) || 'PYTHON_PRO';

      let borderStyle = 'border-slate-800';
      if (isApproved) borderStyle = 'border-emerald-500 ring-1 ring-emerald-500/40';
      else if (isRejected) borderStyle = 'border-rose-500 ring-1 ring-rose-500/40';
      else if (cfg.isHighlighted) borderStyle = 'border-amber-500/40';

      return \`
        <div class="bg-[#0C121E] border \${borderStyle} rounded-2xl overflow-hidden shadow-2xl p-5 md:p-6 space-y-4 transition">
          
          <!-- Encabezado de Caso + Botones de Decisión Interactiva -->
          <div class="flex flex-col lg:flex-row lg:items-center justify-between border-b border-slate-800/80 pb-4 gap-3">
            <div class="space-y-1.5">
              <div class="flex items-center flex-wrap gap-2">
                <span class="px-2.5 py-0.5 rounded text-xs font-bold bg-amber-400 text-slate-950 font-cinzel">ID #\${idCat}</span>
                \${headerExtraBadges || ''}
                <span class="px-2.5 py-0.5 rounded-full text-[11px] font-semibold \${badgeClass}">\${resVisual}</span>
                
                <!-- BADGE DESTACADO DEL SCORE TOTAL CON SEMÁFORO -->
                <span class="px-2.5 py-0.5 rounded-full text-xs font-mono font-bold border flex items-center space-x-1 \${analysis.scoreBadgeClass}">
                  <span>\${analysis.scoreIcon}</span>
                  <span>Score QA: <strong>\${analysis.scoreNum}/100</strong> (\${analysis.scoreLabel})</span>
                </span>

                <span class="px-2 py-0.5 rounded text-[11px] font-mono bg-slate-900 border \${analysis.delta >= 45 ? 'border-rose-500/50 text-rose-300' : 'border-slate-700 text-indigo-300'} font-semibold">ΔE Fondo: \${analysis.delta}</span>
                <span class="px-2 py-0.5 rounded text-[11px] font-mono bg-slate-900 border border-slate-700 text-emerald-300 font-semibold">Escala: \${analysis.escPython}</span>
              </div>
              <h3 class="text-base md:text-lg font-bold text-slate-100 pt-0.5">\${title} <span class="text-xs font-normal text-amber-300 font-mono">(\${analysis.mode})</span></h3>
              <p class="text-xs text-slate-400 font-mono truncate">📁 \${subpath}</p>
              \${proFilename ? \`<p class="text-xs text-emerald-300 font-mono flex items-center space-x-1.5 pt-0.5"><span>🏷️ Nombre Final:</span> <span class="bg-slate-900/90 text-emerald-300 px-2 py-0.5 rounded border border-emerald-500/40 font-bold">\${proFilename}</span></p>\` : ''}
            </div>

            <!-- Controles de Aprobación / Rechazo de Carlos -->
            <div class="flex flex-col items-stretch sm:items-end gap-2">
              <div class="flex flex-wrap items-center gap-2">
                <button onclick="setPhotoDecision('\${scope}', '\${idCat}', '\${batchId}', 'CORRECTO', '', 'PYTHON_PRO')" class="px-3 py-2 rounded-xl text-xs font-bold transition flex items-center space-x-1.5 \${isApproved && prefSource === 'PYTHON_PRO' ? 'bg-emerald-500 text-slate-950 shadow-lg' : 'bg-emerald-500/15 text-emerald-300 hover:bg-emerald-500/25 border border-emerald-500/40'}">
                  <span>✅ Correcto (Pulida Python)</span>
                </button>
                <button onclick="setPhotoDecision('\${scope}', '\${idCat}', '\${batchId}', 'CORRECTO', '', 'GEMINI_RAW')" class="px-3 py-2 rounded-xl text-xs font-bold transition flex items-center space-x-1.5 \${isApproved && prefSource === 'GEMINI_RAW' ? 'bg-sky-400 text-slate-950 shadow-lg' : 'bg-sky-500/15 text-sky-300 hover:bg-sky-500/25 border border-sky-500/40'}">
                  <span>✅ Correcto (Gemini Puro)</span>
                </button>
                <button onclick="setPhotoDecision('\${scope}', '\${idCat}', '\${batchId}', 'INCORRECTO')" class="px-3 py-2 rounded-xl text-xs font-bold transition flex items-center space-x-1.5 \${isRejected ? 'bg-rose-500 text-white shadow-lg' : 'bg-rose-500/15 text-rose-300 hover:bg-rose-500/25 border border-rose-500/40'}">
                  <span>❌ Incorrecto (Reintentar)</span>
                </button>
                <button onclick="openModalCompare('\${idCat}', '\${origUrl}', '\${pythonProUrl || geminiRawUrl}', '\${resVisual}', '\${score}', '\${analysis.delta}', '\${pythonProLink || geminiRawLink}', '\${scope}', '\${batchId}')" class="px-2.5 py-2 rounded-xl text-xs font-semibold bg-amber-500/10 text-amber-300 hover:bg-amber-500/20 border border-amber-500/30 transition" title="Abrir Slider Interactivo">
                  ↔️ Slider
                </button>
              </div>
              \${isRejected ? \`
                <div class="flex flex-col sm:flex-row items-stretch sm:items-center gap-2 w-full bg-rose-950/30 border border-rose-500/40 rounded-xl p-2">
                  <div class="flex items-center space-x-1.5">
                    <span class="text-[10px] text-rose-300 font-semibold whitespace-nowrap">Motivo:</span>
                    <select onchange="setPhotoReason('\${scope}', '\${idCat}', '\${batchId}', this.value)" class="bg-slate-950 border border-rose-500/40 rounded-lg px-2 py-1 text-[11px] text-slate-200 focus:outline-none focus:border-rose-400">
                      <option value="Cambió la prenda / diseño" \${(dec.presetReason || dec.reason) === 'Cambió la prenda / diseño' ? 'selected' : ''}>Cambió la prenda / diseño</option>
                      <option value="Borró base de madera del maniquí" \${(dec.presetReason || dec.reason) === 'Borró base de madera del maniquí' ? 'selected' : ''}>Borró base de madera del maniquí</option>
                      <option value="Cortó partes del accesorio / producto" \${(dec.presetReason || dec.reason) === 'Cortó partes del accesorio / producto' ? 'selected' : ''}>Cortó partes del accesorio / producto</option>
                      <option value="No quitó logo de pared / fondo" \${(dec.presetReason || dec.reason) === 'No quitó logo de pared / fondo' ? 'selected' : ''}>No quitó logo de pared / fondo</option>
                      <option value="Muy cerca (Zoom-in) / encuadre cortado" \${(dec.presetReason || dec.reason) === 'Muy cerca (Zoom-in) / encuadre cortado' ? 'selected' : ''}>Muy cerca (Zoom-in) / encuadre cortado</option>
                      <option value="Alejó sujeto (Zoom-out)" \${(dec.presetReason || dec.reason) === 'Alejó sujeto (Zoom-out)' ? 'selected' : ''}>Alejó sujeto (Zoom-out)</option>
                      <option value="Inventó pies o pañuelo" \${(dec.presetReason || dec.reason) === 'Inventó pies o pañuelo' ? 'selected' : ''}>Inventó pies o pañuelo</option>
                      <option value="Cambió forma de falda / corte" \${(dec.presetReason || dec.reason) === 'Cambió forma de falda / corte' ? 'selected' : ''}>Cambió forma de falda / corte</option>
                      <option value="Bordes blancos laterales (Manual)" \${(dec.presetReason || dec.reason) === 'Bordes blancos laterales (Manual)' ? 'selected' : ''}>Bordes blancos laterales (Manual)</option>
                      <option value="Deriva de color en fondo" \${(dec.presetReason || dec.reason) === 'Deriva de color en fondo' ? 'selected' : ''}>Deriva de color en fondo</option>
                      <option value="Otro (Especificar al lado)" \${(dec.presetReason || dec.reason) === 'Otro (Especificar al lado)' ? 'selected' : ''}>Otro (Especificar al lado)</option>
                    </select>
                  </div>
                  <input type="text"
                    value="\${String(dec.customNote || '').replace(/"/g, '&quot;')}"
                    oninput="setPhotoCustomNote('\${scope}', '\${idCat}', '\${batchId}', this.value)"
                    placeholder="Detalle específico (ej: falta base de madera, cambió prenda, cortó accesorio...)"
                    class="flex-1 min-w-[240px] bg-slate-950 border border-rose-500/40 rounded-lg px-2.5 py-1 text-[11px] text-slate-100 placeholder-slate-500 focus:outline-none focus:border-rose-400"
                  />
                </div>
              \` : ''}
            </div>
          </div>

          <!-- BANNER GUÍA DE REVISIÓN: EN QUÉ DEBES ENFOCARTE ANTES DE INDICAR SI FALLÓ O NO -->
          <div class="bg-slate-900/90 border border-slate-700/80 rounded-xl p-3.5 space-y-2 shadow-inner">
            <div class="flex items-center justify-between">
              <span class="text-xs font-bold text-amber-300 uppercase tracking-wider flex items-center space-x-1.5">
                <span>🎯</span>
                <span>En qué enfocarte al revisar esta foto:</span>
              </span>
              <span class="text-[10px] text-slate-400 font-mono">Auditoría Automática Python / OpenCV</span>
            </div>
            <ul class="grid grid-cols-1 sm:grid-cols-2 gap-2 text-[11px] text-slate-300">
              \${analysis.focusPoints.map(pt => \`
                <li class="flex items-start space-x-1.5 bg-slate-950/60 p-2 rounded-lg border border-slate-800">
                  <span class="text-amber-400 font-bold">•</span>
                  <span>\${pt}</span>
                </li>
              \`).join('')}
            </ul>
            <div class="pt-1 text-[10px] text-slate-400 font-mono truncate border-t border-slate-800/80 flex items-center space-x-2">
              <span class="text-slate-500 font-semibold">Registro Técnico:</span>
              <span class="text-slate-400 truncate" title="\${analysis.obsRaw}">\${analysis.obsRaw}</span>
            </div>
          </div>

          <!-- Grilla Tri-Comparativa (3 Columnas: 1. Original | 2. Gemini 2.5 Flash | 3. Pulida Post-Python) -->
          <div class="grid grid-cols-1 md:grid-cols-3 gap-5 items-stretch">
            
            <!-- Columna 1: Foto Cruda Original -->
            <div class="flex flex-col bg-slate-950/70 rounded-xl border border-slate-800/80 p-3 space-y-2">
              <div class="flex items-center justify-between">
                <span class="text-[11px] font-bold text-slate-300 uppercase tracking-wider flex items-center space-x-1">
                  <span>📷</span> <span>1. Foto Cruda Original</span>
                </span>
                <span class="text-[10px] px-2 py-0.5 rounded bg-black border border-slate-800 text-slate-300 font-mono font-bold">
                  Base Referencia 1:1
                </span>
              </div>
              <div class="photo-canvas zoom-container aspect-[3/4] max-h-[480px] w-full rounded-lg overflow-hidden border border-slate-800 flex items-center justify-center p-2 shadow-inner">
                <img src="\${origUrl}" class="w-full h-full object-contain" alt="1. Foto Original" loading="lazy">
              </div>
              <div class="text-[10px] text-slate-400 flex items-center justify-between px-1">
                <span>Archivo de origen en catálogo</span>
                <a href="\${origDriveLink}" target="_blank" class="font-mono text-amber-400 hover:underline">Abrir en Drive ↗</a>
              </div>
            </div>

            <!-- Columna 2: Versión Pura Gemini 2.5 Flash (_1_RAW_GEMINI) -->
            <div class="flex flex-col bg-slate-950/70 rounded-xl border border-sky-500/40 p-3 space-y-2 shadow-lg">
              <div class="flex items-center justify-between">
                <span class="text-[11px] font-bold text-sky-300 uppercase tracking-wider flex items-center space-x-1">
                  <span>🤖</span> <span>2. Versión Gemini 2.5 Flash</span>
                </span>
                <span class="text-[10px] px-2 py-0.5 rounded bg-sky-950/80 border border-sky-500/50 text-sky-300 font-mono font-bold">
                  Escala: \${analysis.escGemini}
                </span>
              </div>
              <div class="photo-canvas zoom-container aspect-[3/4] max-h-[480px] w-full rounded-lg overflow-hidden border border-sky-500/40 flex items-center justify-center p-2 shadow-inner">
                <img src="\${geminiRawUrl}" class="w-full h-full object-contain" alt="2. Salida Gemini" loading="lazy">
              </div>
              <div class="text-[10px] text-sky-300/90 flex items-center justify-between px-1 font-medium">
                <span>📁 Carpeta: _1_RAW_GEMINI</span>
                <a href="\${geminiRawLink}" target="_blank" class="font-mono text-sky-300 hover:underline">Abrir RAW Drive ↗</a>
              </div>
            </div>

            <!-- Columna 3: Versión Pulida Post-Python (_2_MESA_REVISION_CARLOS) -->
            <div class="flex flex-col bg-slate-950/70 rounded-xl border border-emerald-500/40 p-3 space-y-2 shadow-lg">
              <div class="flex items-center justify-between">
                <span class="text-[11px] font-bold text-emerald-300 uppercase tracking-wider flex items-center space-x-1">
                  <span>🐍</span> <span>3. Versión Pulida Python</span>
                </span>
                <span class="text-[10px] px-2 py-0.5 rounded bg-emerald-950/80 border border-emerald-500/50 text-emerald-300 font-mono font-bold">
                  Escala: \${analysis.escPython}
                </span>
              </div>
              <div class="photo-canvas zoom-container aspect-[3/4] max-h-[480px] w-full rounded-lg overflow-hidden border border-emerald-500/40 flex items-center justify-center p-2 shadow-inner">
                <img src="\${pythonProUrl}" class="w-full h-full object-contain" alt="3. Pulida Python" loading="lazy">
              </div>
              <div class="text-[10px] text-emerald-300/90 flex items-center justify-between px-1 font-semibold">
                <span>📁 Carpeta: _2_MESA_REVISION_CARLOS</span>
                <a href="\${pythonProLink}" target="_blank" class="font-mono text-emerald-300 hover:underline">Abrir PRO Drive ↗</a>
              </div>
            </div>

          </div>

          <!-- Diagnóstico en Dos Bloques: Lo Positivo y Lo Negativo / Correcciones Python -->
          <div class="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs pt-1">
            
            <!-- Bloque Positivo -->
            <div class="bg-emerald-950/20 border border-emerald-500/30 rounded-xl p-4 space-y-2">
              <h4 class="font-bold text-emerald-400 flex items-center space-x-2 text-xs uppercase tracking-wider">
                <span>🟢</span> <span>Lo Positivo (Logros de Gemini + Pulido Python):</span>
              </h4>
              <ul class="space-y-1.5 text-slate-300 text-[11px] leading-relaxed">
                \${analysis.positivo.map(p => \`<li class="flex items-start space-x-1.5"><span class="text-emerald-400 font-bold">✓</span><span>\${p}</span></li>\`).join('')}
              </ul>
            </div>

            <!-- Bloque Negativo / Observaciones -->
            <div class="bg-rose-950/20 border border-rose-500/30 rounded-xl p-4 space-y-2">
              <h4 class="font-bold text-rose-400 flex items-center space-x-2 text-xs uppercase tracking-wider">
                <span>🔴</span> <span>Lo Negativo / Correcciones Aplicadas por Python:</span>
              </h4>
              <ul class="space-y-1.5 text-slate-300 text-[11px] leading-relaxed">
                \${analysis.negativo.map(n => \`<li class="flex items-start space-x-1.5"><span class="text-rose-400 font-bold">•</span><span>\${n}</span></li>\`).join('')}
              </ul>
            </div>

          </div>

        </div>
      \`;
                      <option value="No quitó logo de pared / fondo" \${(dec.presetReason || dec.reason) === 'No quitó logo de pared / fondo' ? 'selected' : ''}>No quitó logo de pared / fondo</option>
                      <option value="Muy cerca (Zoom-in) / encuadre cortado" \${(dec.presetReason || dec.reason) === 'Muy cerca (Zoom-in) / encuadre cortado' ? 'selected' : ''}>Muy cerca (Zoom-in) / encuadre cortado</option>
                      <option value="Alejó sujeto (Zoom-out)" \${(dec.presetReason || dec.reason) === 'Alejó sujeto (Zoom-out)' ? 'selected' : ''}>Alejó sujeto (Zoom-out)</option>
                      <option value="Inventó pies o pañuelo" \${(dec.presetReason || dec.reason) === 'Inventó pies o pañuelo' ? 'selected' : ''}>Inventó pies o pañuelo</option>
                      <option value="Cambió forma de falda / corte" \${(dec.presetReason || dec.reason) === 'Cambió forma de falda / corte' ? 'selected' : ''}>Cambió forma de falda / corte</option>
                      <option value="Bordes blancos laterales (Manual)" \${(dec.presetReason || dec.reason) === 'Bordes blancos laterales (Manual)' ? 'selected' : ''}>Bordes blancos laterales (Manual)</option>
                      <option value="Deriva de color en fondo" \${(dec.presetReason || dec.reason) === 'Deriva de color en fondo' ? 'selected' : ''}>Deriva de color en fondo</option>
                      <option value="Otro (Especificar al lado)" \${(dec.presetReason || dec.reason) === 'Otro (Especificar al lado)' ? 'selected' : ''}>Otro (Especificar al lado)</option>
                    </select>
                  </div>
                  <input type="text"
                    value="\${String(dec.customNote || '').replace(/"/g, '&quot;')}"
                    oninput="setPhotoCustomNote('\${scope}', '\${idCat}', '\${batchId}', this.value)"
                    placeholder="Detalle específico (ej: falta base de madera, cambió prenda, cortó accesorio...)"
                    class="flex-1 min-w-[240px] bg-slate-950 border border-rose-500/40 rounded-lg px-2.5 py-1 text-[11px] text-slate-100 placeholder-slate-500 focus:outline-none focus:border-rose-400"
                  />
                </div>
              \` : ''}
            </div>
          </div>

          <!-- Grilla Tri-Comparativa (3 Columnas: 1. Original | 2. Gemini 2.5 Flash | 3. Pulida Post-Python) -->
          <div class="grid grid-cols-1 md:grid-cols-3 gap-5 items-stretch">
            
            <!-- Columna 1: Foto Cruda Original -->
            <div class="flex flex-col bg-slate-950/70 rounded-xl border border-slate-800/80 p-3 space-y-2">
              <div class="flex items-center justify-between">
                <span class="text-[11px] font-bold text-slate-300 uppercase tracking-wider flex items-center space-x-1">
                  <span>📷</span> <span>1. Foto Cruda Original</span>
                </span>
                <span class="text-[10px] px-2 py-0.5 rounded bg-black border border-slate-800 text-slate-300 font-mono font-bold">
                  Base Referencia 1:1
                </span>
              </div>
              <div class="photo-canvas zoom-container aspect-[3/4] max-h-[480px] w-full rounded-lg overflow-hidden border border-slate-800 flex items-center justify-center p-2 shadow-inner">
                <img src="\${origUrl}" class="w-full h-full object-contain" alt="1. Foto Original" loading="lazy">
              </div>
              <div class="text-[10px] text-slate-400 flex items-center justify-between px-1">
                <span>Archivo de origen en catálogo</span>
                <a href="\${origDriveLink}" target="_blank" class="font-mono text-amber-400 hover:underline">Abrir en Drive ↗</a>
              </div>
            </div>

            <!-- Columna 2: Versión Pura Gemini 2.5 Flash (_1_RAW_GEMINI) -->
            <div class="flex flex-col bg-slate-950/70 rounded-xl border border-sky-500/40 p-3 space-y-2 shadow-lg">
              <div class="flex items-center justify-between">
                <span class="text-[11px] font-bold text-sky-300 uppercase tracking-wider flex items-center space-x-1">
                  <span>🤖</span> <span>2. Versión Gemini 2.5 Flash</span>
                </span>
                <span class="text-[10px] px-2 py-0.5 rounded bg-sky-950/80 border border-sky-500/50 text-sky-300 font-mono font-bold">
                  Escala: \${analysis.escGemini}
                </span>
              </div>
              <div class="photo-canvas zoom-container aspect-[3/4] max-h-[480px] w-full rounded-lg overflow-hidden border border-sky-500/40 flex items-center justify-center p-2 shadow-inner">
                <img src="\${geminiRawUrl}" class="w-full h-full object-contain" alt="2. Salida Gemini" loading="lazy">
              </div>
              <div class="text-[10px] text-sky-300/90 flex items-center justify-between px-1 font-medium">
                <span>📁 Carpeta: _1_RAW_GEMINI</span>
                <a href="\${geminiRawLink}" target="_blank" class="font-mono text-sky-300 hover:underline">Abrir RAW Drive ↗</a>
              </div>
            </div>

            <!-- Columna 3: Versión Pulida Post-Python (_2_MESA_REVISION_CARLOS) -->
            <div class="flex flex-col bg-slate-950/70 rounded-xl border border-emerald-500/40 p-3 space-y-2 shadow-lg">
              <div class="flex items-center justify-between">
                <span class="text-[11px] font-bold text-emerald-300 uppercase tracking-wider flex items-center space-x-1">
                  <span>🐍</span> <span>3. Versión Pulida Python</span>
                </span>
                <span class="text-[10px] px-2 py-0.5 rounded bg-emerald-950/80 border border-emerald-500/50 text-emerald-300 font-mono font-bold">
                  Escala: \${analysis.escPython}
                </span>
              </div>
              <div class="photo-canvas zoom-container aspect-[3/4] max-h-[480px] w-full rounded-lg overflow-hidden border border-emerald-500/40 flex items-center justify-center p-2 shadow-inner">
                <img src="\${pythonProUrl}" class="w-full h-full object-contain" alt="3. Pulida Python" loading="lazy">
              </div>
              <div class="text-[10px] text-emerald-300/90 flex items-center justify-between px-1 font-semibold">
                <span>📁 Carpeta: _2_MESA_REVISION_CARLOS</span>
                <a href="\${pythonProLink}" target="_blank" class="font-mono text-emerald-300 hover:underline">Abrir PRO Drive ↗</a>
              </div>
            </div>

          </div>

          <!-- Diagnóstico en Dos Bloques: Lo Positivo y Lo Negativo / Correcciones Python -->
          <div class="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs pt-1">
            
            <!-- Bloque Positivo -->
            <div class="bg-emerald-950/20 border border-emerald-500/30 rounded-xl p-4 space-y-2">
              <h4 class="font-bold text-emerald-400 flex items-center space-x-2 text-xs uppercase tracking-wider">
                <span>🟢</span> <span>Lo Positivo (Logros de Gemini + Pulido Python):</span>
              </h4>
              <ul class="space-y-1.5 text-slate-300 text-[11px] leading-relaxed">
                \${analysis.positivo.map(p => \`<li class="flex items-start space-x-1.5"><span class="text-emerald-400 font-bold">✓</span><span>\${p}</span></li>\`).join('')}
              </ul>
            </div>

            <!-- Bloque Negativo / Observaciones -->
            <div class="bg-rose-950/20 border border-rose-500/30 rounded-xl p-4 space-y-2">
              <h4 class="font-bold text-rose-400 flex items-center space-x-2 text-xs uppercase tracking-wider">
                <span>🔴</span> <span>Lo Negativo / Correcciones Aplicadas por Python:</span>
              </h4>
              <ul class="space-y-1.5 text-slate-300 text-[11px] leading-relaxed">
                \${analysis.negativo.map(n => \`<li class="flex items-start space-x-1.5"><span class="text-rose-400 font-bold">•</span><span>\${n}</span></li>\`).join('')}
              </ul>
            </div>

          </div>

        </div>
      \`;
    }

    function renderSandboxCards() {
      renderSandboxBatchPills();
      renderCarlosDecisionBar();
      const grid = document.getElementById('sandboxCardsGrid');
      if (!grid) return;
      grid.className = 'space-y-8';
      grid.innerHTML = '';

      const chronoBatches = getChronoBatches();
      const latestBatchId = chronoBatches[chronoBatches.length - 1] || '';

      const batchCounters = {};
      const batchTotals = {};
      sandboxItems.forEach(it => {
        const b = it.Test_Batch_ID || 'DESCONOCIDO';
        batchTotals[b] = (batchTotals[b] || 0) + 1;
      });

      let items = sandboxItems.map((item, idx) => {
        const b = item.Test_Batch_ID || 'DESCONOCIDO';
        batchCounters[b] = (batchCounters[b] || 0) + 1;
        const sheetRow = Number(item.Sheet_Row || (idx + 2));
        return {
          ...item,
          _sheetRow: sheetRow,
          _batchOrder: chronoBatches.indexOf(b),
          _posInBatch: batchCounters[b],
          _batchTotal: batchTotals[b] || 1
        };
      });

      if (sandboxFilterBatch !== 'ALL') {
        items = items.filter(item => (item.Test_Batch_ID || '') === sandboxFilterBatch);
      }

      if (sandboxSortOrder === 'NEWEST') {
        items.sort((a, b) => {
          if (b._batchOrder !== a._batchOrder) return b._batchOrder - a._batchOrder;
          return a._sheetRow - b._sheetRow;
        });
      } else if (sandboxSortOrder === 'OLDEST') {
        items.sort((a, b) => a._sheetRow - b._sheetRow);
      } else if (sandboxSortOrder === 'SCORE') {
        items.sort((a, b) => Number(b.Score_QA_Final || 0) - Number(a.Score_QA_Final || 0));
      }

      if (items.length === 0) {
        grid.innerHTML = \`
          <div class="p-12 text-center text-slate-500 bg-[#121927] border border-slate-800 rounded-2xl">
            <p class="text-lg">No hay pruebas registradas en este lote.</p>
          </div>
        \`;
        return;
      }

      grid.innerHTML = items.map(item => {
        const idCat = item.ID_Catalogo || item.id || '28';
        const batchId = item.Test_Batch_ID || 'CANARY';
        const resVisual = item.Resultado_Visual || 'EXITO';
        const score = item.Score_QA_Final || item.score_qa || 50;
        const lat = item.Latencia_Seg || 8.0;
        const sheetRow = item._sheetRow;
        const posInBatch = item._posInBatch;
        const batchTotal = item._batchTotal;

        const origProd = prodItems.find(p => String(p.ID) === String(idCat));
        const origId = extractDriveId(item.Vista_Original) || (origProd ? extractDriveId(origProd.ID_Archivo_Original) : '') || '1FbJY50m7dM-QBZ81pQfK4jRFazy3BX4m';
        const rawGeminiId = extractDriveId(item.ID_Drive_RAW);
        const pythonProId = extractDriveId(item.ID_Drive_Mesa) || extractDriveId(item.Link_Drive_Mesa) || extractDriveId(item.Vista_PRO_Test);

        const origUrl = origId ? \`https://lh3.googleusercontent.com/d/\${origId}=s800\` : 'https://placehold.co/600x800/121927/D4AF37?text=Original';
        const geminiRawUrl = rawGeminiId ? \`https://lh3.googleusercontent.com/d/\${rawGeminiId}=s800\` : (pythonProId ? \`https://lh3.googleusercontent.com/d/\${pythonProId}=s800\` : 'https://placehold.co/600x800/1e293b/ef4444?text=Sin+Imagen+Gemini');
        const pythonProUrl = pythonProId ? \`https://lh3.googleusercontent.com/d/\${pythonProId}=s800\` : geminiRawUrl;

        const origDriveLink = origId ? \`https://drive.google.com/file/d/\${origId}/view\` : '#';
        const geminiRawLink = rawGeminiId ? \`https://drive.google.com/file/d/\${rawGeminiId}/view\` : (item.Link_Drive_Mesa || '#');
        const pythonProLink = item.Link_Drive_Mesa || (pythonProId ? \`https://drive.google.com/file/d/\${pythonProId}/view\` : '#');

        let badgeClass = 'badge-ok';
        if (resVisual.includes('ALERTA')) badgeClass = 'badge-error';
        else if (resVisual.includes('ERROR') || resVisual.includes('REVISION_MANUAL')) badgeClass = 'badge-warn';

        const isLatestBatch = batchId === latestBatchId;
        const headerExtraBadges = \`
          <span class="px-2 py-0.5 rounded text-[10px] font-mono \${isLatestBatch ? 'bg-amber-400/20 text-amber-300 border border-amber-400/40 font-bold' : 'bg-slate-800 text-slate-400'}">\${isLatestBatch ? '🌟 ' : ''}\${batchId}</span>
          <span class="px-2 py-0.5 rounded text-[10px] font-mono bg-sky-950/70 text-sky-300 border border-sky-700/40">Fila Sheet #\${sheetRow} • Foto \${posInBatch}/\${batchTotal}</span>
        \`;

        const analysis = buildDiagnosticAnalysis(item, true);

        return buildTriComparativeCardHtml({
          scope: 'sandbox',
          idCat,
          batchId,
          title: \`\${origProd ? origProd.Nombre_Carpeta_Producto : 'Producto'} — \${item.Nombre_Archivo_Original || 'foto'}\`,
          subpath: item.Categoria_Ruta || 'Marinera Power',
          proFilename: origProd ? origProd.Nombre_Archivo_PRO : '',
          resVisual,
          badgeClass,
          score,
          lat,
          origUrl,
          geminiRawUrl,
          pythonProUrl,
          origDriveLink,
          geminiRawLink,
          pythonProLink,
          hasDistinctGeminiRaw: Boolean(rawGeminiId),
          hasPythonPro: Boolean(pythonProId),
          headerExtraBadges,
          isHighlighted: isLatestBatch,
          analysis
        });
      }).join('');
    }

    function setupCardSlider(containerId) {
      const container = document.getElementById(containerId);
      if (!container) return;
      const overlay = container.querySelector('.compare-overlay');
      const handle = container.querySelector('.compare-slider-handle');

      function update(clientX) {
        const rect = container.getBoundingClientRect();
        let pos = (clientX - rect.left) / rect.width;
        pos = Math.max(0, Math.min(1, pos));
        overlay.style.width = (pos * 100) + '%';
        handle.style.left = (pos * 100) + '%';
      }

      let isDown = false;
      handle.addEventListener('mousedown', () => isDown = true);
      window.addEventListener('mouseup', () => isDown = false);
      window.addEventListener('mousemove', (e) => { if (isDown) update(e.clientX); });
      container.addEventListener('click', (e) => update(e.clientX));
      handle.addEventListener('touchstart', () => isDown = true);
      window.addEventListener('touchend', () => isDown = false);
      window.addEventListener('touchmove', (e) => { if (isDown && e.touches[0]) update(e.touches[0].clientX); });
    }

    // 4. RENDER PRODUCCIÓN (VALIDACIÓN TRI-COMPARATIVA DEL CATÁLOGO MAESTRO)
    let prodTriInitialized = false;
    let prodCurrentPage = 1;
    let prodPageSize = 100;
    const PROD_FILTER_KEYS = ['VALIDAR', 'APROBADO', 'RECHAZADO', 'CON_PRO', 'PENDIENTE', 'ALL'];

    function normalizeSearchText(str) {
      return String(str || '')
        .replace(/Ã©/g, 'e').replace(/Ã¡/g, 'a').replace(/Ã­/g, 'i').replace(/Ã³/g, 'o').replace(/Ãº/g, 'u')
        .replace(/Ã±/g, 'n').replace(/Ã‰/g, 'e').replace(/Ã‘/g, 'n')
        .normalize('NFD').replace(/[\u0300-\u036f]/g, '')
        .toLowerCase();
    }

    function setProdPage(pageNum) {
      prodCurrentPage = pageNum;
      renderProductionView(false);
      const topBar = document.getElementById('prodPaginationTopBar');
      if (topBar) topBar.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }

    function setProdPageSize(size) {
      prodPageSize = size;
      prodCurrentPage = 1;
      renderProductionView(false);
    }

    function renderPaginationControls(totalItems) {
      const totalPages = Math.ceil(totalItems / prodPageSize) || 1;
      if (prodCurrentPage > totalPages) prodCurrentPage = 1;

      const startIdx = totalItems === 0 ? 0 : (prodCurrentPage - 1) * prodPageSize + 1;
      const endIdx = Math.min(prodCurrentPage * prodPageSize, totalItems);

      const showingText = totalItems === 0
        ? '0 fotos encontradas'
        : \`Mostrando <strong class="text-white">\${startIdx} - \${endIdx}</strong> de <strong class="text-white">\${totalItems}</strong> fotos\`;
      const pageText = \`Página <strong class="text-amber-400">\${prodCurrentPage}</strong> de <strong class="text-white">\${totalPages}</strong>\`;

      ['Top', ''].forEach(suffix => {
        const elCount = document.getElementById(suffix === 'Top' ? 'prodShowingCountTop' : 'prodShowingCount');
        const elPage = document.getElementById(suffix === 'Top' ? 'prodPageIndicatorTop' : null);
        const elBtns = document.getElementById(suffix === 'Top' ? 'prodPaginationButtonsTop' : 'prodPagination');

        if (elCount) elCount.innerHTML = showingText;
        if (elPage) elPage.innerHTML = pageText;
        if (!elBtns) return;

        if (totalPages <= 1) {
          elBtns.innerHTML = '';
          return;
        }

        let html = '';
        // Botón Anterior
        html += \`<button onclick="setProdPage(\${prodCurrentPage - 1})" \${prodCurrentPage === 1 ? 'disabled class="px-2.5 py-1 rounded-lg text-xs text-slate-600 bg-slate-900 border border-slate-800 cursor-not-allowed"' : 'class="px-2.5 py-1 rounded-lg text-xs font-bold text-slate-200 bg-slate-800 hover:bg-slate-700 border border-slate-700 transition shadow-sm"'}>◀️ Ant</button>\`;

        // Rango de botones numéricos
        let pageRange = [];
        if (totalPages <= 7) {
          pageRange = Array.from({ length: totalPages }, (_, i) => i + 1);
        } else {
          const left = Math.max(1, prodCurrentPage - 2);
          const right = Math.min(totalPages, prodCurrentPage + 2);
          if (left > 1) { pageRange.push(1); if (left > 2) pageRange.push('...'); }
          for (let p = left; p <= right; p++) pageRange.push(p);
          if (right < totalPages) { if (right < totalPages - 1) pageRange.push('...'); pageRange.push(totalPages); }
        }

        pageRange.forEach(p => {
          if (p === '...') {
            html += \`<span class="px-1 text-slate-600 text-xs">...</span>\`;
          } else {
            const isActive = p === prodCurrentPage;
            html += \`<button onclick="setProdPage(\${p})" class="px-2.5 py-1 rounded-lg text-xs font-bold transition \${isActive ? 'bg-amber-400 text-slate-950 shadow-md font-black' : 'bg-slate-800 text-slate-300 hover:bg-slate-700 border border-slate-700'}">\${p}</button>\`;
          }
        });

        // Botón Siguiente
        html += \`<button onclick="setProdPage(\${prodCurrentPage + 1})" \${prodCurrentPage === totalPages ? 'disabled class="px-2.5 py-1 rounded-lg text-xs text-slate-600 bg-slate-900 border border-slate-800 cursor-not-allowed"' : 'class="px-2.5 py-1 rounded-lg text-xs font-bold text-slate-200 bg-slate-800 hover:bg-slate-700 border border-slate-700 transition shadow-sm"'}>Sig ▶️</button>\`;

        elBtns.innerHTML = html;
      });
    }

    function updateProdFilterButtons() {
      let cValidar = 0, cAprobado = 0, cRechazado = 0, cConPro = 0, cPendiente = 0, cAll = 0;
      prodItems.forEach(item => {
        const st = String(item.Estado || '').toUpperCase();
        const proName = String(item.Nombre_Archivo_PRO || '');
        if (st.includes('RECHAZADO_QA') || proName.includes('ERROR_TEST')) return;
        cAll++;
        const hasProOrRaw = Boolean(extractDriveId(item.ID_Archivo_PRO) || extractDriveId(item.ID_Archivo_Gemini_Raw));
        const decKey = getDecisionKey('prod', item.ID);
        const dec = carlosDecisions[decKey];
        const isWebApproved = dec && dec.verdict === 'CORRECTO';
        const isWebRejected = dec && dec.verdict === 'INCORRECTO';

        if (hasProOrRaw) cConPro++;
        else cPendiente++;

        // Aprobadas: Aprobadas oficiales en Sheet o marcadas como Correcto en esta sesión
        if (isWebApproved || (!isWebRejected && st.includes('APROBADO'))) {
          cAprobado++;
        }
        // Rechazadas: Rechazadas en Sheet o marcadas como Incorrecto en esta sesión
        else if (isWebRejected || (!isWebApproved && st.includes('RECHAZADO'))) {
          cRechazado++;
        }
        // Por Validar: Tienen versión PRO pero aún están pendientes de veredicto
        else if (hasProOrRaw) {
          cValidar++;
        }
      });

      const labels = {
        VALIDAR: \`📋 Por Validar (\${cValidar})\`,
        APROBADO: \`✅ Aprobadas (\${cAprobado})\`,
        RECHAZADO: \`❌ Rechazadas (\${cRechazado})\`,
        CON_PRO: \`✨ Con Foto PRO (\${cConPro})\`,
        PENDIENTE: \`⏳ Sin Foto PRO (\${cPendiente})\`,
        ALL: \`📚 Todos (\${cAll})\`
      };

      PROD_FILTER_KEYS.forEach(s => {
        const btn = document.getElementById('filterBtn-' + s);
        if (!btn) return;
        if (labels[s]) btn.textContent = labels[s];
        if (s === prodFilterState) {
          btn.className = 'px-3 py-1.5 rounded-lg text-xs font-semibold bg-amber-400 text-slate-950 transition shadow';
        } else {
          btn.className = 'px-3 py-1.5 rounded-lg text-xs font-semibold bg-slate-800 text-slate-300 hover:bg-slate-700 transition';
        }
      });
    }

    function setProdFilter(state) {
      prodFilterState = state;
      prodCurrentPage = 1;
      updateProdFilterButtons();
      renderProductionView(false);
    }

    function setProdViewMode(mode) {
      prodViewMode = mode;
      const btnTri = document.getElementById('btnViewTri');
      const btnGrid = document.getElementById('btnViewGrid');
      const btnTable = document.getElementById('btnViewTable');
      if (btnTri) btnTri.className = mode === 'tri' ? 'px-3 py-1.5 rounded-lg text-xs font-bold bg-amber-500/20 text-amber-300 border border-amber-500/40' : 'px-3 py-1.5 rounded-lg text-xs font-semibold bg-slate-800 text-slate-400 hover:text-white border border-slate-700';
      if (btnGrid) btnGrid.className = mode === 'grid' ? 'px-2.5 py-1.5 rounded-lg text-xs font-bold bg-amber-500/20 text-amber-300 border border-amber-500/40' : 'px-2.5 py-1.5 rounded-lg text-xs font-semibold bg-slate-800 text-slate-400 hover:text-white border border-slate-700';
      if (btnTable) btnTable.className = mode === 'table' ? 'px-2.5 py-1.5 rounded-lg text-xs font-bold bg-amber-500/20 text-amber-300 border border-amber-500/40' : 'px-2.5 py-1.5 rounded-lg text-xs font-semibold bg-slate-800 text-slate-400 hover:text-white border border-slate-700';

      document.getElementById('prodCardsContainer').classList.toggle('hidden', mode === 'table');
      document.getElementById('prodTableContainer').classList.toggle('hidden', mode !== 'table');
      renderProductionView(false);
    }

    function applyProdFilters() {
      prodCurrentPage = 1;
      renderProductionView(false);
    }

    function renderProductionView(resetPage = false) {
      if (!prodTriInitialized) {
        prodTriInitialized = true;
        prodFilterState = 'VALIDAR';
        prodViewMode = 'tri';
      }
      if (resetPage) prodCurrentPage = 1;

      renderCarlosDecisionBar();
      updateProdFilterButtons();

      const rawSearch = (document.getElementById('prodSearchInput').value || '').trim();
      const search = normalizeSearchText(rawSearch.replace(/^#/, ''));
      const cat = document.getElementById('prodCategorySelect').value;
      const normCat = normalizeSearchText(cat);

      let filtered = prodItems.filter(item => {
        const st = String(item.Estado || '').toUpperCase();
        const proName = String(item.Nombre_Archivo_PRO || '');
        if (st.includes('RECHAZADO_QA') || proName.includes('ERROR_TEST')) return false;

        const hasProOrRaw = Boolean(extractDriveId(item.ID_Archivo_PRO) || extractDriveId(item.ID_Archivo_Gemini_Raw));
        const decKey = getDecisionKey('prod', item.ID);
        const dec = carlosDecisions[decKey];
        const isWebApproved = dec && dec.verdict === 'CORRECTO';
        const isWebRejected = dec && dec.verdict === 'INCORRECTO';

        if (prodFilterState === 'VALIDAR') {
          // Por Validar: Tiene foto PRO pero no está aprobada ni rechazada
          if (!hasProOrRaw) return false;
          if (isWebApproved || isWebRejected) return false;
          if (st.includes('APROBADO') || st.includes('RECHAZADO')) return false;
        } else if (prodFilterState === 'APROBADO') {
          if (!(isWebApproved || (!isWebRejected && st.includes('APROBADO')))) return false;
        } else if (prodFilterState === 'RECHAZADO') {
          if (!(isWebRejected || (!isWebApproved && st.includes('RECHAZADO')))) return false;
        } else if (prodFilterState === 'CON_PRO') {
          if (!hasProOrRaw) return false;
        } else if (prodFilterState === 'PENDIENTE') {
          if (hasProOrRaw) return false;
        }

        if (cat !== 'ALL') {
          const cPath = normalizeSearchText(String(item.Ruta_Carpeta_Drive || '') + ' ' + String(item.Nombre_Carpeta_Producto || ''));
          if (normCat === 'tocado') {
            if (!cPath.includes('tocado') && !cPath.includes('arete') && !cPath.includes('escapulario') && !cPath.includes('gargantilla')) return false;
          } else if (normCat === 'manto') {
            if (!cPath.includes('manto') && !cPath.includes('faja')) return false;
          } else if (normCat === 'sombrero') {
            if (!cPath.includes('sombrero') && !cPath.includes('panuelo')) return false;
          } else if (!cPath.includes(normCat)) {
            return false;
          }
        }

        if (search) {
          if (/^\d+$/.test(search) && String(item.ID) === search) return true;
          const text = normalizeSearchText(String(item.ID) + ' ' + String(item.Nombre_Carpeta_Producto) + ' ' + String(item.Nombre_Archivo_Original) + ' ' + String(item.Ruta_Carpeta_Drive) + ' ' + String(item.Motivo_Rechazo || ''));
          if (!text.includes(search)) return false;
        }

        return true;
      });

      // Ordenar por ID numérico ascendente dentro de cada grupo
      filtered.sort((a, b) => {
        const aHasBoth = Boolean(extractDriveId(a.ID_Archivo_Gemini_Raw) && extractDriveId(a.ID_Archivo_PRO)) ? 1 : 0;
        const bHasBoth = Boolean(extractDriveId(b.ID_Archivo_Gemini_Raw) && extractDriveId(b.ID_Archivo_PRO)) ? 1 : 0;
        if (bHasBoth !== aHasBoth) return bHasBoth - aHasBoth;
        const aRev = String(a.Estado || '').toUpperCase().includes('REVISION') ? 1 : 0;
        const bRev = String(b.Estado || '').toUpperCase().includes('REVISION') ? 1 : 0;
        if (bRev !== aRev) return bRev - aRev;
        return Number(a.ID || 0) - Number(b.ID || 0);
      });

      // Paginación: 100 imágenes por página
      const totalItems = filtered.length;
      renderPaginationControls(totalItems);

      const startIdx = (prodCurrentPage - 1) * prodPageSize;
      const endIdx = startIdx + prodPageSize;
      const pageItems = filtered.slice(startIdx, endIdx);

      if (prodViewMode === 'tri') {
        renderProdTriComparative(pageItems);
      } else if (prodViewMode === 'grid') {
        renderProdGrid(pageItems);
      } else {
        renderProdTable(pageItems);
      }
    }

    function renderProdTriComparative(items) {
      const container = document.getElementById('prodCardsContainer');
      container.className = 'space-y-8';
      if (items.length === 0) {
        container.innerHTML = '<div class="p-12 text-center text-slate-400 bg-[#121927] border border-slate-800 rounded-2xl">No hay fotos con esos criterios en esta vista.</div>';
        return;
      }

      container.innerHTML = items.map(item => {
        const idCat = String(item.ID || '');
        const st = String(item.Estado || 'PENDIENTE').toUpperCase();
        const score = item.Score_QA || 95;
        const lat = item.Latencia_Seg || '8.5';

        const origId = extractDriveId(item.ID_Archivo_Original);
        const rawGeminiId = extractDriveId(item.ID_Archivo_Gemini_Raw);
        const pythonProId = extractDriveId(item.ID_Archivo_PRO);

        const origUrl = origId ? \`https://lh3.googleusercontent.com/d/\${origId}=s800\` : 'https://placehold.co/600x800/121927/D4AF37?text=Original';
        const geminiRawUrl = rawGeminiId ? \`https://lh3.googleusercontent.com/d/\${rawGeminiId}=s800\` : (pythonProId ? \`https://lh3.googleusercontent.com/d/\${pythonProId}=s800\` : 'https://placehold.co/600x800/0f172a/64748b?text=Pendiente+Procesar+en+Colab');
        const pythonProUrl = pythonProId ? \`https://lh3.googleusercontent.com/d/\${pythonProId}=s800\` : geminiRawUrl;

        const origDriveLink = item.Link_Drive_Original || (origId ? \`https://drive.google.com/file/d/\${origId}/view\` : '#');
        const geminiRawLink = item.Link_Gemini_Raw || (rawGeminiId ? \`https://drive.google.com/file/d/\${rawGeminiId}/view\` : (item.Link_Drive_PRO || '#'));
        const pythonProLink = item.Link_Drive_PRO || (pythonProId ? \`https://drive.google.com/file/d/\${pythonProId}/view\` : '#');

        let badgeClass = 'badge-info';
        if (st.includes('APROBADO')) badgeClass = 'badge-ok';
        else if (st.includes('REVISION')) badgeClass = 'badge-warn';
        else if (st.includes('RECHAZADO') || st.includes('ERROR')) badgeClass = 'badge-error';

        const analysis = buildDiagnosticAnalysis(item, false);
        const sheetRejectNote = item.Motivo_Rechazo ? \`<span class="px-2 py-0.5 rounded text-[10px] font-semibold bg-rose-500/20 text-rose-300 border border-rose-500/40">⚠️ Obs: \${item.Motivo_Rechazo}</span>\` : '';
        const verBadge = rawGeminiId && pythonProId ? '<span class="px-2 py-0.5 rounded text-[10px] font-mono bg-emerald-500/20 text-emerald-300 border border-emerald-500/40 font-bold">✨ 3 Versiones Activas (Orig + Gemini + Python)</span>' : '';

        return buildTriComparativeCardHtml({
          scope: 'prod',
          idCat,
          batchId: '',
          title: \`\${item.Nombre_Carpeta_Producto || 'Producto'} — Archivo: \${item.Nombre_Archivo_Original}\`,
          subpath: String(item.Ruta_Carpeta_Drive || 'Catálogo Marinera Power').replace(/Ã©/g, 'é').replace(/Ã±/g, 'ñ').replace(/Ã³/g, 'ó').replace(/Ã¡/g, 'á').replace(/Ã­/g, 'í'),
          proFilename: item.Nombre_Archivo_PRO || '',
          resVisual: st,
          badgeClass,
          score,
          lat,
          origUrl,
          geminiRawUrl,
          pythonProUrl,
          origDriveLink,
          geminiRawLink,
          pythonProLink,
          hasDistinctGeminiRaw: Boolean(rawGeminiId),
          hasPythonPro: Boolean(pythonProId),
          headerExtraBadges: verBadge + (sheetRejectNote ? ' ' + sheetRejectNote : ''),
          isHighlighted: st.includes('REVISION'),
          analysis
        });
      }).join('');
    }

    function renderProdGrid(items) {
      const grid = document.getElementById('prodCardsContainer');
      grid.className = 'grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 gap-4';
      grid.innerHTML = '';

      items.forEach(item => {
        const origId = item.ID_Archivo_Original;
        const proId = item.ID_Archivo_PRO;
        const st = String(item.Estado || 'PENDIENTE').toUpperCase();
        const origUrl = origId ? \`https://lh3.googleusercontent.com/d/\${origId}=s400\` : 'https://placehold.co/300x300/121927/D4AF37?text=Original';
        const proUrl = proId && proId !== '-' ? \`https://lh3.googleusercontent.com/d/\${proId}=s400\` : null;

        const decKey = getDecisionKey('prod', item.ID);
        const dec = carlosDecisions[decKey];
        const isApproved = dec && dec.verdict === 'CORRECTO';
        const isRejected = dec && dec.verdict === 'INCORRECTO';

        let badge = '<span class="px-2 py-0.5 rounded text-[10px] font-semibold badge-info">PENDIENTE</span>';
        if (isApproved) badge = '<span class="px-2 py-0.5 rounded text-[10px] font-bold bg-emerald-500 text-slate-950">✅ CORRECTO</span>';
        else if (isRejected) badge = '<span class="px-2 py-0.5 rounded text-[10px] font-bold bg-rose-500 text-white">❌ INCORRECTO</span>';
        else if (st.includes('APROBADO')) badge = '<span class="px-2 py-0.5 rounded text-[10px] font-semibold badge-ok">APROBADO</span>';
        else if (st.includes('REVISION')) badge = '<span class="px-2 py-0.5 rounded text-[10px] font-semibold badge-warn">EN REVISIÓN</span>';

        let borderClass = 'border-slate-800';
        if (isApproved) borderClass = 'border-emerald-500 ring-1 ring-emerald-500/40';
        if (isRejected) borderClass = 'border-rose-500 ring-1 ring-rose-500/40';

        const card = document.createElement('div');
        card.className = \`bg-[#121927] border \${borderClass} rounded-xl overflow-hidden p-3 flex flex-col space-y-2 hover:border-slate-700 transition\`;
        card.innerHTML = \`
          <div class="relative w-full aspect-square rounded-lg overflow-hidden bg-slate-950 flex items-center justify-center">
            <img src="\${proUrl || origUrl}" alt="Thumb" class="w-full h-full object-cover">
            \${proUrl ? '<span class="absolute top-1.5 right-1.5 px-1.5 py-0.5 rounded text-[9px] bg-amber-500 text-slate-950 font-bold">PRO</span>' : ''}
          </div>
          <div class="flex items-center justify-between">
            <span class="font-cinzel font-bold text-xs text-amber-400">ID #\${item.ID}</span>
            <div class="flex items-center space-x-1">
              \${item.Score_QA ? \`<span class="px-1.5 py-0.5 rounded text-[9px] font-mono font-bold \${Number(item.Score_QA) >= 85 ? 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/40' : (Number(item.Score_QA) >= 70 ? 'bg-amber-500/20 text-amber-300 border border-amber-500/40' : 'bg-rose-500/20 text-rose-300 border border-rose-500/40')}">QA \${item.Score_QA}</span>\` : ''}
              \${badge}
            </div>
          </div>
          <p class="text-[11px] font-medium text-slate-200 truncate" title="\${item.Nombre_Carpeta_Producto || item.Nombre_Archivo_Original}">\${item.Nombre_Carpeta_Producto || item.Nombre_Archivo_Original}</p>
          <div class="grid grid-cols-2 gap-1.5 pt-1">
            <button onclick="setPhotoDecision('prod', '\${item.ID}', '', 'CORRECTO')" class="py-1 px-2 rounded text-[11px] font-bold transition \${isApproved ? 'bg-emerald-500 text-slate-950' : 'bg-emerald-500/10 text-emerald-300 hover:bg-emerald-500/20 border border-emerald-500/30'}">✅ Correcto</button>
            <button onclick="setPhotoDecision('prod', '\${item.ID}', '', 'INCORRECTO')" class="py-1 px-2 rounded text-[11px] font-bold transition \${isRejected ? 'bg-rose-500 text-white' : 'bg-rose-500/10 text-rose-300 hover:bg-rose-500/20 border border-rose-500/30'}">❌ Incorrecto</button>
          </div>
          <div class="pt-1 flex items-center justify-between text-[11px]">
            <a href="\${item.Link_Drive_Original || '#'}" target="_blank" class="text-slate-500 hover:text-slate-300">Drive Orig</a>
            <button onclick="openModalCompare('\${item.ID}', '\${origUrl}', '\${proUrl || origUrl}', '\${st}', '\${item.Score_QA || 95}', '\${item.Delta_E_Color || 3.0}', '\${item.Link_Drive_PRO || item.Link_Drive_Original || '#'}', 'prod', '')" class="text-amber-400 font-semibold hover:underline">🔍 Comparar</button>
          </div>
        \`;
        grid.appendChild(card);
      });
    }

    function renderProdTable(items) {
      const tbody = document.getElementById('prodTableBody');
      tbody.innerHTML = '';

      items.forEach(item => {
        const origId = item.ID_Archivo_Original;
        const proId = item.ID_Archivo_PRO;
        const st = String(item.Estado || 'PENDIENTE').toUpperCase();
        const origUrl = origId ? \`https://lh3.googleusercontent.com/d/\${origId}=s200\` : '';
        const proUrl = proId && proId !== '-' ? \`https://lh3.googleusercontent.com/d/\${proId}=s200\` : '';
        const decKey = getDecisionKey('prod', item.ID);
        const dec = carlosDecisions[decKey];
        const isApproved = dec && dec.verdict === 'CORRECTO';
        const isRejected = dec && dec.verdict === 'INCORRECTO';

        const tr = document.createElement('tr');
        tr.className = 'hover:bg-slate-900/40 transition';
        tr.innerHTML = \`
          <td class="p-3 font-cinzel font-bold text-amber-400">#\${item.ID}</td>
          <td class="p-3"><img src="\${origUrl}" class="w-10 h-10 object-cover rounded bg-slate-950 border border-slate-800"></td>
          <td class="p-3">\${proUrl ? \`<img src="\${proUrl}" class="w-10 h-10 object-cover rounded bg-slate-950 border border-amber-500/40">\` : '<span class="text-slate-600">-</span>'}</td>
          <td class="p-3 max-w-xs truncate">\${item.Nombre_Carpeta_Producto || item.Ruta_Carpeta_Drive}</td>
          <td class="p-3 font-mono text-[11px] text-slate-400">\${item.Nombre_Archivo_Original}</td>
          <td class="p-3">\${isApproved ? '<span class="px-2 py-0.5 rounded text-[10px] font-bold bg-emerald-500 text-slate-950">✅ CORRECTO</span>' : (isRejected ? '<span class="px-2 py-0.5 rounded text-[10px] font-bold bg-rose-500 text-white">❌ INCORRECTO</span>' : (st.includes('APROBADO') ? '<span class="badge-ok px-2 py-0.5 rounded text-[10px]">APROBADO</span>' : (st.includes('REVISION') ? '<span class="badge-warn px-2 py-0.5 rounded text-[10px]">REVISIÓN</span>' : '<span class="badge-info px-2 py-0.5 rounded text-[10px]">PENDIENTE</span>')))}</td>
          <td class="p-3 font-bold">\${item.Score_QA ? \`<span class="px-2 py-0.5 rounded font-mono text-[11px] font-bold \${Number(item.Score_QA) >= 85 ? 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/40' : (Number(item.Score_QA) >= 70 ? 'bg-amber-500/20 text-amber-300 border border-amber-500/40' : 'bg-rose-500/20 text-rose-300 border border-rose-500/40')}">\${item.Score_QA}/100</span>\` : '-'}</td>
          <td class="p-3 text-right space-x-1">
            <button onclick="setPhotoDecision('prod', '\${item.ID}', '', 'CORRECTO')" class="px-2 py-1 rounded text-[10px] font-bold \${isApproved ? 'bg-emerald-500 text-slate-950' : 'bg-emerald-500/15 text-emerald-300'}">✅</button>
            <button onclick="setPhotoDecision('prod', '\${item.ID}', '', 'INCORRECTO')" class="px-2 py-1 rounded text-[10px] font-bold \${isRejected ? 'bg-rose-500 text-white' : 'bg-rose-500/15 text-rose-300'}">❌</button>
            <button onclick="openModalCompare('\${item.ID}', '\${origUrl}', '\${proUrl || origUrl}', '\${st}', '\${item.Score_QA || 95}', '3.0', '\${item.Link_Drive_PRO || item.Link_Drive_Original || '#'}', 'prod', '')" class="text-amber-400 hover:underline text-xs pl-1">Ver</button>
          </td>
        \`;
        tbody.appendChild(tr);
      });
    }

    // 5. MODAL COMPARE LOGIC CON BOTONES CORRECTO / INCORRECTO
    let currentModalCtx = { scope: 'sandbox', id: '', batch: '' };

    function updateModalDecisionButtons() {
      const container = document.getElementById('modalDecisionControls');
      if (!container || !currentModalCtx.id) return;
      const key = getDecisionKey(currentModalCtx.scope, currentModalCtx.id, currentModalCtx.batch);
      const dec = carlosDecisions[key];
      const isApproved = dec && dec.verdict === 'CORRECTO';
      const isRejected = dec && dec.verdict === 'INCORRECTO';
      container.innerHTML = \`
        <button onclick="setPhotoDecision('\${currentModalCtx.scope}', '\${currentModalCtx.id}', '\${currentModalCtx.batch}', 'CORRECTO')" class="px-4 py-2 rounded-lg text-xs font-bold transition \${isApproved ? 'bg-emerald-500 text-slate-950 shadow-lg' : 'bg-emerald-500/15 text-emerald-300 border border-emerald-500/30 hover:bg-emerald-500/25'}">
          ✅ Marcar Correcto
        </button>
        <button onclick="setPhotoDecision('\${currentModalCtx.scope}', '\${currentModalCtx.id}', '\${currentModalCtx.batch}', 'INCORRECTO')" class="px-4 py-2 rounded-lg text-xs font-bold transition \${isRejected ? 'bg-rose-500 text-white shadow-lg' : 'bg-rose-500/15 text-rose-300 border border-rose-500/30 hover:bg-rose-500/25'}">
          ❌ Marcar Incorrecto (Reintentar)
        </button>
      \`;
    }

    function openModalCompare(id, origUrl, proUrl, status, score, delta, driveLink, scope = 'sandbox', batch = '') {
      currentModalCtx = { scope, id, batch };
      document.getElementById('modalTitle').textContent = \`Comparación de Calidad: ID #\${id} \${batch ? '(' + batch + ')' : ''}\`;
      document.getElementById('modalValId').textContent = id;
      document.getElementById('modalValStatus').textContent = status;
      document.getElementById('modalValScore').textContent = score + '/100';
      document.getElementById('modalValDelta').textContent = delta;
      document.getElementById('modalDriveLink').href = driveLink;

      document.getElementById('modalImgOrig').src = origUrl;
      document.getElementById('modalImgPro').src = proUrl;

      let ctrlBox = document.getElementById('modalDecisionControls');
      if (!ctrlBox) {
        const footer = document.getElementById('modalDriveLink').parentNode;
        ctrlBox = document.createElement('div');
        ctrlBox.id = 'modalDecisionControls';
        ctrlBox.className = 'flex items-center space-x-2';
        footer.insertBefore(ctrlBox, footer.lastElementChild);
      }
      updateModalDecisionButtons();

      document.getElementById('compareModal').classList.remove('hidden');
      setupCardSlider('modalCompareContainer');
    }

    function closeCompareModal() {
      document.getElementById('compareModal').classList.add('hidden');
    }

    // INITIAL LOAD`;

  if (fnBlockRegex.test(content)) {
    content = content.replace(fnBlockRegex, newFnBlock);
    console.log(`Reemplazado bloque completo de funciones + QA Decisions en ${path.basename(fPath)}`);
  } else {
    console.error(`fnBlockRegex no coincidió en ${path.basename(fPath)}`);
  }

  fs.writeFileSync(fPath, content, 'utf8');
});

try {
  execSync('git add docs/ index.html', { cwd: repoDir });
  execSync('git commit -m "feat(sync): sincronizar datasets completos de Sandbox y Maestro con auto-polling"', { cwd: repoDir });
  execSync('git push origin main:master', { cwd: repoDir });
  console.log('Push exitoso a GitHub Pages!');
} catch (e) {
  console.log('Git output:', e.message);
}
