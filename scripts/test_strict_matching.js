const fs = require('fs');
const path = require('path');

const orig = JSON.parse(fs.readFileSync(path.join(__dirname, 'drive_origin_tree.json'), 'utf8'));
const pro = JSON.parse(fs.readFileSync(path.join(__dirname, 'drive_pro_tree.json'), 'utf8'));

function normalize(s) {
  return s.toLowerCase()
    .normalize('NFD').replace(/[\u0300-\u036f]/g, '')
    .replace(/_pro$/i, '')
    .replace(/[^a-z0-9]/g, ' ')
    .trim().replace(/\s+/g, ' ');
}

// Get leaf folder name
function getLeaf(folderPath) {
  const parts = folderPath.split('/').map(p => p.trim()).filter(Boolean);
  return parts[parts.length - 1] || '';
}

let matchedCount = 0;
const matches = [];

for (const origFile of orig.files) {
  const origLeaf = normalize(getLeaf(origFile.folder_path));
  const origRelPath = origFile.folder_path.replace(/^Fotos catalogo\s*\/\s*/i, '');
  const origBaseName = normalize(path.parse(origFile.name).name);

  // Candidate PRO files
  let matchedPro = null;

  for (const proFile of pro.files) {
    const proLeaf = normalize(getLeaf(proFile.folder_path));
    const proBaseName = normalize(path.parse(proFile.name).name);

    // Exact leaf folder match
    if (origLeaf === proLeaf) {
      // 1. Exact base name match: "1" === "1"
      if (origBaseName === proBaseName) {
        matchedPro = proFile;
        break;
      }
      // 2. Prefix match: e.g. "1" matches "1_escapulario..." or "1.1..."
      const prefixRegex = new RegExp(`^${origBaseName}([^0-9]|$)`, 'i');
      if (prefixRegex.test(proBaseName)) {
        matchedPro = proFile;
        break;
      }
    }
  }

  if (matchedPro) {
    matchedCount++;
    matches.push({
      origName: origFile.name,
      origFolder: origRelPath,
      proName: matchedPro.name,
      proFolder: matchedPro.folder_path.replace(/^Fotos catalogo PRO\s*\/\s*/i, ''),
      proId: matchedPro.id
    });
  }
}

console.log(`STRICT MATCH: ${matchedCount} out of ${orig.files.length} origin files.`);
console.log('Sample 10 strict matches:');
console.log(matches.slice(0, 10));
