# Connecter le projet à Rentila (MCP + API)

Rentila expose deux accès : un **serveur MCP** (recommandé pour le pilotage par Claude) et une
**API OAuth2** (pour les scripts / cron). Tout sous `https://api2.rentila.com`.

## A. MCP — pour l'usage agent (recommandé)

L'ajout du connecteur et la connexion **se font dans votre client Claude** (l'authentification
OAuth s'ouvre dans votre navigateur). Claude ne peut pas s'authentifier à votre place.

### Sur claude.ai / l'app (connecteur personnalisé)
1. **Paramètres → Connecteurs → Ajouter un connecteur personnalisé**.
2. Nom : `Rentila` · URL du serveur : `https://api2.rentila.com/mcp`.
3. **Lancer la connexion** → un onglet Rentila s'ouvre : choisissez votre pays/site Rentila et
   connectez-vous avec **votre email + mot de passe Rentila** (et code 2FA si demandé).
   *Ne collez jamais vos identifiants dans le chat — vous vous authentifiez dans le navigateur.*
4. Revenez dans Claude, activez le connecteur **pour cette conversation**.

### Sur Claude Code (CLI)
Le dépôt fournit `.mcp.json` (serveur `Rentila` déjà déclaré). Lancez l'authentification :
```
claude mcp list         # doit montrer Rentila
/mcp                     # dans Claude Code : authentifier Rentila (OAuth navigateur)
```

### Vérifier
Une fois connecté, les outils `mcp__Rentila__*` apparaissent. Demandez :
> « Quels biens je possède ? »
C'est une lecture seule — parfait pour valider la connexion sans rien modifier.

## B. API directe — pour scripts / cron

1. Générez `client_id` + `client_secret` depuis **votre profil Rentila** (le secret n'est
   affiché **qu'une seule fois**).
2. Renseignez-les en variables d'environnement (jamais dans le code) :
   ```
   cp .env.example .env      # puis remplissez RENTILA_CLIENT_ID / RENTILA_CLIENT_SECRET
   set -a; . ./.env; set +a
   ```
3. Confirmez le **jeton** et les champs renvoyés (étape de vérification) :
   ```
   cp config/rentila_api.example.json config/rentila_api.json
   python3 scripts/rentila_api.py token
   ```
   La commande affiche les **champs de la réponse** (sans dévoiler le token). Si le champ
   attendu (`access_token`) n'est pas là, elle vous dit lequel utiliser → ajustez
   `token_field` dans `config/rentila_api.json`.
4. Interrogez un endpoint (lecture seule d'abord) :
   ```
   python3 scripts/rentila_api.py get /landlord/properties   # chemin arbitraire
   python3 scripts/rentila_api.py biens                       # endpoint 'biens' de la config
   ```

### Chemins vérifiés (doc officielle, testés le 2026-07-10)
- Jeton : `POST /oauth/token` (client_credentials, `auth_mode: body`) → réponse
  `{access_token, token_type: Bearer, expires_in: 3600}` — `token_field` = `access_token`.
- **Tous les endpoints métier sont préfixés `/landlord/`** : `/landlord/properties`,
  `/landlord/tenants`, `/landlord/leases`, `/landlord/payments`, `/landlord/documents`,
  `/landlord/candidates`, `/landlord/profile`, `/landlord/alerts`,
  `/landlord/tenants/balances`…
- La doc interactive complète (`/docs`, `/openapi.json`) n'est consultable que depuis une
  session Rentila connectée dans le navigateur — pas avec le jeton machine.

## Sécurité
- Le **secret** vit uniquement dans `.env` (git-ignoré) et l'environnement — jamais en dur.
- Commencez par des appels **en lecture** ; les écritures viendront après validation, en
  gardant le principe du projet : Claude propose, vous validez.
- MCP vs API : le **MCP** est idéal pour l'usage conversationnel (Claude appelle les outils
  Rentila directement) ; l'**API** sert aux automatisations non interactives (cron, scripts).
