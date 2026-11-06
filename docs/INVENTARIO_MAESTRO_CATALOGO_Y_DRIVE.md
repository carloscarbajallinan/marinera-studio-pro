# 📊 Inventario Maestro de Catálogo & Auditoría Google Drive: Marinera Power

> **Carpeta Madre:** [Fotos catalogo (`1SERKR606LbQEYkgLTgDB0f-pUoMhvNz4`)](https://drive.google.com/drive/u/0/folders/1SERKR606LbQEYkgLTgDB0f-pUoMhvNz4)  
> **Hoja de Control Oficial:** [Control_Proceso (`1kRsCZ7ZpPxyxrSEkUrYRl3NHahrQQche90RKK2yedQ8`)](https://docs.google.com/spreadsheets/d/1kRsCZ7ZpPxyxrSEkUrYRl3NHahrQQche90RKK2yedQ8/edit?gid=0#gid=0)  
> **Fecha de Auditoría:** 31 de Octubre de 2026  

---

## 📈 1. Resumen Ejecutivo de la Auditoría

| Indicador | Cantidad | Observaciones |
| :--- | :--- | :--- |
| **Total Fotos Originales (Madre)** | **863 fotos** | Distribuidas en 192 subcarpetas en Google Drive |
| **Registros en Google Sheets** | **866 filas** | Pestaña `Control_Proceso` con IDs de seguimiento |
| **Fotos PRO Generadas (Detectadas)** | **210 fotos** | Repartidas en las 4 carpetas `_Pro` históricas |
| **Fotos PRO Validadas (Limpias)** | **189 fotos** | Listas para publicación en e-commerce |
| **Fotos con Marca "CORREGIR"** | **21 fotos** | Contienen feedback específico de encuadre/manos |
| **Fotos con Múltiples Versiones PRO** | **19 grupos** | Iteraciones `PRO 1`, `PRO 2`, `PRO 3` |
| **Fotos Pendientes de Procesamiento** | **674 fotos** | Restante para completar el 100% del catálogo |
| **Tiempo Estimado de Procesamiento** | **~3.37 horas** | A 18s/foto (12s throttling + 6s inferencia API) |

---

## 🌳 2. Árbol de Niveles de la Carpeta Madre (`Fotos catalogo`)

```
Fotos catalogo/ (1SERKR606LbQEYkgLTgDB0f-pUoMhvNz4)
├── Ofertas/ (Sin fotos directas; subcarpetas de temporada)
│   ├── Blusas/
│   ├── Faldas/
│   └── Trajes/
│
├── Para ella/ (818 fotos en total - 94.8% del catálogo)
│   ├── Trajes completos/ (267 fotos)
│   │   ├── Traje Elegante/ (Modelos por tela y pedrería)
│   │   └── Traje Tradicional/ (Mochera, Huanchaquera, Monsefú)
│   ├── Falda/ (230 fotos)
│   │   ├── Anaco/ (Variantes regionales)
│   │   ├── Falda de Ensayo/ (Razo 1 bobo, 2 bobos, contrabobo)
│   │   └── Falda Profesional/ (Faldas de concurso con vuelillo)
│   ├── Blusa/ (154 fotos)
│   │   ├── Elegante/
│   │   └── Tradicional/
│   ├── Accesorios/ (81 fotos)
│   │   ├── Aretes para Marinera/ (Filigrana de Catacaos)
│   │   ├── Escapulario para Mujer de Marinera/ (Bordados devocionales)
│   │   ├── Faja de Hilo para Marinera/
│   │   ├── Juego de Collar y Aretes para Marinera/
│   │   ├── Mantos/ (Manto de Leche, Manto de Pava bordado)
│   │   ├── Pardos de Marinera/ (Pardos de Hilo y de Lana)
│   │   ├── Pañuelos Bordado para Mujer/ (Blanco y Colores)
│   │   ├── Sombrero de Mujer para Marinera/
│   │   └── Tocados/ (Peinetas, Látex con Pedrería, Kits)
│   ├── Blusa con enagues bordados/ (74 fotos)
│   │   └── 9 Modelos: Corazón, Espiga, Flores, Oregano, Pavas Entero, Ramas, Semi Calado...
│   └── Enagues/ (12 fotos)
│       ├── Enagues de bruselas con brillo/
│       └── Enagues organza/
│
├── Para ensayos/ (13 fotos)
│   ├── Medias Antideslizantes para Marinera/ (9 fotos: Cerradas y sin dedos)
│   ├── Cintas para Dedos para Marinera/ (3 fotos)
│   └── Polo de Ensayo para Marinera/ (1 foto)
│
└── Para él/ (32 fotos)
    ├── Sombrero de Marinera para Hombre/ (9 fotos: Concurso y Ensayo)
    ├── Camisa de Marinera para Hombre/ (7 fotos)
    ├── Escapulario para Hombre/ (5 fotos)
    ├── Faja de Hilo para Hombre/ (5 fotos)
    ├── Pañuelos Bordados para Hombre/ (3 fotos)
    └── Poncho de Lana para Marinera/ (3 fotos)
```

---

## 🔄 3. Mapeo de Carpetas Fuente vs Carpetas `_Pro`

| Carpeta Fuente Original en Drive | Carpeta Destino `_Pro` Existente | ID de Carpeta Pro | Estado de Cobertura |
| :--- | :--- | :--- | :--- |
| `Para ella / Accesorios / ...` | `Accesorios ella pro` | `1GRS1qrfwtVCa1J3vHNWnEAQsHMqoifMf` | Parcial (Aretes, Escapularios, Mantos, Tocados) |
| `Para ella / Falda / Falda de Ensayo / ... razo 2 bobos ...` | `Falda de Ensayo de razo 2 bobos con contrabobo pro` | `18eP1LHW5UEMyG3aNSa2sbaaOmLAotzVY` | Contiene pruebas de Razo y lotes históricos |
| `Para ella / Falda / Falda de Ensayo / ... razo 1 bobo ...` | `Faldas de Ensayo de razo 1 bobo pro` | `1YXSP_I8kiNIHwtEnmQZGeSzcajpJR_Jz` | Amplia cobertura de colores (Azul, Vino, Morado, Negro) |
| General de Catálogo | `Fotos catalogo pro` | `12K1p6iYudsDDsdV_flxaT3c9btknfz6f` | Carpeta raíz de salida general |

---

## ⚠️ 4. Auditoría de Errores y Feedback ("CORREGIR")

Se identificaron **21 archivos** que contienen observaciones explícitas incorporadas en su nombre de archivo o en las notas del Google Sheet. Estos deben ser reprocesados aplicando las nuevas directivas del Brand Book:

1. **Encuadre y Proporción:**
   * `IMG_0935 corregir esta muy lejos, acercar.HEIC` -> *Problema:* El sujeto está muy lejano; recortar en relación 2:3 centrando la prenda.
   * `IMG_0940 corregir, mas cerca el traje.heic` -> *Problema:* Acercar la toma al torso y falda.
   * `1841c6d0 corregir, centrar foto esta muy abajo.JPG` -> *Problema:* Centrado vertical inadecuado.
   * `IMG_0977 corregir, poner al medio solo si se puede.jpg` -> *Problema:* Reencuadre simétrico.
2. **Artefactos Visuales y Fondos:**
   * `foto (4) corregir, no puede haber marcos blancos.png` -> *Problema:* Lienzo con bordes blancos residuales; aplicar `#E5E1DE` hasta los bordes.
   * `foto corregir, quitar bordes blancos.png` -> *Problema:* Bordes blancos sin sangrado.
   * `34a63e97 corregir quitar el piso.JPG` -> *Problema:* Piso visible en la toma original; reemplazar por sombra de contacto en lienzo plano.
3. **Anatomía y Extremidades:**
   * `foto (2) corregir mano.png` -> *Problema:* La IA distorsionó o cortó la mano; aplicar regla de preservación anatómica.
   * `IMG_0716 corregir pie.JPG` -> *Problema:* Corte o deformación en pies descalzos.
   * `IMG_0962 corregir, quitar mano.HEIC` -> *Problema:* Mano de ayudante sosteniendo la prenda.
   * `59c902a0 corregir, agregar brazo con pañuelo tal como esta en la original.JPG` -> *Problema:* Se había eliminado el brazo con el pañuelo en vuelo.
   * `d72049af corregir mano, no importa con el pañuelo.JPG`
4. **Fidelidad Textil y de Color:**
   * `IMG_0930 corregir falda.HEIC` -> *Problema:* Caída o color de la falda alterado.
   * `IMG_0936 corregir, arreglar la pretina.HEIC` -> *Problema:* Deformación en la pretina de la falda.
   * `IMG_0943 corregir, foto equivocada es todo negro.HEIC` -> *Problema:* Falda negra procesada con colores cambiados.
   * `IMG_0965 corregir, no corresponde a la foto original.HEIC`
   * `5. CORREGIR` (Mantos de leche)
   * `9 barnie primaveral CORREGIR` (Tocados)

---

## 🔀 5. Fotos con Múltiples Versiones PRO

Se detectaron **19 conjuntos de imágenes** donde existen variantes iterativas (`PRO 1`, `PRO 2`, `PRO 3`). Ejemplos destacados:
* `IMG_0716`: 3 versiones (`PRO.jpg`, `PRO2.jpg`, `PRO3.jpg`).
* `IMG_0962`: 3 versiones (`PRO.jpg`, `PRO2.jpg`, `pro3.jpg`).
* `foto (3) Lila con cinta morada`: 3 versiones (`PRO1.jpg`, `PRO2.jpg`, `Pro3.jpg`).
* `7309F0C2`: 3 versiones (`PRO 1.jpg`, `PRO2.jpg`, `PRO 3.jpg`).
* `IMG_0930`: 2 versiones (`PRO1.jpg`, `PRO2.jpg`).
* `IMG_0935`: 2 versiones (`PRO1.jpg`, `PRO2.jpg`).
* `781c5a14`: 2 versiones (`PRO.jpg`, `PRO2.jpg`).
* `d72049af`: 2 versiones (`PRO.jpg`, `PRO2.jpg`).

**Recomendación:** Se debe seleccionar la mejor versión de cada una para el catálogo final de Shopify y archivar las variantes descartadas.

---

## ⏱️ 6. Estimación de Tiempo para Procesar las 674 Fotos Pendientes

* **Restricción Técnica:** Para cuentas de Google Workspace Tier 1, la API de Gemini exige respetar un límite de 10 a 15 llamadas por minuto.
* **Tiempo por foto:**
  * Pausa de Throttling: `12 segundos`
  * Inferencia de API y descarga en memoria: `~5 a 7 segundos`
  * Subida a Google Drive y escritura en Sheets: `~1 segundo`
  * **Total por foto:** **~18 a 20 segundos**
* **Cálculo Total:**
  * **674 fotos × 18 segundos = 12,132 segundos = 202.2 minutos = 3.37 horas**.
* **Estrategia de Ejecución:**
  * **Vía Google Apps Script:** Se necesitan **52 lotes de 4 minutos** disparados por reloj (Time-Driven Trigger) cada 5 minutos.
  * **Vía Script Local de Python (Recomendada):** Puede ejecutarse de forma continua sin límites de tiempo de ejecución de Google Apps Script, guardando directamente en local y sincronizando a Google Drive.
