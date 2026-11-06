const fs = require('fs');
const path = require('path');

const orig = JSON.parse(fs.readFileSync(path.join(__dirname, 'drive_origin_tree.json'), 'utf8'));
const pro = JSON.parse(fs.readFileSync(path.join(__dirname, 'drive_pro_tree.json'), 'utf8'));

// Helper to normalize strings for comparison
function cleanStr(s) {
  return s.toLowerCase()
    .normalize('NFD').replace(/[\u0300-\u036f]/g, '') // remove accents
    .replace(/[^a-z0-9]/g, ' ') // letters and digits only
    .trim().replace(/\s+/g, ' ');
}

// Build map of PRO files
// A PRO file belongs to a folder. Let's see how PRO folders relate to ORIGIN folders.
console.log('Mapping PRO files...');

// Let's print out all unique PRO relative folder paths
const proFolderMap = new Map();
for (const f of pro.folders) {
  // strip root 'Fotos catalogo PRO / '
  const relPath = f.path.replace(/^Fotos catalogo PRO\s*\/\s*/i, '');
  proFolderMap.set(f.id, { ...f, relPath });
}

// Let's inspect matching for each origin file
let matchedCount = 0;
const matchDetails = [];

for (const origFile of orig.files) {
  // Origin relative path: e.g. "Para ella / Accesorios / Mantos / Manto de Leche"
  const origRelFolder = origFile.folder_path.replace(/^Fotos catalogo\s*\/\s*/i, '');
  const origBaseName = path.parse(origFile.name).name.trim(); // "1", "2", "3", etc.
  
  // Clean parts
  const cleanOrigFolder = cleanStr(origRelFolder);
  const cleanOrigBase = cleanStr(origBaseName);

  // Find candidate PRO files
  let matchedPro = null;

  for (const proFile of pro.files) {
    const proRelFolder = proFile.folder_path.replace(/^Fotos catalogo PRO\s*\/\s*/i, '');
    const proBaseName = path.parse(proFile.name).name.trim();

    const cleanProFolder = cleanStr(proRelFolder);
    const cleanProBase = cleanStr(proBaseName);

    // Check if folders match:
    // Notice PRO folders often have "_Pro" or "Accesorios ella pro" inserted.
    // e.g. "para ella / accesorios / mantos / manto de leche" vs "para ella pro / accesorios pro / accesorios ella pro / mantos / manto de leche pro"
    // Let's check if the leaf folder (category) matches:
    const origParts = origRelFolder.split('/').map(p => cleanStr(p));
    const origLeaf = origParts[origParts.length - 1]; // e.g. "manto de leche"

    const proParts = proRelFolder.split('/').map(p => cleanStr(p).replace(/\s*pro$/i, ''));
    const proLeaf = proParts[proParts.length - 1]; // e.g. "manto de leche"

    if (origLeaf === proLeaf || cleanProFolder.includes(origLeaf)) {
      // Folder matches! Now check file name match:
      // In PRO, names can be "1", "1_Escapulario_Mujer_PRO...", "1.1...", "1_1_..."
      if (cleanProBase === cleanOrigBase) {
        matchedPro = proFile;
        break;
      }
      // Check if starts with origBaseName (e.g. orig="1", pro="1_Collar..." or "1.1...")
      // But ensure word boundary so "1" doesn't match "10"
      const prefixRegex = new RegExp(`^${cleanOrigBase}([^0-9]|$)`, 'i');
      if (prefixRegex.test(cleanProBase)) {
        matchedPro = proFile;
        break;
      }
    }
  }

  if (matchedPro) {
    matchedCount++;
    matchDetails.push({
      origFile: origFile.name,
      origFolder: origRelFolder,
      proFile: matchedPro.name,
      proFolder: matchedPro.folder_path,
      proId: matchedPro.id
    });
  }
}

console.log(`Matched ${matchedCount} out of ${orig.files.length} origin files.`);
console.log('Sample 10 matches:');
console.log(matchDetails.slice(0, 10));
