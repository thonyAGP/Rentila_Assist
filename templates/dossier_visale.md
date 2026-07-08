# Dossier Visale — préparation — {{identite.prenoms}} {{identite.nom_naissance}}

> Aide à la préparation du dossier de **garantie Visale** (Action Logement).
> ⚠️ Visale est demandé par le **candidat locataire** sur [visale.fr](https://www.visale.fr) : il obtient un **visa certifié** (numéro de certificat). Le bailleur crée ensuite le **contrat de cautionnement** avec ce numéro.
> Ce document ne remplace pas la démarche officielle — il prépare les infos et vérifie l'éligibilité de principe.

## 1. Éligibilité de principe (à confirmer sur visale.fr)

| Critère | Situation du candidat | OK ? |
|---|---|---|
| Âge | Né le {{identite.date_naissance}} → 18–30 ans éligible quelle que soit la situation | ⬜ |
| Situation | {{situation.statut}} / {{situation.type_contrat}} | ⬜ |
| Plafond de loyer | Loyer charges comprises : {{logement.loyer_cc}} € (plafond usuel : 1500 € Île-de-France, 1300 € ailleurs) | ⬜ |
| Taux d'effort | Loyer CC {{logement.loyer_cc}} € vs revenu {{situation.revenu_mensuel_net}} € (règle usuelle ≤ 50 % des ressources) | ⬜ |

> Les +30 ans peuvent être éligibles sous conditions (embauche récente, mutation, contrat précaire…). **À vérifier au cas par cas.**

## 2. Informations candidat (pré-remplies)

| Champ | Valeur |
|---|---|
| Nom / Prénom | {{identite.nom_naissance}} {{identite.prenoms}} |
| Date de naissance | {{identite.date_naissance}} |
| Nationalité | {{identite.nationalite}} |
| Email | {{contact.email}} |
| Téléphone | {{contact.telephone}} |
| Statut | {{situation.statut}} |
| Employeur | {{situation.employeur}} |
| Type de contrat | {{situation.type_contrat}} |
| Revenu mensuel net | {{situation.revenu_mensuel_net}} € |

## 3. Pièces justificatives à réunir par le candidat

- ⬜ Pièce d'identité en cours de validité (fournie : {{piece_identite.type}} n° {{piece_identite.numero}})
- ⬜ Justificatif de situation :
  - Salarié : contrat de travail ou 3 derniers bulletins de salaire
  - Étudiant : carte étudiant ou certificat de scolarité
  - Alternant : contrat d'alternance
  - Autre : selon situation
- ⬜ Justificatif de ressources (avis d'imposition le plus récent, ou attestation)
- ⬜ RIB (pour certaines démarches)

## 4. Informations du logement (pour le contrat de cautionnement)

| Champ | Valeur |
|---|---|
| Adresse du logement | {{logement.adresse}} |
| Type / surface | {{logement.type}} — {{logement.surface}} m² |
| Meublé | {{logement.meuble}} |
| Loyer hors charges | {{logement.loyer_hc}} € |
| Charges | {{logement.charges}} € |
| Loyer charges comprises | {{logement.loyer_cc}} € |
| Date d'entrée souhaitée | {{logement.date_disponibilite}} |

## 5. Numéro de visa Visale

- Visa certifié obtenu par le candidat : **{{visale.numero_visa}}**
- Éligibilité pressentie : **{{visale.eligible_pressenti}}**

## Prochaines étapes
1. Candidat → crée son espace sur visale.fr, dépose les justificatifs, obtient le **visa certifié**.
2. Bailleur → saisit le n° de visa dans son espace Action Logement et génère le **contrat de cautionnement** avant la signature du bail.

---
*Vérifiez toujours les conditions à jour sur [visale.fr](https://www.visale.fr). Source dossier : {{meta.source_email}}.*
