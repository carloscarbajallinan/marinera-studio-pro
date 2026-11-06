const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

const SPREADSHEET_ID = '1kRsCZ7ZpPxyxrSEkUrYRl3NHahrQQche90RKK2yedQ8';
const SHEET_NAME = 'Control_Total_Drive_V2';

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

// Map PRO files by normalized leaf folder
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
  'Ruta_Carpeta_Drive',
  'Nombre_Carpeta_Producto',
  'ID_Carpeta_Drive',
  'Nombre_Archivo_Original',
  'ID_Archivo_Original',
  'Link_Drive_Original',
  'Estado',
  'Ruta_Carpeta_PRO',
  'Nombre_Archivo_PRO',
  'ID_Archivo_PRO',
  'Link_Drive_PRO',
  'Vista_Original',
  'Vista_PRO'
];

const rows = [];
let matchedCount = 0;

for (let i = 0; i < orig.files.length; i++) {
  const f = orig.files[i];
  const origLeaf = normalize(getLeaf(f.folder_path));
  const origBase = normalize(path.parse(f.name).name);
  const rawLeaf = getLeaf(f.folder_path);

  // Look for match among PRO files in same leaf folder
  let matchedPro = null;
  const candidates = proByLeaf.get(origLeaf) || [];

  for (const c of candidates) {
    const cBase = normalize(path.parse(c.name).name);
    // 1. Exact base match: "1" === "1"
    if (origBase === cBase) {
      matchedPro = c;
      break;
    }
    // 2. Prefix match: e.g. orig="1", c="1_escapulario_mujer_pro..." or "1.1..."
    const prefixRegex = new RegExp(`^${origBase}([^0-9]|$)`, 'i');
    if (prefixRegex.test(cBase)) {
      matchedPro = c;
      break;
    }
  }

  const id = String(i + 1);
  const origFolder = f.folder_path;
  const prodName = rawLeaf;
  const origFolderId = f.folder_id;
  const origName = f.name;
  const origId = f.id;
  const origLink = f.link;
  const origView = `=IMAGE("https://lh3.googleusercontent.com/d/${origId}")`;

  let estado = 'PENDIENTE';
  let proFolder = '';
  let proName = '';
  let proId = '';
  let proLink = '';
  let proView = '';

  if (matchedPro) {
    matchedCount++;
    estado = 'COMPLETADO';
    proFolder = matchedPro.folder_path;
    proName = matchedPro.name;
    proId = matchedPro.id;
    proLink = matchedPro.link;
    proView = `=IMAGE("https://lh3.googleusercontent.com/d/${proId}")`;
  }

  rows.push([
    id,
    origFolder,
    prodName,
    origFolderId,
    origName,
    origId,
    origLink,
    estado,
    proFolder,
    proName,
    proId,
    proLink,
    origView,
    proView
  ]);
}

console.log(`Prepared ${rows.length} rows.`);
console.log(`Matched PRO: ${matchedCount} / ${rows.length} (${((matchedCount/rows.length)*100).toFixed(1)}%)`);
console.log(`Pending: ${rows.length - matchedCount}`);

// Write header first
const headerBatch = [
  {
    op: 'write',
    range: `${SHEET_NAME}!A1:N1`,
    data: [headers]
  }
];
const headerBatchFile = path.join(__dirname, 'batch_header.json');
fs.writeFileSync(headerBatchFile, JSON.stringify(headerBatch, null, 2), 'utf8');

console.log('Writing header...');
execSync(`gsheets mutate batch ${SPREADSHEET_ID} -f "${headerBatchFile}"`, { stdio: 'inherit' });

// Write data in chunks of 150 rows
const CHUNK_SIZE = 150;
for (let start = 0; start < rows.length; start += CHUNK_SIZE) {
  const end = Math.min(start + CHUNK_SIZE, rows.length);
  const chunk = rows.slice(start, end);
  const startRow = start + 2; // 1-indexed, after header
  const endRow = end + 1;
  const range = `${SHEET_NAME}!A${startRow}:N${endRow}`;

  console.log(`Writing rows ${startRow} to ${endRow} (${chunk.length} rows)...`);
  const chunkBatch = [
    {
      op: 'write',
      range: range,
      data: chunk
    }
  ];
  const chunkBatchFile = path.join(__dirname, `batch_chunk_${startRow}.json`);
  fs.writeFileSync(chunkBatchFile, JSON.stringify(chunkBatch, null, 2), 'utf8');
  execSync(`gsheets mutate batch ${SPREADSHEET_ID} -f "${chunkBatchFile}"`, { stdio: 'inherit' });
  fs.unlinkSync(chunkBatchFile); // cleanup
}

fs.unlinkSync(headerBatchFile);
console.log('Master table uploaded successfully!');
