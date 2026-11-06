import subprocess
from pathlib import Path

root = Path(r"C:\Users\LENOVO\Documents\Carlitos\IA\Antigravity\Profesionalización de catálogo\Cliente Marinera Power")
canary_dir = root / "docs" / "canary"
canary_dir.mkdir(parents=True, exist_ok=True)

downloads = [
    # Originals
    ("1qeDrvd-WToWQhpi7huIKCQYzQVpb3pry", canary_dir / "canary_1_orig.png"),
    ("12XvgqScSlNtbTowfU28iaATUUUgvVS3m", canary_dir / "canary_2_orig.jpg"),
    ("1daSZANJ06M1oAoiGj3ax_UdSOUNYA856", canary_dir / "canary_3_orig.jpg"),
    ("1FbJY50m7dM-QBZ81pQfK4jRFazy3BX4m", canary_dir / "canary_4_orig.jpg"),
    ("17j63s--nF7fAcBhwyIsYUcgxLMFeT1Kl", canary_dir / "canary_5_orig.jpg"),
    # PROs
    ("1S2rDiJk3Zfq21ubYBX-vqywJ-SC-XtEJ", canary_dir / "canary_1_pro.jpg"),
    ("1Kd1sSmPlKhxYJ9rKoD6yaHfJxHHfP36i", canary_dir / "canary_2_pro.jpg"),
    ("12x3fZK-fBXOl_3E9s_DJJsoefXH7GuO0", canary_dir / "canary_3_pro.jpg"),
    ("1RqMdROIcAd9tXEFaJegCVTGeAj2AK7iZ", canary_dir / "canary_4_pro.jpg"),
    ("1FlZ112AaTsWvavrEeAZJ2YyjK6JmxLeW", canary_dir / "canary_5_pro.jpg"),
]

for file_id, dest in downloads:
    if not dest.exists():
        print(f"Downloading {dest.name}...")
        cmd = f'gdrive.cmd readonly download {file_id} --out "{dest}"'
        subprocess.run(cmd, shell=True, capture_output=True)
    else:
        print(f"Already exists: {dest.name}")

print("Canary assets downloaded successfully!")
