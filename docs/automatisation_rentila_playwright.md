# Piloter Rentila avec Playwright

Objectif : que Claude prenne la main sur Rentila pour **configurer ce qui manque** (charges
d'eau, taxe foncière, tableau d'amortissement…) et exploiter l'appli à fond — avec extraction
des mêmes informations et **validation humaine avant toute écriture**.

## Où ça s'exécute (important)
Le pilotage doit tourner **là où vous êtes authentifié sur Rentila** : votre ordinateur (ou
une session navigateur que vous ouvrez). Cette session cloud n'a pas accès à votre compte
Rentila connecté — elle sert à **écrire et tester le code**, pas à piloter votre compte réel.

Sur votre machine :
```
cd automation
npm install            # installe Playwright
npx playwright install chromium
```

## Le principe : jamais deviner, toujours cartographier
Je ne connais pas les sélecteurs internes de Rentila. Le workflow les **capture sur le vrai
site** au lieu de les inventer :

1. **Connexion** (une fois) — ouvre un navigateur visible, vous vous connectez (identifiants,
   2FA), la session est sauvegardée et réutilisée. Aucun mot de passe stocké, seulement les
   cookies (dans `automation/.auth/`, git-ignoré).
   ```
   node automation/connexion.mjs
   ```

2. **Cartographie** — sur chaque page à automatiser (fiche bien, onglet charges, fiscalité),
   liste les champs (id, name, label, valeur actuelle) et leurs sélecteurs.
   ```
   node automation/cartographier.mjs "https://www.rentila.com/..." --sortie carte.json
   ```
   Envoyez-moi la `carte.json` : je cale `config/rentila_selectors.json` dessus.

3. **Configuration** — remplit les champs d'un bien depuis `config/biens_fiscal.json`.
   **Mode DRY-RUN par défaut** : il lit la valeur actuelle, montre ce qu'il écrirait et prend
   une capture, **sans rien modifier**. Vous validez, puis vous appliquez.
   ```
   node automation/configurer_bien.mjs T2-RIVOLI              # dry-run (aucune écriture)
   node automation/configurer_bien.mjs T2-RIVOLI --appliquer  # écrit après votre validation
   ```

## Tableau d'amortissement
Calculé côté Python (déterministe), indépendamment du navigateur :
```
python3 scripts/amortissement.py T2-RIVOLI --sortie amortissement_T2.md --json amort_T2.json
```
Amortissement linéaire par composants (bâti décomposé, mobilier, travaux), prorata la 1re
année, terrain non amortissable. Une fois la structure du module LMNP de Rentila cartographiée,
on ajoute les champs correspondants dans `rentila_selectors.json` pour le report automatique.

## Données d'entrée
`config/biens_fiscal.json` (depuis `.example`) par bien : prix, frais, quote-part terrain,
composants, mobilier, travaux, **taxe foncière**, **charges d'eau**, TEOM récupérable.

## Sécurité & bonnes pratiques
- **DRY-RUN d'abord, toujours.** N'appliquez qu'après avoir lu le récap et la capture.
- La **session** (`.auth/`) et les **captures** sont git-ignorées (cookies + données perso).
- Le pilotage utilise **votre compte** : vérifiez que les CGU de Rentila ne l'interdisent pas.
- Commencez par **un seul bien**, un seul champ, en dry-run, avant d'étendre.
- Le point de **validation humaine** du projet reste la règle : Claude prépare et propose,
  vous validez avant que ce soit écrit.

## Variante « agent » (plus tard)
Pour un pilotage réellement conversationnel (Claude explore et remplit en autonomie), on peut
brancher un **serveur MCP Playwright** sur votre machine : Claude conduit le navigateur pas à
pas, en s'arrêtant sur les validations. Les scripts ci-dessus restent la base fiable et
reproductible.
