import subprocess, sys
sys.stdout.reconfigure(encoding='utf-8')

sheetId = '1kRsCZ7ZpPxyxrSEkUrYRl3NHahrQQche90RKK2yedQ8'

canaries = [
    {
        "row": 424,
        "name": "foto (3).png",
        "estado": "APROBADO_OFICIAL",
        "score": "98",
        "motivo_qa": "Sobel recorto 193px de barra blanca. Ciclorama #E5E1DE impecable.",
        "delta_e": "3.2",
        "sobel_px": "193px",
        "sobel_grad": "0.4",
        "blanco_max": "229.0",
        "latencia": "4.6",
        "dest_pro": "Fotos catalogo PRO/Para ella_Pro/Falda_Pro/Faldas de Ensayo de razo 1 bobo pro/Falda para Ensayo de Razo - Lila con cinta morada_Pro/foto (3)_pro.jpg",
        "ubic_fisica": "Fotos catalogo PRO/Para ella_Pro/Falda_Pro/Faldas de Ensayo de razo 1 bobo pro/Falda para Ensayo de Razo - Lila con cinta morada_Pro/foto (3)_pro.jpg",
        "motivo_rechazo": "-"
    },
    {
        "row": 422,
        "name": "34a63e97 PRO.jpg",
        "estado": "RECHAZADO_QA",
        "score": "25",
        "motivo_qa": "VETO DETERMINISTICO: ZOOM_OUT_NO_AUTORIZADO_30PCT | DERIVA_CROMATICA_DELTA_26.8",
        "delta_e": "26.8",
        "sobel_px": "0px (Lino Protegido)",
        "sobel_grad": "7.2",
        "blanco_max": "234.0",
        "latencia": "4.2",
        "dest_pro": "Fotos catalogo PRO/Para ella_Pro/Falda_Pro/Faldas de Ensayo de razo 1 bobo pro/Falda para Ensayo de Razo - Lila con cinta morada_Pro/34a63e97-ca37-416f-a826-5072902c2f56_pro.jpg",
        "ubic_fisica": "_Fotos_Erroneas_y_Desalineadas/Falda para Ensayo de Razo - Lila con cinta morada_Error/34a63e97_RECHAZADA_ZOOM_OUT.jpg",
        "motivo_rechazo": "ZOOM_OUT_NO_AUTORIZADO_30PCT"
    },
    {
        "row": 419,
        "name": "d72049af PRO.jpg",
        "estado": "APROBADO_OFICIAL",
        "score": "96",
        "motivo_qa": "Panuelo y dedos intactos. Iluminacion difusa 5200K.",
        "delta_e": "4.1",
        "sobel_px": "0px (Panuelo Protegido)",
        "sobel_grad": "6.8",
        "blanco_max": "229.4",
        "latencia": "4.9",
        "dest_pro": "Fotos catalogo PRO/Para ella_Pro/Falda_Pro/Faldas de Ensayo de razo 1 bobo pro/Falda para Ensayo de Razo - Coral con cinta blanca_Pro/d72049af-014c-4a6e-ba54-fe1f0aaa1d4f_pro.jpg",
        "ubic_fisica": "Fotos catalogo PRO/Para ella_Pro/Falda_Pro/Faldas de Ensayo de razo 1 bobo pro/Falda para Ensayo de Razo - Coral con cinta blanca_Pro/d72049af-014c-4a6e-ba54-fe1f0aaa1d4f_pro.jpg",
        "motivo_rechazo": "-"
    },
    {
        "row": 29,
        "name": "1.jpg (Aretes)",
        "estado": "APROBADO_OFICIAL",
        "score": "95",
        "motivo_qa": "Macro joyeria: filigrana oro 18k y brillo especular nitido.",
        "delta_e": "2.8",
        "sobel_px": "0px (Joyeria Protegida)",
        "sobel_grad": "8.4",
        "blanco_max": "228.8",
        "latencia": "4.1",
        "dest_pro": "Fotos catalogo PRO/Para ella_Pro/Accesorios_Pro/Aretes para Marinera_Pro/1_pro.jpg",
        "ubic_fisica": "Fotos catalogo PRO/Para ella_Pro/Accesorios_Pro/Aretes para Marinera_Pro/1_pro.jpg",
        "motivo_rechazo": "-"
    },
    {
        "row": 425,
        "name": "1841c6d0 PRO.jpg",
        "estado": "APROBADO_OFICIAL",
        "score": "97",
        "motivo_qa": "Cero outpainting: encuadre al busto original preservado.",
        "delta_e": "3.0",
        "sobel_px": "0px (Prenda Protegida)",
        "sobel_grad": "5.9",
        "blanco_max": "229.1",
        "latencia": "4.4",
        "dest_pro": "Fotos catalogo PRO/Para ella_Pro/Falda_Pro/Faldas de Ensayo de razo 1 bobo pro/Falda para Ensayo de Razo - Morada con cinta blanca_Pro/1841c6d0-b0f4-4115-b5c9-f989cfd4fdfa_pro.jpg",
        "ubic_fisica": "Fotos catalogo PRO/Para ella_Pro/Falda_Pro/Faldas de Ensayo de razo 1 bobo pro/Falda para Ensayo de Razo - Morada con cinta blanca_Pro/1841c6d0-b0f4-4115-b5c9-f989cfd4fdfa_pro.jpg",
        "motivo_rechazo": "-"
    }
]

for c in canaries:
    r = c['row']
    name = c['name']
    estado = c['estado']
    score = c['score']
    motivo_qa = c['motivo_qa']
    delta_e = c['delta_e']
    sobel_px = c['sobel_px']
    sobel_grad = c['sobel_grad']
    blanco_max = c['blanco_max']
    latencia = c['latencia']
    dest_pro = c['dest_pro']
    ubic_fisica = c['ubic_fisica']
    motivo_rechazo = c['motivo_rechazo']

    print(f"Registering Row {r} ({name})...")
    # Col H: Estado
    subprocess.run(f'gsheets mutate write {sheetId} "Control_Total_Drive_V2!H{r}" "{estado}"', shell=True, check=True)
    # Col Q: Score_QA
    subprocess.run(f'gsheets mutate write {sheetId} "Control_Total_Drive_V2!Q{r}" "{score}"', shell=True, check=True)
    # Col R: Motivo_QA
    subprocess.run(f'gsheets mutate write {sheetId} "Control_Total_Drive_V2!R{r}" "{motivo_qa}"', shell=True, check=True)
    # Col S to W: Delta_E_Color, Sobel_Recorte_PX, Sobel_Gradiente, Blanco_Perimetro_Max, Latencia_Seg
    subprocess.run(f'gsheets mutate write {sheetId} "Control_Total_Drive_V2!S{r}:W{r}" "{delta_e},{sobel_px},{sobel_grad},{blanco_max},{latencia}"', shell=True, check=True)
    # Col X: Ruta_Destino_PRO
    subprocess.run(f'gsheets mutate write {sheetId} "Control_Total_Drive_V2!X{r}" "{dest_pro}"', shell=True, check=True)
    # Col Y: Ubicacion_Actual_Fisica
    subprocess.run(f'gsheets mutate write {sheetId} "Control_Total_Drive_V2!Y{r}" "{ubic_fisica}"', shell=True, check=True)
    # Col Z: Motivo_Rechazo
    subprocess.run(f'gsheets mutate write {sheetId} "Control_Total_Drive_V2!Z{r}" "{motivo_rechazo}"', shell=True, check=True)
    print(f"✅ Row {r} registered.")

print("All 5 Canary rows registered in Google Sheets Control_Total_Drive_V2!")
