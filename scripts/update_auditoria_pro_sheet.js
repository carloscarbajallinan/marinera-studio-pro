const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

const SPREADSHEET_ID = '1kRsCZ7ZpPxyxrSEkUrYRl3NHahrQQche90RKK2yedQ8';
const SHEET_NAME = 'Auditoria_Fotos_PRO';

const origPath = path.join(__dirname, 'drive_origin_tree.json');
const proPath = path.join(__dirname, 'drive_pro_tree.json');

const orig = JSON.parse(fs.readFileSync(origPath, 'utf8'));
const pro = JSON.parse(fs.readFileSync(proPath, 'utf8'));

// The 13 moved to _Fotos_Erroneas_y_Desalineadas
const movedToErroneas = new Set([
  '1AvYf0vtlMOMakeVloQQ7vgg2xNiL_dVE',
  '1x1ElpEqS3D0sQTEgCWr__lrIsWQWLOs8',
  '1IkPT_smNCaoi78GajbTbJI-2mhNWfxBE',
  '15XHPBCJV2sqt7QmR_PeXv6IuW8sgjvcD',
  '1YGniu1e_WQ8nvXzdd7UhFEqWc9lXNATN',
  '1JMDMxxQmaNAOfrh1Eh-3oJA8KFYOqLpq',
  '1iAhWg8s5H4R5-0t9MM0BOrNMgoCP11BJ',
  '1s_zYybSDywy0irzu6E_B2YLfi_5ELFpf',
  '1edkeS9CCHoA716T1RSrLJeuzJJaoLN0m',
  '1ssQ0Liqvq4zf3x-VnhCQD6VTBnfQnaGA',
  '1Xv-w3FrRk9xNWh3_R886FZWjDZHgbV0_',
  '1yRuPh3s8wHNV1nTfOnZdOVXqQFLBmJhl',
  '1deC6y6Q6TXQhQgPK7FUH9yKVS6YY73Um'
]);

// The 21 moved to Fotos_Con_Feedback_Corregir
const movedToFeedback = new Set([
  '1SEwWSfFvoQGeFwBJnCsV56aqkxgBd5Ii',
  '1zQvQwap3QVU9YItDGv5GDpFseFKGAzZ4',
  '1HY84V4-F_34aBLzzyWIoRBzDkRsU5Muo',
  '1dtlpoaaHb_Xb7LOPB2onlYYTSJtVvNlW',
  '1SFkDS9pcEn9tJs2h7XY6UkTXjP05ILpI',
  '1WGM1AKDJKknAA4y3rpuPROElITzU7jLJ',
  '1czCK7cbVJA_SXr4lzbejlCGxqBD0MjYc',
  '1wEPzHb8NdcKNXDtbgSNb4R_8J_gmLT4D',
  '13ZynO8V3ZtA9Fh_T1cp9Bg7lSBqF_DM0',
  '1hyDi4dw3mnW7lTZF94XSbnmuGAFXkKLb',
  '1cXO8MR2XQ3ywRQ-pLW2Kz7krHPZCFhsI',
  '1h_Mu3269fTceDvz-22GBVlQyOUch22dr',
  '1EV27gAun31OescAc9RKb_UYXZq_XHIu6',
  '1Cg-BOApginfEAFUfI4IgeLvpKeZJJPnd',
  '1rbiuU5SI3dLyeMtBL3bXl49BqfcOx_ie',
  '1NrwR5KoUgz77o1WvSxh-0VWMyWFMbHwx',
  '11TlBefZMhrReI6bNerFJVKCxJbpLBLbs',
  '1ccO-dq_TTvZyDhTKhcCCSI-uOLqod_6y',
  '1oRlOisSnwW3pdFcVSoYvf1QScSeoPE12',
  '1z0nb_N1SEJBGx_4r0jF9_S7uhxahPfQa',
  '1_DS9CaV8-2Rr87b_fzk9V5ZuqAlDKfbB'
]);

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
let huerfanosCount = 0;
let validCount = 0;

for (let i = 0; i < pro.files.length; i++) {
  const p = pro.files[i];
  const name = p.name;
  const ext = path.extname(name).toLowerCase();
  const leaf = normalize(getLeaf(p.folder_path));

  // Determine current folder location description
  let folderDesc = p.folder_path.replace(/^Fotos catalogo PRO\s*\/\s*/i, '');
  if (movedToErroneas.has(p.id)) {
    folderDesc = '_Fotos_Erroneas_y_Desalineadas';
  } else if (movedToFeedback.has(p.id)) {
    folderDesc = '_Fotos_Erroneas_y_Desalineadas / Fotos_Con_Feedback_Corregir';
  }

  // Base key
  let baseKey = '';
  const mImg = name.match(/(IMG_\d+)/i);
  const mFoto = name.match(/(foto\s*\(\d+\))/i);
  const mUuid = name.match(/([0-9a-f]{8})/i);
  const mNum = name.match(/^(\d+)/);

  if (mImg) baseKey = mImg[1].toUpperCase();
  else if (mFoto) baseKey = mFoto[1];
  else if (mUuid && !mNum) baseKey = mUuid[1];
  else if (mNum) baseKey = mNum[1];

  // Origin match attempt
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
    if (normalize(o.name) === normalize(name)) {
      matchedOrig = o;
      break;
    }
  }

  // Classification logic
  let tipo = 'PRO_FINAL';
  let estadoAuditoria = 'VALIDO_CATALOGO';

  if (movedToErroneas.has(p.id)) {
    tipo = name.includes('ERROR_TEST') ? 'ERRONEA_TEST' : 'INSTRUCCION_TEXTO';
    estadoAuditoria = 'MOVIDO_A_ERRONEAS';
  } else if (movedToFeedback.has(p.id)) {
    tipo = 'FEEDBACK_REVISION';
    estadoAuditoria = 'MOVIDO_A_FEEDBACK_CORREGIR';
  } else if (ext === '.heic') {
    tipo = 'FOTO_CRUDA_INP';
    estadoAuditoria = 'INSUMO_CRUDO_HEIC';
  } else if (/^IMG_\d+\.(jpe?g|png)$/i.test(name)) {
    tipo = 'FOTO_CRUDA_INP';
    estadoAuditoria = 'INSUMO_CRUDO_CAMARA';
  } else if (/[0-9a-f]{8}-[0-9a-f]{4}/i.test(name) && !name.includes('PRO')) {
    tipo = 'FOTO_CRUDA_INP';
    estadoAuditoria = 'INSUMO_CRUDO_UUID';
  } else if (!matchedOrig && (name.includes('PRO') || ext === '.png' || ext === '.jpg')) {
    tipo = 'HUERFANO_PRO_IA';
    estadoAuditoria = 'HUERFANO (CREADO SOLO CON IA / SIN BASE EN CATALOGO)';
    huerfanosCount++;
  } else if (/PRO\s*[0-9]|_v[0-9]|PRO[1-9]/i.test(name)) {
    tipo = 'PRO_ITERACION';
    estadoAuditoria = 'MULTI_VERSION_DISPONIBLE';
    validCount++;
  } else {
    tipo = 'PRO_FINAL';
    estadoAuditoria = 'VALIDO_CATALOGO';
    validCount++;
  }

  // Find siblings in folder sharing baseKey
  const folderFiles = proByFolder.get(p.folder_id) || [];
  const siblings = [];
  if (baseKey) {
    for (const f of folderFiles) {
      if (f.id !== p.id && f.name.toUpperCase().includes(baseKey)) {
        siblings.push(f.name);
      }
    }
  }

  const id = String(i + 1);
  const subcarpetaPro = folderDesc;
  const nombrePro = name;
  const idPro = p.id;
  const linkPro = `https://drive.google.com/file/d/${p.id}/view`;
  const correlacionBase = baseKey || '-';
  const hermanosPro = siblings.length > 0 ? siblings.slice(0, 3).join(' | ') : '-';
  const carpetaOrig = matchedOrig ? matchedOrig.folder_path : (origCandidates.length > 0 ? origCandidates[0].folder_path : 'NO_EXISTE_EN_ORIGEN');
  const fotoOrig = matchedOrig ? matchedOrig.name : 'SIN_FOTO_BASE';
  const idOrig = matchedOrig ? matchedOrig.id : '-';
  const linkOrig = matchedOrig ? matchedOrig.link : '-';
  const vistaPro = (tipo === 'INSTRUCCION_TEXTO') ? '' : `=IMAGE("https://lh3.googleusercontent.com/d/${p.id}")`;

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

console.log(`Summary: Total ${rows.length} rows. Huérfanos: ${huerfanosCount}, Válidos/Iterados: ${validCount}`);

// Write header
const headerBatch = [{ op: 'write', range: `${SHEET_NAME}!A1:N1`, data: [headers] }];
const headerBatchFile = path.join(__dirname, 'batch_auditoria_hdr.json');
fs.writeFileSync(headerBatchFile, JSON.stringify(headerBatch, null, 2), 'utf8');
execSync(`gsheets mutate batch ${SPREADSHEET_ID} -f "${headerBatchFile}"`, { stdio: 'inherit' });
fs.unlinkSync(headerBatchFile);

// Write in chunks
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

console.log('Auditoria_Fotos_PRO updated successfully with Huérfanos and Feedback separation!');
