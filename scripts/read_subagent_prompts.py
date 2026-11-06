import json

transcript_path = r"C:\Users\LENOVO\.gemini\antigravity\brain\962e4442-d376-4718-bf2b-1847cdd964db\.system_generated\logs\transcript.jsonl"

with open(transcript_path, "r", encoding="utf-8") as f:
    for line in f:
        data = json.loads(line)
        tool_calls = data.get("tool_calls", [])
        for tc in tool_calls:
            if tc.get("name") == "invoke_subagent":
                args = tc.get("args", {})
                print("Role:", args.get("Role"))
                print("TypeName:", args.get("TypeName"))
                print("Prompt:\n", args.get("Prompt"))
                print("="*60)
