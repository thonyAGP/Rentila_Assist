# Rentila Assist

Assistant d'automatisation pour la gestion locative. À chaque nouveau locataire, vous recevez
un **lot de pièces** (pièce d'identité, PDF de garantie Visale, certificat de scolarité,
attestation d'assurance, état des lieux). Claude les **classe et range**, **extrait les infos
clés** (code Visale, noms, bien), prépare l'**activation Visale** et vérifie que le dossier est
**prêt à signer** — puis vous présente un récapitulatif **« À VALIDER »** avant toute action.

Rien n'est finalisé sans votre validation.

## Ce que ça fait

1. **Classe et range les pièces** dans `dossiers/<location>/pieces/` avec des noms clairs,
   prêts à téléverser dans la page « pièces » de la location.
2. **Extrait** : noms des locataires (pièce d'identité), **code Visale** + validité (PDF
   Visale), établissement (certificat de scolarité), assureur/contrat (assurance), **bien +
   noms** (état des lieux).
3. **Prépare l'activation Visale** : code visa + caractéristiques du logement à saisir sur
   visale.fr pour activer la couverture.
4. **Vérifie la complétude** : quelles pièces manquent → verdict **contrat prêt à signer**.

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
      │  preparer_dossier.py (si .eml)
      ▼
  Claude : classe + lit chaque pièce → donnees.json
      │  organiser_pieces.py   (range/renomme les pièces)
      │  remplir_templates.py  (fiche + activation Visale)
      │  verifier_completude.py(récap + verdict)
      ▼
  ⏸️  « À VALIDER »  ── vous validez ──►  finalisation (contrat prêt à signer)
```

## Arborescence

| Chemin | Rôle |
|---|---|
| `.claude/skills/nouveau-locataire/` | Le workflow que Claude exécute |
| `schemas/dossier.schema.json` | Structure des données du dossier |
| `templates/fiche_locataire.md` | Fiche récap locataire(s) + logement |
| `templates/visale_activation.md` | Aide à l'activation Visale (code + logement) |
| `scripts/preparer_dossier.py` | Déballe un `.eml` en dossier de travail |
| `scripts/organiser_pieces.py` | Range/renomme les pièces (nomenclature standard) |
| `scripts/remplir_templates.py` | Génère les documents depuis `donnees.json` |
| `scripts/verifier_completude.py` | Checklist + verdict « prêt à signer » |
| `config/logement.yaml` | Vos biens loués (à créer depuis l'exemple) |
| `config/pieces_requises.yaml` | Pièces exigées pour la signature |
| `inbox/` · `dossiers/` | Emails à traiter · un sous-dossier par location |
| `docs/` | Transfert email, Visale, état des lieux, automatisation |

## Notes
- Champs non lus → `⚠️ à compléter`, jamais inventés ; signalés dans `meta.champs_incertains`.
- Les dossiers (pièces d'identité, etc.) sont **git-ignorés**.
- Scripts en **bibliothèque standard** uniquement (PyYAML utilisé s'il est présent).
