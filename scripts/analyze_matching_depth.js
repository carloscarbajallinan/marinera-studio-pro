const fs = require('fs');
const path = require('path');

const orig = JSON.parse(fs.readFileSync(path.join(__dirname, 'drive_origin_tree.json'), 'utf8'));
const pro = JSON.parse(fs.readFileSync(path.join(__dirname, 'drive_pro_tree.json'), 'utf8'));

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

const matchedOrig = new Set();
const matchedPro = new Set();
const pairs = [];

for (const origFile of orig.files) {
  const origLeaf = normalize(getLeaf(origFile.folder_path));
  const origBase = normalize(path.parse(origFile.name).name);
  const candidates = proByLeaf.get(origLeaf) || [];

  let match = null;
  for (const c of candidates) {
    const cBase = normalize(path.parse(c.name).name);
    if (origBase === cBase) {
      match = c;
      break;
    }
    const prefixRegex = new RegExp(`^${origBase}([^0-9]|$)`, 'i');
    if (prefixRegex.test(cBase)) {
      match = c;
      break;
    }
  }

  if (match) {
    matchedOrig.add(origFile.id);
    matchedPro.add(match.id);
    pairs.push({
      origFile,
      proFile: match
    });
  }
}

console.log('=== MATCHING STATS ===');
console.log('Total Origin files:', orig.files.length);
console.log('Total PRO files:', pro.files.length);
console.log('Matched pairs:', pairs.length);
console.log('Unique PRO files matched:', matchedPro.size);
console.log('Unique PRO files UNMATCHED:', pro.files.length - matchedPro.size);

// Analyze unmatched PRO files
const unmatchedPro = pro.files.filter(p => !matchedPro.has(p.id));
const unmatchedByFolder = {};
for (const p of unmatchedPro) {
  unmatchedByFolder[p.folder_path] = (unmatchedByFolder[p.folder_path] || 0) + 1;
}

console.log('\n=== UNMATCHED PRO FILES BY FOLDER ===');
for (const [folder, count] of Object.entries(unmatchedByFolder)) {
  console.log(`[${count}] ${folder}`);
}

console.log('\n=== SAMPLE UNMATCHED PRO FILES (first 15) ===');
for (const p of unmatchedPro.slice(0, 15)) {
  console.log(`- Folder: ${p.folder_path}`);
  console.log(`  Name: ${p.name} | ID: ${p.id}`);
}
