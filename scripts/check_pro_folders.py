import subprocess
import json

def get_folders(parent_id, path=""):
    cmd = ["gdrive", "readonly", "ls", parent_id, "--json", "--max", "0"]
    res = subprocess.run(cmd, capture_output=True, text=True, shell=True)
    if res.returncode != 0:
        return []
    try:
        items = json.loads(res.stdout)
    except:
        return []
    folders = []
    for it in items:
        if it.get("mimeType") == "application/vnd.google-apps.folder":
            subpath = f"{path} / {it['name']}"
            folders.append({"id": it["id"], "path": subpath, "name": it["name"]})
            folders.extend(get_folders(it["id"], subpath))
    return folders

all_f = get_folders("1-nLdBpIPPbZXpzmOAxjpbkc39ykhl8K-", "Fotos catalogo PRO")
print(f"Total PRO folders now: {len(all_f)}")
for f in all_f[:20]:
    print(" ", f["path"])

with open("pro_folders_latest.json", "w", encoding="utf-8") as out:
    json.dump(all_f, out, indent=2, ensure_ascii=False)
