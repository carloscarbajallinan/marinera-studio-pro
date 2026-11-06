import json

transcript_path = r"C:\Users\LENOVO\.gemini\antigravity\brain\962e4442-d376-4718-bf2b-1847cdd964db\.system_generated\logs\transcript.jsonl"

with open(transcript_path, "r", encoding="utf-8") as f:
    for idx, line in enumerate(f):
        data = json.loads(line)
        if data.get("type") == "PLANNER_RESPONSE":
            tc_names = [tc.get("name") for tc in data.get("tool_calls", [])]
            if "invoke_subagent" in tc_names:
                print(f"Line {idx}: step {data.get('step_index')} invoked subagents: {len(tc_names)}")
                for tc in data.get("tool_calls", []):
                    if tc.get("name") == "invoke_subagent":
                        print("  Arg:", tc.get("args", {}).get("Role"))
