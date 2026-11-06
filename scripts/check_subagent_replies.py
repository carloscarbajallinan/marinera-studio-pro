import json

transcript_path = r"C:\Users\LENOVO\.gemini\antigravity\brain\962e4442-d376-4718-bf2b-1847cdd964db\.system_generated\logs\transcript.jsonl"

with open(transcript_path, "r", encoding="utf-8") as f:
    lines = f.readlines()

for idx in [176, 177, 178, 179, 180, 181, 182, 183, 184, 185, 186, 187]:
    if idx < len(lines):
        data = json.loads(lines[idx])
        print(f"Line {idx} | Source: {data.get('source')} | Type: {data.get('type')}")
        content = data.get("content", "")
        if content:
            print("  Content preview:", content[:200].replace("\n", " "))
        tc = data.get("tool_calls", [])
        if tc:
            print("  Tool calls:", [t.get("name") for t in tc])
