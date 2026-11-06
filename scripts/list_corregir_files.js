const fs = require('fs');
const path = require('path');

const proPath = path.join(__dirname, 'drive_pro_tree.json');
const pro = JSON.parse(fs.readFileSync(proPath, 'utf8'));

// Find all files in PRO containing "corregir"
const corregirFiles = pro.files.filter(f => /corregir/i.test(f.name));

console.log(`Total archivos que dicen 'corregir': ${corregirFiles.length}`);
for (const f of corregirFiles) {
  console.log(`ID: ${f.id} | Name: "${f.name}" | Folder: "${f.folder_path}"`);
}
