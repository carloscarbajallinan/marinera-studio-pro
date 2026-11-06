# 📜 ESTÁNDARES OFICIALES DE EDICIÓN: MARINERA POWER
**Documento Normativo Maestro de Calidad y Ejecución Industrial**  
**Última Actualización:** 5 de Noviembre de 2026

---

## 1. Regla de Oro del Sujeto (Tamaño, Posición y Pose)
* **La persona o producto debe quedar exactamente donde está:** Con el mismo tamaño de cuerpo, en la misma posición dentro del encuadre y con la misma pose exacta que tiene en la foto original (brazos alzados, pañuelo arriba, falda extendida).
* **Prohibido alejar la cámara o achicar a la persona:** La persona NO debe verse como una miniatura ni lejos al fondo de una habitación vacía.
* **Prohibido alterar la pose:** No le pidas a la IA que imite poses de otras fotos de referencia; debe mantener exactamente la pose original.
* **Cero Outpainting en Encuadres Cortados:** Si la foto viene cortada al busto o cintura, mantén ese corte idéntico. Queda prohibido inventar piernas, caderas o extremidades fuera de campo.
* **Bloqueo Estricto de Relación de Aspecto:** La imagen generada debe mantener exactamente la misma proporción del lienzo original. Si la entrada es 9:16, la salida debe ser 9:16. Prohibido recortar o deformar las proporciones del lienzo.

---

## 2. Regla del Fondo, Piso y Joyas
* **Fondo:** Cambia únicamente lo que rodea al sujeto por un fondo de estudio liso y parejo en color gris claro (#E5E1DE / RGB: 229, 225, 222).
* **Piso Limpio:** Si la foto original tiene piso de madera, parquet o baldosas, bórralo por completo y pon piso liso del mismo gris claro. Renderiza únicamente una sombra suave y transparente bajo los pies. Prohibido dejar manchas oscuras o aspecto de piso sucio.
* **Aretes Rectos y Simétricos:** Los aretes de filigrana deben colgar rectos y simétricos como en la foto original. Prohibido torcerlos o doblar los ganchos.
* **Pañuelo Íntegro:** El pañuelo blanco de marinera debe mantener su calado y puntas completas sin recortes ni deformaciones.

---

## 3. Límite de Reprocesos y Captura Obligatoria de Tokens
* **Máximo 1 Reproceso por Imagen:** Cada archivo tiene un límite estricto de 1 reintento. Si falla tras el primer reintento, el script salta inmediatamente al siguiente archivo sin trabar el lote.
* **Principio de Cero Pérdida de Tokens:** Si se invocó la API de Gemini y se generó una imagen nueva, **esa imagen DEBE ser capturada y guardada en Google Drive en todos los casos**.
  * Si la imagen aprueba el post-control: Se guarda en `Fotos catalogo PRO/<Subcarpeta>_Pro/`.
  * Si la imagen reprueba el post-control o tiene defectos: Se guarda en `_Fotos_Erroneas_y_Desalineadas/<Subcarpeta>_Error/`.
  * **Prohibido desechar en memoria imágenes generadas por las que ya se pagaron tokens.** Todo resultado generado se archiva con su ID y enlace en Sheets.

---

## 4. Rutas Físicas en Google Drive
* **Carpeta Base Origen:**  
  📁 `/content/drive/MyDrive/Emprendimiento/Marinera power 2026/Fotos catalogo/`  
  *(ID: `1SERKR606LbQEYkgLTgDB0f-pUoMhvNz4`)*
* **Carpeta Salida Aprobadas:** `Fotos catalogo PRO/` *(ID: `1-nLdBpIPPbZXpzmOAxjpbkc39ykhl8K-`)*
* **Carpeta Cuarentena Rechazadas:** `_Fotos_Erroneas_y_Desalineadas/` *(ID: `16wT0ogNsfd-r2U1bGuuw01Rdxj269bxW`)*

---

## 5. Registro Permanente en Google Sheets ('Control_Total_Drive_V2')
Spreadsheet ID: `1kRsCZ7ZpPxyxrSEkUrYRl3NHahrQQche90RKK2yedQ8`.  
Cada foto procesada debe registrar en sus columnas dedicadas:
* `Estado`: `APROBADO_OFICIAL` o `RECHAZADO_QA`.
* `Ruta_Destino_PRO`: Dónde debería estar en `Fotos catalogo PRO`.
* `Ubicacion_Actual_Fisica`: Dónde quedó guardada realmente (en `_Pro` o en `_Fotos_Erroneas_y_Desalineadas`).
* `Motivo_Rechazo`: Causa exacta (`MODELO_ENCOGIDA`, `PISO_SUCIO`, `ARETE_TORCIDO`, `DERIVA_COLOR`, etc.).
* `Delta_E_Color`: Desviación numérica calculada frente a #E5E1DE en las 4 esquinas.
* `Sobel_Recorte_PX`: Píxeles recortados en bordes.
* `Version_Prompt`: Versión del prompt utilizada.
* `Fórmula Imagen`: `=IMAGE("https://lh3.googleusercontent.com/d/{ID}=s400")`.

---

## 6. Seguridad Operativa y Control de Ejecución en Colab
* **Backup Obligatorio:** Antes de ejecutar lotes en Colab, generar una copia de seguridad de la hoja en Drive.
* **Bucle Masivo Deshabilitado:** La Celda 7 permanece con `HABILITAR_BUCLE_MASIVO = False` hasta la aprobación del Canary Test.
* **Canary Test:** Ejecución exclusiva de la Celda 6 con las 5 fotos críticas del historial registrando todas las métricas en Sheets y en `checkpoint_pipeline.json`.
