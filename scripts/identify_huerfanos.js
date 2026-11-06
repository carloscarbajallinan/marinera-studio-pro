const fs = require('fs');
const path = require('path');

const origPath = path.join(__dirname, 'drive_origin_tree.json');
const proPath = path.join(__dirname, 'drive_pro_tree.json');

const orig = JSON.parse(fs.readFileSync(origPath, 'utf8'));
const pro = JSON.parse(fs.readFileSync(proPath, 'utf8'));

function normalize(s) {
  if (!s) return '';
  return s.toLowerCase()
    .normalize('NFD').replace(/[\u0300-\u036f]/g, '')
    .replace(/_pro$/i, '')
    .replace(/[^a-z0-9]/g, ' ')
    .trim().replace(/\s+/g, ' ');
}

function getLeaf(folderPath) {
  const parts = folderPath.split('/').map(p => p.trim()).filter(Boolean);
  return parts[parts.length - 1] || '';
}

// Map origin files by leaf
const origByLeaf = new Map();
for (const o of orig.files) {
  const leaf = normalize(getLeaf(o.folder_path));
  if (!origByLeaf.has(leaf)) origByLeaf.set(leaf, []);
  origByLeaf.get(leaf).push(o);
}

// Check PRO renders
const huerfanos = [];
const conOrigen = [];

for (const p of pro.files) {
  const name = p.name;
  // Ignore error test and text files
  if (name.includes('ERROR_TEST')) continue;
  if (name.startsWith('corregir,')) continue;

  const leaf = normalize(getLeaf(p.folder_path));
  const rawLeaf = getLeaf(p.folder_path);
  const origCandidates = origByLeaf.get(leaf) || [];

  // If there are NO candidates in the original catalog at all for this category:
  if (origCandidates.length === 0) {
    huerfanos.push({
      reason: 'CATEGORIA_INEXISTENTE_EN_ORIGEN',
      file: p,
      rawLeaf
    });
    continue;
  }

  // Extract base key
  const mImg = name.match(/(IMG_\d+)/i);
  const mFoto = name.match(/(foto\s*\(\d+\))/i);
  const mUuid = name.match(/([0-9a-f]{8})/i);
  const mNum = name.match(/^(\d+)/);

  let baseKey = '';
  if (mImg) baseKey = mImg[1].toUpperCase();
  else if (mFoto) baseKey = mFoto[1];
  else if (mUuid && !mNum) baseKey = mUuid[1];
  else if (mNum) baseKey = mNum[1];

  // Try to match with any origin file in this category
  let matched = false;
  for (const o of origCandidates) {
    const oBase = normalize(path.parse(o.name).name);
    if (baseKey && normalize(baseKey) === oBase) {
      matched = true;
      break;
    }
    const prefixRegex = new RegExp(`^${normalize(baseKey)}([^0-9]|$)`, 'i');
    if (baseKey && prefixRegex.test(oBase)) {
      matched = true;
      break;
    }
    // Also check if origin filename is contained in PRO name or vice versa
    if (normalize(o.name) === normalize(p.name)) {
      matched = true;
      break;
    }
  }

  if (matched) {
    conOrigen.push({ file: p, rawLeaf });
  } else {
    huerfanos.push({
      reason: 'SIN_FOTO_BASE_EN_CATALOGO_ORIGINAL',
      file: p,
      rawLeaf,
      origAvailableInFolder: origCandidates.map(o => o.name)
    });
  }
}

console.log(`=== ANÁLISIS DE HUÉRFANOS (PRO SIN FOTO CRUDA ORIGINAL) ===`);
console.log(`Total PRO analizados: ${conOrigen.length + huerfanos.length}`);
console.log(`Con Foto Original Base: ${conOrigen.length}`);
console.log(`Huérfanos identificados: ${huerfanos.length}`);

console.log('\n--- DETALLE DE HUÉRFANOS ---');
const huerfanosByFolder = {};
for (const h of huerfanos) {
  huerfanosByFolder[h.rawLeaf] = (huerfanosByFolder[h.rawLeaf] || 0) + 1;
}

for (const [folder, count] of Object.entries(huerfanosByFolder)) {
  console.log(`\n[${count} huérfanos] Carpeta: ${folder}`);
  const items = huerfanos.filter(h => h.rawLeaf === folder);
  for (const it of items) {
    console.log(`   -> "${it.file.name}" (ID: ${it.file.id}) | Razón: ${it.reason}`);
    if (it.origAvailableInFolder) {
      console.log(`      (En catálogo original sólo existen: [${it.origAvailableInFolder.join(', ')}])`);
    }
  }
}
