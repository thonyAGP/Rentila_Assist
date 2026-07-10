#!/usr/bin/env python3
"""Client de l'API Rentila (OAuth2 client_credentials) — bibliotheque standard uniquement.

Le secret n'est JAMAIS code en dur : il est lu depuis les variables d'environnement
RENTILA_CLIENT_ID et RENTILA_CLIENT_SECRET.

⚠️ A VERIFIER contre la documentation Rentila avant de s'y fier (config/rentila_api.json) :
   - le chemin du token (`token_path`, par defaut /oauth/token) ;
   - le NOM DU CHAMP du token dans la reponse (`token_field`, par defaut access_token) ;
   - les chemins des endpoints (biens, locataires, locations).
La sous-commande `token` affiche les champs reellement renvoyes pour lever le doute.

Usage :
    export RENTILA_CLIENT_ID=...   RENTILA_CLIENT_SECRET=...
    python3 scripts/rentila_api.py token            # recupere un jeton et montre la reponse
    python3 scripts/rentila_api.py get /properties  # GET authentifie sur un chemin arbitraire
    python3 scripts/rentila_api.py biens            # GET sur l'endpoint 'biens' de la config
"""
import argparse
import base64
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

RACINE = Path(__file__).resolve().parent.parent
CONFIG = RACINE / "config" / "rentila_api.json"
DEFAUT = {
    "base_url": "https://api2.rentila.com",
    "token_path": "/oauth/token",
    "token_field": "access_token",   # A VERIFIER dans la doc
    "auth_mode": "body",             # 'body' (client_id/secret dans le corps) ou 'basic' (en-tete)
    "endpoints": {"biens": "/properties", "locataires": "/tenants", "locations": "/rentals"},
}


def charger_config() -> dict:
    conf = dict(DEFAUT)
    if CONFIG.exists():
        conf.update({k: v for k, v in json.loads(CONFIG.read_text(encoding="utf-8")).items()
                     if not k.startswith("_")})
    return conf


def _post_form(url: str, data: dict, headers: dict) -> tuple[int, dict | str]:
    corps = urllib.parse.urlencode(data).encode()
    req = urllib.request.Request(url, data=corps, headers=headers, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            brut = r.read().decode()
            return r.status, _json_ou_texte(brut)
    except urllib.error.HTTPError as e:
        return e.code, _json_ou_texte(e.read().decode(errors="replace"))


def _get(url: str, token: str) -> tuple[int, dict | str]:
    req = urllib.request.Request(url, headers={"Authorization": f"Bearer {token}",
                                               "Accept": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return r.status, _json_ou_texte(r.read().decode())
    except urllib.error.HTTPError as e:
        return e.code, _json_ou_texte(e.read().decode(errors="replace"))


def _json_ou_texte(s: str):
    try:
        return json.loads(s)
    except json.JSONDecodeError:
        return s[:2000]


def obtenir_token(conf: dict, verbeux: bool = False) -> str | None:
    cid = os.environ.get("RENTILA_CLIENT_ID")
    secret = os.environ.get("RENTILA_CLIENT_SECRET")
    if not cid or not secret:
        print("Erreur : definissez RENTILA_CLIENT_ID et RENTILA_CLIENT_SECRET dans l'environnement.",
              file=sys.stderr)
        return None
    url = conf["base_url"].rstrip("/") + conf["token_path"]
    data = {"grant_type": "client_credentials"}
    headers = {"Content-Type": "application/x-www-form-urlencoded", "Accept": "application/json"}
    if conf.get("auth_mode") == "basic":
        jeton = base64.b64encode(f"{cid}:{secret}".encode()).decode()
        headers["Authorization"] = f"Basic {jeton}"
    else:
        data["client_id"] = cid
        data["client_secret"] = secret

    statut, rep = _post_form(url, data, headers)
    if statut != 200 or not isinstance(rep, dict):
        print(f"Echec token (HTTP {statut}) : {rep}", file=sys.stderr)
        return None

    champ = conf["token_field"]
    if verbeux:
        # ne jamais afficher la valeur du token en entier
        apercu = {k: (str(v)[:12] + "…" if "token" in k.lower() else v) for k, v in rep.items()}
        print(f"Reponse token — champs disponibles : {list(rep.keys())}")
        print(f"Apercu (tokens tronques) : {json.dumps(apercu, ensure_ascii=False)}")
        if champ not in rep:
            print(f"⚠️ Le champ configure '{champ}' est ABSENT. Ajustez 'token_field' dans "
                  f"config/rentila_api.json selon la doc (candidats : "
                  f"{[k for k in rep if 'token' in k.lower()]}).", file=sys.stderr)
    return rep.get(champ)


def main() -> int:
    p = argparse.ArgumentParser(description="Client API Rentila (OAuth2 client_credentials).")
    sub = p.add_subparsers(dest="cmd", required=True)
    sub.add_parser("token", help="Recupere un jeton et affiche les champs de la reponse")
    g = sub.add_parser("get", help="GET authentifie sur un chemin")
    g.add_argument("chemin", help="Ex: /properties")
    b = sub.add_parser("biens", help="GET sur l'endpoint 'biens' de la config")
    for nom in ("locataires", "locations"):
        sub.add_parser(nom, help=f"GET sur l'endpoint '{nom}' de la config")
    args = p.parse_args()
    conf = charger_config()

    if args.cmd == "token":
        tok = obtenir_token(conf, verbeux=True)
        if tok:
            print("Jeton obtenu ✔ (valeur masquee). Vous pouvez utiliser `get`.")
            return 0
        return 1

    # commandes GET
    tok = obtenir_token(conf)
    if not tok:
        return 1
    if args.cmd == "get":
        chemin = args.chemin
    else:
        chemin = conf["endpoints"].get(args.cmd)
        if not chemin:
            print(f"Endpoint '{args.cmd}' non defini dans config/rentila_api.json.", file=sys.stderr)
            return 1
    url = conf["base_url"].rstrip("/") + (chemin if chemin.startswith("/") else "/" + chemin)
    statut, rep = _get(url, tok)
    print(f"HTTP {statut} — {url}")
    print(json.dumps(rep, ensure_ascii=False, indent=2) if isinstance(rep, (dict, list)) else rep)
    return 0 if statut == 200 else 2


if __name__ == "__main__":
    raise SystemExit(main())
