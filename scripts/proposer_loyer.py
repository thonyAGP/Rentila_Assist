#!/usr/bin/env python3
"""Propose un loyer pour une remise en location, d'apres l'ancien contrat du bien.

Cherche dans registre/contrats.json le contrat le plus recent pour <REF>, applique le
coefficient `parametres.revalorisation_relocation` de config/logement.yaml, et propose le
loyer HC + charges. En zone tendue, le loyer de relocation est en principe plafonne a
l'ancien loyer revalorise IRL : a verifier selon la commune.

Peut aussi ecrire la proposition dans donnees.json (bloc `contrat`) avec --slug.

Usage:
    python3 scripts/proposer_loyer.py T2-RIVOLI
    python3 scripts/proposer_loyer.py T2-RIVOLI --slug t2-rivoli-coloc
"""
import argparse
import json
import sys
from pathlib import Path

RACINE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RACINE / "scripts"))
from remplir_templates import charger_yaml  # noqa: E402


def dernier_contrat(ref: str) -> dict | None:
    chemin = RACINE / "registre" / "contrats.json"
    if not chemin.exists():
        return None
    contrats = json.loads(chemin.read_text(encoding="utf-8"))
    du_bien = [c for c in contrats if c.get("bien") == ref]
    if not du_bien:
        return None
    # le plus recent par date_debut
    return max(du_bien, key=lambda c: c.get("date_debut") or "")


def bien_config(ref: str) -> dict:
    conf = charger_yaml(RACINE / "config" / "logement.yaml")
    for b in (conf.get("biens", []) if isinstance(conf, dict) else []):
        if b.get("ref") == ref:
            return b
    return {}


def coefficient() -> float:
    conf = charger_yaml(RACINE / "config" / "logement.yaml")
    params = conf.get("parametres", {}) if isinstance(conf, dict) else {}
    try:
        return float(params.get("revalorisation_relocation", 1.0))
    except (TypeError, ValueError):
        return 1.0


def main() -> int:
    p = argparse.ArgumentParser(description="Propose un loyer d'apres l'ancien contrat.")
    p.add_argument("ref", help="Reference du bien (ex: T2-RIVOLI)")
    p.add_argument("--slug", help="Ecrit la proposition dans dossiers/<slug>/donnees.json")
    args = p.parse_args()

    coef = coefficient()
    ancien = dernier_contrat(args.ref)
    bien = bien_config(args.ref)

    if ancien:
        loyer = round((ancien.get("loyer_hc") or 0) * coef)
        charges = ancien.get("charges")
        source = f"ancien contrat {ancien.get('date_debut')} (x{coef})"
        print(f"Ancien contrat trouve pour {args.ref} : loyer HC {ancien.get('loyer_hc')} € "
              f"+ charges {charges} € (debut {ancien.get('date_debut')})")
    elif bien:
        loyer = bien.get("loyer_hc")
        charges = bien.get("charges")
        source = "config logement (aucun ancien contrat)"
        print(f"Aucun ancien contrat pour {args.ref} : reprise du loyer de config/logement.yaml")
    else:
        print(f"Aucune donnee pour le bien '{args.ref}'.", file=sys.stderr)
        return 1

    print(f"→ Loyer HC propose : {loyer} €  |  charges : {charges} €  ({source})")

    if args.slug:
        dpath = RACINE / "dossiers" / args.slug / "donnees.json"
        if not dpath.exists():
            print(f"Attention : {dpath} introuvable, proposition non ecrite.", file=sys.stderr)
            return 0
        donnees = json.loads(dpath.read_text(encoding="utf-8"))
        contrat = donnees.get("contrat") or {}
        contrat.update({
            "loyer_hc_propose": loyer,
            "charges_proposees": charges,
            "source_proposition": source,
        })
        donnees["contrat"] = contrat
        dpath.write_text(json.dumps(donnees, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"Proposition ecrite dans {dpath.relative_to(RACINE)} (bloc contrat).")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
