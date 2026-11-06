const { execSync } = require('child_process');

const targetFolderId = '16wT0ogNsfd-r2U1bGuuw01Rdxj269bxW';

const filesToMove = [
  // 10 ERROR_TEST
  { id: '1AvYf0vtlMOMakeVloQQ7vgg2xNiL_dVE', name: '3_Escapulario_Mujer_PRO_1x1_ERROR_TEST.jpg' },
  { id: '1x1ElpEqS3D0sQTEgCWr__lrIsWQWLOs8', name: '4_Escapulario_Mujer_PRO_1x1_ERROR_TEST.jpg' },
  { id: '1IkPT_smNCaoi78GajbTbJI-2mhNWfxBE', name: '5_Escapulario_Mujer_PRO_1x1_ERROR_TEST.jpg' },
  { id: '15XHPBCJV2sqt7QmR_PeXv6IuW8sgjvcD', name: '6_Escapulario_Mujer_PRO_1x1_ERROR_TEST.jpg' },
  { id: '1YGniu1e_WQ8nvXzdd7UhFEqWc9lXNATN', name: '1_Collar_Aretes_Filigrana_PRO_1x1_ERROR_TEST.jpg' },
  { id: '1JMDMxxQmaNAOfrh1Eh-3oJA8KFYOqLpq', name: '2_Collar_Aretes_Filigrana_PRO_1x1_ERROR_TEST.jpg' },
  { id: '1iAhWg8s5H4R5-0t9MM0BOrNMgoCP11BJ', name: '3_Collar_Aretes_Filigrana_PRO_1x1_ERROR_TEST.jpg' },
  { id: '1s_zYybSDywy0irzu6E_B2YLfi_5ELFpf', name: '4_Collar_Aretes_Filigrana_PRO_1x1_ERROR_TEST.jpg' },
  { id: '1edkeS9CCHoA716T1RSrLJeuzJJaoLN0m', name: '1_Manto_Pava_Bordado_PRO_1x1_ERROR_TEST.jpg' },
  { id: '1ssQ0Liqvq4zf3x-VnhCQD6VTBnfQnaGA', name: '2_Manto_Pava_Bordado_PRO_1x1_ERROR_TEST.jpg' },
  // 3 instrucciones de texto en fotos lista para procesar
  { id: '1Xv-w3FrRk9xNWh3_R886FZWjDZHgbV0_', name: 'corregir, la dimencion de la foto es muy delgado mejorar las proporciones' },
  { id: '1yRuPh3s8wHNV1nTfOnZdOVXqQFLBmJhl', name: 'corregir, no corresponde a la imagen original volverlo hacer' },
  { id: '1deC6y6Q6TXQhQgPK7FUH9yKVS6YY73Um', name: 'corregir, no se ha modificado nada' }
];

console.log(`Moving ${filesToMove.length} files to _Fotos_Erroneas_y_Desalineadas (${targetFolderId})...`);

for (const f of filesToMove) {
  try {
    console.log(`Moving: ${f.name} (${f.id})...`);
    execSync(`gdrive mutate mv ${f.id} ${targetFolderId}`, { stdio: 'inherit' });
  } catch (e) {
    console.error(`Error moving ${f.name}:`, e.message);
  }
}

console.log('Finished moving files.');
