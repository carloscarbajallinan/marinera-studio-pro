const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

const repoDir = 'C:\\Users\\LENOVO\\Documents\\Carlitos\\IA\\Antigravity\\Profesionalización de catálogo\\Cliente Marinera Power';

[
  path.join(repoDir, 'index.html'),
  path.join(repoDir, 'docs', 'index.html')
].forEach(fPath => {
  if (!fs.existsSync(fPath)) return;
  let code = fs.readFileSync(fPath, 'utf8');

  // 1. Inyectar extractDriveId si no existe
  if (!code.includes('function extractDriveId(')) {
    const helperCode = `
    function extractDriveId(val) {
      if (!val || typeof val !== 'string') return '';
      const str = val.trim();
      if (str === '-' || str.endsWith('.jpg') || str.endsWith('.png') || str.endsWith('.jpeg')) {
        return '';
      }
      const match = str.match(/\\/d\\/([a-zA-Z0-9_-]{25,})/);
      if (match) return match[1];
      if (/^[a-zA-Z0-9_-]{25,}$/.test(str)) return str;
      return '';
    }
`;
    code = code.replace('// 2. LIVE FETCH FROM GOOGLE SHEETS', helperCode + '\n    // 2. LIVE FETCH FROM GOOGLE SHEETS');
  }

  // 2. Mejorar resolución de URLs en renderSandboxCards
  const oldSandboxLookup = `        const origProd = prodItems.find(p => String(p.ID) === String(idCat));
        const origId = origProd ? origProd.ID_Archivo_Original : (item.orig_drive_id || '1FbJY50m7dM-QBZ81pQfK4jRFazy3BX4m');
        const origUrl = origId ? \`https://lh3.googleusercontent.com/d/\${origId}=s600\` : 'https://placehold.co/600x600/121927/D4AF37?text=Original';
        const proUrl = driveMesaId ? \`https://lh3.googleusercontent.com/d/\${driveMesaId}=s600\` : (item.Link_Drive_Mesa || origUrl);`;

  const newSandboxLookup = `        const driveMesaId = extractDriveId(item.ID_Drive_Mesa) || extractDriveId(item.Link_Drive_Mesa) || extractDriveId(item.Vista_PRO_Test);
        const origProd = prodItems.find(p => String(p.ID) === String(idCat));
        const origId = extractDriveId(item.Vista_Original) || (origProd ? extractDriveId(origProd.ID_Archivo_Original) : '') || extractDriveId(item.orig_drive_id) || '1FbJY50m7dM-QBZ81pQfK4jRFazy3BX4m';
        const origUrl = origId ? \`https://lh3.googleusercontent.com/d/\${origId}=s600\` : 'https://placehold.co/600x600/121927/D4AF37?text=Original';
        const proUrl = driveMesaId ? \`https://lh3.googleusercontent.com/d/\${driveMesaId}=s600\` : (resVisual.includes('ERROR') ? 'https://placehold.co/600x600/1e293b/ef4444?text=Error+API+Gemini' : origUrl);`;

  if (code.includes('const driveMesaId = item.ID_Drive_Mesa || \'\';')) {
    code = code.replace('const driveMesaId = item.ID_Drive_Mesa || \'\';\n\n' + oldSandboxLookup, newSandboxLookup);
  }

  // 3. Auto-sync y auto-refresh en DOMContentLoaded
  const oldDomLoaded = `    // INITIAL LOAD
    window.addEventListener('DOMContentLoaded', () => {
      updateCounters();
      renderSandboxCards();
      renderProductionView();
    });`;

  const newDomLoaded = `    // INITIAL LOAD CON AUTO-SYNC EN VIVO Y POLLING CADA 25s
    window.addEventListener('DOMContentLoaded', () => {
      updateCounters();
      renderSandboxCards();
      renderProductionView();
      // Consulta en vivo inmediata al cargar
      syncLiveFromGoogleSheets();
      // Auto-actualización periódica en segundo plano
      setInterval(syncLiveFromGoogleSheets, 25000);
    });`;

  if (code.includes(oldDomLoaded)) {
    code = code.replace(oldDomLoaded, newDomLoaded);
  }

  fs.writeFileSync(fPath, code, 'utf8');
  console.log(`Patched JavaScript in ${fPath}`);
});

try {
  execSync('git add docs/ index.html', { cwd: repoDir });
  execSync('git commit -m "feat(ui): auto-sync en vivo cada 25s y extractor infalible de Google Drive IDs"', { cwd: repoDir });
  execSync('git push origin main:master', { cwd: repoDir });
  console.log('Pushed JS patch to GitHub Pages!');
} catch (e) {
  console.log('Git output:', e.message);
}
