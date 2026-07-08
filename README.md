# Rentila Assist

Assistant d'automatisation pour la gestion locative. Quand un nouveau locataire arrive,
vous **transférez son email** (avec la photo de sa pièce d'identité) : Claude lit la pièce,
**remplit la fiche locataire**, **prépare le dossier Visale**, définit la **photo de profil**,
puis vous présente un récapitulatif **« À VALIDER »** avant toute finalisation.

Rien n'est finalisé sans votre validation.

## Démarrage rapide

1. **Configurez vos biens** :
   ```
   cp config/logement.example.yaml config/logement.yaml
   # éditez avec vos logements et vos coordonnées de bailleur
   ```

2. **Amenez un email dans `inbox/`** (voir `docs/regle_transfert_email.md`) — par ex.
   téléchargez l'email du locataire au format `.eml` et déposez-le dans `inbox/`.

3. **Déballez-le** :
   ```
   python3 scripts/preparer_dossier.py inbox/mon_email.eml --nom "Dupont Marie"
   ```

4. **Demandez à Claude de traiter le dossier** (skill **`nouveau-locataire`**). Claude :
   - lit la pièce d'identité (vision) et remplit `dossiers/<slug>/donnees.json`,
   - choisit la photo de profil,
   - génère `fiche_locataire.md` et `dossier_visale.md`,
   - vous présente le récap **À VALIDER**.

5. **Validez** (ou corrigez un champ). Claude finalise et liste les actions restantes sur
   votre plateforme de gestion locative.

## Arborescence

| Chemin | Rôle |
|---|---|
| `.claude/skills/nouveau-locataire/` | Le workflow que Claude exécute |
| `templates/` | Modèles fiche locataire + dossier Visale |
| `schemas/locataire.schema.json` | Structure des données extraites |
| `scripts/preparer_dossier.py` | Déballe un `.eml` en dossier de travail |
| `scripts/remplir_templates.py` | Remplit les modèles depuis `donnees.json` + logement |
| `config/logement.yaml` | Vos biens loués (à créer depuis l'exemple) |
| `inbox/` | Emails transférés à traiter |
| `dossiers/` | Un sous-dossier par locataire |
| `docs/` | Règle de transfert, mémo Visale, automatisation |

## Documents produits par dossier
- **Fiche locataire** (`fiche_locataire.md`) — identité, contact, situation, garant, logement.
- **Dossier Visale** (`dossier_visale.md`) — éligibilité, infos candidat, checklist, logement.
- **Photo de profil** (`photo_profil.jpg`).
- **donnees.json** — données structurées réutilisables.

## Notes
- Les champs non lisibles restent vides et signalés (`⚠️ à compléter`) — jamais inventés.
- Visale : la demande officielle se fait par le candidat sur [visale.fr](https://www.visale.fr).
  Voir `docs/visale.md`.
- Extension possible : workflow **départ / état des lieux** (mentionné mais non prioritaire).
