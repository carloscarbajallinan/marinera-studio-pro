const { execSync } = require('child_process');

try {
  const raw = execSync('gsheets readonly read 1kRsCZ7ZpPxyxrSEkUrYRl3NHahrQQche90RKK2yedQ8 "Registro_Pruebas_Sandbox!A1:R15" --json').toString();
  const data = JSON.parse(raw.substring(raw.indexOf('[')));
  data.forEach((r, idx) => {
    console.log(`[Row ${idx}] Batch: ${r[1]} | ID: ${r[2]} | File: ${r[5]} | Modo: ${r[6]} | Status: ${r[7]} | Score: ${r[8]} | VistaPRO: ${r[13]} | ID_Mesa: ${r[15]}`);
  });
} catch (e) {
  console.error("Error:", e.message);
}
