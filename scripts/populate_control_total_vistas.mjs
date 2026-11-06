import fs from 'fs';
import https from 'https';

const SPREADSHEET_ID = '1kRsCZ7ZpPxyxrSEkUrYRl3NHahrQQche90RKK2yedQ8';
const tokenData = JSON.parse(fs.readFileSync('C:/Users/LENOVO/.gemini/antigravity/plugin_data/gsheets/token.json'));
const accessToken = tokenData.token.access_token;

function apiRequest(method, endpoint, body) {
  return new Promise((resolve, reject) => {
    const options = {
      hostname: 'sheets.googleapis.com',
      path: endpoint,
      method: method,
      headers: {
        'Authorization': `Bearer ${accessToken}`,
        'Content-Type': 'application/json'
      }
    };

    const req = https.request(options, (res) => {
      let data = '';
      res.on('data', chunk => data += chunk);
      res.on('end', () => {
        try {
          const parsed = JSON.parse(data);
          if (res.statusCode >= 200 && res.statusCode < 300) {
            resolve(parsed);
          } else {
            reject(new Error(`API Error ${res.statusCode}: ${JSON.stringify(parsed)}`));
          }
        } catch (e) {
          reject(e);
        }
      });
    });

    req.on('error', reject);
    if (body) req.write(JSON.stringify(body));
    req.end();
  });
}

async function main() {
  console.log("1. Generando fórmulas de visualización para Control_Total_Fotos (866 filas)...");
  
  const totalRows = 867;
  const values = [];
  
  // Fila 1: Headers
  values.push(["Vista_Original", "Vista_PRO"]);
  
  // Filas 2 a 867
  for (let r = 2; r <= totalRows; r++) {
    const formulaOrig = `=IF(ISBLANK(D${r}), "", IMAGE("https://lh3.googleusercontent.com/d/" & D${r}))`;
    const formulaPro = `=IF(ISBLANK(H${r}), "", IMAGE("https://lh3.googleusercontent.com/d/" & H${r}))`;
    values.push([formulaOrig, formulaPro]);
  }

  const updateBody = {
    valueInputOption: "USER_ENTERED",
    data: [
      {
        range: `Control_Total_Fotos!K1:L${totalRows}`,
        values: values
      }
    ]
  };

  const res = await apiRequest('POST', `/v4/spreadsheets/${SPREADSHEET_ID}/values:batchUpdate`, updateBody);
  console.log(`[OK] ${res.totalUpdatedCells} celdas actualizadas en Control_Total_Fotos con fórmulas de previsualización.`);

  // 2. Leer Control_Total_Fotos para cruzar y actualizar las fotos que ya fueron creadas
  console.log("\n2. Vinculando fotos creadas en Control_Total_Fotos...");
  const sheetData = await apiRequest('GET', `/v4/spreadsheets/${SPREADSHEET_ID}/values/Control_Total_Fotos!A1:I${totalRows}`);
  const rows = sheetData.values || [];

  // Mapeo de fotos creadas por ID Original
  const createdPhotos = {
    // 5 Fotos PRO V2
    "1T0z_DfDEmrr6H9wbiNGfg5RmBg8MneYX": {
      namePro: "2_1_aretes_marinera_PRO_v2.jpg",
      idPro: "1prc92aNl0PEh0PZcoMtZwIp-oZWI2Qtu",
      linkPro: "https://drive.google.com/file/d/1prc92aNl0PEh0PZcoMtZwIp-oZWI2Qtu/view"
    },
    "1mtiG5AJj24HzoSuvu_amXKo-Por54CLq": {
      namePro: "2_1_aretes_para_marinera_PRO_v2.jpg",
      idPro: "1g5H5nfYAExFzuKLSu4LSjF13FKu35nCH",
      linkPro: "https://drive.google.com/file/d/1g5H5nfYAExFzuKLSu4LSjF13FKu35nCH/view"
    },
    "1MQdfxQoWrRHOsGsAFd6_jziGKoqmyw24": {
      namePro: "2_1_MANTO_DE_LECHE_PRO_v2.jpg",
      idPro: "1mSa6YNMWkPp5qEZg3fxF84tDScZ7HOGu",
      linkPro: "https://drive.google.com/file/d/1mSa6YNMWkPp5qEZg3fxF84tDScZ7HOGu/view"
    },
    "1Hf2Y6MLDWayEHFl46aRAZm52z0NOb8PP": {
      namePro: "2_2_MANTO_DE_LECHE_PRO_v2.jpg",
      idPro: "1vNkqHdCmydyQkr8TS7XGP7EE3PSlvbDx",
      linkPro: "https://drive.google.com/file/d/1vNkqHdCmydyQkr8TS7XGP7EE3PSlvbDx/view"
    },
    "1t2jde5a9D55KbOwpqelT-MX-Z8LK4Jvv": {
      namePro: "2_1_Pardos_de_hilo_PRO_v2.jpg",
      idPro: "1UBSXB17tRakEPEO3obG3-IJ_uSTY-XHn",
      linkPro: "https://drive.google.com/file/d/1UBSXB17tRakEPEO3obG3-IJ_uSTY-XHn/view"
    }
  };

  const syncUpdates = [];
  for (let i = 1; i < rows.length; i++) {
    const rowNum = i + 1;
    const origId = rows[i][3]; // Columna D
    if (origId && createdPhotos[origId]) {
      const match = createdPhotos[origId];
      syncUpdates.push({
        range: `Control_Total_Fotos!F${rowNum}:I${rowNum}`,
        values: [["COMPLETADO", match.namePro, match.idPro, match.linkPro]]
      });
      console.log(`  -> Fila ${rowNum} vinculada: ${match.namePro}`);
    }
  }

  if (syncUpdates.length > 0) {
    const syncRes = await apiRequest('POST', `/v4/spreadsheets/${SPREADSHEET_ID}/values:batchUpdate`, {
      valueInputOption: "USER_ENTERED",
      data: syncUpdates
    });
    console.log(`[OK] ${syncRes.totalUpdatedRows} filas vinculadas en Control_Total_Fotos.`);
  }

  console.log("\nProceso finalizado exitosamente.");
}

main().catch(console.error);
