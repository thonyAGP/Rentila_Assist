# Fiche locataire — {{identite.civilite}} {{identite.prenoms}} {{identite.nom_naissance}}

> Fiche générée automatiquement à partir de la pièce d'identité et de l'email transféré.
> Statut : **BROUILLON — À VALIDER**. Les champs marqués `⚠️` sont incertains, à vérifier.

## Photo de profil
![Photo de profil]({{photo_profil}})

## Identité
| Champ | Valeur |
|---|---|
| Civilité | {{identite.civilite}} |
| Nom de naissance | {{identite.nom_naissance}} |
| Nom d'usage | {{identite.nom_usage}} |
| Prénom(s) | {{identite.prenoms}} |
| Sexe | {{identite.sexe}} |
| Date de naissance | {{identite.date_naissance}} |
| Lieu de naissance | {{identite.lieu_naissance}} |
| Nationalité | {{identite.nationalite}} |

## Pièce d'identité
| Champ | Valeur |
|---|---|
| Type | {{piece_identite.type}} |
| Numéro | {{piece_identite.numero}} |
| Délivrée le | {{piece_identite.date_delivrance}} |
| Expire le | {{piece_identite.date_expiration}} |
| Autorité | {{piece_identite.autorite_delivrance}} |

## Contact
| Champ | Valeur |
|---|---|
| Email | {{contact.email}} |
| Téléphone | {{contact.telephone}} |
| Adresse actuelle | {{contact.adresse_actuelle}} |

## Situation professionnelle
| Champ | Valeur |
|---|---|
| Statut | {{situation.statut}} |
| Employeur | {{situation.employeur}} |
| Type de contrat | {{situation.type_contrat}} |
| Revenu mensuel net | {{situation.revenu_mensuel_net}} € |

## Garant
| Champ | Valeur |
|---|---|
| Nom complet | {{garant.nom_complet}} |
| Lien | {{garant.lien}} |
| Email | {{garant.email}} |

## Logement concerné
| Champ | Valeur |
|---|---|
| Adresse | {{logement.adresse}} |
| Type | {{logement.type}} |
| Surface | {{logement.surface}} m² |
| Meublé | {{logement.meuble}} |
| Loyer hors charges | {{logement.loyer_hc}} € |
| Charges | {{logement.charges}} € |
| Dépôt de garantie | {{logement.depot_garantie}} € |
| Disponible le | {{logement.date_disponibilite}} |

---
*Source : {{meta.source_email}} — Confiance globale : {{meta.confiance_globale}}*
