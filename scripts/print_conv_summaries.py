import json
from pathlib import Path

def print_conv(cid):
    p = Path(r"C:\Users\LENOVO\.gemini\antigravity\brain") / cid / ".system_generated" / "logs" / "transcript.jsonl"
    print("="*60)
    print("CONVERSATION:", cid)
    with open(p, "r", encoding="utf-8") as f:
        for line in f:
            d = json.loads(line)
            if d.get("type") in ["USER_INPUT"]:
                print(f"USER ({d.get('created_at')}): {d.get('content')[:150]}")
            elif d.get("type") == "PLANNER_RESPONSE" and d.get("content"):
                print(f"AGENT ({d.get('created_at')}): {d.get('content')[:200].replace(chr(10), ' ')}")

print_conv("083d309e-943b-4129-bfb8-5900d687f400")
print_conv("e283df04-078c-487f-8f29-5245acfbf0d3")
print_conv("e6ec4803-103e-4594-a773-9b73de295c10")
