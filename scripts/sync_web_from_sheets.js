const { execSync } = require('child_process');
const fs = require('fs');
const path = require('path');

const repoDir = 'C:\\Users\\LENOVO\\Documents\\Carlitos\\IA\\Antigravity\\Profesionalización de catálogo\\Cliente Marinera Power';
const sheetId = '1kRsCZ7ZpPxyxrSEkUrYRl3NHahrQQche90RKK2yedQ8';

console.log('Fetching live data from Google Sheet Control_Total_Drive_V2...');
const raw = execSync(`gsheets readonly read ${sheetId} "Control_Total_Drive_V2!A1:R800" --json`, { maxBuffer: 30 * 1024 * 1024 }).toString();

const jsonStart = raw.indexOf('[');
const rows = JSON.parse(raw.substring(jsonStart));

console.log(`Read ${rows.length} rows from Sheet.`);
const headers = rows[0];
console.log('Headers:', headers);

const items = rows.slice(1).map(r => {
  return {
    ID: r[0] || '',
    Carpeta_Ruta_Original: r[1] || '',
    Nombre_Carpeta_Producto: r[2] || '',
    ID_Carpeta_Drive: r[3] || '',
    Nombre_Archivo_Original: r[4] || '',
    ID_Archivo_Original: r[5] || '',
    Link_Drive_Original: r[6] || '',
    Estado: r[7] || 'PENDIENTE',
    Carpeta_Ruta_PRO: r[8] || '',
    Nombre_Foto_PRO: r[9] || '',
    ID_Foto_PRO: r[10] || '',
    Link_Drive_PRO: r[11] || '',
    Vista_Original: r[12] || '',
    Vista_PRO: r[13] || '',
    Link_Gemini_Raw: r[14] || '',
    ID_Archivo_Gemini_Raw: r[15] || '',
    Score_QA: r[16] || '',
    Motivo_QA: r[17] || ''
  };
});

// Write to docs/catalog_live_sheet.json
const destJson = path.join(repoDir, 'docs', 'catalog_live_sheet.json');
fs.writeFileSync(destJson, JSON.stringify(items, null, 2), 'utf8');
console.log(`Saved ${items.length} items to ${destJson}`);

// Update docs/index.html showcaseItems
const docsHtmlPath = path.join(repoDir, 'docs', 'index.html');
const rootHtmlPath = path.join(repoDir, 'index.html');

[docsHtmlPath, rootHtmlPath].forEach(fPath => {
  let content = fs.readFileSync(fPath, 'utf8');
  const sTag = 'const showcaseItems = ';
  const eTag = ';\n    \n    let qaMode =';
  const sIdx = content.indexOf(sTag);
  const eIdx = content.indexOf(eTag, sIdx);
  if (sIdx !== -1 && eIdx !== -1) {
    const before = content.substring(0, sIdx + sTag.length);
    const after = content.substring(eIdx);
    content = before + JSON.stringify(items) + after;
    fs.writeFileSync(fPath, content, 'utf8');
    console.log(`Updated showcaseItems in ${fPath}`);
  }
});

// Commit and push
try {
  execSync('git add docs/ index.html', { cwd: repoDir });
  execSync('git commit -m "feat(sync): sincronizar catalogo y metricas desde Google Sheet Control_Total_Drive_V2"', { cwd: repoDir });
  execSync('git push origin main:master', { cwd: repoDir });
  console.log('Pushed sheet sync to GitHub Pages!');
} catch (e) {
  console.log('Git output:', e.message);
}
