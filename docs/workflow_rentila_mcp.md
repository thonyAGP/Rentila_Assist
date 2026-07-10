# Workflow via le MCP Rentila — correspondance des étapes

Depuis la connexion du connecteur **Rentila**, Claude agit directement dans Rentila. Le MCP
devient la source de vérité (registre, historique des loyers) et la cible de finalisation.
**Toute écriture reste soumise à votre validation** (« À VALIDER » d'abord).

## Correspondance étape → outil MCP

| Étape du dossier | Outil MCP (lecture) | Outil MCP (écriture, après validation) |
|---|---|---|
| Choisir le bien | `query_properties` (11 biens), `get_record(properties, id)` | — |
| Locataire existant ? | `query_tenants` (search), `search` | — |
| Créer / compléter le locataire | — | `create_tenant` / `update_tenant` |
| Loyer d'après l'ancien contrat | `query_leases(property_id=…)` → dernier loyer | — |
| Candidature | `query_candidates` | `create_candidate`, `accept_candidature` |
| Ranger les pièces | `query_documents` | `create_document` (+ `commit_temp_documents`) |
| Bail | `query_leases` | `create_lease`, puis `activate_lease` |
| État des lieux | `query_handovers` | `create_handover` |
| Signature | `query_signatures` | `start_signing_procedure`, `create_signature` |
| Compteurs (eau…) | `query_meters`, `previous_meter_reading` | `create_meter`, `update_meter` |
| Solde / impayés | `get_tenant_balances`, `get_lease_balance` | — |

> Astuce : `get_form_data(module=…)` donne les listes de référence (types de bien, statuts,
> types de bail…) pour remplir les bons identifiants avant une écriture.

## Ce que le MCP NE couvre pas
- **Visale** : l'activation se fait sur visale.fr (le MCP Rentila ne l'expose pas). On garde
  `visale_activation.md` + éventuelle capture HAR côté Visale.
- **Amortissement LMNP** : calcul côté `scripts/amortissement.py` ; report dans Rentila selon
  ce que le module comptable expose (à vérifier via les outils documents/settings).

## Règles
1. **Lecture d'abord** : toujours interroger (query_*) et présenter un « À VALIDER » avant tout
   `create_*`/`update_*`.
2. **Ne jamais inventer** : un champ absent des pièces reste vide et signalé.
3. **Idempotence** : vérifier l'existence (`query_tenants`, `query_leases`) avant de créer,
   pour compléter au lieu de dupliquer.
4. **Écritures groupées** (`mass_*`, `delete_record`) : à confirmer explicitement, une par une.

## Les scripts locaux restent utiles hors-ligne
`rechercher_locataire.py`, `proposer_loyer.py`, `enregistrer.py` et le registre local servent
de **repli hors connexion** ou de cache. Quand le MCP est connecté, il fait autorité.
