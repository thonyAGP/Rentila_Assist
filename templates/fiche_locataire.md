# Fiche locataire — {{location.ref}}

> Générée automatiquement à partir des pièces reçues. **BROUILLON — À VALIDER.**
> Champs marqués `⚠️ à compléter` = non lus / absents, à vérifier (jamais inventés).

## Locataire(s)
{{bloc.locataires_detail}}

## Logement
| Champ | Valeur |
|---|---|
| Référence | {{location.ref}} |
| Adresse | {{location.adresse}} |
| Type | {{location.type}} |
| Surface | {{location.surface}} m² |
| Meublé | {{location.meuble}} |
| Loyer hors charges | {{location.loyer_hc}} € |
| Charges | {{location.charges}} € |
| Loyer charges comprises | {{location.loyer_cc}} € |
| Dépôt de garantie | {{location.depot_garantie}} € |
| Date d'entrée | {{location.date_disponibilite}} |

## Garantie Visale
| Champ | Valeur |
|---|---|
| Code visa | {{visale.code_visa}} |
| Validité | {{visale.validite_debut}} → {{visale.validite_fin}} |
| Statut | {{visale.statut_activation}} |

## Assurance habitation
| Champ | Valeur |
|---|---|
| Assureur | {{assurance_habitation.assureur}} |
| N° contrat | {{assurance_habitation.numero_contrat}} |
| Validité | {{assurance_habitation.validite_debut}} → {{assurance_habitation.validite_fin}} |

## État des lieux
| Champ | Valeur |
|---|---|
| Type | {{etat_des_lieux.type}} |
| Bien | {{etat_des_lieux.bien}} |
| Date | {{etat_des_lieux.date}} |

---
*Source : {{meta.source_email}} — Confiance : {{meta.confiance_globale}}*
