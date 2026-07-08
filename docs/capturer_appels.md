# Capturer vos saisies (analyse des appels réseau)

Quand une plateforme n'a pas d'API utilisable (Visale, et Rentila selon votre compte), on
**capture les requêtes réseau** pendant que vous faites la saisie **une fois à la main**.
Le fichier obtenu (HAR) contient les appels exacts à rejouer pour automatiser.

## Enregistrer un HAR (Chrome / Edge / Firefox)

1. Ouvrez le site (Rentila ou visale.fr) et **connectez-vous**.
2. Ouvrez les outils développeur : **F12** (ou clic droit → *Inspecter*).
3. Onglet **Réseau** (Network).
4. Cochez **Conserver le journal** (*Preserve log*) et, si dispo, filtrez sur **Fetch/XHR**.
5. Cliquez sur 🗑️ pour vider, puis **faites la saisie complète** que vous voulez automatiser :
   - Rentila : créer un locataire + une location + téléverser une pièce.
   - Visale : enregistrer un contrat (visa + caractéristiques du logement) jusqu'à *Valider*.
6. Clic droit dans la liste des requêtes → **Enregistrer tout dans un fichier HAR**
   (*Save all as HAR with content*).
7. Déposez le fichier dans le projet (ex: `captures/rentila_locataire.har`).

## Extraire les appels

```
python3 scripts/analyser_har.py captures/rentila_locataire.har --sortie captures/appels_rentila.md
python3 scripts/analyser_har.py captures/visale_contrat.har --domaine visale.fr --sortie captures/appels_visale.md
```
Le script isole les **mutations** (POST/PUT/PATCH/DELETE) — celles qui portent vos saisies —
avec URL, en-têtes utiles, et **corps de la requête** (les champs envoyés). À partir de là je
peux écrire un petit client qui rejoue ces appels avec les données d'un dossier.

## ⚠️ Sécurité — important
- Un HAR contient **vos cookies de session et des données personnelles**. Le script **masque**
  les cookies/tokens dans le rapport Markdown, mais **le HAR brut, lui, contient tout**.
- Ne committez **jamais** un HAR ni le rapport dans git (le dossier `captures/` est git-ignoré).
- Considérez votre session comme un mot de passe : après capture, vous pouvez vous déconnecter
  pour invalider le cookie.
- Rejouer des appels d'un site tiers relève de **votre compte et de vos identifiants** ;
  vérifiez que les CGU de la plateforme ne l'interdisent pas.

## Alternative sans capture : l'import CSV (Rentila)
Rentila permet d'**importer des locataires / biens / locations en CSV/Excel**. Si cette voie
vous convient, pas besoin de HAR : voir `docs/integration.md` → *Rentila / Import CSV*.
