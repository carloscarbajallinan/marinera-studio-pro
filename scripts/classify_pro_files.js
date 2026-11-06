const fs = require('fs');
const path = require('path');

const proPath = path.join(__dirname, 'drive_pro_tree.json');
const origPath = path.join(__dirname, 'drive_origin_tree.json');
const proMetaPath = path.join(__dirname, 'pro_files_metadata.json');

const pro = JSON.parse(fs.readFileSync(proPath, 'utf8'));
const orig = JSON.parse(fs.readFileSync(origPath, 'utf8'));
const proMeta = JSON.parse(fs.readFileSync(proMetaPath, 'utf8'));

const proMetaMap = new Map();
for (const m of proMeta) {
  if (!m.error) proMetaMap.set(m.id, m);
}

// Group origin files by leaf folder
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

const origByLeaf = new Map();
for (const o of orig.files) {
  const leaf = normalize(getLeaf(o.folder_path));
  if (!origByLeaf.has(leaf)) origByLeaf.set(leaf, []);
  origByLeaf.get(leaf).push(o);
}

// Let's examine every PRO file
const classified = [];

for (const p of pro.files) {
  const leaf = normalize(getLeaf(p.folder_path));
  const rawLeaf = getLeaf(p.folder_path);
  const origCandidates = origByLeaf.get(leaf) || [];
  const name = p.name;
  const ext = path.extname(name).toLowerCase();
  const m = proMetaMap.get(p.id);

  let type = 'PRO_VALID';
  let notes = '';

  // Checks
  if (name.includes('ERROR_TEST')) {
    type = 'ERRONEA_TEST';
    notes = 'Prueba anterior con prompt no estandarizado';
  } else if (name.startsWith('corregir') || name.includes('no corresponde') || name.includes('no se ha modificado')) {
    type = 'INSTRUCCION_TEXTO';
    notes = 'Archivo de texto/instrucción de corrección';
  } else if (name.toLowerCase().includes('corregir')) {
    type = 'CRUDA_FEEDBACK';
    notes = 'Foto cruda base con nota de corrección en el nombre';
  } else if (ext === '.heic') {
    type = 'CRUDA_HEIC';
    notes = 'Foto cruda directa de iPhone en formato HEIC';
  } else if (/^IMG_\d+\.(jpe?g|png)$/i.test(name)) {
    type = 'CRUDA_IMG';
    notes = 'Foto cruda de cámara sin post-procesar';
  } else if (/[0-9a-f]{8}-[0-9a-f]{4}/i.test(name) && !name.includes('PRO')) {
    type = 'CRUDA_UUID';
    notes = 'Foto cruda con identificador UUID de cámara';
  } else {
    type = 'PRO_RENDER';
    notes = 'Foto PRO editada para catálogo';
  }

  classified.push({
    id: p.id,
    name: p.name,
    folder: p.folder_path,
    rawLeaf,
    size: p.size,
    created: m ? m.createdTime : 'N/A',
    type,
    notes,
    origCandidatesCount: origCandidates.length
  });
}

// Stats by type
const typeCounts = {};
for (const c of classified) {
  typeCounts[c.type] = (typeCounts[c.type] || 0) + 1;
}

console.log('=== CLASIFICACIÓN DE LOS 245 ARCHIVOS PRO ===');
console.log(typeCounts);

console.log('\n--- ARCHIVOS ERRONEOS / INSTRUCCIONES / CRUDAS SIN EDITAR ---');
const badOrRaw = classified.filter(c => c.type !== 'PRO_RENDER');
console.log(`Total archivos que no son renders finales: ${badOrRaw.length}`);
for (const b of badOrRaw) {
  console.log(`[${b.type}] ${b.rawLeaf} -> ${b.name} (${b.id})`);
}
