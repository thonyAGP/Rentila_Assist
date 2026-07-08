---
name: nouveau-locataire
description: >
  Traite l'arrivee d'un nouveau locataire a partir d'un email transfere contenant
  la piece d'identite. Lit la piece d'identite (vision), remplit la fiche locataire,
  prepare le dossier Visale, definit la photo de profil, puis presente un recapitulatif
  "A VALIDER" avant toute finalisation. Utiliser quand l'utilisateur transfere un email
  de nouveau locataire, depose une photo de piece d'identite, ou demande de "traiter un
  dossier locataire".
---

# Skill : Nouveau locataire

Objectif : automatiser l'entree d'un nouveau locataire tout en laissant l'humain valider
avant finalisation. **Rien n'est finalise sans validation explicite de l'utilisateur.**

## Principe de securite des donnees
- Ne JAMAIS inventer une valeur. Si un champ n'est pas lisible sur la piece ou absent de
  l'email, laisser `null` et l'ajouter dans `meta.champs_incertains`.
- Toujours signaler le niveau de confiance et les champs a re-verifier.

## Etapes

### 1. Localiser le dossier
- Si un `.eml` vient d'etre depose dans `inbox/`, le deballer :
  ```
  python3 scripts/preparer_dossier.py inbox/<fichier>.eml
  ```
  (option `--nom "Nom Prenom"` pour forcer le nom du dossier)
- Si l'utilisateur a directement depose des images/PDF, creer `dossiers/<slug>/pieces/`
  et y placer les fichiers, plus un `meta.json` minimal.
- Le dossier de travail est `dossiers/<slug>/`.

### 2. Lire la piece d'identite (vision)
- Lire chaque image/PDF de `dossiers/<slug>/pieces/` avec l'outil Read.
- Extraire les champs selon `schemas/locataire.schema.json` :
  identite (nom de naissance, nom d'usage, prenoms, sexe, date et lieu de naissance,
  nationalite), piece (type, numero, dates, autorite), et la MRZ si lisible pour recouper.
- Recouper les dates avec la MRZ quand elle est presente.
- Lire `dossiers/<slug>/email.txt` pour recuperer **email**, **telephone**, **adresse
  actuelle**, **situation professionnelle**, et un eventuel **garant** ou **numero Visale**.

### 3. Definir la photo de profil
- Reperer la photo d'identite sur la piece.
- Si une photo de portrait separee est fournie dans les pieces, la preferer.
- Copier/recadrer l'image retenue vers `dossiers/<slug>/photo_profil.jpg` et renseigner
  `photo_profil` dans les donnees. (Pour un recadrage precis, utiliser Pillow si dispo ;
  sinon copier la photo fournie telle quelle et le noter dans `champs_incertains`.)

### 4. Ecrire donnees.json
- Ecrire `dossiers/<slug>/donnees.json` conforme au schema.
- Renseigner `meta.confiance_globale` (Haute/Moyenne/Faible) et `meta.champs_incertains`.
- Pour Visale, pre-evaluer `visale.eligible_pressenti` (Oui/Non/A verifier) selon l'age
  (18-30 ans = eligible quelle que soit la situation) et le plafond de loyer du bien.

### 5. Remplir les documents
- Associer le bon bien : demander/deviner la `ref` (`config/logement.yaml`), la passer en
  `--bien`.
  ```
  python3 scripts/remplir_templates.py <slug> --bien <REF>
  ```
- Cela genere `fiche_locataire.md` et `dossier_visale.md` dans le dossier.

### 6. Presenter "A VALIDER" (checkpoint humain)
Afficher a l'utilisateur, de facon concise :
- Un **tableau des champs extraits** avec la source (piece d'identite / email) ;
- Les **champs incertains ou manquants** en evidence ;
- Le **verdict d'eligibilite Visale** de principe et ce qui reste a confirmer ;
- Le chemin de la **photo de profil** retenue ;
- Les deux documents generes.

Puis demander explicitement : **« Je valide ? Corriges-tu un champ avant de finaliser ? »**
Ne PAS finaliser tant que l'utilisateur n'a pas valide.

### 7. Finaliser (uniquement apres validation)
- Appliquer les corrections eventuelles dans `donnees.json` et re-remplir les templates.
- Marquer `meta.statut = "valide"` dans `dossiers/<slug>/meta.json`.
- Recapituler les actions manuelles restantes cote plateforme de gestion locative :
  creer la fiche locataire (copier les champs / importer la photo de profil), lancer la
  demande Visale, preparer le bail.

## Rappels
- Documents prioritaires : **fiche locataire** + **dossier Visale**.
- Visale : la demande officielle se fait par le candidat sur visale.fr ; verifier les
  conditions a jour (voir `docs/visale.md`).
