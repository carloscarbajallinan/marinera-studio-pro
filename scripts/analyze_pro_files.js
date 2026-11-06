const fs = require('fs');
const path = require('path');

const origPath = path.join(__dirname, 'drive_origin_tree.json');
const proPath = path.join(__dirname, 'drive_pro_tree.json');

const orig = JSON.parse(fs.readFileSync(origPath, 'utf8'));
const pro = JSON.parse(fs.readFileSync(proPath, 'utf8'));

console.log('Total Origin files:', orig.files.length);
console.log('Total PRO files:', pro.files.length);

const foldersWithFiles = {};
for (const f of pro.files) {
  foldersWithFiles[f.folder_path] = (foldersWithFiles[f.folder_path] || 0) + 1;
}

console.log('\n--- PRO FOLDERS WITH FILES ---');
for (const [k, v] of Object.entries(foldersWithFiles)) {
  console.log(`[${v}] ${k}`);
}
