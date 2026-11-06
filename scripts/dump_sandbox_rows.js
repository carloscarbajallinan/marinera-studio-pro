const { execSync } = require('child_process');

try {
  const raw = execSync('gsheets readonly read 1kRsCZ7ZpPxyxrSEkUrYRl3NHahrQQche90RKK2yedQ8 "Registro_Pruebas_Sandbox!A1:R11" --json').toString();
  const data = JSON.parse(raw.substring(raw.indexOf('[')));
  console.log(JSON.stringify(data, null, 2));
} catch (e) {
  console.error("Error:", e.message);
}
