const https = require('https');

const sheetId = '1kRsCZ7ZpPxyxrSEkUrYRl3NHahrQQche90RKK2yedQ8';
const url = `https://docs.google.com/spreadsheets/d/${sheetId}/gviz/tq?tqx=out:json&sheet=Registro_Pruebas_Sandbox`;

https.get(url, res => {
  let data = '';
  res.on('data', chunk => data += chunk);
  res.on('end', () => {
    const match = data.match(/setResponse\((.*)\);/);
    if (match) {
      const parsed = JSON.parse(match[1]);
      console.log("Cols:", parsed.table.cols.map(c => ({ id: c.id, label: c.label })));
      console.log("Total rows:", parsed.table.rows.length);
      console.log("Row 0 cells:", parsed.table.rows[0].c.map(c => c ? (c.f || c.v) : null));
      console.log("Row 1 cells:", parsed.table.rows[1].c.map(c => c ? (c.f || c.v) : null));
    } else {
      console.log("No match:", data.substring(0, 300));
    }
  });
}).on('error', e => console.error(e));
