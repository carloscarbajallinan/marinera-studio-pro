import subprocess, json, sys
sys.stdout.reconfigure(encoding='utf-8')

canaries = [
    ('28', '1FbJY50m7dM-QBZ81pQfK4jRFazy3BX4m', 'Aretes'),
    ('418', '1daSZANJ06M1oAoiGj3ax_UdSOUNYA856', 'Falda Coral'),
    ('421', '12XvgqScSlNtbTowfU28iaATUUUgvVS3m', 'Falda Lila 34a6'),
    ('423', '1qeDrvd-WToWQhpi7huIKCQYzQVpb3pry', 'Falda Lila foto(3)'),
    ('424', '17j63s--nF7fAcBhwyIsYUcgxLMFeT1Kl', 'Falda Morada 1841')
]

print("VERIFICANDO ACCESO DIRECTO DRIVE API PARA CADA ID CANARY:")
for c_id, drive_id, desc in canaries:
    try:
        out = subprocess.check_output(f'gdrive readonly info {drive_id}', shell=True, text=True)
        name_line = [l for l in out.splitlines() if 'Name:' in l][0]
        size_line = [l for l in out.splitlines() if 'Size:' in l][0]
        print(f"✅ ID {c_id} ({desc}): {name_line.strip()} | {size_line.strip()} | Drive ID: {drive_id}")
    except Exception as e:
        print(f"❌ ID {c_id} ({desc}): Error {e}")
