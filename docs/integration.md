# Intégration Rentila & Visale — état des lieux et stratégie

Résumé de ce que proposent les deux plateformes et de la voie retenue pour automatiser la
saisie depuis un dossier traité par Rentila Assist. *(Constaté en juillet 2026 — à
reconfirmer sur vos comptes, les offres évoluent.)*

## Rentila

| Voie | Disponible ? | Détail |
|---|---|---|
| API REST publique documentée | ❌ non trouvée | Aucune doc développeur publique pour créer locataires/locations. |
| Synchro Airbnb / iCal | ✅ | Pour les locations saisonnières (réservations/disponibilités), hors périmètre. |
| **Import CSV / Excel** | ✅ **confirmé** | Locataires, biens et locations importables via des **modèles téléchargeables** depuis votre compte. |
| Mention **« API & MCP »** | ⚠️ à vérifier | Citée dans les offres (page tarifs) mais **sans documentation publique**. Si un **serveur MCP** existe, Claude peut s'y connecter directement. |

### Voie recommandée : import CSV
La plus simple et sans risque. Le workflow génère un fichier d'import à partir de
`donnees.json`, que vous chargez dans Rentila.
- **À me fournir** : téléchargez le **modèle d'import locataires** (CSV) depuis Rentila
  (*Mon compte* → import) et donnez-moi son **en-tête de colonnes**. Je mappe les champs
  du dossier dessus (voir `config/rentila_import.example.yaml` et
  `scripts/exporter_rentila_csv.py`).

### Piste à explorer : API & MCP
Si votre offre expose une **API** ou un **serveur MCP** :
- **MCP** = idéal : Claude s'y connecte nativement (comme aux autres serveurs MCP), et crée
  locataire/location/pièces directement, sans CSV ni capture. Récupérez l'URL du serveur MCP
  et la méthode d'authentification depuis votre compte Rentila.
- **API REST** : récupérez la doc / le jeton d'API depuis votre compte ; je code le client.

### Repli : analyse de vos saisies
Si ni CSV ni API/MCP ne conviennent → **capture HAR** d'une création manuelle, puis
`scripts/analyser_har.py` (voir `docs/capturer_appels.md`).

## Visale (Action Logement)

| Voie | Disponible ? | Détail |
|---|---|---|
| API publique | ❌ | Aucune API bailleur. Tout passe par l'espace bailleur web. |
| Import fichier | ❌ | Non proposé. |
| **Analyse des saisies (HAR)** | ✅ seule voie | Capturer l'enregistrement d'un contrat (visa + caractéristiques) et rejouer les appels. |

### Voie retenue : capture HAR
1. `visale_activation.md` vous donne déjà **toutes les valeurs à saisir**.
2. Faites **une fois** la saisie à la main en capturant le réseau (voir `docs/capturer_appels.md`).
3. `scripts/analyser_har.py capture.har --domaine visale.fr` extrait les appels.
4. Je construis un client qui rejoue *Enregistrer un contrat* avec les données du dossier.

> ⚠️ Visale est un service Action Logement : rejouer des appels se fait **avec votre compte**
> et sous votre responsabilité. Le point de **validation humaine** reste de toute façon en place.

## En pratique — ce dont j'ai besoin de vous
1. **Rentila** : l'**en-tête du modèle d'import CSV locataires** (le plus rapide), **ou** l'info
   API/MCP de votre compte si elle existe.
2. **Visale** : un **HAR** d'un enregistrement de contrat (une fois), pour reconstituer les appels.
