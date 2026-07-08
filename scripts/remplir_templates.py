#!/usr/bin/env python3
"""Remplit les templates (fiche locataire, dossier Visale) a partir des donnees.

Lit :
  - dossiers/<slug>/donnees.json   (rempli par Claude apres lecture de la piece d'identite)
  - config/logement.yaml           (optionnel : infos du bien loue)
Ecrit :
  - dossiers/<slug>/fiche_locataire.md
  - dossiers/<slug>/dossier_visale.md

Remplace les placeholders {{chemin.vers.champ}} par les valeurs.
Les valeurs manquantes deviennent "⚠️ à compléter" pour rester visibles a la validation.

Pas de dependance obligatoire ; PyYAML est utilise si present, sinon un mini-parseur
gere le format simple du fichier logement.example.yaml.

Usage:
    python3 scripts/remplir_templates.py dupont-marie
    python3 scripts/remplir_templates.py dupont-marie --bien T2-RIVOLI
"""
import argparse
import json
import re
import sys
from pathlib import Path

RACINE = Path(__file__).resolve().parent.parent
MANQUANT = "⚠️ à compléter"


def charger_yaml(chemin: Path) -> dict:
    if not chemin.exists():
        return {}
    try:
        import yaml  # type: ignore
        return yaml.safe_load(chemin.read_text(encoding="utf-8")) or {}
    except ImportError:
        return _mini_yaml(chemin.read_text(encoding="utf-8"))


def _mini_yaml(texte: str) -> dict:
    """Parseur minimal pour la structure de logement.example.yaml (listes/dicos simples)."""
    racine: dict = {}
    pile = [(-1, racine)]
    dernier_item: dict | None = None
    for ligne_brute in texte.splitlines():
        if not ligne_brute.strip() or ligne_brute.strip().startswith("#"):
            continue
        ligne = ligne_brute.split(" #")[0].rstrip()
        indent = len(ligne) - len(ligne.lstrip())
        contenu = ligne.strip()
        while pile and indent <= pile[-1][0] and len(pile) > 1:
            pile.pop()
        parent = pile[-1][1]
        if contenu.startswith("- "):
            item: dict = {}
            if isinstance(parent, list):
                parent.append(item)
            corps = contenu[2:]
            if ":" in corps:
                cle, val = corps.split(":", 1)
                item[cle.strip()] = _val(val.strip())
            dernier_item = item
            pile.append((indent, item))
        elif contenu.endswith(":"):
            cle = contenu[:-1].strip()
            # regarde si la suite est une liste
            enfant: list = []
            parent[cle] = enfant
            pile.append((indent, enfant))
        else:
            cle, val = contenu.split(":", 1)
            cible = pile[-1][1]
            if isinstance(cible, list):
                cible = dernier_item if dernier_item is not None else {}
            cible[cle.strip()] = _val(val.strip())
    return racine


def _val(v: str):
    v = v.strip().strip('"').strip("'")
    if v in ("true", "True"):
        return True
    if v in ("false", "False"):
        return False
    if re.fullmatch(r"-?\d+", v):
        return int(v)
    if re.fullmatch(r"-?\d+\.\d+", v):
        return float(v)
    return v


def resoudre(chemin: str, donnees: dict):
    """Resout 'a.b.c' dans un dict imbrique ; renvoie None si absent."""
    courant = donnees
    for cle in chemin.split("."):
        if isinstance(courant, dict) and cle in courant:
            courant = courant[cle]
        else:
            return None
    return courant


def remplir(template: str, contexte: dict) -> str:
    def remplacer(m):
        valeur = resoudre(m.group(1).strip(), contexte)
        if valeur is None or valeur == "":
            return MANQUANT
        if isinstance(valeur, bool):
            return "Oui" if valeur else "Non"
        return str(valeur)

    return re.sub(r"\{\{([^}]+)\}\}", remplacer, template)


def main() -> int:
    p = argparse.ArgumentParser(description="Remplit les templates locataire/Visale.")
    p.add_argument("slug", help="Nom du dossier dans dossiers/ (ex: dupont-marie)")
    p.add_argument("--bien", help="Ref du bien dans config/logement.yaml")
    args = p.parse_args()

    dossier = RACINE / "dossiers" / args.slug
    donnees_path = dossier / "donnees.json"
    if not donnees_path.exists():
        print(f"Erreur : {donnees_path} introuvable. Claude doit d'abord remplir donnees.json.", file=sys.stderr)
        return 1

    donnees = json.loads(donnees_path.read_text(encoding="utf-8"))

    # Logement
    conf = charger_yaml(RACINE / "config" / "logement.yaml")
    biens = conf.get("biens", []) if isinstance(conf, dict) else []
    bien = {}
    if biens:
        if args.bien:
            bien = next((b for b in biens if b.get("ref") == args.bien), {})
            if not bien:
                print(f"Attention : bien '{args.bien}' introuvable, aucun bien associe.", file=sys.stderr)
        else:
            bien = biens[0]

    contexte = dict(donnees)
    contexte["logement"] = bien

    for nom_tpl, sortie in [("fiche_locataire.md", "fiche_locataire.md"),
                            ("dossier_visale.md", "dossier_visale.md")]:
        tpl = (RACINE / "templates" / nom_tpl).read_text(encoding="utf-8")
        (dossier / sortie).write_text(remplir(tpl, contexte), encoding="utf-8")
        print(f"Ecrit : {(dossier / sortie).relative_to(RACINE)}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
