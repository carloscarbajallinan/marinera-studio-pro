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
                        data = json.loads(line)
                        if data.get("type") == "USER_INPUT":
                            content = data.get("content", "")
                            if any(k in content.lower() for k in ["profesionalizaci", "marinera", "ventana de contexto", "consumo"]):
                                print("="*60)
                                print(f"Conv ID: {conv_dir.name}")
                                print(f"Prompt: {content[:250].strip()}")
                                break
            except Exception:
                pass
