#!/usr/bin/env python3
"""Cherche si un locataire existe deja dans registre/locataires.json.

Sert a decider : COMPLETER un locataire existant, ou CREER un nouveau.
Correspondance par email, sinon par (nom + prenom + date de naissance).

Deux usages :
  - Requete unique :
        python3 scripts/rechercher_locataire.py --email marie@x.fr
        python3 scripts/rechercher_locataire.py --nom Dupont --prenom Marie --naissance 1998-04-12
  - Sur un dossier : annote chaque locataire de donnees.json avec statut_profil
    ("existant"/"nouveau") et complete les champs connus manquants :
        python3 scripts/rechercher_locataire.py --slug t2-rivoli-coloc
"""
import argparse
import json
import re
import sys
import unicodedata
from pathlib import Path

RACINE = Path(__file__).resolve().parent.parent
CHAMPS_COMPLETABLES = ["civilite", "nom", "prenoms", "date_naissance", "email", "telephone",
                       "adresse_actuelle", "nationalite", "lieu_naissance"]


def norm(s: str) -> str:
    s = unicodedata.normalize("NFKD", s or "").encode("ascii", "ignore").decode()
    return re.sub(r"\s+", " ", s).strip().lower()


def charger_registre() -> list:
    chemin = RACINE / "registre" / "locataires.json"
    if not chemin.exists():
        return []
    return json.loads(chemin.read_text(encoding="utf-8"))


def trouver(registre: list, *, email=None, nom=None, prenom=None, naissance=None) -> dict | None:
    if email:
        for r in registre:
            if r.get("email") and norm(r["email"]) == norm(email):
                return r
    if nom and naissance:
        for r in registre:
            meme_nom = norm(r.get("nom", "")) == norm(nom)
            meme_naiss = (r.get("date_naissance") or "") == naissance
            meme_prenom = (not prenom) or norm(prenom) in norm(r.get("prenoms", "")) \
                or norm(r.get("prenoms", "")) in norm(prenom)
            if meme_nom and meme_naiss and meme_prenom:
                return r
    return None


def main() -> int:
    p = argparse.ArgumentParser(description="Cherche un locataire existant.")
    p.add_argument("--email")
    p.add_argument("--nom")
    p.add_argument("--prenom")
    p.add_argument("--naissance")
    p.add_argument("--slug", help="Annoter donnees.json d'un dossier")
    args = p.parse_args()

    registre = charger_registre()

    if args.slug:
        dpath = RACINE / "dossiers" / args.slug / "donnees.json"
        if not dpath.exists():
            print(f"Erreur : {dpath} introuvable.", file=sys.stderr)
            return 1
        donnees = json.loads(dpath.read_text(encoding="utf-8"))
        for loc in donnees.get("locataires", []) or []:
            existant = trouver(registre, email=loc.get("email"), nom=loc.get("nom"),
                               prenom=loc.get("prenoms"), naissance=loc.get("date_naissance"))
            if existant:
                loc["statut_profil"] = "existant"
                loc.setdefault("id", existant.get("id"))
                if not loc.get("id"):
                    loc["id"] = existant.get("id")
                completes = []
                for champ in CHAMPS_COMPLETABLES:
                    if not loc.get(champ) and existant.get(champ):
                        loc[champ] = existant[champ]
                        completes.append(champ)
                nom_aff = f"{loc.get('prenoms')} {loc.get('nom')}"
                print(f"EXISTANT : {nom_aff} (id={existant.get('id')})"
                      + (f" — complete: {', '.join(completes)}" if completes else ""))
            else:
                loc["statut_profil"] = "nouveau"
                print(f"NOUVEAU  : {loc.get('prenoms')} {loc.get('nom')} — a creer")
        dpath.write_text(json.dumps(donnees, ensure_ascii=False, indent=2), encoding="utf-8")
        return 0

    # requete unique
    r = trouver(registre, email=args.email, nom=args.nom, prenom=args.prenom, naissance=args.naissance)
    if r:
        print("EXISTANT :")
        print(json.dumps(r, ensure_ascii=False, indent=2))
    else:
        print("NOUVEAU : aucun locataire correspondant dans le registre.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
