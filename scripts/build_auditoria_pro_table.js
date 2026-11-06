const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

const SPREADSHEET_ID = '1kRsCZ7ZpPxyxrSEkUrYRl3NHahrQQche90RKK2yedQ8';
const SHEET_NAME = 'Auditoria_Fotos_PRO';

const origPath = path.join(__dirname, 'drive_origin_tree.json');
const proPath = path.join(__dirname, 'drive_pro_tree.json');
const proMetaPath = path.join(__dirname, 'pro_files_metadata.json');

const orig = JSON.parse(fs.readFileSync(origPath, 'utf8'));
const pro = JSON.parse(fs.readFileSync(proPath, 'utf8'));
const proMeta = JSON.parse(fs.readFileSync(proMetaPath, 'utf8'));

const proMetaMap = new Map();
for (const m of proMeta) {
  if (!m.error) proMetaMap.set(m.id, m);
}

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

// Map origin files by normalized leaf folder
const origByLeaf = new Map();
for (const o of orig.files) {
  const leaf = normalize(getLeaf(o.folder_path));
  if (!origByLeaf.has(leaf)) origByLeaf.set(leaf, []);
  origByLeaf.get(leaf).push(o);
}

// Group all PRO files by folder_id to find siblings
const proByFolder = new Map();
for (const p of pro.files) {
  if (!proByFolder.has(p.folder_id)) proByFolder.set(p.folder_id, []);
  proByFolder.get(p.folder_id).push(p);
}

const headers = [
  'ID',
  'Subcarpeta_PRO',
  'Nombre_Archivo_PRO',
  'ID_Archivo_PRO',
  'Link_Drive_PRO',
  'Tipo_Clasificacion',
  'Correlacion_Base',
  'Relacion_Hermanos_PRO',
  'Carpeta_Catalogo_Original',
  'Foto_Original_Catalogo',
  'ID_Original_Catalogo',
  'Link_Original_Catalogo',
  'Estado_Auditoria',
  'Vista_Previa_PRO'
];

const rows = [];

for (let i = 0; i < pro.files.length; i++) {
  const p = pro.files[i];
  const name = p.name;
  const ext = path.extname(name).toLowerCase();
  const folder = p.folder_path.replace(/^Fotos catalogo PRO\s*\/\s*/i, '');
  const leaf = normalize(getLeaf(p.folder_path));
  const rawLeaf = getLeaf(p.folder_path);

  // Classify type
  let tipo = 'PRO_FINAL';
  let estadoAuditoria = 'VALIDO_CATALOGO';

  if (name.includes('ERROR_TEST')) {
    tipo = 'ERRONEA_TEST';
    estadoAuditoria = 'MOVIDO_A_ERRONEAS';
  } else if (name.startsWith('corregir,') || name.includes('no corresponde') || name.includes('no se ha modificado')) {
    tipo = 'INSTRUCCION_TEXTO';
    estadoAuditoria = 'MOVIDO_A_ERRONEAS';
  } else if (name.toLowerCase().includes('corregir')) {
    tipo = 'FEEDBACK_REVISION';
    estadoAuditoria = 'INSUMO_CON_FEEDBACK';
  } else if (ext === '.heic') {
    tipo = 'FOTO_CRUDA_INP';
    estadoAuditoria = 'INSUMO_CRUDO_HEIC';
  } else if (/^IMG_\d+\.(jpe?g|png)$/i.test(name)) {
    tipo = 'FOTO_CRUDA_INP';
    estadoAuditoria = 'INSUMO_CRUDO_CAMARA';
  } else if (/[0-9a-f]{8}-[0-9a-f]{4}/i.test(name) && !name.includes('PRO')) {
    tipo = 'FOTO_CRUDA_INP';
    estadoAuditoria = 'INSUMO_CRUDO_UUID';
  } else if (/PRO\s*[0-9]|_v[0-9]|PRO[1-9]/i.test(name)) {
    tipo = 'PRO_ITERACION';
    estadoAuditoria = 'MULTI_VERSION_DISPONIBLE';
  } else {
    tipo = 'PRO_FINAL';
    estadoAuditoria = 'VALIDO_CATALOGO';
  }

  // Extract base key (e.g. "5" from "5. CORREGIR", "IMG_0716" from "IMG_0716 PRO.jpg", "foto (2)")
  let baseKey = '';
  const mImg = name.match(/(IMG_\d+)/i);
  const mFoto = name.match(/(foto\s*\(\d+\))/i);
  const mUuid = name.match(/([0-9a-f]{8})/i);
  const mNum = name.match(/^(\d+)/);

  if (mImg) baseKey = mImg[1].toUpperCase();
  else if (mFoto) baseKey = mFoto[1];
  else if (mUuid && !mNum) baseKey = mUuid[1];
  else if (mNum) baseKey = mNum[1];

  // Find siblings in PRO folder sharing baseKey
  const folderFiles = proByFolder.get(p.folder_id) || [];
  const siblings = [];
  if (baseKey) {
    for (const f of folderFiles) {
      if (f.id !== p.id && f.name.toUpperCase().includes(baseKey)) {
        siblings.push(f.name);
      }
    }
  }

  // Find matching original file in Fotos catalogo
  const origCandidates = origByLeaf.get(leaf) || [];
  let matchedOrig = null;

  for (const o of origCandidates) {
    const oBase = normalize(path.parse(o.name).name);
    if (baseKey && normalize(baseKey) === oBase) {
      matchedOrig = o;
      break;
    }
    const prefixRegex = new RegExp(`^${normalize(baseKey)}([^0-9]|$)`, 'i');
    if (baseKey && prefixRegex.test(oBase)) {
      matchedOrig = o;
      break;
    }
  }

  const id = String(i + 1);
  const subcarpetaPro = folder;
  const nombrePro = name;
  const idPro = p.id;
  const linkPro = `https://drive.google.com/file/d/${p.id}/view`;
  const correlacionBase = baseKey || '-';
  const hermanosPro = siblings.length > 0 ? siblings.slice(0, 3).join(' | ') : '-';
  const carpetaOrig = matchedOrig ? matchedOrig.folder_path : (origCandidates.length > 0 ? origCandidates[0].folder_path : '-');
  const fotoOrig = matchedOrig ? matchedOrig.name : '-';
  const idOrig = matchedOrig ? matchedOrig.id : '-';
  const linkOrig = matchedOrig ? matchedOrig.link : '-';
  const vistaPro = tipo === 'INSTRUCCION_TEXTO' ? '' : `=IMAGE("https://lh3.googleusercontent.com/d/${p.id}")`;

  rows.push([
    id,
    subcarpetaPro,
    nombrePro,
    idPro,
    linkPro,
    tipo,
    correlacionBase,
    hermanosPro,
    carpetaOrig,
    fotoOrig,
    idOrig,
    linkOrig,
    estadoAuditoria,
    vistaPro
  ]);
}

console.log(`Prepared ${rows.length} rows for ${SHEET_NAME}.`);

// Write header
const headerBatch = [{ op: 'write', range: `${SHEET_NAME}!A1:N1`, data: [headers] }];
const headerBatchFile = path.join(__dirname, 'batch_auditoria_hdr.json');
fs.writeFileSync(headerBatchFile, JSON.stringify(headerBatch, null, 2), 'utf8');
execSync(`gsheets mutate batch ${SPREADSHEET_ID} -f "${headerBatchFile}"`, { stdio: 'inherit' });
fs.unlinkSync(headerBatchFile);

// Write data in chunks
const CHUNK_SIZE = 125;
for (let start = 0; start < rows.length; start += CHUNK_SIZE) {
  const end = Math.min(start + CHUNK_SIZE, rows.length);
  const chunk = rows.slice(start, end);
  const startRow = start + 2;
  const endRow = end + 1;
  const range = `${SHEET_NAME}!A${startRow}:N${endRow}`;

  console.log(`Writing ${SHEET_NAME} rows ${startRow} to ${endRow}...`);
  const chunkBatch = [{ op: 'write', range, data: chunk }];
  const chunkFile = path.join(__dirname, `batch_auditoria_${startRow}.json`);
  fs.writeFileSync(chunkFile, JSON.stringify(chunkBatch, null, 2), 'utf8');
  execSync(`gsheets mutate batch ${SPREADSHEET_ID} -f "${chunkFile}"`, { stdio: 'inherit' });
  fs.unlinkSync(chunkFile);
}

console.log('Auditoria_Fotos_PRO populated successfully!');
