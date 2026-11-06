const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

const AUDIT_ROOT_ID = '16wT0ogNsfd-r2U1bGuuw01Rdxj269bxW'; // _Fotos_Erroneas_y_Desalineadas
const TEMP_FEEDBACK_ID = '1HMFP95kwxmOvH4K2tiCrW3yXgCmRAZDh';

const proPath = path.join(__dirname, 'drive_pro_tree.json');
const pro = JSON.parse(fs.readFileSync(proPath, 'utf8'));

// The 34 files to structure
const fileCategoryMap = [
  // 10 ERROR_TEST
  { id: '1AvYf0vtlMOMakeVloQQ7vgg2xNiL_dVE', name: '3_Escapulario_Mujer_PRO_1x1_ERROR_TEST.jpg', cat: 'Escapulario para Mujer de Marinera_Pro' },
  { id: '1x1ElpEqS3D0sQTEgCWr__lrIsWQWLOs8', name: '4_Escapulario_Mujer_PRO_1x1_ERROR_TEST.jpg', cat: 'Escapulario para Mujer de Marinera_Pro' },
  { id: '1IkPT_smNCaoi78GajbTbJI-2mhNWfxBE', name: '5_Escapulario_Mujer_PRO_1x1_ERROR_TEST.jpg', cat: 'Escapulario para Mujer de Marinera_Pro' },
  { id: '15XHPBCJV2sqt7QmR_PeXv6IuW8sgjvcD', name: '6_Escapulario_Mujer_PRO_1x1_ERROR_TEST.jpg', cat: 'Escapulario para Mujer de Marinera_Pro' },
  { id: '1YGniu1e_WQ8nvXzdd7UhFEqWc9lXNATN', name: '1_Collar_Aretes_Filigrana_PRO_1x1_ERROR_TEST.jpg', cat: 'Juego de Collar y Aretes para Marinera_Pro' },
  { id: '1JMDMxxQmaNAOfrh1Eh-3oJA8KFYOqLpq', name: '2_Collar_Aretes_Filigrana_PRO_1x1_ERROR_TEST.jpg', cat: 'Juego de Collar y Aretes para Marinera_Pro' },
  { id: '1iAhWg8s5H4R5-0t9MM0BOrNMgoCP11BJ', name: '3_Collar_Aretes_Filigrana_PRO_1x1_ERROR_TEST.jpg', cat: 'Juego de Collar y Aretes para Marinera_Pro' },
  { id: '1s_zYybSDywy0irzu6E_B2YLfi_5ELFpf', name: '4_Collar_Aretes_Filigrana_PRO_1x1_ERROR_TEST.jpg', cat: 'Juego de Collar y Aretes para Marinera_Pro' },
  { id: '1edkeS9CCHoA716T1RSrLJeuzJJaoLN0m', name: '1_Manto_Pava_Bordado_PRO_1x1_ERROR_TEST.jpg', cat: 'Manto de Pava bordado_Pro' },
  { id: '1ssQ0Liqvq4zf3x-VnhCQD6VTBnfQnaGA', name: '2_Manto_Pava_Bordado_PRO_1x1_ERROR_TEST.jpg', cat: 'Manto de Pava bordado_Pro' },
  // 3 instrucciones de texto
  { id: '1Xv-w3FrRk9xNWh3_R886FZWjDZHgbV0_', name: 'corregir, la dimencion de la foto es muy delgado mejorar las proporciones', cat: 'Falda de Ensayo de razo 2 bobos con contrabobo pro' },
  { id: '1yRuPh3s8wHNV1nTfOnZdOVXqQFLBmJhl', name: 'corregir, no corresponde a la imagen original volverlo hacer', cat: 'Falda de Ensayo de razo 2 bobos con contrabobo pro' },
  { id: '1deC6y6Q6TXQhQgPK7FUH9yKVS6YY73Um', name: 'corregir, no se ha modificado nada', cat: 'Falda de Ensayo de razo 2 bobos con contrabobo pro' },
  // 21 corregir feedback
  { id: '1SEwWSfFvoQGeFwBJnCsV56aqkxgBd5Ii', name: 'foto (2) corregir mano.png', cat: 'Falda para Ensayo de Razo - Azul Eléctrico con cinta blanca_Pro' },
  { id: '1zQvQwap3QVU9YItDGv5GDpFseFKGAzZ4', name: 'IMG_0716 corregir pie.JPG', cat: 'Falda para Ensayo de Razo - Azul Marino con cinta blanca_Pro' },
  { id: '1HY84V4-F_34aBLzzyWIoRBzDkRsU5Muo', name: 'IMG_0930 corregir falda.HEIC', cat: 'Falda para Ensayo de Razo - Azul Marino con cinta blanca_Pro' },
  { id: '1dtlpoaaHb_Xb7LOPB2onlYYTSJtVvNlW', name: ' IMG_0936 corregir, arreglar la pretina.HEIC', cat: 'Falda para Ensayo de Razo - Azul Marino Entero_Pro' },
  { id: '1SFkDS9pcEn9tJs2h7XY6UkTXjP05ILpI', name: 'IMG_0935 corregir esta muy lejos, acercar.HEIC', cat: 'Falda para Ensayo de Razo - Azul Marino Entero_Pro' },
  { id: '1WGM1AKDJKknAA4y3rpuPROElITzU7jLJ', name: 'IMG_0940 corregir, mas cerca el traje.heic', cat: 'Falda para Ensayo de Razo - Azul Marino Entero_Pro' },
  { id: '1czCK7cbVJA_SXr4lzbejlCGxqBD0MjYc', name: 'd72049af corregir mano, no importa con el pañuelo.JPG', cat: 'Falda para Ensayo de Razo - Coral con cinta blanca_Pro' },
  { id: '1wEPzHb8NdcKNXDtbgSNb4R_8J_gmLT4D', name: 'IMG_0977 corregir, poner al medio solo si se puede.jpg', cat: 'Falda para Ensayo de Razo - Coral con cinta blanca_Pro' },
  { id: '13ZynO8V3ZtA9Fh_T1cp9Bg7lSBqF_DM0', name: '34a63e97 corregir quitar el piso.JPG', cat: 'Falda para Ensayo de Razo - Lila con cinta morada_Pro' },
  { id: '1hyDi4dw3mnW7lTZF94XSbnmuGAFXkKLb', name: 'foto (3)corregir no puede haber bordes blancos.png', cat: 'Falda para Ensayo de Razo - Lila con cinta morada_Pro' },
  { id: '1cXO8MR2XQ3ywRQ-pLW2Kz7krHPZCFhsI', name: '1841c6d0 corregir, centrar foto esta muy abajo .JPG', cat: 'Falda para Ensayo de Razo - Morada con cinta blanca_Pro' },
  { id: '1h_Mu3269fTceDvz-22GBVlQyOUch22dr', name: 'foto corregir, quitar bordes blancos.png', cat: 'Falda para Ensayo de Razo - Morada con cinta blanca_Pro' },
  { id: '1EV27gAun31OescAc9RKb_UYXZq_XHIu6', name: 'IMG_0943 corregir, foto equivocada es todo negro.HEIC', cat: 'Falda para Ensayo de Razo - Negro entero_Pro' },
  { id: '1Cg-BOApginfEAFUfI4IgeLvpKeZJJPnd', name: '781c5a14 corregir, se puede centrar?.JPG', cat: 'Falda para Ensayo de Razo - Rosada con cinta blanca_Pro' },
  { id: '1rbiuU5SI3dLyeMtBL3bXl49BqfcOx_ie', name: '59c902a0 corregir, agregar brazo con pañuelo tal como esta en la original.JPG', cat: 'Falda para Ensayo de Razo - Turquesa con cinta blanca_Pro' },
  { id: '1NrwR5KoUgz77o1WvSxh-0VWMyWFMbHwx', name: 'IMG_0971 corregir.HEIC', cat: 'Falda para Ensayo de Razo - Verde jade con cinta blanca_Pro' },
  { id: '11TlBefZMhrReI6bNerFJVKCxJbpLBLbs', name: 'IMG_0965 corregir, no corresponde a la foto original.HEIC', cat: 'Falda para Ensayo de Razo - Vino con cinta perla_Pro' },
  { id: '1ccO-dq_TTvZyDhTKhcCCSI-uOLqod_6y', name: 'foto (4) corregir, no puede haber marcos blancos.png', cat: 'Falda para Ensayo de Razo - Vino Entero_Pro' },
  { id: '1oRlOisSnwW3pdFcVSoYvf1QScSeoPE12', name: 'IMG_0962 corregir, quitar mano.HEIC', cat: 'Falda para Ensayo de Razo - Vino Entero_Pro' },
  { id: '1z0nb_N1SEJBGx_4r0jF9_S7uhxahPfQa', name: '5. CORREGIR', cat: 'Manto de Leche_Pro' },
  { id: '1_DS9CaV8-2Rr87b_fzk9V5ZuqAlDKfbB', name: '9 barnie primaveral CORREGIR', cat: 'Tocado con Peineta para Marinera_Pro' }
];

// Unique categories
const uniqueCats = Array.from(new Set(fileCategoryMap.map(f => f.cat)));
console.log(`Found ${uniqueCats.length} unique category folders to create in _Fotos_Erroneas_y_Desalineadas:`);
console.log(uniqueCats);

// 1. Create subfolders inside AUDIT_ROOT_ID
const catFolderIds = new Map();

for (const catName of uniqueCats) {
  try {
    console.log(`Creating folder: "${catName}"...`);
    const out = execSync(`gdrive mutate mkdir "${catName}" --parent ${AUDIT_ROOT_ID} --json`).toString();
    const parsed = JSON.parse(out);
    catFolderIds.set(catName, parsed.id);
    console.log(` -> Created ID: ${parsed.id}`);
  } catch (e) {
    console.error(`Error creating ${catName}:`, e.message);
  }
}

// 2. Move each file to its corresponding category folder
console.log('\nMoving files into their category subfolders...');
for (const item of fileCategoryMap) {
  const targetFolder = catFolderIds.get(item.cat);
  if (!targetFolder) {
    console.error(`No target folder found for ${item.cat}`);
    continue;
  }
  try {
    console.log(`Moving: "${item.name}" -> "${item.cat}" (${targetFolder})...`);
    execSync(`gdrive mutate mv ${item.id} ${targetFolder}`, { stdio: 'inherit' });
  } catch (e) {
    console.error(`Error moving ${item.name}:`, e.message);
  }
}

// 3. Remove empty temporary feedback folder
try {
  console.log(`\nTrashing empty temporary folder ${TEMP_FEEDBACK_ID}...`);
  execSync(`gdrive mutate trash ${TEMP_FEEDBACK_ID}`, { stdio: 'inherit' });
} catch (e) {
  console.warn('Could not trash temp folder:', e.message);
}

console.log('\nTree organization completed successfully!');
