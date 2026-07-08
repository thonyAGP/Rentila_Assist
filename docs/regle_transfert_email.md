# Mettre en place la règle de transfert d'email

Le workflow démarre quand un email de nouveau locataire (avec la photo de la pièce
d'identité en pièce jointe) arrive dans `inbox/`. Voici comment y amener les emails.

## Option A — Manuel (fonctionne tout de suite)

1. Dans votre messagerie, ouvrez l'email du locataire.
2. « Télécharger le message » au format **.eml** (Gmail : menu ⋮ → *Télécharger le message*).
3. Déposez le `.eml` dans le dossier `inbox/` du projet.
4. Demandez à Claude de traiter le dossier (skill **nouveau-locataire**).

## Option B — Règle de transfert Gmail (semi-automatique)

Créez une **règle** pour isoler les emails de locataires, puis un déclencheur qui les récupère.

### 1. Filtre Gmail
1. Gmail → ⚙️ → *Voir tous les paramètres* → **Filtres et adresses bloquées** → *Créer un filtre*.
2. Critère au choix, par ex. : objet contenant `[LOCATION]`, ou expéditeur = votre agence,
   ou emails avec pièce jointe adressés à une adresse dédiée.
3. Action : appliquer le libellé **`Locataires/Entrée`** (et éventuellement *Transférer à*
   une adresse dédiée).

### 2. Convention d'objet (recommandée)
Demandez au locataire (ou mettez vous-même) une référence de bien dans l'objet, ex :
`[LOCATION][T2-RIVOLI] Dossier Marie Dupont`.
Le skill s'en sert pour associer le bon logement (`config/logement.yaml`).

### 3. Récupération automatique (optionnelle)
Deux façons d'amener les emails libellés dans `inbox/` :
- **Poller Gmail API** : script à exécuter via une *Routine* (voir `automatisation.md`).
  Nécessite des identifiants OAuth Google (non fournis par défaut).
- **Transfert vers un service mail-to-webhook** qui écrit le `.eml` dans le dépôt.

> Tant que l'intégration automatique n'est pas branchée, l'option A (dépôt manuel du `.eml`)
> couvre 100 % du besoin : l'automatisation utile (lecture pièce d'identité + remplissage +
> validation) est faite par Claude, pas par le transport de l'email.

## Ce qui doit se trouver dans l'email
- La **photo de la pièce d'identité** (recto, et verso si CNI) en pièce jointe.
- Idéalement : email de contact, téléphone, situation professionnelle, et le bien visé.
- Facultatif : photo de portrait dédiée (sinon la photo de la pièce sert de profil).
