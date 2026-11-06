const fs = require('fs');
const path = require('path');

const proMeta = JSON.parse(fs.readFileSync(path.join(__dirname, 'pro_files_metadata.json'), 'utf8'));
const orig = JSON.parse(fs.readFileSync(path.join(__dirname, 'drive_origin_tree.json'), 'utf8'));
const pro = JSON.parse(fs.readFileSync(path.join(__dirname, 'drive_pro_tree.json'), 'utf8'));

const proMetaMap = new Map();
for (const m of proMeta) {
  if (!m.error) proMetaMap.set(m.id, m);
}

// 1. Analyze File Types / Naming in PRO
let rawHeicCount = 0;
let rawJpgCount = 0;
let iterationsCount = 0;
let finalProCount = 0;
let errorTestCount = 0;

const proBreakdown = {
  rawHeicOrJpg: [], // intermediate un-edited files stored in PRO folders
  iterations: [],   // PRO1, PRO2, PRO3, v2
  errorTest: [],     // ERROR_TEST from previous run
  standardPro: []    // cleanly named PRO files
};

for (const f of pro.files) {
  const name = f.name;
  const ext = path.extname(name).toLowerCase();
  const m = proMetaMap.get(f.id);
  const created = m ? m.createdTime : 'unknown';

  if (name.includes('ERROR_TEST')) {
    errorTestCount++;
    proBreakdown.errorTest.push({ name, folder: f.folder_path, created });
  } else if (ext === '.heic' || name.toLowerCase().includes('corregir') || (name.startsWith('IMG_') && !name.includes('PRO'))) {
    rawHeicCount++;
    proBreakdown.rawHeicOrJpg.push({ name, folder: f.folder_path, created });
  } else if (/PRO\s*[0-9]|_v[0-9]|PRO[1-9]/i.test(name)) {
    iterationsCount++;
    proBreakdown.iterations.push({ name, folder: f.folder_path, created });
  } else {
    finalProCount++;
    proBreakdown.standardPro.push({ name, folder: f.folder_path, created });
  }
}

console.log('=== DESGLOSE DE LOS 245 ARCHIVOS EN FOTOS CATALOGO PRO ===');
console.log(`1. Archivos en crudo (.HEIC, fotos base IMG_ sin editar, o con etiqueta 'corregir'): ${rawHeicCount}`);
console.log(`2. Iteraciones / Variaciones (PRO1, PRO2, PRO3, v2 del mismo producto): ${iterationsCount}`);
console.log(`3. Archivos de prueba anteriores marcados ERROR_TEST: ${errorTestCount}`);
console.log(`4. Fotos PRO estándar / finales: ${finalProCount}`);
console.log(`TOTAL: ${rawHeicCount + iterationsCount + errorTestCount + finalProCount}`);

// 2. Timeline Analysis
console.log('\n=== ONDAS CRONOLÓGICAS DE TRABAJO EN PRO ===');
const waves = {
  'Julio 2026 (Primeras Faldas y Accesorios)': [],
  'Agosto 2026 (Segunda Ola de Faldas y Retoques)': [],
  'Septiembre 2026 (Tercera Ola Masiva: Faldas, Mantos, Tocados, Pañuelos)': [],
  'Noviembre 2026 (Pipeline Antigravity / Gemini Actual)': []
};

for (const f of pro.files) {
  const m = proMetaMap.get(f.id);
  const dateStr = (m && m.createdTime) ? m.createdTime.slice(0, 7) : 'other';
  if (dateStr === '2026-07') waves['Julio 2026 (Primeras Faldas y Accesorios)'].push(f);
  else if (dateStr === '2026-08') waves['Agosto 2026 (Segunda Ola de Faldas y Retoques)'].push(f);
  else if (dateStr === '2026-09') waves['Septiembre 2026 (Tercera Ola Masiva: Faldas, Mantos, Tocados, Pañuelos)'].push(f);
  else if (dateStr === '2026-11') waves['Noviembre 2026 (Pipeline Antigravity / Gemini Actual)'].push(f);
}

for (const [w, items] of Object.entries(waves)) {
  console.log(`\n* ${w}: ${items.length} archivos`);
  // Sample categories in this wave
  const cats = new Set(items.map(it => it.folder_path.split('/').pop().trim()));
  console.log(`  Categorías tocadas (${cats.size}): ${Array.from(cats).slice(0, 5).join(', ')}...`);
}
