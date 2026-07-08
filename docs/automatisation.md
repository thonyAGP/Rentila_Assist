# Automatisation — déclencher le traitement sans intervention

Le principe voulu : **tout se traite automatiquement, et Claude vous présente juste le
récapitulatif à valider** avant finalisation. Voici comment câbler ça.

## Le point de validation reste humain (voulu)
Le skill `nouveau-locataire` s'arrête toujours à l'étape « À VALIDER » et attend votre
accord. C'est le garde-fou : l'extraction et le remplissage sont automatiques, la
finalisation est validée.

## Déclencher automatiquement le traitement

### Via une Routine (Claude Code)
Vous pouvez programmer une session qui, à intervalle régulier, regarde `inbox/`, traite les
nouveaux `.eml` et vous présente les dossiers à valider.

Prompt type de la Routine (session qui reprend ce projet) :
> « Regarde `inbox/`. Pour chaque nouvel email non traité, exécute le skill
>   *nouveau-locataire* jusqu'à l'étape À VALIDER, puis présente-moi les dossiers à valider.
>   Ne finalise rien sans mon accord. »

Cadence conseillée : 1×/jour ou à la demande. (Voir l'outil de création de Routine de votre
environnement Claude Code.)

### Alimenter inbox/ automatiquement (optionnel)
Pour que les emails arrivent seuls dans `inbox/` :
- **Gmail API** : un script planifié récupère les messages du libellé `Locataires/Entrée`,
  écrit chaque message en `.eml` dans `inbox/`. Nécessite des identifiants OAuth Google.
- **Service mail-to-webhook** : votre règle Gmail transfère vers une adroit dédiée d'un
  service qui dépose le `.eml` dans le dépôt via un commit/API.

> Sans ces branchements, le dépôt manuel du `.eml` dans `inbox/` (voir
> `regle_transfert_email.md`) déclenche le même workflow.

## Chaîne complète visée
```
Email locataire ──(règle Gmail)──► inbox/*.eml
        │
        ▼  (Routine ou manuel)
  preparer_dossier.py ──► dossiers/<slug>/ (pièces + email.txt)
        │
        ▼  (skill nouveau-locataire : vision + remplissage)
  donnees.json + photo_profil + fiche + dossier Visale
        │
        ▼
  ⏸️  RÉCAP « À VALIDER »  ── vous validez ──► finalisation
```
