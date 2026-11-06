const fs = require('fs');
const path = require('path');

const proMeta = JSON.parse(fs.readFileSync(path.join(__dirname, 'pro_files_metadata.json'), 'utf8'));
const orig = JSON.parse(fs.readFileSync(path.join(__dirname, 'drive_origin_tree.json'), 'utf8'));
const pro = JSON.parse(fs.readFileSync(path.join(__dirname, 'drive_pro_tree.json'), 'utf8'));

// Attach metadata to pro files
const proMetaMap = new Map();
for (const m of proMeta) {
  proMetaMap.set(m.id, m);
}

// Let's inspect folders of unmatched PRO files
// E.g. Falda para Ensayo de Razo - Azul Marino con cinta blanca_Pro
console.log('--- Analyzing Falda files in PRO vs Origin ---');
const proFaldas = pro.files.filter(f => f.folder_path.includes('Falda para Ensayo de Razo - Azul Marino con cinta blanca'));
console.log('PRO files in Azul Marino con cinta blanca:', proFaldas.length);
for (const f of proFaldas) {
  const m = proMetaMap.get(f.id);
  console.log(`  PRO: ${f.name} | Created: ${m ? m.createdTime : 'N/A'}`);
}

const origFaldas = orig.files.filter(f => f.folder_path.includes('Azul Marino con cinta blanca') || f.folder_path.includes('Azul Marino'));
console.log('ORIGIN files matching Azul Marino:', origFaldas.length);
for (const f of origFaldas) {
  console.log(`  ORIG: ${f.name} | Folder: ${f.folder_path}`);
}
