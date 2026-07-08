# Rentila Assist — instructions projet

Assistant de gestion locative. Automatise l'entrée d'un nouveau locataire à partir d'un
email transféré, et s'arrête toujours sur une **validation humaine** avant de finaliser.

## Workflow principal
Quand l'utilisateur transfère un email de locataire, dépose des pièces, ou demande de
« traiter un dossier locataire » → utiliser le skill **`nouveau-locataire`**
(`.claude/skills/nouveau-locataire/SKILL.md`).

Le locataire fournit un **lot de pièces** : pièce d'identité, PDF de garantie Visale,
certificat de scolarité, attestation d'assurance, état des lieux.

Étapes : recevoir le lot → **classer et lire chaque pièce** (vision + lecture PDF) → remplir
`donnees.json` → **ranger les pièces** (nomenclature standard) → générer fiche locataire +
**aide à l'activation Visale** → **vérifier la complétude** → **présenter « À VALIDER »** →
finaliser après accord.

## Règles impératives
- **Ne jamais inventer** une donnée. Champ illisible/absent → `null` + ajouter à
  `meta.champs_incertains`. Signaler la confiance.
- **Ne jamais finaliser** sans validation explicite de l'utilisateur.
- Objectifs clés : **ranger les pièces**, **extraire le code Visale + caractéristiques du
  logement** pour activer la couverture, **extraire bien + noms de l'état des lieux**, et
  aboutir à un **contrat prêt à signer**.
- Données personnelles sensibles (pièces d'identité) : rester dans `dossiers/`, ne pas les
  exposer ailleurs. Ces dossiers sont git-ignorés.

## Scripts (bibliothèque standard uniquement, PyYAML utilisé s'il est présent)
- `scripts/preparer_dossier.py <fichier.eml> [--nom "Nom Prénom"]` — déballe un email.
- `scripts/organiser_pieces.py <slug>` — range/renomme les pièces.
- `scripts/remplir_templates.py <slug> [--bien REF]` — génère fiche + activation Visale.
- `scripts/verifier_completude.py <slug>` — récap « À VALIDER » + verdict prêt à signer.

## Config
- `config/logement.yaml` — biens loués + bailleur (copié depuis `.example`).
- `config/pieces_requises.yaml` — pièces exigées pour la signature.
