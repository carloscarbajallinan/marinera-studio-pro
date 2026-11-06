const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

const SPREADSHEET_ID = '1kRsCZ7ZpPxyxrSEkUrYRl3NHahrQQche90RKK2yedQ8';
const SHEET_NAME = 'Control_Total_Fotos';

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

const proByLeaf = new Map();
for (const p of pro.files) {
  const leaf = normalize(getLeaf(p.folder_path));
  if (!proByLeaf.has(leaf)) {
    proByLeaf.set(leaf, []);
  }
  proByLeaf.get(leaf).push(p);
}

const headers = [
  'ID',
  'Carpeta_Ruta_Original',
  'Nombre_Archivo_Original',
  'ID_Archivo_Original',
  'Link_Drive_Original',
  'Estado',
  'Carpeta_Ruta_PRO',
  'Nombre_Foto_PRO',
  'ID_Foto_PRO',
  'Link_Drive_PRO',
  'Observaciones_Feedback',
  'Vista_Original',
  'Vista_PRO'
];

const rows = [];
for (let i = 0; i < orig.files.length; i++) {
  const f = orig.files[i];
  const origLeaf = normalize(getLeaf(f.folder_path));
  const origBase = normalize(path.parse(f.name).name);

  let matchedPro = null;
  const candidates = proByLeaf.get(origLeaf) || [];

  for (const c of candidates) {
    const cBase = normalize(path.parse(c.name).name);
    if (origBase === cBase) {
      matchedPro = c;
      break;
    }
    const prefixRegex = new RegExp(`^${origBase}([^0-9]|$)`, 'i');
    if (prefixRegex.test(cBase)) {
      matchedPro = c;
      break;
    }
  }

  const id = String(i + 1);
  const origFolder = f.folder_path;
  const origName = f.name;
  const origId = f.id;
  const origLink = f.link;
  const origView = `=IMAGE("https://lh3.googleusercontent.com/d/${origId}")`;

  let estado = 'PENDIENTE';
  let proFolder = '';
  let proName = '';
  let proId = '';
  let proLink = '';
  let obs = '';
  let proView = '';

  if (matchedPro) {
    estado = 'COMPLETADO';
    proFolder = matchedPro.folder_path;
    proName = matchedPro.name;
    proId = matchedPro.id;
    proLink = matchedPro.link;
    obs = 'Versión PRO identificada en Google Drive';
    proView = `=IMAGE("https://lh3.googleusercontent.com/d/${proId}")`;
  }

  rows.push([
    id,
    origFolder,
    origName,
    origId,
    origLink,
    estado,
    proFolder,
    proName,
    proId,
    proLink,
    obs,
    origView,
    proView
  ]);
}

console.log(`Syncing ${rows.length} rows to ${SHEET_NAME}...`);

// Update header
const headerBatch = [{ op: 'write', range: `${SHEET_NAME}!A1:M1`, data: [headers] }];
const headerBatchFile = path.join(__dirname, 'batch_header_ctf.json');
fs.writeFileSync(headerBatchFile, JSON.stringify(headerBatch, null, 2), 'utf8');
execSync(`gsheets mutate batch ${SPREADSHEET_ID} -f "${headerBatchFile}"`, { stdio: 'inherit' });
fs.unlinkSync(headerBatchFile);

// Write in chunks
const CHUNK_SIZE = 150;
for (let start = 0; start < rows.length; start += CHUNK_SIZE) {
  const end = Math.min(start + CHUNK_SIZE, rows.length);
  const chunk = rows.slice(start, end);
  const startRow = start + 2;
  const endRow = end + 1;
  const range = `${SHEET_NAME}!A${startRow}:M${endRow}`;

  console.log(`Writing ${SHEET_NAME} rows ${startRow} to ${endRow}...`);
  const chunkBatch = [{ op: 'write', range, data: chunk }];
  const chunkFile = path.join(__dirname, `batch_ctf_${startRow}.json`);
  fs.writeFileSync(chunkFile, JSON.stringify(chunkBatch, null, 2), 'utf8');
  execSync(`gsheets mutate batch ${SPREADSHEET_ID} -f "${chunkFile}"`, { stdio: 'inherit' });
  fs.unlinkSync(chunkFile);
}

console.log('Control_Total_Fotos synced successfully!');
