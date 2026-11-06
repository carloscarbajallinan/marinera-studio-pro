import json
from pathlib import Path

p = Path(r"C:\Users\LENOVO\.gemini\antigravity\brain\083d309e-943b-4129-bfb8-5900d687f400\.system_generated\logs\transcript.jsonl")

with open(p, "r", encoding="utf-8") as f:
    for line in f:
        d = json.loads(line)
        if d.get("type") == "USER_INPUT":
            print(f"\n[USER]: {d.get('content')[:300]}")
        elif d.get("type") == "PLANNER_RESPONSE" and d.get("content"):
            c = d.get('content')[:300].encode('ascii', errors='replace').decode('ascii')
            print(f"[AGENT]: {c.replace(chr(10), ' ')}")
