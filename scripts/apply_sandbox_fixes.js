const fs = require('fs');
const { execSync } = require('child_process');

const sheetId = '1kRsCZ7ZpPxyxrSEkUrYRl3NHahrQQche90RKK2yedQ8';

const updates = [
  // Row 2 (ID 28, Batch 1)
  {
    row: 2,
    origId: '1FbJY50m7dM-QBZ81pQfK4jRFazy3BX4m',
    proId: '1yRoaPAnM99ZCEbiVCa6Vn8hXcfF0Ci5V',
    rawId: '1rUTxON3dhX-aEK5VhqFYNoFGB1paqYpG'
  },
  // Row 3 (ID 418, Batch 1)
  {
    row: 3,
    origId: '1daSZANJ06M1oAoiGj3ax_UdSOUNYA856',
    proId: '1wESfHW8HYF3tUm5IM4ewnkbuJeeGSvZB',
    rawId: '1raZ3eZwV02mzN7oovNdWNz4hQoLfoDXx'
  },
  // Row 4 (ID 421, Batch 1)
  {
    row: 4,
    origId: '12XvgqScSlNtbTowfU28iaATUUUgvVS3m',
    proId: '1_WkHyVaY0s2lON7_dPJOjPmUbgbPsROR',
    rawId: '1NiMDAgHQJ4jA1KrkoxRn5Y7e3u_3mnZx'
  },
  // Row 5 (ID 423, Batch 1)
  {
    row: 5,
    origId: '1qeDrvd-WToWQhpi7huIKCQYzQVpb3pry',
    proId: '1_XokrYvZ5-VFAps71v02K-q9Ns_EZckw',
    rawId: '1UX6gilVcqENXEJ_FGKjiwq4AM8gmlICO'
  },
  // Row 6 (ID 424, Batch 1)
  {
    row: 6,
    origId: '17j63s--nF7fAcBhwyIsYUcgxLMFeT1Kl',
    proId: '1fyKG0ifHau7SSew3C9n6N_yxjM1u_iwu',
    rawId: '1swEs0yda-FjgFhiYwKAf-LQ7AgIVXhDh'
  },
  // Row 7 (ID 28, Batch 2)
  {
    row: 7,
    origId: '1FbJY50m7dM-QBZ81pQfK4jRFazy3BX4m',
    proId: '1Boipw4ZMadlw6VDTofTXw-jZ8mxpJhEA',
    rawId: '1rUTxON3dhX-aEK5VhqFYNoFGB1paqYpG'
  },
  // Row 8 (ID 418, Batch 2)
  {
    row: 8,
    origId: '1daSZANJ06M1oAoiGj3ax_UdSOUNYA856',
    proId: '1dm3IJYDtp0DXh9RiCm8-xEPYYUMR_Dfk',
    rawId: '1raZ3eZwV02mzN7oovNdWNz4hQoLfoDXx'
  },
  // Row 9 (ID 421, Batch 2 - Error API)
  {
    row: 9,
    origId: '12XvgqScSlNtbTowfU28iaATUUUgvVS3m',
    proId: '',
    rawId: ''
  },
  // Row 10 (ID 423, Batch 2)
  {
    row: 10,
    origId: '1qeDrvd-WToWQhpi7huIKCQYzQVpb3pry',
    proId: '1qQ0tHUNltS1rxma4e3mvxUSI-OFpHSDS',
    rawId: '1u79Gy2eK3l8vFaXZXpjfXJhnDiEneoer'
  },
  // Row 11 (ID 424, Batch 2)
  {
    row: 11,
    origId: '17j63s--nF7fAcBhwyIsYUcgxLMFeT1Kl',
    proId: '1ql7DwrxPiSleM8LnacDKdcIVRZekba3B',
    rawId: '1swEs0yda-FjgFhiYwKAf-LQ7AgIVXhDh'
  }
];

const batchOps = [];

updates.forEach(u => {
  const formulaOrig = u.origId ? `=IMAGE("https://lh3.googleusercontent.com/d/${u.origId}=s400")` : '';
  const formulaPro = u.proId ? `=IMAGE("https://lh3.googleusercontent.com/d/${u.proId}=s400")` : '';
  const linkPro = u.proId ? `https://drive.google.com/file/d/${u.proId}/view` : '';

  // Col M: Vista_Original, Col N: Vista_PRO_Test, Col O: ID_Drive_RAW, Col P: ID_Drive_Mesa, Col Q: Link_Drive_Mesa
  batchOps.push({
    op: 'write',
    range: `Registro_Pruebas_Sandbox!M${u.row}:Q${u.row}`,
    data: [[
      formulaOrig,
      formulaPro,
      u.rawId,
      u.proId,
      linkPro
    ]]
  });
});

const batchFilePath = 'C:\\Users\\LENOVO\\Documents\\Carlitos\\IA\\Antigravity\\Profesionalización de catálogo\\Cliente Marinera Power\\scripts\\batch_fix_sandbox.json';
fs.writeFileSync(batchFilePath, JSON.stringify(batchOps, null, 2), 'utf8');
console.log('Batch JSON written. Executing gsheets mutate batch...');

try {
  const out = execSync(`gsheets mutate batch ${sheetId} -f "${batchFilePath}"`).toString();
  console.log('Batch result:', out);
} catch (e) {
  console.error('Error executing batch:', e.message);
}
