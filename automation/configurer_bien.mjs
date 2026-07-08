// Configure un bien sur Rentila : remplit les champs manquants (taxe fonciere, charges
// d'eau, et tout champ defini dans les selecteurs). PILOTE PAR CONFIG, pas de selecteur
// devine : les selecteurs viennent de la cartographie (cartographier.mjs).
//
// SECURITE : mode DRY-RUN par defaut — il navigue, lit la valeur actuelle, montre ce qu'il
// remplirait et prend une capture, SANS RIEN ECRIRE. Ajoutez --appliquer pour ecrire
// reellement (apres votre validation du dry-run).
//
// Usage :
//   node automation/configurer_bien.mjs T2-RIVOLI                 (dry-run)
//   node automation/configurer_bien.mjs T2-RIVOLI --appliquer      (ecrit)
import { lancer, contexteAuth, lireJson, assurerDossier } from './lib/browser.mjs';

const args = process.argv.slice(2);
const ref = args.find((a) => !a.startsWith('--'));
const appliquer = args.includes('--appliquer');
const SELECTEURS = 'config/rentila_selectors.json';
const FISCAL = 'config/biens_fiscal.json';

if (!ref) { console.error('Indiquez la ref du bien. Ex: node automation/configurer_bien.mjs T2-RIVOLI'); process.exit(1); }

let sel, fiscal;
try { sel = lireJson(SELECTEURS); } catch { console.error(`Manque ${SELECTEURS} (copiez l'exemple et calez-le via la cartographie).`); process.exit(1); }
try { fiscal = lireJson(FISCAL); } catch { console.error(`Manque ${FISCAL} (copiez biens_fiscal.example.json).`); process.exit(1); }

const biens = fiscal.biens || fiscal;
const bien = biens.find((b) => b.ref === ref);
if (!bien) { console.error(`Bien '${ref}' absent de ${FISCAL}.`); process.exit(1); }

const base = sel.base_url || process.env.RENTILA_URL || 'https://www.rentila.com';
const idRentila = (sel.biens && sel.biens[ref] && sel.biens[ref].id) || null;
const AUTH = sel.auth || 'automation/.auth/rentila.json';

const resoudre = (obj, chemin) => chemin.split('.').reduce((o, k) => (o == null ? o : o[k]), obj);
const urlDe = (tpl) => base + tpl.replaceAll('{id}', idRentila ?? '').replaceAll('{ref}', ref);

console.log(`\n=== ${appliquer ? 'APPLIQUER' : 'DRY-RUN'} — bien ${ref} ===`);
if (!appliquer) console.log('(aucune ecriture ; ajoutez --appliquer apres avoir valide ce qui suit)\n');

const browser = await lancer({ headless: appliquer ? true : true });
const context = await contexteAuth(browser, AUTH);
const page = await context.newPage();

const rapport = [];
for (const champ of sel.champs || []) {
  const voulu = champ.valeur_directe ?? resoudre(bien, champ.cle);
  if (voulu == null || voulu === '') { console.log(`- ${champ.libelle}: pas de valeur dans biens_fiscal (ignore)`); continue; }
  try {
    await page.goto(urlDe(champ.url), { waitUntil: 'networkidle' }).catch(() => page.goto(urlDe(champ.url)));
    const loc = page.locator(champ.selecteur);
    await loc.waitFor({ timeout: 8000 });
    const actuel = champ.type === 'select' ? await loc.inputValue().catch(() => null) : await loc.inputValue().catch(() => null);
    const changement = String(actuel ?? '') !== String(voulu);
    console.log(`- ${champ.libelle}: actuel="${actuel ?? ''}" -> voulu="${voulu}" ${changement ? '➤ à modifier' : '(déjà à jour)'}`);
    rapport.push({ champ: champ.libelle, actuel, voulu, changement });

    if (appliquer && changement) {
      if (champ.type === 'select') await loc.selectOption(String(voulu));
      else { await loc.fill(''); await loc.fill(String(voulu)); }
      if (champ.bouton_valider) await page.click(champ.bouton_valider).catch(() => {});
      console.log(`    ✔ écrit`);
    }
  } catch (e) {
    console.log(`- ${champ.libelle}: ⚠️ champ introuvable (${champ.selecteur}) — recartographier la page. ${e.message.split('\n')[0]}`);
    rapport.push({ champ: champ.libelle, erreur: e.message.split('\n')[0] });
  }
}

// Capture d'ecran de controle
const shot = `automation/captures/${ref}_${appliquer ? 'apres' : 'dryrun'}.png`;
assurerDossier(shot);
await page.screenshot({ path: shot, fullPage: true }).catch(() => {});
console.log(`\nCapture : ${shot}`);
if (!appliquer) console.log('Validez ce dry-run, puis relancez avec --appliquer pour écrire.');

await browser.close();
process.exit(0);
