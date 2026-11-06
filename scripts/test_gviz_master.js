const https = require('https');

const sheetId = '1kRsCZ7ZpPxyxrSEkUrYRl3NHahrQQche90RKK2yedQ8';
const url = `https://docs.google.com/spreadsheets/d/${sheetId}/gviz/tq?tqx=out:json&sheet=Control_Total_Drive_V2`;

https.get(url, res => {
  let data = '';
  res.on('data', chunk => data += chunk);
  res.on('end', () => {
    const match = data.match(/setResponse\((.*)\);/);
    if (match) {
      const parsed = JSON.parse(match[1]);
      console.log("Cols in Control_Total_Drive_V2:", parsed.table.cols.map(c => ({ id: c.id, label: c.label })));
      console.log("Total rows in Control_Total_Drive_V2:", parsed.table.rows.length);
    } else {
      console.log("No match:", data.substring(0, 300));
    }
  });
}).on('error', e => console.error(e));
