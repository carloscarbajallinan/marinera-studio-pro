const { execSync } = require('child_process');

try {
  const raw = execSync('gsheets readonly read 1kRsCZ7ZpPxyxrSEkUrYRl3NHahrQQche90RKK2yedQ8 "Control_Total_Drive_V2!A1:N500" --json').toString();
  const data = JSON.parse(raw.substring(raw.indexOf('[')));
  const canaryIds = ['28', '418', '421', '423', '424'];
  data.forEach((r, idx) => {
    if (canaryIds.includes(String(r[0]))) {
      console.log(`ID: ${r[0]} | File: ${r[4]} | OrigID: ${r[5]} | Folder: ${r[1]}`);
    }
  });
} catch (e) {
  console.error("Error:", e.message);
}
