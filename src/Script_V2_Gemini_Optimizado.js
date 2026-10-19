/**
 * MARINERA STUDIO PRO - V2 (GEMINI OPTIMIZADO)
 * Arquitectura resiliente de producción para Google Sheets & Google Drive.
 */

const CONFIG = {
  MODELO: "gemini-2.5-flash-image",
  LIMITE_TIEMPO_MS: 240000,           // 4 minutos (evita timeout de 6 min de Apps Script)
  THROTTLING_MS: 12000,               // 12 segundos entre llamadas (respeta 10 IPM de Tier 1)
  MAX_REINTENTOS: 1,                  // MÁXIMO 1 REINTENTO (Total 2 intentos antes de bloqueo)
  SUFIJO_PRO: "_Pro",
  CARPETA_MADRE_DEFECTO_ID: "1SERKR606LbQEYkgLTgDB0f-pUoMhvNz4", // Fotos catalogo Marinera Power
  COLOR_FONDO_ESTUDIO: "#E5E1DE",
  
  // PROMPT ANTI-ALUCINACIONES CON ANCLAJE ESTRICTO
  PROMPT: "Actúa como un laboratorio fotográfico profesional de e-commerce de alta gama. " +
          "OBJETIVO: Estandarizar esta fotografía preservando al 100% el producto y su entorno directo. " +
          "REGLAS ESTRICTAS DE NO ALUCINACIÓN: " +
          "1. NO modifiques, no redibujes, no alteres ni cambies las facciones de rostros, manos, piel o anatomía de los modelos. " +
          "2. NO alteres las texturas, colores, bordados, encajes, accesorios, ni la pose exacta de las prendas. " +
          "3. NO realices zoom in ni zoom out: mantén estrictamente la distancia de cámara y la relación de aspecto 2:3 original. " +
          "4. FONDO ÚNICO: Reemplaza completamente el fondo original por una pared de estudio lisa y limpia de color gris cálido uniforme (#E5E1DE). Sin viñetas, sin gradientes, sin efectos artificiales. " +
          "5. ANCLAJE Y SOMBRAS: Genera sombra de contacto natural y sutil en el suelo/base donde se apoya el producto o modelo. " +
          "6. Entrega nitidez 4K sin artefactos ni marcas de agua. Devuelve únicamente la imagen resultante en formato binario."
};

/**
 * Crea el Menú Personalizado al abrir la hoja de cálculo
 */
function onOpen() {
  SpreadsheetApp.getUi()
    .createMenu("🎨 Marinera Studio Pro")
    .addItem("🔍 1. Escanear Carpeta (Modal UI)", "mostrarModalEscaneo")
    .addItem("⚡ 2. Procesar Cola de Imágenes", "procesarColaDeImagenes")
    .addItem("🔗 3. Mapear Original vs Versión Pro", "generarMapeoMaestroOriginalVsPro")
    .addItem("🛡️ 4. Auditar Archivos en Drive", "auditarArchivosGeneradosDrive")
    .addSeparator()
    .addItem("⏰ Activar Disparador Automático", "activarProcesamientoContinuo")
    .addItem("⏹️ Detener Disparadores", "desactivarActivadores")
    .addToUi();
}

/**
 * Muestra la Ventana Modal para Escanear Carpeta
 */
function mostrarModalEscaneo() {
  const html = HtmlService.createHtmlOutputFromFile("ModalEscaneo")
    .setWidth(550)
    .setHeight(480)
    .setTitle("Marinera Studio - Escanear Carpeta de Drive");
  SpreadsheetApp.getUi().showModalDialog(html, "Escanear y Pre-validar Carpeta");
}

/**
 * Backend del Modal: Analiza la carpeta y devuelve estadísticas antes de cargar
 */
function preEscanearCarpeta(carpetaIdOUrl) {
  try {
    const carpetaId = extraerIdCarpeta(carpetaIdOUrl);
    const carpeta = DriveApp.getFolderById(carpetaId);
    
    let conteo = { total: 0, jpg: 0, png: 0, heic: 0, otros: 0, nuevos: 0, existentes: 0 };
    const hoja = obtenerOCrearHoja("Control_Proceso");
    const idsRegistrados = obtenerIdsOriginalesRegistrados(hoja);
    
    escanearRecursivoConteo(carpeta, conteo, idsRegistrados);
    
    return {
      exito: true,
      nombreCarpeta: carpeta.getName(),
      idCarpeta: carpetaId,
      conteo: conteo
    };
  } catch (e) {
    return { exito: false, error: e.toString() };
  }
}

/**
 * Backend del Modal: Confirma la indexación incremental de las fotos validadas
 */
function confirmarCargaIncremental(carpetaId) {
  try {
    const carpeta = DriveApp.getFolderById(carpetaId);
    const hoja = obtenerOCrearHoja("Control_Proceso");
    const idsRegistrados = obtenerIdsOriginalesRegistrados(hoja);
    
    let nuevosRegistros = [];
    let ultimoId = hoja.getLastRow() > 1 ? Number(hoja.getRange(hoja.getLastRow(), 1).getValue()) || 0 : 0;
    
    escanearRecursivoCarga(carpeta, carpeta.getName(), nuevosRegistros, idsRegistrados, ultimoId);
    
    if (nuevosRegistros.length > 0) {
      hoja.getRange(hoja.getLastRow() + 1, 1, nuevosRegistros.length, nuevosRegistros[0].length).setValues(nuevosRegistros);
    }
    
    return { exito: true, agregados: nuevosRegistros.length };
  } catch (e) {
    return { exito: false, error: e.toString() };
  }
}

/**
 * PROCESADOR POR LOTES RESILIENTE (ANTI-LOOP & CUOTA SAFE)
 */
function procesarColaDeImagenes() {
  const tiempoInicio = new Date().getTime();
  const apiKey = PropertiesService.getScriptProperties().getProperty("GEMINI_API_KEY");
  
  if (!apiKey) {
    SpreadsheetApp.getUi().alert("Error: Configura 'GEMINI_API_KEY' en Propiedades del Script.");
    return;
  }
  
  const hoja = obtenerOCrearHoja("Control_Proceso");
  const datos = hoja.getDataRange().getValues();
  
  let pendientesEnCola = 0;
  for (let i = 1; i < datos.length; i++) {
    const estado = String(datos[i][6]).trim();
    const intentos = Number(datos[i][9]) || 0;
    
    if (estado === "PENDIENTE" || (estado === "ERROR_REINTENTABLE" && intentos <= CONFIG.MAX_REINTENTOS)) {
      pendientesEnCola++;
    }
  }
  
  if (pendientesEnCola === 0) {
    console.log("No hay tareas pendientes en cola. Deteniendo disparadores.");
    desactivarActivadores();
    return;
  }
  
  for (let i = 1; i < datos.length; i++) {
    if (new Date().getTime() - tiempoInicio > CONFIG.LIMITE_TIEMPO_MS) {
      console.log("Tiempo límite de 4 min alcanzado. Pausa preventiva.");
      break;
    }
    
    const fila = i + 1;
    const estado = String(datos[i][6]).trim();
    let intentos = Number(datos[i][9]) || 0;
    
    if (estado === "PENDIENTE" || (estado === "ERROR_REINTENTABLE" && intentos <= CONFIG.MAX_REINTENTOS)) {
      const carpetaOrigenRuta = String(datos[i][1]);
      const nombreArchivoOriginal = String(datos[i][2]);
      const archivoIdOriginal = String(datos[i][3]);
      
      try {
        hoja.getRange(fila, 7).setValue("EN_PROCESO");
        SpreadsheetApp.flush();
        
        const infoImagen = obtenerBytesImagenSegura(archivoIdOriginal);
        const carpetaDestino = obtenerOCrearCarpetaDestinoPro(carpetaOrigenRuta);
        
        const resultadoBase64 = ejecutarLlamadaGemini(apiKey, infoImagen.base64, infoImagen.mimeType);
        
        if (resultadoBase64) {
          const blobDecodificado = Utilities.newBlob(
            Utilities.base64Decode(resultadoBase64),
            "image/jpeg",
            nombreArchivoOriginal.replace(/\.[^/.]+$/, "") + "_pro.jpg"
          );
          
          const nuevoArchivo = carpetaDestino.createFile(blobDecodificado);
          
          hoja.getRange(fila, 5).setValue(carpetaDestino.getName());
          hoja.getRange(fila, 6).setValue(nuevoArchivo.getId());
          hoja.getRange(fila, 7).setValue("COMPLETADO");
          hoja.getRange(fila, 8).setValue(new Date());
          hoja.getRange(fila, 9).setValue("OK [Optimizado con éxito]");
          hoja.getRange(fila, 10).setValue(intentos);
          hoja.getRange(fila, 11).setValue(nuevoArchivo.getUrl());
        } else {
          throw new Error("La API respondió sin datos binarios de imagen.");
        }
      } catch (err) {
        intentos++;
        const errorMsg = err.toString();
        const esErrorTransitorio = errorMsg.includes("429") || errorMsg.includes("503");
        
        const nuevoEstado = (esErrorTransitorio && intentos <= CONFIG.MAX_REINTENTOS) 
                            ? "ERROR_REINTENTABLE" 
                            : "ERROR_DEFINITIVO";
        
        hoja.getRange(fila, 7).setValue(nuevoEstado);
        hoja.getRange(fila, 8).setValue(new Date());
        hoja.getRange(fila, 9).setValue(errorMsg);
        hoja.getRange(fila, 10).setValue(intentos);
        console.error("Fallo en fila " + fila + " (" + nuevoEstado + "): " + errorMsg);
      }
      
      SpreadsheetApp.flush();
      Utilities.sleep(CONFIG.THROTTLING_MS);
    }
  }
}

/**
 * Obtiene los bytes de la imagen soportando JPG, PNG y HEIC de iPhone en máxima calidad
 */
function obtenerBytesImagenSegura(archivoId) {
  const archivo = DriveApp.getFileById(archivoId);
  const nombre = archivo.getName().toLowerCase();
  const mimeOriginal = archivo.getMimeType().toLowerCase();
  
  if (mimeOriginal.includes("heif") || mimeOriginal.includes("heic") || nombre.endsWith(".heic")) {
    const urlThumbnailHd = "https://lh3.googleusercontent.com/u/0/d/" + archivoId + "=s2048";
    const opciones = { headers: { Authorization: "Bearer " + ScriptApp.getOAuthToken() }, muteHttpExceptions: true };
    const respuesta = UrlFetchApp.fetch(urlThumbnailHd, opciones);
    
    if (respuesta.getResponseCode() === 200) {
      return {
        base64: Utilities.base64Encode(respuesta.getBlob().getBytes()),
        mimeType: "image/jpeg"
      };
    }
  }
  
  const blob = archivo.getBlob();
  return {
    base64: Utilities.base64Encode(blob.getBytes()),
    mimeType: blob.getMimeType()
  };
}

/**
 * Llamada HTTP resiliente a Gemini 2.5 Flash Image con control de temperatura baja
 */
function ejecutarLlamadaGemini(apiKey, base64Data, mimeType) {
  const url = "https://generativelanguage.googleapis.com/v1beta/models/" + CONFIG.MODELO + ":generateContent?key=" + apiKey;
  
  const payload = {
    contents: [{
      parts: [
        { text: CONFIG.PROMPT },
        { inlineData: { mimeType: mimeType, data: base64Data } }
      ]
    }],
    generationConfig: {
      responseModalities: ["IMAGE"],
      temperature: 0.1
    }
  };
  
  const options = {
    method: "post",
    contentType: "application/json",
    payload: JSON.stringify(payload),
    muteHttpExceptions: true
  };
  
  for (let intento = 0; intento < 3; intento++) {
    const respuesta = UrlFetchApp.fetch(url, options);
    const codigo = respuesta.getResponseCode();
    const texto = respuesta.getContentText();
    
    if (codigo === 200) {
      const json = JSON.parse(texto);
      if (json.candidates && json.candidates[0].content && json.candidates[0].content.parts) {
        const parteImg = json.candidates[0].content.parts.find(p => p.inlineData);
        if (parteImg && parteImg.inlineData) return parteImg.inlineData.data;
      }
      throw new Error("Respuesta 200 pero sin contenido 'inlineData'.");
    } else if (codigo === 429 || codigo === 503) {
      Utilities.sleep(Math.pow(2, intento) * 4000);
    } else {
      throw new Error("Error Gemini HTTP " + codigo + ": " + texto);
    }
  }
  return null;
}

/**
 * FUNCIÓN DE MAPEO MAESTRO: Correlaciona fotos Originales vs Versión Pro
 */
function generarMapeoMaestroOriginalVsPro() {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  let hojaMapeo = ss.getSheetByName("Mapeo_Maestro_Pro");
  if (!hojaMapeo) hojaMapeo = ss.insertSheet("Mapeo_Maestro_Pro");
  hojaMapeo.clear();
  
  const encabezados = [
    "ID Mapeo", "Categoría / Subcarpeta", "Nombre Original", "ID Foto Original", 
    "Enlace Original", "Tiene Versión Pro", "Nombre Archivo Pro", "ID Archivo Pro", 
    "Enlace Pro", "Estado Correlación"
  ];
  hojaMapeo.getRange(1, 1, 1, encabezados.length).setValues([encabezados]).setFontWeight("bold").setBackground("#D9E1F2");
  
  const hojaControl = ss.getSheetByName("Control_Proceso");
  let mapaProcesados = {};
  if (hojaControl && hojaControl.getLastRow() > 1) {
    const datosControl = hojaControl.getRange(2, 1, hojaControl.getLastRow() - 1, 11).getValues();
    for (let r = 0; r < datosControl.length; r++) {
      const idOrig = String(datosControl[r][3]).trim();
      const idPro = String(datosControl[r][5]).trim();
      const est = String(datosControl[r][6]).trim();
      if (est === "COMPLETADO" && idPro) {
        mapaProcesados[idOrig] = {
          idPro: idPro,
          carpetaDestino: datosControl[r][4],
          enlacePro: datosControl[r][10] || ("https://drive.google.com/file/d/" + idPro + "/view")
        };
      }
    }
  }
  
  const carpetaMadre = DriveApp.getFolderById(CONFIG.CARPETA_MADRE_DEFECTO_ID);
  let filasMapeo = [];
  let contador = 1;
  recorrerCarpetasParaMapeo(carpetaMadre, carpetaMadre.getName(), filasMapeo, mapaProcesados, contador);
  
  if (filasMapeo.length > 0) {
    hojaMapeo.getRange(2, 1, filasMapeo.length, encabezados.length).setValues(filasMapeo);
  }
  SpreadsheetApp.getUi().alert("Mapeo completado. Se analizaron " + filasMapeo.length + " imágenes del catálogo.");
}

function recorrerCarpetasParaMapeo(carpeta, rutaActual, filasMapeo, mapaProcesados, contador) {
  const archivos = carpeta.getFiles();
  while (archivos.hasNext()) {
    const arc = archivos.next();
    const idArc = arc.getId();
    const nomArc = arc.getName();
    const mime = arc.getMimeType();
    
    if (mime.startsWith("image/") || nomArc.toLowerCase().endsWith(".heic")) {
      const proInfo = mapaProcesados[idArc];
      const tienePro = proInfo ? "SÍ" : "PENDIENTE";
      const idPro = proInfo ? proInfo.idPro : "";
      const enlacePro = proInfo ? proInfo.enlacePro : "";
      
      filasMapeo.push([
        contador++,
        rutaActual,
        nomArc,
        idArc,
        "https://drive.google.com/file/d/" + idArc + "/view",
        tienePro,
        proInfo ? (nomArc.replace(/\.[^/.]+$/, "") + "_pro.jpg") : "-",
        idPro,
        enlacePro,
        tienePro === "SÍ" ? "PROCESADA OK" : "REQUIERE OPTIMIZACIÓN"
      ]);
    }
  }
  
  const subcarpetas = carpeta.getFolders();
  while (subcarpetas.hasNext()) {
    const sub = subcarpetas.next();
    if (!sub.getName().endsWith("_Pro")) {
      recorrerCarpetasParaMapeo(sub, rutaActual + " / " + sub.getName(), filasMapeo, mapaProcesados, contador);
    }
  }
}

function auditarArchivosGeneradosDrive() {
  const hoja = obtenerOCrearHoja("Control_Proceso");
  const datos = hoja.getDataRange().getValues();
  let confirmados = 0, perdidos = 0;
  
  for (let i = 1; i < datos.length; i++) {
    const estado = datos[i][6];
    const idPro = datos[i][5];
    if (estado === "COMPLETADO" && idPro) {
      try {
        const file = DriveApp.getFileById(idPro);
        if (file.isTrashed()) throw new Error("Papelera");
        confirmados++;
      } catch (e) {
        hoja.getRange(i + 1, 9).setValue("ALERTA: Archivo no hallado en Drive");
        perdidos++;
      }
    }
  }
  SpreadsheetApp.getUi().alert("Auditoría: " + confirmados + " fotos Pro verificadas. (" + perdidos + " no encontradas).");
}

function extraerIdCarpeta(urlOId) {
  if (!urlOId) throw new Error("Ingresa un enlace o ID de carpeta.");
  const coincidencia = urlOId.match(/[-\w]{25,}/);
  return coincidencia ? coincidencia[0] : urlOId.trim();
}

function obtenerOCrearHoja(nombre) {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  let hoja = ss.getSheetByName(nombre);
  if (!hoja) {
    hoja = ss.insertSheet(nombre);
    const headers = [
      "ID", "Carpeta Origen", "Nombre Original", "ID Archivo Original", 
      "Carpeta Destino", "ID Archivo Destino", "Estado", "Fecha Procesamiento", 
      "Mensaje / Diagnóstico", "Intentos", "Enlace Pro"
    ];
    hoja.getRange(1, 1, 1, headers.length).setValues([headers]).setFontWeight("bold").setBackground("#EFEFEF");
  }
  return hoja;
}

function obtenerIdsOriginalesRegistrados(hoja) {
  const ids = new Set();
  if (hoja.getLastRow() > 1) {
    const valores = hoja.getRange(2, 4, hoja.getLastRow() - 1, 1).getValues();
    for (let r = 0; r < valores.length; r++) {
      if (valores[r][0]) ids.add(String(valores[r][0]).trim());
    }
  }
  return ids;
}

function escanearRecursivoConteo(carpeta, conteo, idsRegistrados) {
  const archivos = carpeta.getFiles();
  while (archivos.hasNext()) {
    const arc = archivos.next();
    const nombre = arc.getName().toLowerCase();
    const mime = arc.getMimeType().toLowerCase();
    
    if (mime.includes("jpeg") || nombre.endsWith(".jpg") || nombre.endsWith(".jpeg")) conteo.jpg++;
    else if (mime.includes("png") || nombre.endsWith(".png")) conteo.png++;
    else if (mime.includes("heif") || mime.includes("heic") || nombre.endsWith(".heic")) conteo.heic++;
    else conteo.otros++;
    
    conteo.total++;
    if (idsRegistrados.has(arc.getId())) conteo.existentes++;
    else conteo.nuevos++;
  }
  
  const subs = carpeta.getFolders();
  while (subs.hasNext()) {
    escanearRecursivoConteo(subs.next(), conteo, idsRegistrados);
  }
}

function escanearRecursivoCarga(carpeta, ruta, nuevosRegistros, idsRegistrados, contador) {
  const archivos = carpeta.getFiles();
  while (archivos.hasNext()) {
    const arc = archivos.next();
    const id = arc.getId();
    if (!idsRegistrados.has(id)) {
      contador++;
      nuevosRegistros.push([
        contador, ruta, arc.getName(), id, "", "", "PENDIENTE", "", "", 0, ""
      ]);
      idsRegistrados.add(id);
    }
  }
  const subs = carpeta.getFolders();
  while (subs.hasNext()) {
    const sub = subs.next();
    escanearRecursivoCarga(sub, ruta + " / " + sub.getName(), nuevosRegistros, idsRegistrados, contador);
  }
}

function obtenerOCrearCarpetaDestinoPro(rutaOrigen) {
  const nombreDestino = rutaOrigen.split("/").pop().trim() + CONFIG.SUFIJO_PRO;
  const carpetas = DriveApp.getFoldersByName(nombreDestino);
  if (carpetas.hasNext()) return carpetas.next();
  return DriveApp.createFolder(nombreDestino);
}

function activarProcesamientoContinuo() {
  desactivarActivadores();
  ScriptApp.newTrigger("procesarColaDeImagenes").timeBased().everyMinutes(15).create();
  SpreadsheetApp.getUi().alert("Disparador instalado con éxito cada 15 min.");
}

function desactivarActivadores() {
  const activadores = ScriptApp.getProjectTriggers();
  for (let i = 0; i < activadores.length; i++) {
    if (activadores[i].getHandlerFunction() === "procesarColaDeImagenes") {
      ScriptApp.deleteTrigger(activadores[i]);
    }
  }
}
