#!/usr/bin/env python3
"""Range et renomme les pieces d'un dossier selon une nomenclature standard.

Lit donnees.json -> pieces[] (chaque piece a `type`, `fichier_origine`, `locataire`).
Renomme le fichier correspondant dans dossiers/<slug>/pieces/ en :
    <type>[_<slug-locataire>].<ext>
et met a jour le champ `fichier` dans donnees.json.

Objectif : des noms clairs, prets a etre televerses dans la page "pieces" de la location.

Usage:
    python3 scripts/organiser_pieces.py dupont-marie
"""
import argparse
import json
import re
import sys
import unicodedata
from pathlib import Path

RACINE = Path(__file__).resolve().parent.parent


def slug(texte: str) -> str:
    texte = unicodedata.normalize("NFKD", texte or "").encode("ascii", "ignore").decode()
    texte = re.sub(r"[^\w\s-]", "", texte).strip().lower()
    return re.sub(r"[\s_-]+", "-", texte)


def main() -> int:
    p = argparse.ArgumentParser(description="Range et renomme les pieces du dossier.")
    p.add_argument("slug")
    args = p.parse_args()

    dossier = RACINE / "dossiers" / args.slug
    pieces_dir = dossier / "pieces"
    donnees_path = dossier / "donnees.json"
    if not donnees_path.exists():
        print(f"Erreur : {donnees_path} introuvable.", file=sys.stderr)
        return 1

    donnees = json.loads(donnees_path.read_text(encoding="utf-8"))
    pieces = donnees.get("pieces", []) or []
    utilises: set[str] = set()

    for pc in pieces:
        origine = pc.get("fichier_origine") or pc.get("fichier")
        if not origine:
            continue
        src = pieces_dir / Path(origine).name
        if not src.exists():
            print(f"  ignore (introuvable) : {origine}", file=sys.stderr)
            continue
        ext = src.suffix.lower()
        base = pc.get("type") or "autre"
        if pc.get("locataire"):
            base += "_" + slug(pc["locataire"])
        cible_nom = base + ext
        # evite les collisions (ex: 2 CNI sans locataire distinct)
        n = 2
        while cible_nom in utilises or ((pieces_dir / cible_nom).exists() and (pieces_dir / cible_nom) != src):
            cible_nom = f"{base}_{n}{ext}"
            n += 1
        utilises.add(cible_nom)
        cible = pieces_dir / cible_nom
        if cible != src:
            src.rename(cible)
        pc["fichier"] = cible_nom
        print(f"  {origine}  ->  {cible_nom}")

    donnees_path.write_text(json.dumps(donnees, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"donnees.json mis a jour ({len(pieces)} piece(s)).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
