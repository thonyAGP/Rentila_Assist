# Garantie Visale — activation par le bailleur

Visale est une **caution locative gratuite** d'Action Logement. Dans ce workflow, le
locataire a **déjà obtenu son visa** (il vous envoie le PDF avec son **code visa**) : votre
rôle est d'**activer la couverture** en enregistrant le contrat de location sur visale.fr.

> ⚠️ Règles susceptibles d'évoluer — confirmez sur [visale.fr](https://www.visale.fr).

## Ce que le projet extrait du PDF Visale
- Le **numéro / code de visa** (à saisir sur le site).
- Le **bénéficiaire** (locataire couvert).
- Les **dates de validité** du visa.

Ces champs vont dans `donnees.json` → `visale`, puis dans `visale_activation.md`.

## Activation sur visale.fr (espace bailleur)
1. *Enregistrer un contrat de location*.
2. Saisir le **numéro de visa**.
3. Renseigner les **caractéristiques du logement** (adresse, type, surface, meublé, loyer HC,
   charges, loyer CC, dépôt de garantie, date d'effet du bail) — toutes reprises dans
   `visale_activation.md`.
4. Vérifier la cohérence loyer / plafond du visa.
5. **Valider** → la couverture est activée.
6. Ranger l'accusé / contrat de cautionnement dans les pièces de la location.

## Points de vigilance
- Le **loyer charges comprises** doit rester dans le plafond du visa.
- Le **visa doit être valide** à la date d'effet du bail.
- Le **nom du bénéficiaire** doit correspondre au locataire signataire.
