import subprocess
import json
import time
from pathlib import Path

def list_folder(folder_id):
    cmd = ["gdrive", "readonly", "ls", folder_id, "--json", "--max", "0"]
    for attempt in range(3):
        res = subprocess.run(cmd, capture_output=True, text=True, shell=True)
        if res.returncode == 0:
            try:
                return json.loads(res.stdout)
            except Exception as e:
                print(f"Error parsing JSON for {folder_id}: {e}")
                return []
        else:
            print(f"Retry {attempt+1} for folder {folder_id}...")
            time.sleep(2)
    return []

def crawl_tree(root_id, root_name="Fotos catalogo"):
    print(f"Iniciando escaneo de: {root_name} ({root_id})")
    all_files = []
    all_folders = []
    
    # Cola de carpetas a explorar: (folder_id, current_path)
    queue = [(root_id, root_name)]
    
    while queue:
        current_id, current_path = queue.pop(0)
        items = list_folder(current_id)
        
        folder_count = 0
        file_count = 0
        for item in items:
            item_name = item.get("name", "")
            item_id = item.get("id", "")
            item_mime = item.get("mimeType", "")
            
            if item_mime == "application/vnd.google-apps.folder":
                subpath = f"{current_path} / {item_name}"
                all_folders.append({
                    "id": item_id,
                    "name": item_name,
                    "path": subpath,
                    "parent_id": current_id
                })
                queue.append((item_id, subpath))
                folder_count += 1
            else:
                all_files.append({
                    "id": item_id,
                    "name": item_name,
                    "mime_type": item_mime,
                    "folder_id": current_id,
                    "folder_path": current_path,
                    "size": item.get("size", "0"),
                    "link": f"https://drive.google.com/file/d/{item_id}/view"
                })
                file_count += 1
                
        print(f"  [{current_path}] -> {folder_count} subcarpetas, {file_count} archivos.")
        time.sleep(0.1) # Breve respiro para no saturar API
        
    print(f"Escaneo finalizado para {root_name}: Total {len(all_folders)} carpetas, {len(all_files)} archivos.")
    return {"folders": all_folders, "files": all_files}

if __name__ == "__main__":
    t0 = time.time()
    
    # 1. Escanear Fotos catalogo (ORIGINALES)
    origin_tree = crawl_tree("1SERKR606LbQEYkgLTgDB0f-pUoMhvNz4", "Fotos catalogo")
    with open("C:/Users/LENOVO/Documents/Carlitos/IA/Antigravity/Profesionalización de catálogo/Cliente Marinera Power/scripts/drive_origin_tree.json", "w", encoding="utf-8") as f:
        json.dump(origin_tree, f, indent=2)
        
    # 2. Escanear Fotos catalogo PRO (SALIDAS PRO)
    pro_tree = crawl_tree("1-nLdBpIPPbZXpzmOAxjpbkc39ykhl8K-", "Fotos catalogo PRO")
    with open("C:/Users/LENOVO/Documents/Carlitos/IA/Antigravity/Profesionalización de catálogo/Cliente Marinera Power/scripts/drive_pro_tree.json", "w", encoding="utf-8") as f:
        json.dump(pro_tree, f, indent=2)
        
    print(f"\nProceso completo en {time.time() - t0:.1f} segundos.")
