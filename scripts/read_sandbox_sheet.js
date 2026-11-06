const { execSync } = require('child_process');

try {
  const raw = execSync('gsheets readonly read 1kRsCZ7ZpPxyxrSEkUrYRl3NHahrQQche90RKK2yedQ8 "Registro_Pruebas_Sandbox!A1:R15" --json').toString();
  const jsonStart = raw.indexOf('[');
  if (jsonStart !== -1) {
    const data = JSON.parse(raw.substring(jsonStart));
    console.log("Total rows:", data.length);
    console.log("Headers:", JSON.stringify(data[0]));
    if (data.length > 1) {
      console.log("Row 1 (First data):", JSON.stringify(data[1]));
      console.log("Row Last:", JSON.stringify(data[data.length - 1]));
    }
  } else {
    console.log("Raw output:", raw);
  }
} catch (e) {
  console.error("Error:", e.message);
}
