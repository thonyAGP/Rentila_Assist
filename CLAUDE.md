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
`donnees.json` → **détecter locataire existant / proposer le loyer** → **ranger les pièces**
(nomenclature standard) → générer fiche locataire + **aide à l'activation Visale** →
**vérifier la complétude** → **présenter « À VALIDER »** → finaliser après accord.

Cas à gérer :
- **Profil locataire complet = priorité n°1** (sans profil, pas de dossier de location).
- **Colocation** : plusieurs emails pour une même location → rattacher avec `--dossier <slug>`.
- **Locataire existant** → le compléter (registre) plutôt que le recréer ; loyer proposé
  d'après l'ancien contrat du bien.

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
- `scripts/preparer_dossier.py <fichier.eml> [--nom N] [--dossier SLUG]` — déballe un email ;
  `--dossier` rattache à une location existante (colocation multi-emails).
- `scripts/rechercher_locataire.py --slug <slug>` — existant→complète / nouveau→à créer.
- `scripts/proposer_loyer.py <REF> [--slug <slug>]` — loyer d'après l'ancien contrat du bien.
- `scripts/organiser_pieces.py <slug>` — range/renomme les pièces.
- `scripts/remplir_templates.py <slug> [--bien REF]` — génère fiche + activation Visale.
- `scripts/verifier_completude.py <slug>` — récap « À VALIDER » + verdict prêt à signer.
- `scripts/enregistrer.py <slug>` — finalise : met à jour le registre (locataires + contrat).

## Config & registre
- `config/logement.yaml` — biens loués + bailleur + coefficient de revalorisation (copié depuis `.example`).
- `config/pieces_requises.yaml` — pièces exigées pour la signature.
- `registre/locataires.json` — locataires connus (détection existant/nouveau). Git-ignoré.
- `registre/contrats.json` — historique des contrats par bien (proposition de loyer). Git-ignoré.
