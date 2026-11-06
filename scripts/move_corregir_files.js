const { execSync } = require('child_process');

const targetFolderId = '1HMFP95kwxmOvH4K2tiCrW3yXgCmRAZDh';

const filesToMove = [
  { id: '1SEwWSfFvoQGeFwBJnCsV56aqkxgBd5Ii', name: 'foto (2) corregir mano.png' },
  { id: '1zQvQwap3QVU9YItDGv5GDpFseFKGAzZ4', name: 'IMG_0716 corregir pie.JPG' },
  { id: '1HY84V4-F_34aBLzzyWIoRBzDkRsU5Muo', name: 'IMG_0930 corregir falda.HEIC' },
  { id: '1dtlpoaaHb_Xb7LOPB2onlYYTSJtVvNlW', name: ' IMG_0936 corregir, arreglar la pretina.HEIC' },
  { id: '1SFkDS9pcEn9tJs2h7XY6UkTXjP05ILpI', name: 'IMG_0935 corregir esta muy lejos, acercar.HEIC' },
  { id: '1WGM1AKDJKknAA4y3rpuPROElITzU7jLJ', name: 'IMG_0940 corregir, mas cerca el traje.heic' },
  { id: '1czCK7cbVJA_SXr4lzbejlCGxqBD0MjYc', name: 'd72049af corregir mano, no importa con el pañuelo.JPG' },
  { id: '1wEPzHb8NdcKNXDtbgSNb4R_8J_gmLT4D', name: 'IMG_0977 corregir, poner al medio solo si se puede.jpg' },
  { id: '13ZynO8V3ZtA9Fh_T1cp9Bg7lSBqF_DM0', name: '34a63e97 corregir quitar el piso.JPG' },
  { id: '1hyDi4dw3mnW7lTZF94XSbnmuGAFXkKLb', name: 'foto (3)corregir no puede haber bordes blancos.png' },
  { id: '1cXO8MR2XQ3ywRQ-pLW2Kz7krHPZCFhsI', name: '1841c6d0 corregir, centrar foto esta muy abajo .JPG' },
  { id: '1h_Mu3269fTceDvz-22GBVlQyOUch22dr', name: 'foto corregir, quitar bordes blancos.png' },
  { id: '1EV27gAun31OescAc9RKb_UYXZq_XHIu6', name: 'IMG_0943 corregir, foto equivocada es todo negro.HEIC' },
  { id: '1Cg-BOApginfEAFUfI4IgeLvpKeZJJPnd', name: '781c5a14 corregir, se puede centrar?.JPG' },
  { id: '1rbiuU5SI3dLyeMtBL3bXl49BqfcOx_ie', name: '59c902a0 corregir, agregar brazo con pañuelo tal como esta en la original.JPG' },
  { id: '1NrwR5KoUgz77o1WvSxh-0VWMyWFMbHwx', name: 'IMG_0971 corregir.HEIC' },
  { id: '11TlBefZMhrReI6bNerFJVKCxJbpLBLbs', name: 'IMG_0965 corregir, no corresponde a la foto original.HEIC' },
  { id: '1ccO-dq_TTvZyDhTKhcCCSI-uOLqod_6y', name: 'foto (4) corregir, no puede haber marcos blancos.png' },
  { id: '1oRlOisSnwW3pdFcVSoYvf1QScSeoPE12', name: 'IMG_0962 corregir, quitar mano.HEIC' },
  { id: '1z0nb_N1SEJBGx_4r0jF9_S7uhxahPfQa', name: '5. CORREGIR' },
  { id: '1_DS9CaV8-2Rr87b_fzk9V5ZuqAlDKfbB', name: '9 barnie primaveral CORREGIR' }
];

console.log(`Moving ${filesToMove.length} corregir files to Fotos_Con_Feedback_Corregir (${targetFolderId})...`);

for (const f of filesToMove) {
  try {
    console.log(`Moving: ${f.name} (${f.id})...`);
    execSync(`gdrive mutate mv ${f.id} ${targetFolderId}`, { stdio: 'inherit' });
  } catch (e) {
    console.error(`Error moving ${f.name}:`, e.message);
  }
}

console.log('Finished moving corregir files.');
