const fs = require('fs');
const path = require('path');
const { exec } = require('child_process');

const origPath = path.join(__dirname, 'drive_origin_tree.json');
const orig = JSON.parse(fs.readFileSync(origPath, 'utf8'));

// Sample 150 origin files across categories
const sampledOrig = [];
const step = Math.max(1, Math.floor(orig.files.length / 150));
for (let i = 0; i < orig.files.length; i += step) {
  sampledOrig.push(orig.files[i]);
}

async function fetchInfo(id) {
  return new Promise((resolve) => {
    exec(`gdrive readonly info ${id} --json`, (err, stdout) => {
      if (err) resolve({ id, error: true });
      else {
        try { resolve(JSON.parse(stdout)); }
        catch (e) { resolve({ id, error: true }); }
      }
    });
  });
}

async function run() {
  console.log(`Sampling ${sampledOrig.length} origin files for date analysis...`);
  const results = [];
  const concurrency = 15;
  for (let i = 0; i < sampledOrig.length; i += concurrency) {
    const chunk = sampledOrig.slice(i, i + concurrency);
    const chunkResults = await Promise.all(chunk.map(f => fetchInfo(f.id)));
    results.push(...chunkResults);
    process.stdout.write(`\rProgress: ${results.length}/${sampledOrig.length}`);
  }
  console.log('\nDone fetching origin sample metadata.');

  const dateHistogram = {};
  const ownerHistogram = {};
  for (const r of results) {
    if (r.error) continue;
    const dateStr = (r.createdTime || r.modifiedTime || '').slice(0, 10);
    dateHistogram[dateStr] = (dateHistogram[dateStr] || 0) + 1;
    const owner = (r.owners && r.owners[0] && r.owners[0].displayName) || 'Unknown';
    ownerHistogram[owner] = (ownerHistogram[owner] || 0) + 1;
  }

  console.log('\n=== ORIGIN FILES CREATION/UPLOAD DATES (SAMPLE) ===');
  for (const [d, count] of Object.entries(dateHistogram).sort()) {
    console.log(`${d}: ${count} files`);
  }

  console.log('\n=== ORIGIN FILES OWNERS (SAMPLE) ===');
  for (const [o, count] of Object.entries(ownerHistogram)) {
    console.log(`${o}: ${count} files`);
  }
}

run();
