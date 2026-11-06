import json
from pathlib import Path

brain_root = Path(r"C:\Users\LENOVO\.gemini\antigravity\brain")

matches = []
for p in brain_root.rglob("transcript.jsonl"):
    conv_id = p.parent.parent.name
    try:
        with open(p, "r", encoding="utf-8") as f:
            first_line = f.readline()
            if first_line:
                data = json.loads(first_line)
                content = data.get("content", "")
                # Buscar términos
                if "marinera" in content.lower() or "catálogo" in content.lower() or "profesionalización" in content.lower():
                    matches.append((conv_id, p, content[:150].replace("\n", " ")))
    except Exception:
        pass

print(f"Total conversaciones encontradas con Marinera / Catálogo: {len(matches)}")
for cid, p, c in matches:
    print(f"\nID: {cid}")
    print(f"  First prompt: {c}")
