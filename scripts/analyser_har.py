#!/usr/bin/env python3
"""Analyse un fichier HAR (capture reseau du navigateur) pour en extraire les appels API.

Quand aucune API publique n'est documentee (Visale ; Rentila selon le compte), on capture
vos saisies sur le site (DevTools -> Network -> Export HAR, voir docs/capturer_appels.md) et
ce script en extrait les requetes utiles : methode, URL, parametres, corps (form/JSON),
statut de reponse. But : reconstituer les appels a rejouer pour automatiser la saisie.

Filtre par domaine (rentila / visale par defaut) et ignore le bruit (images, css, js,
fonts, tracking).

Usage:
    python3 scripts/analyser_har.py capture.har
    python3 scripts/analyser_har.py capture.har --domaine visale.fr
    python3 scripts/analyser_har.py capture.har --sortie appels.md
"""
import argparse
import json
import sys
from pathlib import Path
from urllib.parse import urlparse

EXT_BRUIT = (".png", ".jpg", ".jpeg", ".gif", ".svg", ".webp", ".ico",
             ".css", ".js", ".woff", ".woff2", ".ttf", ".map")
DOMAINES_BRUIT = ("google", "gstatic", "doubleclick", "facebook", "hotjar",
                  "segment", "sentry", "cloudflare", "recaptcha", "analytics")
ENTETES_UTILES = ("content-type", "authorization", "x-csrf-token", "x-xsrf-token",
                  "x-requested-with", "cookie")


def est_pertinent(url: str, domaines: list[str]) -> bool:
    p = urlparse(url)
    host = p.netloc.lower()
    if domaines and not any(d in host for d in domaines):
        return False
    if any(b in host for b in DOMAINES_BRUIT):
        return False
    if any(p.path.lower().endswith(ext) for ext in EXT_BRUIT):
        return False
    return True


def tronquer(txt: str, n: int = 2000) -> str:
    return txt if len(txt) <= n else txt[:n] + f"\n... [tronque, {len(txt)} caracteres]"


def extraire(entry: dict) -> dict:
    req = entry.get("request", {})
    resp = entry.get("response", {})
    post = req.get("postData", {})
    corps = post.get("text")
    if not corps and post.get("params"):
        corps = "&".join(f"{p.get('name')}={p.get('value')}" for p in post["params"])
    entetes = {h["name"].lower(): h["value"] for h in req.get("headers", [])
               if h["name"].lower() in ENTETES_UTILES}
    # masque la valeur des cookies/tokens (sensibles) mais signale leur presence
    for cle in ("cookie", "authorization", "x-csrf-token", "x-xsrf-token"):
        if cle in entetes:
            entetes[cle] = "<present, masque>"
    return {
        "methode": req.get("method"),
        "url": req.get("url"),
        "type_contenu": post.get("mimeType"),
        "entetes": entetes,
        "corps": tronquer(corps) if corps else None,
        "statut": resp.get("status"),
        "reponse_type": resp.get("content", {}).get("mimeType"),
    }


def main() -> int:
    p = argparse.ArgumentParser(description="Extrait les appels API d'un fichier HAR.")
    p.add_argument("har", type=Path)
    p.add_argument("--domaine", action="append", default=None,
                   help="Filtrer par domaine (repetable). Defaut: rentila + visale.")
    p.add_argument("--sortie", type=Path, help="Ecrire un rapport Markdown")
    p.add_argument("--json", dest="json_out", type=Path, help="Ecrire le detail en JSON")
    args = p.parse_args()

    if not args.har.exists():
        print(f"Erreur : {args.har} introuvable.", file=sys.stderr)
        return 1

    domaines = [d.lower() for d in (args.domaine or ["rentila", "visale"])]
    har = json.loads(args.har.read_text(encoding="utf-8"))
    entries = har.get("log", {}).get("entries", [])

    appels = [extraire(e) for e in entries
              if est_pertinent(e.get("request", {}).get("url", ""), domaines)
              and e.get("request", {}).get("method") in ("POST", "PUT", "PATCH", "DELETE", "GET")]
    # priorite aux mutations (POST/PUT/PATCH/DELETE) qui portent la saisie
    mutations = [a for a in appels if a["methode"] != "GET"]

    print(f"Domaines : {', '.join(domaines)}")
    print(f"Requetes pertinentes : {len(appels)} (dont {len(mutations)} mutations POST/PUT/PATCH/DELETE)")
    print()
    for a in mutations:
        print(f"  {a['methode']:6} {a['statut']}  {a['url']}")

    if args.json_out:
        args.json_out.write_text(json.dumps(appels, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"\nDetail JSON : {args.json_out}")

    if args.sortie:
        lignes = [f"# Appels capturés — {args.har.name}", "",
                  f"Domaines : {', '.join(domaines)} · {len(appels)} requêtes ({len(mutations)} mutations)",
                  "", "> ⚠️ Les cookies/tokens sont masqués. Ne partagez pas ce rapport tel quel s'il contient des données personnelles.", ""]
        for a in (mutations or appels):
            lignes += [
                f"## {a['methode']} {urlparse(a['url']).path}",
                f"- **URL** : `{a['url']}`",
                f"- **Statut** : {a['statut']} · réponse {a['reponse_type']}",
                f"- **Content-Type** : {a['type_contenu']}",
                f"- **En-têtes** : {a['entetes']}",
                "- **Corps** :", "```", a['corps'] or "(vide)", "```", "",
            ]
        args.sortie.write_text("\n".join(lignes), encoding="utf-8")
        print(f"Rapport Markdown : {args.sortie}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
