const fs = require('fs');
const path = require('path');

const proPath = path.join(__dirname, 'drive_pro_tree.json');
const origPath = path.join(__dirname, 'drive_origin_tree.json');

const pro = JSON.parse(fs.readFileSync(proPath, 'utf8'));
const orig = JSON.parse(fs.readFileSync(origPath, 'utf8'));

// Find all files in PRO containing "corregir" (case-insensitive)
const proCorregir = pro.files.filter(f => /corregir/i.test(f.name));

console.log(`Found ${proCorregir.length} files with 'corregir' in PRO folders:`);

// Group all PRO files by folder_id
const proFilesByFolder = new Map();
for (const f of pro.files) {
  if (!proFilesByFolder.has(f.folder_id)) {
    proFilesByFolder.set(f.folder_id, []);
  }
  proFilesByFolder.get(f.folder_id).push(f);
}

const analysis = [];

for (const c of proCorregir) {
  const folderFiles = proFilesByFolder.get(c.folder_id) || [];
  // Find siblings in the same folder
  const siblings = folderFiles.map(f => f.name);

  // Extract base identifier (e.g. "5" from "5. CORREGIR", or "IMG_0930" from "IMG_0930 corregir falda.HEIC")
  const mNum = c.name.match(/^(\d+)/);
  const mImg = c.name.match(/(IMG_\d+)/i);
  
  let baseKey = '';
  if (mImg) baseKey = mImg[1].toUpperCase();
  else if (mNum) baseKey = mNum[1];

  // Look for siblings sharing this base identifier
  const relatedSiblings = folderFiles.filter(f => {
    if (f.id === c.id) return false;
    if (baseKey) {
      return f.name.toUpperCase().includes(baseKey);
    }
    return false;
  });

  analysis.push({
    corregirFile: c.name,
    folder: c.folder_path.split('/').slice(-2).join(' / '),
    baseKey,
    totalFilesInFolder: folderFiles.length,
    relatedSiblings: relatedSiblings.map(s => s.name),
    allFilesInFolder: siblings
  });
}

for (const a of analysis) {
  console.log(`\n========================================`);
  console.log(`CARPETA: ${a.folder}`);
  console.log(`ARCHIVO CORREGIR: "${a.corregirFile}" (Clave base: ${a.baseKey || 'N/A'})`);
  console.log(`HERMANOS RELACIONADOS EN LA MISMA CARPETA:`);
  if (a.relatedSiblings.length > 0) {
    for (const s of a.relatedSiblings) {
      console.log(`   -> "${s}"`);
    }
  } else {
    console.log(`   (Ninguno con la misma clave numérica directa)`);
  }
  console.log(`TODOS LOS ARCHIVOS DE ESTA CARPETA (${a.totalFilesInFolder}):`);
  for (const f of a.allFilesInFolder) {
    console.log(`      * ${f}`);
  }
}
