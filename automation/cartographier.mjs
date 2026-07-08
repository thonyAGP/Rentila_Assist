// Cartographie une page Rentila : liste tous les champs de formulaire (id, name, type,
// label, placeholder) et les liens/boutons, pour construire les selecteurs sans deviner.
// A lancer sur chaque page a automatiser (fiche bien, onglet charges, fiscalite...).
//
// Usage :
//   node automation/cartographier.mjs "https://www.rentila.com/xxx" [--sortie carte.json]
import { lancer, contexteAuth } from './lib/browser.mjs';
import { writeFileSync } from 'node:fs';

const args = process.argv.slice(2);
const url = args.find((a) => a.includes('://'));
const iSortie = args.indexOf('--sortie');
const sortie = iSortie >= 0 ? args[iSortie + 1] : null;
const AUTH = 'automation/.auth/rentila.json';

if (!url) {
  console.error('Indiquez une URL. Ex: node automation/cartographier.mjs "https://www.rentila.com/..."');
  process.exit(1);
}

const browser = await lancer({ headless: true });
const context = await contexteAuth(browser, AUTH);
const page = await context.newPage();
await page.goto(url, { waitUntil: 'networkidle' }).catch(() => page.goto(url));

// Extraction cote page : champs + labels associes + liens/boutons
const carte = await page.evaluate(() => {
  const labelPour = (el) => {
    if (el.id) {
      const l = document.querySelector(`label[for="${el.id}"]`);
      if (l) return l.textContent.trim();
    }
    const p = el.closest('label');
    return p ? p.textContent.trim() : null;
  };
  const champs = [...document.querySelectorAll('input, select, textarea')].map((el) => ({
    tag: el.tagName.toLowerCase(),
    type: el.type || null,
    id: el.id || null,
    name: el.getAttribute('name') || null,
    placeholder: el.getAttribute('placeholder') || null,
    label: labelPour(el),
    valeur_actuelle: el.value || null,
    selecteur: el.id ? `#${el.id}` : (el.getAttribute('name') ? `[name="${el.getAttribute('name')}"]` : null),
  }));
  const actions = [...document.querySelectorAll('button, a[href]')].slice(0, 80).map((el) => ({
    tag: el.tagName.toLowerCase(),
    texte: (el.textContent || '').trim().slice(0, 60),
    href: el.getAttribute('href') || null,
    id: el.id || null,
  }));
  return { titre: document.title, champs, actions };
});

const resultat = { url, ...carte };
console.log(`Page : ${carte.titre}`);
console.log(`Champs de formulaire trouves : ${carte.champs.length}`);
for (const c of carte.champs) {
  console.log(`  ${(c.label || c.placeholder || '(sans label)').padEnd(35)} -> ${c.selecteur || '(pas de selecteur stable)'} [${c.type || c.tag}]`);
}

if (sortie) {
  writeFileSync(sortie, JSON.stringify(resultat, null, 2), 'utf-8');
  console.log(`\nCarte ecrite dans ${sortie} — envoyez-la moi pour caler config/rentila_selectors.json.`);
}

await browser.close();
process.exit(0);
