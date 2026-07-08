# Rentila Assist — instructions projet

Assistant de gestion locative. Automatise l'entrée d'un nouveau locataire à partir d'un
email transféré, et s'arrête toujours sur une **validation humaine** avant de finaliser.

## Workflow principal
Quand l'utilisateur transfère un email de locataire, dépose une pièce d'identité, ou demande
de « traiter un dossier locataire » → utiliser le skill **`nouveau-locataire`**
(`.claude/skills/nouveau-locataire/SKILL.md`).

Étapes : déballer l'email → lire la pièce d'identité (vision) → remplir `donnees.json` →
choisir la photo de profil → générer fiche locataire + dossier Visale → **présenter « À
VALIDER »** → finaliser après accord.

## Règles impératives
- **Ne jamais inventer** une donnée. Champ illisible/absent → `null` + ajouter à
  `meta.champs_incertains`. Signaler la confiance.
- **Ne jamais finaliser** sans validation explicite de l'utilisateur.
- Documents prioritaires : **fiche locataire** et **dossier Visale**.
- Données personnelles sensibles (pièces d'identité) : rester dans `dossiers/`, ne pas les
  exposer ailleurs. Ces dossiers sont git-ignorés.

## Scripts
- `scripts/preparer_dossier.py <fichier.eml> [--nom "Nom Prénom"]` — déballe un email.
- `scripts/remplir_templates.py <slug> [--bien REF]` — remplit les modèles.

Les deux n'utilisent que la bibliothèque standard (PyYAML utilisé s'il est présent).

## Config
`config/logement.yaml` (copié depuis `.example`) décrit les biens loués et le bailleur.

## Extension
Un workflow **départ / état des lieux** est mentionné dans le README comme évolution future.
