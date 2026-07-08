#!/usr/bin/env python3
"""Remplit les documents d'un dossier a partir de donnees.json + config logement.

Lit :
  - dossiers/<slug>/donnees.json   (rempli par Claude apres lecture des pieces)
  - config/logement.yaml           (infos des biens loues)
Ecrit :
  - dossiers/<slug>/fiche_locataire.md
  - dossiers/<slug>/visale_activation.md

Placeholders : {{a.b.c}} (valeur simple) et {{bloc.xxx}} (bloc genere).
Valeur manquante => "⚠️ à compléter" (jamais inventee).

Pas de dependance obligatoire ; PyYAML utilise s'il est present, sinon mini-parseur.

Usage:
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
    """Parseur minimal pour logement.example.yaml (dicos + listes d'objets simples)."""
    racine: dict = {}
    pile = [(-1, racine)]
    dernier_item: dict | None = None
    for ligne_brute in texte.splitlines():
        if not ligne_brute.strip() or ligne_brute.strip().startswith("#"):
            continue
        ligne = ligne_brute.split(" #")[0].rstrip()
        indent = len(ligne) - len(ligne.lstrip())
        contenu = ligne.strip()
        while len(pile) > 1 and indent <= pile[-1][0]:
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
    courant = donnees
    for cle in chemin.split("."):
        if isinstance(courant, dict) and cle in courant:
            courant = courant[cle]
        else:
            return None
    return courant


def fmt(valeur):
    if valeur is None or valeur == "":
        return MANQUANT
    if isinstance(valeur, bool):
        return "Oui" if valeur else "Non"
    return str(valeur)


def bloc_locataires(locataires: list) -> str:
    if not locataires:
        return "_Aucun locataire renseigné._"
    lignes = []
    for loc in locataires:
        nom = " ".join(x for x in [loc.get("civilite"), loc.get("prenoms"), loc.get("nom")] if x) or MANQUANT
        contact = " · ".join(x for x in [loc.get("email"), loc.get("telephone")] if x) or MANQUANT
        lignes.append(f"- **{nom}** — {contact}")
    return "\n".join(lignes)


def bloc_locataires_detail(locataires: list) -> str:
    if not locataires:
        return "_Aucun locataire renseigné._"
    entete = "| Civilité | Nom | Prénom(s) | Naissance | Email | Téléphone |\n|---|---|---|---|---|---|"
    lignes = [entete]
    for loc in locataires:
        lignes.append("| {} | {} | {} | {} | {} | {} |".format(
            fmt(loc.get("civilite")), fmt(loc.get("nom")), fmt(loc.get("prenoms")),
            fmt(loc.get("date_naissance")), fmt(loc.get("email")), fmt(loc.get("telephone")),
        ))
    return "\n".join(lignes)


def remplir(template: str, contexte: dict) -> str:
    def remplacer(m):
        cle = m.group(1).strip()
        if cle == "bloc.locataires":
            return bloc_locataires(contexte.get("locataires", []))
        if cle == "bloc.locataires_detail":
            return bloc_locataires_detail(contexte.get("locataires", []))
        return fmt(resoudre(cle, contexte))
    return re.sub(r"\{\{([^}]+)\}\}", remplacer, template)


def main() -> int:
    p = argparse.ArgumentParser(description="Remplit les documents du dossier.")
    p.add_argument("slug", help="Nom du dossier dans dossiers/ (ex: dupont-marie)")
    p.add_argument("--bien", help="Ref du bien dans config/logement.yaml (sinon celui de donnees.location.ref)")
    args = p.parse_args()

    dossier = RACINE / "dossiers" / args.slug
    donnees_path = dossier / "donnees.json"
    if not donnees_path.exists():
        print(f"Erreur : {donnees_path} introuvable. Claude doit d'abord remplir donnees.json.", file=sys.stderr)
        return 1

    donnees = json.loads(donnees_path.read_text(encoding="utf-8"))

    conf = charger_yaml(RACINE / "config" / "logement.yaml")
    biens = conf.get("biens", []) if isinstance(conf, dict) else []
    ref = args.bien or (donnees.get("location") or {}).get("ref")
    bien = {}
    if biens:
        bien = next((b for b in biens if b.get("ref") == ref), {}) if ref else biens[0]
        if ref and not bien:
            print(f"Attention : bien '{ref}' introuvable dans logement.yaml.", file=sys.stderr)
    # loyer_cc calcule si absent
    if bien and "loyer_cc" not in bien and "loyer_hc" in bien:
        bien = dict(bien)
        bien["loyer_cc"] = (bien.get("loyer_hc") or 0) + (bien.get("charges") or 0)

    contexte = dict(donnees)
    contexte["location"] = {**(donnees.get("location") or {}), **bien}

    for nom_tpl in ("fiche_locataire.md", "visale_activation.md"):
        tpl = (RACINE / "templates" / nom_tpl).read_text(encoding="utf-8")
        (dossier / nom_tpl).write_text(remplir(tpl, contexte), encoding="utf-8")
        print(f"Ecrit : {(dossier / nom_tpl).relative_to(RACINE)}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
