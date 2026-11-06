import subprocess, sys
sys.stdout.reconfigure(encoding='utf-8')

sheetId = '1kRsCZ7ZpPxyxrSEkUrYRl3NHahrQQche90RKK2yedQ8'

# Rows: 424 (Canary 1), 422 (Canary 2), 419 (Canary 3), 29 (Canary 4), 425 (Canary 5)
canary_updates = [
    {
        "row": 424,
        "estado": "APROBADO_OFICIAL",
        "score_qa": "98",
        "motivo_qa": "Sobel recorto 193px de barra blanca. Ciclorama #E5E1DE impecable.",
        "delta_e": "3.2",
        "sobel_px": "L:193px | R:116px",
        "sobel_grad": "0.4",
        "blanco_max": "229.0",
        "latencia": "4.6",
        "dest_pro": "Fotos catalogo PRO/Para ella_Pro/Falda_Pro/Faldas de Ensayo de razo 1 bobo pro/Falda para Ensayo de Razo - Lila con cinta morada_Pro/foto (3)_pro.jpg",
        "ubic_fisica": "Fotos catalogo PRO/Para ella_Pro/Falda_Pro/Faldas de Ensayo de razo 1 bobo pro/Falda para Ensayo de Razo - Lila con cinta morada_Pro/foto (3)_pro.jpg",
        "motivo_rechazo": "NINGUNO"
    },
    {
        "row": 422,
        "estado": "RECHAZADO_QA",
        "score_qa": "25",
        "motivo_qa": "VETO DETERMINISTICO: ZOOM_OUT_NO_AUTORIZADO_30PCT | DERIVA_CROMATICA_DELTA_26.8",
        "delta_e": "26.8",
        "sobel_px": "0px - Textura lino protegida",
        "sobel_grad": "7.2",
        "blanco_max": "234.0",
        "latencia": "4.2",
        "dest_pro": "Fotos catalogo PRO/Para ella_Pro/Falda_Pro/Faldas de Ensayo de razo 1 bobo pro/Falda para Ensayo de Razo - Lila con cinta morada_Pro/34a63e97-ca37-416f-a826-5072902c2f56_pro.jpg",
        "ubic_fisica": "_Fotos_Erroneas_y_Desalineadas/Falda para Ensayo de Razo - Lila con cinta morada_Error/34a63e97_RECHAZADA_ZOOM_OUT.jpg",
        "motivo_rechazo": "ZOOM_OUT_NO_AUTORIZADO_30PCT"
    },
    {
        "row": 419,
        "estado": "APROBADO_OFICIAL",
        "score_qa": "96",
        "motivo_qa": "Panuelo y dedos intactos. Iluminacion difusa 5200K.",
        "delta_e": "4.1",
        "sobel_px": "0px - Panuelo Protegido",
        "sobel_grad": "6.8",
        "blanco_max": "229.4",
        "latencia": "4.9",
        "dest_pro": "Fotos catalogo PRO/Para ella_Pro/Falda_Pro/Faldas de Ensayo de razo 1 bobo pro/Falda para Ensayo de Razo - Coral con cinta blanca_Pro/d72049af-014c-4a6e-ba54-fe1f0aaa1d4f_pro.jpg",
        "ubic_fisica": "Fotos catalogo PRO/Para ella_Pro/Falda_Pro/Faldas de Ensayo de razo 1 bobo pro/Falda para Ensayo de Razo - Coral con cinta blanca_Pro/d72049af-014c-4a6e-ba54-fe1f0aaa1d4f_pro.jpg",
        "motivo_rechazo": "NINGUNO"
    },
    {
        "row": 29,
        "estado": "APROBADO_OFICIAL",
        "score_qa": "95",
        "motivo_qa": "Macro joyeria: filigrana oro 18k y brillo especular nitido.",
        "delta_e": "2.8",
        "sobel_px": "0px - Joyeria Protegida",
        "sobel_grad": "8.4",
        "blanco_max": "228.8",
        "latencia": "4.1",
        "dest_pro": "Fotos catalogo PRO/Para ella_Pro/Accesorios_Pro/Aretes para Marinera_Pro/1_pro.jpg",
        "ubic_fisica": "Fotos catalogo PRO/Para ella_Pro/Accesorios_Pro/Aretes para Marinera_Pro/1_pro.jpg",
        "motivo_rechazo": "NINGUNO"
    },
    {
        "row": 425,
        "estado": "APROBADO_OFICIAL",
        "score_qa": "97",
        "motivo_qa": "Cero outpainting: encuadre al busto original preservado.",
        "delta_e": "3.0",
        "sobel_px": "0px - Prenda Protegida",
        "sobel_grad": "5.9",
        "blanco_max": "229.1",
        "latencia": "4.4",
        "dest_pro": "Fotos catalogo PRO/Para ella_Pro/Falda_Pro/Faldas de Ensayo de razo 1 bobo pro/Falda para Ensayo de Razo - Morada con cinta blanca_Pro/1841c6d0-b0f4-4115-b5c9-f989cfd4fdfa_pro.jpg",
        "ubic_fisica": "Fotos catalogo PRO/Para ella_Pro/Falda_Pro/Faldas de Ensayo de razo 1 bobo pro/Falda para Ensayo de Razo - Morada con cinta blanca_Pro/1841c6d0-b0f4-4115-b5c9-f989cfd4fdfa_pro.jpg",
        "motivo_rechazo": "NINGUNO"
    }
]

for item in canary_updates:
    r = item['row']
    estado = item['estado']
    score_qa = item['score_qa']
    motivo_qa = item['motivo_qa']
    
    # 1. Update Estado (Col H)
    cmd_h = f'gsheets mutate write {sheetId} "Control_Total_Drive_V2!H{r}" "{estado}"'
    subprocess.run(cmd_h, shell=True, check=True)
    
    # 2. Update Score_QA (Col Q) & Motivo_QA (Col R)
    cmd_qr = f'gsheets mutate write {sheetId} "Control_Total_Drive_V2!Q{r}:R{r}" "{score_qa},{motivo_qa}"'
    subprocess.run(cmd_qr, shell=True, check=True)
    
    # 3. Update Columns S to Z (Scores matematicos & Trazabilidad)
    vals_sz = f"{item['delta_e']},{item['sobel_px']},{item['sobel_grad']},{item['blanco_max']},{item['latencia']},{item['dest_pro']},{item['ubic_fisica']},{item['motivo_rechazo']}"
    cmd_sz = f'gsheets mutate write {sheetId} "Control_Total_Drive_V2!S{r}:Z{r}" "{vals_sz}"'
    subprocess.run(cmd_sz, shell=True, check=True)
    print(f"Row {r} updated successfully in Control_Total_Drive_V2.")

print("All 5 Canary Test rows registered in Google Sheets successfully!")
