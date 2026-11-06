# 🗺️ Mapeo Maestro de Google Drive, Google Sheets y Entorno Local

Este documento correlaciona de forma exhaustiva las fuentes de datos, los identificadores en la nube y las rutas locales en Windows para el proyecto **Marinera Power**.

---

## 1. Entorno Cloud (Google Drive & Sheets)

### A. Carpeta Madre de Fotos en Google Drive
* **Nombre:** `Fotos catalogo Marinera Power`
* **ID de Carpeta en Google Drive:** `1SERKR606LbQEYkgLTgDB0f-pUoMhvNz4`
* **URL Directa:** [https://drive.google.com/drive/u/0/folders/1SERKR606LbQEYkgLTgDB0f-pUoMhvNz4](https://drive.google.com/drive/u/0/folders/1SERKR606LbQEYkgLTgDB0f-pUoMhvNz4)

### B. Estructura de Subcarpetas en Drive
Las imágenes se organizan por categoría de indumentaria. Las subcarpetas generadas automáticamente por los scripts llevan el sufijo `_Pro`:

* **Carpeta Madre:** `Fotos catalogo` (`1SERKR606LbQEYkgLTgDB0f-pUoMhvNz4`)
* **Carpeta Espejo de Salidas Oficiales:** `Para ella_Pro` (`1DyK3P_kYjN-BcNNjRc-Il6ODJm4vvTZZ`)
  * `Accesorios_Pro` (`1x91cwokaFUKPbQ4oFBZNl3Vb9AErE8V6`) -> Contiene `Accesorios ella pro`
  * `Blusa_Pro` (`1W65XLefStPTtyYsHbIbIh3B3ePF0j4yC`)
  * `Blusa con enagues bordados_Pro` (`1ZwIZ5JneJAUCod3bVFIp1HPc-rL6siXD`)
  * `Enagues_Pro` (`1b9xGIwP4nUo8h4z7okbDCH2K5GvvlZ0Q`)
  * `Falda_Pro` (`1zgZAHdgGPHmZYJqcX3jOsnisgNYZpYvz`) -> Contiene `Faldas de Ensayo... 1 bobo` y `2 bobos`
  * `Trajes completos_Pro` (`1JoTcwL9ms7d3HQppwDAmwaaesgfQz-x9`)

### C. Hoja de Control de Procesamiento (Google Sheets)
* **URL:** [https://docs.google.com/spreadsheets/d/1kRsCZ7ZpPxyxrSEkUrYRl3NHahrQQche90RKK2yedQ8/edit?gid=0#gid=0](https://docs.google.com/spreadsheets/d/1kRsCZ7ZpPxyxrSEkUrYRl3NHahrQQche90RKK2yedQ8/edit?gid=0#gid=0)
* **Pestañas Activas del Sistema:**
  1. `Control_Total_Fotos` (ID: `1966494245`): Matriz unificada de todas las 866 fotos con estado (`COMPLETADO`, `PENDIENTE`, `CORREGIR`), links a originales y pro, observaciones de encuadre.
  2. `Registro_Imagenes_Creadas` (ID: `779499709`): Bitácora de auditoría de fotos procesadas por el motor local/agente con links a Drive y ruta local.
  3. `Control_Proceso`: Pestaña original histórica del prototipo Apps Script.
  1. `ID_Archivo`: Identificador único incremental o hash del archivo.
  2. `Nombre_Archivo`: Nombre físico original (ej. `2 Manto de Pava bordado.jpg`).
  3. `Carpeta_Origen`: Nombre de la subcarpeta madre.
  4. `Estado_Proceso`: Estados posibles:
     * `NUEVO`: Detectado por el modal, pendiente de ejecución.
     * `EN_PROCESO`: Siendo procesado actualmente.
     * `COMPLETADO`: Imagen procesada y guardada en carpeta `_Pro`.
     * `ERROR_REINTENTO`: Falló 1 vez; programada para reintento.
     * `BLOQUEADO`: Superó el límite de reintentos; requiere revisión manual.
  5. `URL_Drive_Original`: Enlace al archivo madre en Drive.
  6. `URL_Drive_Pro`: Enlace al archivo resultante en la carpeta `_Pro`.
  7. `Fecha_Proceso`: Timestamp ISO de finalización.
  8. `Intentos`: Contador de reintentos (0, 1 o 2).

---

## 2. Entorno Local en Windows

* **Directorio Maestro del Proyecto:**
  `C:\Users\LENOVO\Documents\Carlitos\IA\Antigravity\Profesionalización de Catalogo\Cliente Marinera Power\`
* **Banco de Fotos de Prueba y Muestras Reales:**
  `C:\Users\LENOVO\Pictures\Marinera Power\`
  * Subcarpetas locales:
    * `#0044EE turquesa con cinta blanca\` (Muestras de vestidos de concurso)
    * `#353C51 Azul marino\` (Trajes señoriales)
    * `fotos creadas\` (149+ archivos de joyas, mantos, escapularios y tocados)
* **Carpeta de Salidas Locales PRO:**
  `C:\Users\LENOVO\Documents\Carlitos\IA\Antigravity\Profesionalización de Catalogo\Cliente Marinera Power\output\`
