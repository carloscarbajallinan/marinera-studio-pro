const fs = require('fs');
const path = require('path');

const htmlPath = 'C:\\Users\\LENOVO\\Documents\\Carlitos\\IA\\Antigravity\\Profesionalización de catálogo\\Cliente Marinera Power\\index.html';
const content = fs.readFileSync(htmlPath, 'utf8');

console.log("HTML length:", content.length);
console.log("Contains extractDriveId:", content.includes('function extractDriveId'));
console.log("Contains syncLiveFromGoogleSheets:", content.includes('syncLiveFromGoogleSheets()'));
console.log("Contains setInterval auto-sync:", content.includes('setInterval(syncLiveFromGoogleSheets, 25000)'));

// Extract sandboxItems length from string
const matchSb = content.match(/let sandboxItems = (\[.*?\]);\s*let prodItems/s);
if (matchSb) {
  const sb = JSON.parse(matchSb[1]);
  console.log("Embedded sandboxItems count:", sb.length);
  console.log("Latest sandbox item:", sb[sb.length - 1].Test_Batch_ID, sb[sb.length - 1].ID_Catalogo, sb[sb.length - 1].ID_Drive_Mesa);
} else {
  console.log("Could not parse sandboxItems via regex");
}
