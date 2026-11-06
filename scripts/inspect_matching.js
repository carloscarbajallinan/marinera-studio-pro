const fs = require('fs');
const path = require('path');

const origPath = path.join(__dirname, 'drive_origin_tree.json');
const proPath = path.join(__dirname, 'drive_pro_tree.json');

const orig = JSON.parse(fs.readFileSync(origPath, 'utf8'));
const pro = JSON.parse(fs.readFileSync(proPath, 'utf8'));

console.log('--- ORIGIN: Mantos / Manto de Leche ---');
const origManto = orig.files.filter(f => f.folder_path.includes('Manto de Leche'));
console.log(origManto.map(f => ({ name: f.name, id: f.id, path: f.folder_path })));

console.log('\n--- PRO: Manto de Leche_Pro ---');
const proManto = pro.files.filter(f => f.folder_path.includes('Manto de Leche'));
console.log(proManto.map(f => ({ name: f.name, id: f.id, path: f.folder_path })));

console.log('\n--- ORIGIN: Escapulario ---');
const origEsc = orig.files.filter(f => f.folder_path.includes('Escapulario'));
console.log(origEsc.map(f => ({ name: f.name, id: f.id, path: f.folder_path })));

console.log('\n--- PRO: Escapulario ---');
const proEsc = pro.files.filter(f => f.folder_path.includes('Escapulario'));
console.log(proEsc.map(f => ({ name: f.name, id: f.id, path: f.folder_path })));
