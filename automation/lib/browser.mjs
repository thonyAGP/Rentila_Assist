// Utilitaires navigateur Playwright pour le pilotage de Rentila.
// Charge Playwright depuis node_modules (npm install) ou, a defaut, depuis l'install
// globale (utile en environnement de test). executablePath surchargeable via CHROMIUM_PATH.
import { readFileSync, mkdirSync, existsSync } from 'node:fs';
import { dirname, resolve } from 'node:path';

export async function chargerChromium() {
  try {
    return (await import('playwright')).chromium;
  } catch {
    return (await import('/opt/node22/lib/node_modules/playwright/index.mjs')).chromium;
  }
}

export function lireJson(chemin) {
  return JSON.parse(readFileSync(chemin, 'utf-8'));
}

// Lance un navigateur. headless=false pour la connexion manuelle (2FA, captcha).
export async function lancer({ headless = true } = {}) {
  const chromium = await chargerChromium();
  const opts = { headless };
  if (process.env.CHROMIUM_PATH) opts.executablePath = process.env.CHROMIUM_PATH;
  return chromium.launch(opts);
}

// Ouvre un contexte en reutilisant la session sauvegardee si elle existe.
export async function contexteAuth(browser, cheminAuth) {
  const opts = existsSync(cheminAuth) ? { storageState: cheminAuth } : {};
  return browser.newContext(opts);
}

export function assurerDossier(cheminFichier) {
  mkdirSync(dirname(resolve(cheminFichier)), { recursive: true });
}
