import json
from pathlib import Path

brain_root = Path(r"C:\Users\LENOVO\.gemini\antigravity\brain")

for conv_dir in brain_root.iterdir():
    if conv_dir.is_dir() and conv_dir.name not in ["tempmediaStorage"]:
        transcript_path = conv_dir / ".system_generated" / "logs" / "transcript.jsonl"
        if transcript_path.exists():
            try:
                with open(transcript_path, "r", encoding="utf-8") as f:
                    for line in f:
                        if "📸" in line or "Profesionalización de Catálogo" in line:
                            data = json.loads(line)
                            content = data.get("content", "")
                            print("="*60)
                            print(f"Found in Conv ID: {conv_dir.name}")
                            print(f"Type: {data.get('type')} | Created: {data.get('created_at')}")
                            print(f"Preview: {content[:300].replace('\n', ' ')}")
                            break
            except Exception as e:
                pass
