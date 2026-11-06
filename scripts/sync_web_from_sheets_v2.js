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

const sandboxItems = rowsSb.slice(1).map(r => {
  return {
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

  // Reemplazo robusto de DOMContentLoaded
  const domRegex = /\/\/\s*INITIAL LOAD[\s\S]*?window\.addEventListener\('DOMContentLoaded'[\s\S]*?\}\);/;
  const newDom = `// INITIAL LOAD CON AUTO-SYNC EN VIVO Y POLLING CADA 25s
    window.addEventListener('DOMContentLoaded', () => {
      updateCounters();
      renderSandboxCards();
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
