// Connexion a Rentila : ouvre un navigateur visible, vous vous connectez a la main
// (identifiants, 2FA, captcha eventuel), puis la session est sauvegardee et reutilisee
// par les autres scripts. Aucune donnee de mot de passe n'est stockee : seule la session
// (cookies) est enregistree dans automation/.auth/rentila.json (git-ignore).
//
// Usage : node automation/connexion.mjs
import { lancer, assurerDossier } from './lib/browser.mjs';

const BASE = process.env.RENTILA_URL || 'https://www.rentila.com';
const AUTH = 'automation/.auth/rentila.json';

const browser = await lancer({ headless: false });
const context = await browser.newContext();
const page = await context.newPage();

console.log(`Ouverture de ${BASE} — connectez-vous dans la fenetre, puis revenez ici.`);
await page.goto(BASE);

console.log('Quand vous etes connecte (tableau de bord affiche), appuyez sur Entree ici...');
await new Promise((res) => process.stdin.once('data', res));

assurerDossier(AUTH);
await context.storageState({ path: AUTH });
console.log(`Session sauvegardee dans ${AUTH}. Les prochains scripts la reutiliseront.`);

await browser.close();
process.exit(0);
