/**
 * MARINERA STUDIO PRO - V2 (PIPELINE HÍBRIDO)
 * Segmentación precisa de producto/modelo + Fondo de estudio exacto #E5E1DE.
 */

const CONFIG = {
  API_PROVIDER_URL: "https://sdk.photoroom.com/v1/segment", 
  COLOR_FONDO_HEX: "#E5E1DE",          // Gris cálido exacto
  ASPECT_RATIO: "2:3",                // Relación de aspecto estándar e-commerce
  LIMITE_TIEMPO_MS: 240000,           // 4 minutos
  THROTTLING_MS: 3000,                // 3 segundos
  MAX_REINTENTOS: 1,                  // Máximo 1 reintento
  SUFIJO_PRO: "_Pro",
  CARPETA_MADRE_DEFECTO_ID: "1SERKR606LbQEYkgLTgDB0f-pUoMhvNz4"
};

function onOpen() {
  SpreadsheetApp.getUi()
    .createMenu("🎨 Marinera Studio (Híbrido)")
    .addItem("🔍 1. Escanear Carpeta (Modal UI)", "mostrarModalEscaneo")
    .addItem("⚡ 2. Procesar Cola (Segmentación Limpia)", "procesarColaHibrida")
    .addItem("🔗 3. Mapear Original vs Versión Pro", "generarMapeoMaestroOriginalVsPro")
    .addItem("🛡️ 4. Auditar Archivos en Drive", "auditarArchivosGeneradosDrive")
    .addSeparator()
    .addItem("⏰ Activar Disparador Automático", "activarProcesamientoContinuoHibrido")
    .addItem("⏹️ Detener Disparadores", "desactivarActivadores")
    .addToUi();
}

function mostrarModalEscaneo() {
  const html = HtmlService.createHtmlOutputFromFile("ModalEscaneo")
    .setWidth(550)
    .setHeight(480)
    .setTitle("Marinera Studio - Escanear Carpeta de Drive");
  SpreadsheetApp.getUi().showModalDialog(html, "Escanear y Pre-validar Carpeta");
}

function preEscanearCarpeta(carpetaIdOUrl) {
  try {
    const carpetaId = extraerIdCarpeta(carpetaIdOUrl);
    const carpeta = DriveApp.getFolderById(carpetaId);
    let conteo = { total: 0, jpg: 0, png: 0, heic: 0, otros: 0, nuevos: 0, existentes: 0 };
    const hoja = obtenerOCrearHoja("Control_Proceso");
    const idsRegistrados = obtenerIdsOriginalesRegistrados(hoja);
    escanearRecursivoConteo(carpeta, conteo, idsRegistrados);
    return { exito: true, nombreCarpeta: carpeta.getName(), idCarpeta: carpetaId, conteo: conteo };
  } catch (e) {
    return { exito: false, error: e.toString() };
  }
}

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

function procesarColaHibrida() {
  const tiempoInicio = new Date().getTime();
  const apiKey = PropertiesService.getScriptProperties().getProperty("REMOVAL_API_KEY") || 
                 PropertiesService.getScriptProperties().getProperty("GEMINI_API_KEY");
  
  if (!apiKey) {
    SpreadsheetApp.getUi().alert("Error: Configura tu API Key en Propiedades del Script.");
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
        
        const resultadoBlob = ejecutarSegmentacionYFondo(apiKey, infoImagen.bytes, infoImagen.mimeType, nombreArchivoOriginal);
        
        if (resultadoBlob) {
          const nuevoArchivo = carpetaDestino.createFile(resultadoBlob);
          
          hoja.getRange(fila, 5).setValue(carpetaDestino.getName());
          hoja.getRange(fila, 6).setValue(nuevoArchivo.getId());
          hoja.getRange(fila, 7).setValue("COMPLETADO");
          hoja.getRange(fila, 8).setValue(new Date());
          hoja.getRange(fila, 9).setValue("OK [Segmentación 100% fiel]");
          hoja.getRange(fila, 10).setValue(intentos);
          hoja.getRange(fila, 11).setValue(nuevoArchivo.getUrl());
        } else {
          throw new Error("No se pudo obtener la imagen procesada.");
        }
      } catch (err) {
        intentos++;
        const errorMsg = err.toString();
        const esErrorTransitorio = errorMsg.includes("429") || errorMsg.includes("503") || errorMsg.includes("500");
        const nuevoEstado = (esErrorTransitorio && intentos <= CONFIG.MAX_REINTENTOS) 
                            ? "ERROR_REINTENTABLE" 
                            : "ERROR_DEFINITIVO";
        
        hoja.getRange(fila, 7).setValue(nuevoEstado);
        hoja.getRange(fila, 8).setValue(new Date());
        hoja.getRange(fila, 9).setValue(errorMsg);
        hoja.getRange(fila, 10).setValue(intentos);
        console.error("Fallo fila " + fila + ": " + errorMsg);
      }
      
      SpreadsheetApp.flush();
      Utilities.sleep(CONFIG.THROTTLING_MS);
    }
  }
}

function ejecutarSegmentacionYFondo(apiKey, bytes, mimeType, nombreOriginal) {
  const options = {
    method: "post",
    headers: {
      "x-api-key": apiKey
    },
    payload: {
      image_file: Utilities.newBlob(bytes, mimeType, "input.jpg"),
      bg_color: CONFIG.COLOR_FONDO_HEX.replace("#", ""),
      format: "jpg"
    },
    muteHttpExceptions: true
  };
  
  for (let intento = 0; intento < 3; intento++) {
    const res = UrlFetchApp.fetch(CONFIG.API_PROVIDER_URL, options);
    const code = res.getResponseCode();
    if (code === 200) {
      return Utilities.newBlob(res.getBlob().getBytes(), "image/jpeg", nombreOriginal.replace(/\.[^/.]+$/, "") + "_pro.jpg");
    } else if (code === 429 || code >= 500) {
      Utilities.sleep(2000 * (intento + 1));
    } else {
      throw new Error("Error API Segmentación HTTP " + code + ": " + res.getContentText());
    }
  }
  return null;
}

function obtenerBytesImagenSegura(archivoId) {
  const archivo = DriveApp.getFileById(archivoId);
  const nombre = archivo.getName().toLowerCase();
  const mimeOriginal = archivo.getMimeType().toLowerCase();
  
  if (mimeOriginal.includes("heif") || mimeOriginal.includes("heic") || nombre.endsWith(".heic")) {
    const urlThumbnailHd = "https://lh3.googleusercontent.com/u/0/d/" + archivoId + "=s2048";
    const opciones = { headers: { Authorization: "Bearer " + ScriptApp.getOAuthToken() }, muteHttpExceptions: true };
    const respuesta = UrlFetchApp.fetch(urlThumbnailHd, opciones);
    if (respuesta.getResponseCode() === 200) {
      return { bytes: respuesta.getBlob().getBytes(), mimeType: "image/jpeg" };
    }
  }
  const blob = archivo.getBlob();
  return { bytes: blob.getBytes(), mimeType: blob.getMimeType() };
}

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
      filasMapeo.push([
        contador++,
        rutaActual,
        nomArc,
        idArc,
        "https://drive.google.com/file/d/" + idArc + "/view",
        tienePro,
        proInfo ? (nomArc.replace(/\.[^/.]+$/, "") + "_pro.jpg") : "-",
        proInfo ? proInfo.idPro : "",
        proInfo ? proInfo.enlacePro : "",
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
        if (file.isTrashed()) throw new Error();
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
    const headers = ["ID", "Carpeta Origen", "Nombre Original", "ID Archivo Original", "Carpeta Destino", "ID Archivo Destino", "Estado", "Fecha Procesamiento", "Mensaje / Diagnóstico", "Intentos", "Enlace Pro"];
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
  while (subs.hasNext()) escanearRecursivoConteo(subs.next(), conteo, idsRegistrados);
}

function escanearRecursivoCarga(carpeta, ruta, nuevosRegistros, idsRegistrados, contador) {
  const archivos = carpeta.getFiles();
  while (archivos.hasNext()) {
    const arc = archivos.next();
    const id = arc.getId();
    if (!idsRegistrados.has(id)) {
      contador++;
      nuevosRegistros.push([contador, ruta, arc.getName(), id, "", "", "PENDIENTE", "", "", 0, ""]);
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

function activarProcesamientoContinuoHibrido() {
  desactivarActivadores();
  ScriptApp.newTrigger("procesarColaHibrida").timeBased().everyMinutes(15).create();
  SpreadsheetApp.getUi().alert("Disparador instalado con éxito cada 15 min.");
}

function desactivarActivadores() {
  const activadores = ScriptApp.getProjectTriggers();
  for (let i = 0; i < activadores.length; i++) {
    if (activadores[i].getHandlerFunction() === "procesarColaHibrida" || activadores[i].getHandlerFunction() === "procesarColaDeImagenes") {
      ScriptApp.deleteTrigger(activadores[i]);
    }
  }
}
