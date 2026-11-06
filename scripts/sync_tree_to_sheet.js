const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

const SPREADSHEET_ID = '1kRsCZ7ZpPxyxrSEkUrYRl3NHahrQQche90RKK2yedQ8';
const SHEET_NAME = 'Auditoria_Fotos_PRO';

const origPath = path.join(__dirname, 'drive_origin_tree.json');
const proPath = path.join(__dirname, 'drive_pro_tree.json');

const orig = JSON.parse(fs.readFileSync(origPath, 'utf8'));
const pro = JSON.parse(fs.readFileSync(proPath, 'utf8'));

// The 34 files with their category tree in _Fotos_Erroneas_y_Desalineadas
const fileCategoryMap = new Map([
  // 10 ERROR_TEST
  ['1AvYf0vtlMOMakeVloQQ7vgg2xNiL_dVE', 'Escapulario para Mujer de Marinera_Pro'],
  ['1x1ElpEqS3D0sQTEgCWr__lrIsWQWLOs8', 'Escapulario para Mujer de Marinera_Pro'],
  ['1IkPT_smNCaoi78GajbTbJI-2mhNWfxBE', 'Escapulario para Mujer de Marinera_Pro'],
  ['15XHPBCJV2sqt7QmR_PeXv6IuW8sgjvcD', 'Escapulario para Mujer de Marinera_Pro'],
  ['1YGniu1e_WQ8nvXzdd7UhFEqWc9lXNATN', 'Juego de Collar y Aretes para Marinera_Pro'],
  ['1JMDMxxQmaNAOfrh1Eh-3oJA8KFYOqLpq', 'Juego de Collar y Aretes para Marinera_Pro'],
  ['1iAhWg8s5H4R5-0t9MM0BOrNMgoCP11BJ', 'Juego de Collar y Aretes para Marinera_Pro'],
  ['1s_zYybSDywy0irzu6E_B2YLfi_5ELFpf', 'Juego de Collar y Aretes para Marinera_Pro'],
  ['1edkeS9CCHoA716T1RSrLJeuzJJaoLN0m', 'Manto de Pava bordado_Pro'],
  ['1ssQ0Liqvq4zf3x-VnhCQD6VTBnfQnaGA', 'Manto de Pava bordado_Pro'],
  // 3 instrucciones de texto
  ['1Xv-w3FrRk9xNWh3_R886FZWjDZHgbV0_', 'Falda de Ensayo de razo 2 bobos con contrabobo pro'],
  ['1yRuPh3s8wHNV1nTfOnZdOVXqQFLBmJhl', 'Falda de Ensayo de razo 2 bobos con contrabobo pro'],
  ['1deC6y6Q6TXQhQgPK7FUH9yKVS6YY73Um', 'Falda de Ensayo de razo 2 bobos con contrabobo pro'],
  // 21 corregir feedback
  ['1SEwWSfFvoQGeFwBJnCsV56aqkxgBd5Ii', 'Falda para Ensayo de Razo - Azul Eléctrico con cinta blanca_Pro'],
  ['1zQvQwap3QVU9YItDGv5GDpFseFKGAzZ4', 'Falda para Ensayo de Razo - Azul Marino con cinta blanca_Pro'],
  ['1HY84V4-F_34aBLzzyWIoRBzDkRsU5Muo', 'Falda para Ensayo de Razo - Azul Marino con cinta blanca_Pro'],
  ['1dtlpoaaHb_Xb7LOPB2onlYYTSJtVvNlW', 'Falda para Ensayo de Razo - Azul Marino Entero_Pro'],
  ['1SFkDS9pcEn9tJs2h7XY6UkTXjP05ILpI', 'Falda para Ensayo de Razo - Azul Marino Entero_Pro'],
  ['1WGM1AKDJKknAA4y3rpuPROElITzU7jLJ', 'Falda para Ensayo de Razo - Azul Marino Entero_Pro'],
  ['1czCK7cbVJA_SXr4lzbejlCGxqBD0MjYc', 'Falda para Ensayo de Razo - Coral con cinta blanca_Pro'],
  ['1wEPzHb8NdcKNXDtbgSNb4R_8J_gmLT4D', 'Falda para Ensayo de Razo - Coral con cinta blanca_Pro'],
  ['13ZynO8V3ZtA9Fh_T1cp9Bg7lSBqF_DM0', 'Falda para Ensayo de Razo - Lila con cinta morada_Pro'],
  ['1hyDi4dw3mnW7lTZF94XSbnmuGAFXkKLb', 'Falda para Ensayo de Razo - Lila con cinta morada_Pro'],
  ['1cXO8MR2XQ3ywRQ-pLW2Kz7krHPZCFhsI', 'Falda para Ensayo de Razo - Morada con cinta blanca_Pro'],
  ['1h_Mu3269fTceDvz-22GBVlQyOUch22dr', 'Falda para Ensayo de Razo - Morada con cinta blanca_Pro'],
  ['1EV27gAun31OescAc9RKb_UYXZq_XHIu6', 'Falda para Ensayo de Razo - Negro entero_Pro'],
  ['1Cg-BOApginfEAFUfI4IgeLvpKeZJJPnd', 'Falda para Ensayo de Razo - Rosada con cinta blanca_Pro'],
  ['1rbiuU5SI3dLyeMtBL3bXl49BqfcOx_ie', 'Falda para Ensayo de Razo - Turquesa con cinta blanca_Pro'],
  ['1NrwR5KoUgz77o1WvSxh-0VWMyWFMbHwx', 'Falda para Ensayo de Razo - Verde jade con cinta blanca_Pro'],
  ['11TlBefZMhrReI6bNerFJVKCxJbpLBLbs', 'Falda para Ensayo de Razo - Vino con cinta perla_Pro'],
  ['1ccO-dq_TTvZyDhTKhcCCSI-uOLqod_6y', 'Falda para Ensayo de Razo - Vino Entero_Pro'],
  ['1oRlOisSnwW3pdFcVSoYvf1QScSeoPE12', 'Falda para Ensayo de Razo - Vino Entero_Pro'],
  ['1z0nb_N1SEJBGx_4r0jF9_S7uhxahPfQa', 'Manto de Leche_Pro'],
  ['1_DS9CaV8-2Rr87b_fzk9V5ZuqAlDKfbB', 'Tocado con Peineta para Marinera_Pro']
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

const origByLeaf = new Map();
for (const o of orig.files) {
  const leaf = normalize(getLeaf(o.folder_path));
  if (!origByLeaf.has(leaf)) origByLeaf.set(leaf, []);
  origByLeaf.get(leaf).push(o);
}

const proByFolder = new Map();
for (const p of pro.files) {
  if (!proByFolder.has(p.folder_id)) proByFolder.set(p.folder_id, []);
  proByFolder.get(p.folder_id).push(p);
}

const headers = [
  'ID',
  'Subcarpeta_PRO_Actual',
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
  const leaf = normalize(getLeaf(p.folder_path));

  let folderDesc = p.folder_path.replace(/^Fotos catalogo PRO\s*\/\s*/i, '');
  if (fileCategoryMap.has(p.id)) {
    const sub = fileCategoryMap.get(p.id);
    folderDesc = `_Fotos_Erroneas_y_Desalineadas / ${sub}`;
  }

  let baseKey = '';
  const mImg = name.match(/(IMG_\d+)/i);
  const mFoto = name.match(/(foto\s*\(\d+\))/i);
  const mUuid = name.match(/([0-9a-f]{8})/i);
  const mNum = name.match(/^(\d+)/);

  if (mImg) baseKey = mImg[1].toUpperCase();
  else if (mFoto) baseKey = mFoto[1];
  else if (mUuid && !mNum) baseKey = mUuid[1];
  else if (mNum) baseKey = mNum[1];

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

  let tipo = 'PRO_FINAL';
  let estadoAuditoria = 'VALIDO_CATALOGO';

  if (fileCategoryMap.has(p.id)) {
    if (name.includes('ERROR_TEST')) {
      tipo = 'ERRONEA_TEST';
      estadoAuditoria = 'ERRONEA (EN ARBOL DE AUDITORIA)';
    } else if (name.startsWith('corregir,') || name.includes('no corresponde') || name.includes('no se ha modificado')) {
      tipo = 'INSTRUCCION_TEXTO';
      estadoAuditoria = 'INSTRUCCION (EN ARBOL DE AUDITORIA)';
    } else {
      tipo = 'FEEDBACK_CORREGIR';
      estadoAuditoria = 'FEEDBACK_REVISION (EN ARBOL DE AUDITORIA)';
    }
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
  } else if (/PRO\s*[0-9]|_v[0-9]|PRO[1-9]/i.test(name)) {
    tipo = 'PRO_ITERACION';
    estadoAuditoria = 'MULTI_VERSION_DISPONIBLE';
  } else {
    tipo = 'PRO_FINAL';
    estadoAuditoria = 'VALIDO_CATALOGO';
  }

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

// Write header
const headerBatch = [{ op: 'write', range: `${SHEET_NAME}!A1:N1`, data: [headers] }];
const headerBatchFile = path.join(__dirname, 'batch_tree_hdr.json');
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
  const chunkFile = path.join(__dirname, `batch_tree_${startRow}.json`);
  fs.writeFileSync(chunkFile, JSON.stringify(chunkBatch, null, 2), 'utf8');
  execSync(`gsheets mutate batch ${SPREADSHEET_ID} -f "${chunkFile}"`, { stdio: 'inherit' });
  fs.unlinkSync(chunkFile);
}

console.log('Auditoria_Fotos_PRO synchronized with complete tree structure!');
