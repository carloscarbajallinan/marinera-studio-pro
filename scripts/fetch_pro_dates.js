const fs = require('fs');
const path = require('path');
const { exec } = require('child_process');

const proPath = path.join(__dirname, 'drive_pro_tree.json');
const pro = JSON.parse(fs.readFileSync(proPath, 'utf8'));

// Fetch info for each PRO file
async function fetchInfo(id) {
  return new Promise((resolve) => {
    exec(`gdrive readonly info ${id} --json`, (err, stdout) => {
      if (err) {
        resolve({ id, error: true });
      } else {
        try {
          resolve(JSON.parse(stdout));
        } catch (e) {
          resolve({ id, error: true });
        }
      }
    });
  });
}

async function run() {
  console.log(`Fetching Drive metadata for ${pro.files.length} PRO files...`);
  const results = [];
  const concurrency = 15;
  
  for (let i = 0; i < pro.files.length; i += concurrency) {
    const chunk = pro.files.slice(i, i + concurrency);
    const chunkResults = await Promise.all(chunk.map(f => fetchInfo(f.id)));
    results.push(...chunkResults);
    process.stdout.write(`\rProgress: ${results.length}/${pro.files.length}`);
  }
  console.log('\nDone fetching metadata.');

  // Save to file
  const outPath = path.join(__dirname, 'pro_files_metadata.json');
  fs.writeFileSync(outPath, JSON.stringify(results, null, 2), 'utf8');
  console.log(`Saved to ${outPath}`);

  // Summary analysis
  const dateHistogram = {};
  const ownerHistogram = {};
  for (const r of results) {
    if (r.error) continue;
    const dateStr = (r.createdTime || r.modifiedTime || '').slice(0, 10);
    dateHistogram[dateStr] = (dateHistogram[dateStr] || 0) + 1;

    const owner = (r.owners && r.owners[0] && r.owners[0].displayName) || 'Unknown';
    ownerHistogram[owner] = (ownerHistogram[owner] || 0) + 1;
  }

  console.log('\n=== PRO FILES CREATION/UPLOAD DATES ===');
  for (const [d, count] of Object.entries(dateHistogram).sort()) {
    console.log(`${d}: ${count} files`);
  }

  console.log('\n=== PRO FILES OWNERS ===');
  for (const [o, count] of Object.entries(ownerHistogram)) {
    console.log(`${o}: ${count} files`);
  }
}

run();
