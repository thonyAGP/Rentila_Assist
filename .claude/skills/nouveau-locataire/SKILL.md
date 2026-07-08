---
name: nouveau-locataire
description: >
  Traite le dossier d'un nouveau locataire a partir d'un lot de pieces (piece d'identite,
  PDF de garantie Visale, certificat de scolarite, attestation d'assurance, etat des lieux).
  Classe et range les pieces, extrait les infos clefs (code Visale, noms, bien), prepare
  l'activation Visale et la fiche locataire, verifie la completude, puis presente un
  recapitulatif "A VALIDER" avant toute finalisation. Utiliser quand l'utilisateur transfere
  un email de locataire, depose des pieces, ou demande de "traiter un dossier locataire".
---

# Skill : Nouveau locataire

Objectif : recevoir un lot de pieces, tout ranger et extraire, preparer l'activation Visale
et verifier que le dossier est **pret a signer** — en laissant l'humain valider.
**Rien n'est finalise sans validation explicite de l'utilisateur.**

## Priorites
1. **PROFIL LOCATAIRE COMPLET = condition n1.** Sans profil (identite + contact) saisissable,
   pas de dossier de location. C'est l'objectif prioritaire : remplir le profil de chaque
   locataire, signaler tout champ manquant.
2. **Colocation** : une location peut recevoir **plusieurs emails** (un par colocataire).
   Les rattacher au meme dossier et fusionner les locataires.
3. **Locataire deja connu** : le completer plutot que le recreer ; **proposer le loyer**
   d'apres l'ancien contrat du bien.

## Regles de securite des donnees
- Ne JAMAIS inventer une valeur. Champ illisible/absent => `null` + l'ajouter dans
  `meta.champs_incertains`. Signaler la confiance.
- Les pieces (identite, etc.) restent dans `dossiers/<slug>/` (git-ignore).

## Types de pieces attendues
piece d'identite · garantie Visale (PDF) · certificat de scolarite · attestation d'assurance
habitation · etat des lieux · (RIB, justificatif de revenus, autre).

## Etapes

### 1. Recevoir le lot (gerer la colocation)
- Email `.eml` dans `inbox/` -> `python3 scripts/preparer_dossier.py inbox/<fichier>.eml --nom "Nom Prenom"`.
- **Colocation / 2e email pour le meme bien** : rattacher au dossier existant avec
  `--dossier <slug>` (ex: `--dossier t2-rivoli-coloc`). Nommer le dossier d'apres le bien
  (pas d'un seul locataire) quand plusieurs emails sont attendus.
- Ou pieces deposees directement -> les placer dans `dossiers/<slug>/pieces/`.

### 2. Classer et lire chaque piece (vision + lecture PDF)
Pour chaque fichier de `dossiers/<slug>/pieces/`, avec l'outil Read :
- **Identifier le type** de document.
- **Extraire les champs utiles** selon le type :
  - *Piece d'identite* : civilite, nom, prenoms, date de naissance, nationalite ; extraire la
    photo de portrait pour la photo de profil du locataire.
  - *Garantie Visale (PDF)* : **numero/code du visa**, beneficiaire, dates de validite.
  - *Certificat de scolarite* : etablissement, annee, nom de l'etudiant.
  - *Attestation d'assurance* : assureur, n° de contrat, dates, bien couvert.
  - *Etat des lieux (PDF)* : type (entree/sortie), **bien**, **noms des locataires**, date.
- Lire aussi `dossiers/<slug>/email.txt` (email, telephone, situation, bien concerne).

### 3. Ecrire donnees.json
- Ecrire `dossiers/<slug>/donnees.json` conforme a `schemas/dossier.schema.json` :
  `locataires[]`, `pieces[]` (avec `type`, `fichier_origine`, `locataire`), `visale`,
  `assurance_habitation`, `etat_des_lieux`, `meta`.
- Renseigner `location.ref` (le bien loue ; le deviner depuis l'objet de l'email ou demander).
- En colocation, **un objet locataire par personne** dans `locataires[]` ; ne pas ecraser
  un colocataire deja present si tu retraites le dossier.

### 3bis. Locataire existant + loyer propose
```
python3 scripts/rechercher_locataire.py --slug <slug>   # existant -> complete ; sinon "nouveau"
python3 scripts/proposer_loyer.py <REF> --slug <slug>    # loyer d'apres l'ancien contrat du bien
```
- `rechercher_locataire.py` annote chaque locataire (`statut_profil` existant/nouveau) et
  complete les champs connus depuis `registre/locataires.json`.
- `proposer_loyer.py` ecrit `contrat.loyer_hc_propose` / `charges_proposees` depuis le
  dernier contrat du bien (revalorisation configurable). Le bailleur validera/ajustera.

### 4. Ranger les pieces (nomenclature standard)
```
python3 scripts/organiser_pieces.py <slug>
```
Renomme les fichiers en `type[_locataire].ext` (prets a televerser dans la page "pieces"
de la location) et met a jour `donnees.json`.

### 5. Preparer les documents
```
python3 scripts/remplir_templates.py <slug> --bien <REF>
```
Genere `fiche_locataire.md` et `visale_activation.md` (code Visale + caracteristiques du
logement a saisir sur visale.fr pour activer la couverture).

### 6. Verifier la completude
```
python3 scripts/verifier_completude.py <slug>
```
Genere `recapitulatif.md` : inventaire des pieces, checklist (present/manquant), statut
Visale et etat des lieux, et le verdict **CONTRAT PRET A SIGNER** ou la liste des manquants.

### 7. Presenter "A VALIDER" (checkpoint humain)
Afficher `recapitulatif.md` a l'utilisateur, en mettant en avant :
- les pieces rangees et celles qui **manquent** ;
- le **code Visale** extrait et les caracteristiques a saisir pour l'activation ;
- pour l'etat des lieux : le **bien** et les **noms** extraits ;
- les **champs incertains**.

Puis demander explicitement : **« Je valide ? Un champ a corriger avant de finaliser ? »**
Ne PAS finaliser tant que l'utilisateur n'a pas valide.

### 8. Finaliser (apres validation seulement)
- Appliquer les corrections dans `donnees.json` (dont `contrat.loyer_hc_retenu`), re-lancer
  les scripts concernes.
- Enregistrer au registre : `python3 scripts/enregistrer.py <slug>`
  (upsert des locataires + historisation du contrat -> loyer propose la prochaine fois ;
  passe `meta.statut = "valide"`).
- Rappeler les actions a faire cote plateforme et visale.fr :
  1. **Creer / completer le profil de chaque locataire** (identite + contact + photo de profil).
  2. Televerser les pieces de `pieces/` dans la page "pieces" de la location.
  3. Sur visale.fr : saisir le code visa + caracteristiques (`visale_activation.md`), **valider**.
  4. Enregistrer l'etat des lieux dans les pieces.
  5. Quand tout est complet -> **contrat pret a signer**.

## Rappels
- Visale : la couverture s'active cote bailleur en saisissant le code du locataire ; voir `docs/visale.md`.
- Etat des lieux : voir `docs/etat_des_lieux.md`.
