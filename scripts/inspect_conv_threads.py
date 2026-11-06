import json
from pathlib import Path

convs = [
    "962e4442-d376-4718-bf2b-1847cdd964db",
    "e6ec4803-103e-4594-a773-9b73de295c10",
    "e283df04-078c-487f-8f29-5245acfbf0d3",
    "9fb61915-1c5d-4f86-81e1-814fd0fee077",
    "9fafa467-c0f1-4daa-8568-f84dce8c64ca"
]

brain_root = Path(r"C:\Users\LENOVO\.gemini\antigravity\brain")

for cid in convs:
    p = brain_root / cid / ".system_generated" / "logs" / "transcript.jsonl"
    if p.exists():
        print("="*70)
        print("CONVERSATION:", cid)
        with open(p, "r", encoding="utf-8") as f:
            for line in f:
                d = json.loads(line)
                if d.get("type") == "USER_INPUT":
                    c = d.get("content", "").replace("\n", " ")
                    print(f"  [{d.get('created_at')}] USER: {c[:120]}")
