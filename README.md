# Marinera Studio Pro - Automated Catalog Optimization

Sistema integral de optimización masiva de fotografías de catálogo e-commerce para indumentaria y accesorios de Marinera peruana, conectando Google Sheets, Google Drive y modelos de Inteligencia Artificial (Gemini Multimodal y Segmentación Híbrida).

---

## 🚀 Arquitectura y Opciones Disponibles

### Opción A: Gemini 2.5 Flash Image Optimizado (`src/Script_V2_Gemini_Optimizado.js`)
* **Modelo:** `gemini-2.5-flash-image` multimodal con `responseModalities: ["IMAGE"]`.
* **Prompt Anti-Alucinación:** Temperatura ultrabaja (0.1), directivas estrictas de preservación anatómica y textil, relación de aspecto fija 2:3 y fondo uniforme `#E5E1DE`.
* **Control de Costos:** Límite máximo de **1 reintento** (`MAX_REINTENTOS = 1`) y circuito de bloqueo para erradicar cobros duplicados.

### Opción B: Pipeline Híbrido (`src/Script_V2_Pipeline_Hibrido.js`)
* **Modelo:** Segmentación de precisión (Background Removal) + Composición en lienzo de color sólido `#E5E1DE`.
* **Ventaja:** 100% libre de alucinaciones. Prendas, bordados, filigranas y rostros permanecen idénticos píxel por píxel.

---

## 🛠️ Características Principales del Sistema

1. **Interfaz Visual en Google Sheets (`🎨 Marinera Studio Pro`):**
   * Menú personalizado con ventana modal interactiva (`src/ModalEscaneo.html`).
   * Permite pegar cualquier enlace o ID de carpeta de Google Drive.
   * Realiza un pre-escaneo con desglose por tipo de archivo (`JPG`, `PNG`, `HEIC`) antes de confirmar.
2. **Indexación Incremental:**
   * No borra el historial de la hoja. Compara los IDs de archivo y solo añade a la cola los registros nuevos.
3. **Soporte Nativo HEIC/HEIF de iPhone:**
   * Extrae la versión en alta resolución generada por Google Drive en memoria (`=s2048`) sin alterar ni degradar el archivo original.
4. **Mapeador Maestro:**
   * Función integrada para correlacionar en tiempo real las carpetas madre con las carpetas de salida `_Pro`.
5. **Auditoría de Archivos:**
   * Verifica la existencia real y estado de los archivos en Google Drive.

---

## 📁 Estructura del Repositorio

```
marinera-studio-pro/
├── src/
│   ├── Script_V2_Gemini_Optimizado.js  # Código de producción (Opción A)
│   ├── Script_V2_Pipeline_Hibrido.js   # Código de producción (Opción B)
│   └── ModalEscaneo.html              # Interfaz modal de escaneo en Sheets
├── docs/
│   └── Mapeo_Maestro_Fotos_Originales_vs_Pro.md  # Auditoría y correlación de fotos
└── README.md
```

---

## ⚙️ Configuración en Google Apps Script

1. Abre tu hoja de cálculo de control en Google Sheets.
2. Ve a **Extensiones > Apps Script**.
3. Pega el código de `Script_V2_Gemini_Optimizado.js` (o la versión híbrida) en `Código.gs`.
4. Crea un archivo HTML llamado `ModalEscaneo` y pega el contenido de `src/ModalEscaneo.html`.
5. En **Configuración del proyecto > Propiedades del script**, agrega:
   * `GEMINI_API_KEY`: Tu clave de Google AI Studio.
6. Recarga la hoja de cálculo para ver el nuevo menú **🎨 Marinera Studio Pro**.
