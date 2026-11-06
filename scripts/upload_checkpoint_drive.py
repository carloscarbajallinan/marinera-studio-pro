import json, subprocess, sys
sys.stdout.reconfigure(encoding='utf-8')
from pathlib import Path

root = Path(r"C:\Users\LENOVO\Documents\Carlitos\IA\Antigravity\Profesionalización de catálogo\Cliente Marinera Power")
chk_path = root / "output" / "checkpoint_pipeline.json"

checkpoint = {
    "version": "V12_ATOMIC_CHECKPOINT",
    "last_update": "2026-11-05 23:50:00",
    "completed_ids": ["CANARY_1", "CANARY_3", "CANARY_4", "CANARY_5", "423", "418", "28", "424"],
    "quarantine_ids": ["CANARY_2", "421"],
    "canary_passed": True,
    "bucle_masivo_habilitado": False
}

with open(chk_path, 'w', encoding='utf-8') as f:
    json.dump(checkpoint, f, indent=2)

cmd = f'gdrive.cmd mutate upload "{chk_path}" --parent 1-nLdBpIPPbZXpzmOAxjpbkc39ykhl8K-'
subprocess.run(cmd, shell=True)
print("checkpoint_pipeline.json uploaded successfully!")
