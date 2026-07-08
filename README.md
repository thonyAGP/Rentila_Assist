# Rentila Assist

Assistant d'automatisation pour la gestion locative. À chaque nouveau locataire, vous recevez
un **lot de pièces** (pièce d'identité, PDF de garantie Visale, certificat de scolarité,
attestation d'assurance, état des lieux). Claude les **classe et range**, **extrait les infos
clés** (code Visale, noms, bien), prépare l'**activation Visale** et vérifie que le dossier est
**prêt à signer** — puis vous présente un récapitulatif **« À VALIDER »** avant toute action.

Rien n'est finalisé sans votre validation.

## Ce que ça fait

1. **Remplit le profil de chaque locataire** (identité + contact depuis la pièce d'identité)
   — priorité n°1 : sans profil complet, pas de dossier de location.
2. **Classe et range les pièces** dans `dossiers/<location>/pieces/` avec des noms clairs,
   prêts à téléverser dans la page « pièces » de la location.
3. **Extrait** : noms des locataires (pièce d'identité), **code Visale** + validité (PDF
   Visale), établissement (certificat de scolarité), assureur/contrat (assurance), **bien +
   noms** (état des lieux).
4. **Gère la colocation** : plusieurs emails (un par colocataire) rattachés à une même location.
5. **Détecte les locataires connus** : complète un locataire existant plutôt que le recréer,
   et **propose le loyer d'après l'ancien contrat** du bien.
6. **Prépare l'activation Visale** : code visa + caractéristiques du logement à saisir sur
   visale.fr pour activer la couverture.
7. **Vérifie la complétude** : profil + pièces → verdict **contrat prêt à signer**.

## Démarrage rapide

1. **Configurez** vos biens et vos pièces requises :
   ```
   cp config/logement.example.yaml config/logement.yaml
   cp config/pieces_requises.example.yaml config/pieces_requises.yaml
   ```
2. **Amenez les pièces** dans `inbox/` (email `.eml`) ou directement dans
   `dossiers/<slug>/pieces/`.
3. **Traitez** — demandez à Claude (skill **`nouveau-locataire`**). Claude classe, extrait,
   range, prépare l'activation Visale, vérifie la complétude et présente le récap **À VALIDER**.
4. **Validez** → Claude finalise et liste les actions restantes (téléverser les pièces,
   activer Visale sur le site, enregistrer l'état des lieux).

## Chaîne

```
Lot de pièces ──► inbox/ ou dossiers/<slug>/pieces/
      │  preparer_dossier.py [--dossier SLUG]  (si .eml ; --dossier = colocation)
      ▼
  Claude : classe + lit chaque pièce → donnees.json
      │  rechercher_locataire.py (existant→complète / nouveau)
      │  proposer_loyer.py       (loyer d'après l'ancien contrat)
      │  organiser_pieces.py     (range/renomme les pièces)
      │  remplir_templates.py    (fiche + activation Visale)
      │  verifier_completude.py  (récap + verdict : profil + pièces)
      ▼
  ⏸️  « À VALIDER »  ── vous validez ──►  enregistrer.py (registre) → contrat prêt à signer
```

## Arborescence

| Chemin | Rôle |
|---|---|
| `.claude/skills/nouveau-locataire/` | Le workflow que Claude exécute |
| `schemas/dossier.schema.json` | Structure des données du dossier |
| `templates/fiche_locataire.md` | Fiche récap locataire(s) + logement + bail |
| `templates/visale_activation.md` | Aide à l'activation Visale (code + logement) |
| `scripts/preparer_dossier.py` | Déballe un `.eml` (option `--dossier` pour colocation) |
| `scripts/rechercher_locataire.py` | Détecte locataire existant / nouveau (registre) |
| `scripts/proposer_loyer.py` | Propose le loyer d'après l'ancien contrat du bien |
| `scripts/organiser_pieces.py` | Range/renomme les pièces (nomenclature standard) |
| `scripts/remplir_templates.py` | Génère les documents depuis `donnees.json` |
| `scripts/verifier_completude.py` | Checklist profil + pièces, verdict « prêt à signer » |
| `scripts/enregistrer.py` | Finalise : met à jour le registre (locataires + contrat) |
| `scripts/exporter_rentila_csv.py` | Génère un CSV d'import locataires pour Rentila |
| `scripts/analyser_har.py` | Extrait les appels API d'une capture réseau (HAR) |
| `scripts/amortissement.py` | Calcule le tableau d'amortissement LMNP d'un bien |
| `automation/` | Pilotage Playwright de Rentila (connexion, cartographie, config) |
| `config/logement.yaml` · `config/pieces_requises.yaml` | Biens + pièces exigées (depuis `.example`) |
| `registre/locataires.json` · `registre/contrats.json` | Locataires connus · historique des contrats |
| `inbox/` · `dossiers/` | Emails à traiter · un sous-dossier par location |
| `docs/` | Transfert email, Visale, état des lieux, automatisation |

## Saisie sur Rentila / Visale
Voir `docs/integration.md`. En résumé :
- **Rentila** : pas d'API REST publique documentée, mais **import CSV** des locataires
  (`exporter_rentila_csv.py`) ; mention « API & MCP » à vérifier dans votre compte.
- **Visale** : pas d'API → **capture de vos saisies** (HAR) puis `analyser_har.py` pour
  reconstituer les appels (`docs/capturer_appels.md`).

## Piloter Rentila (Playwright) — configurer les biens à fond
Voir `docs/automatisation_rentila_playwright.md`. S'exécute **sur votre machine** (où vous
êtes connecté à Rentila), avec **dry-run + validation avant écriture** :
1. `node automation/connexion.mjs` — connexion (session réutilisée, aucun mot de passe stocké).
2. `node automation/cartographier.mjs "<url>"` — capture les champs/sélecteurs d'une page.
3. `node automation/configurer_bien.mjs <REF>` — remplit taxe foncière, charges d'eau, etc.
   (dry-run ; `--appliquer` pour écrire). Amortissement via `scripts/amortissement.py`.

## Notes
- Champs non lus → `⚠️ à compléter`, jamais inventés ; signalés dans `meta.champs_incertains`.
- Les dossiers (pièces d'identité, etc.) sont **git-ignorés**.
- Scripts en **bibliothèque standard** uniquement (PyYAML utilisé s'il est présent).
