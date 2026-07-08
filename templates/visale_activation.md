# Activation Visale — {{location.ref}}

> Aide à la saisie sur [visale.fr](https://www.visale.fr) (espace bailleur) pour **activer la
> couverture**. Le locataire a déjà obtenu son visa : ces infos sont à recopier sur le site,
> puis **valider pour activer**.
> ⚠️ Vérifiez la validité du visa avant de saisir le bail.

## 1. Code Visale (fourni par le locataire)
| Champ | Valeur |
|---|---|
| **Numéro de visa** | **{{visale.code_visa}}** |
| Bénéficiaire | {{visale.beneficiaire}} |
| Valide du | {{visale.validite_debut}} |
| Valide au | {{visale.validite_fin}} |

## 2. Caractéristiques du logement à saisir
| Champ visale.fr | Valeur |
|---|---|
| Adresse du logement | {{location.adresse}} |
| Type de logement | {{location.type}} |
| Surface habitable | {{location.surface}} m² |
| Location meublée | {{location.meuble}} |
| Loyer hors charges | {{location.loyer_hc}} € |
| Provision pour charges | {{location.charges}} € |
| Loyer charges comprises | {{location.loyer_cc}} € |
| Dépôt de garantie | {{location.depot_garantie}} € |
| Date de prise d'effet du bail | {{location.date_disponibilite}} |

## 3. Locataire(s) couvert(s)
{{bloc.locataires}}

## 4. Étapes sur visale.fr
1. Espace bailleur → *Enregistrer un contrat de location*.
2. Saisir le **numéro de visa** ci-dessus.
3. Renseigner les **caractéristiques du logement** (tableau §2) et le(s) locataire(s).
4. Vérifier la cohérence loyer / plafond du visa.
5. **Valider** → la couverture est activée. Conserver l'accusé / contrat de cautionnement dans les pièces.

---
*Statut d'activation : {{visale.statut_activation}}. Source : {{meta.source_email}}.*
