#!/usr/bin/env python3
"""Finalise un dossier valide : met a jour le registre.

A lancer APRES validation humaine. Pour chaque locataire du dossier :
  - upsert dans registre/locataires.json (cree ou complete).
Et enregistre le contrat retenu dans registre/contrats.json (pour proposer le loyer
lors de la prochaine remise en location du bien).

Marque aussi meta.statut = "valide" dans donnees.json.

Usage:
    python3 scripts/enregistrer.py t2-rivoli-coloc
"""
import argparse
import json
import re
import sys
import unicodedata
from pathlib import Path

RACINE = Path(__file__).resolve().parent.parent
REGISTRE = RACINE / "registre"
CHAMPS_LOC = ["civilite", "nom", "prenoms", "date_naissance", "email", "telephone",
              "adresse_actuelle", "nationalite", "lieu_naissance"]


def slugid(loc: dict) -> str:
    base = f"{loc.get('nom','')}-{(loc.get('prenoms') or '').split(' ')[0]}"
    annee = (loc.get("date_naissance") or "")[:4]
    s = unicodedata.normalize("NFKD", f"{base}-{annee}").encode("ascii", "ignore").decode()
    return re.sub(r"[^\w]+", "-", s).strip("-").lower()


def _load(chemin: Path) -> list:
    return json.loads(chemin.read_text(encoding="utf-8")) if chemin.exists() else []


def _save(chemin: Path, data) -> None:
    chemin.parent.mkdir(parents=True, exist_ok=True)
    chemin.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def main() -> int:
    p = argparse.ArgumentParser(description="Finalise un dossier valide (maj registre).")
    p.add_argument("slug")
    args = p.parse_args()

    dossier = RACINE / "dossiers" / args.slug
    dpath = dossier / "donnees.json"
    if not dpath.exists():
        print(f"Erreur : {dpath} introuvable.", file=sys.stderr)
        return 1
    donnees = json.loads(dpath.read_text(encoding="utf-8"))

    loc_reg = _load(REGISTRE / "locataires.json")
    par_id = {r.get("id"): r for r in loc_reg if r.get("id")}
    ref = (donnees.get("location") or {}).get("ref")

    ids_dossier = []
    for loc in donnees.get("locataires", []) or []:
        lid = loc.get("id") or slugid(loc)
        loc["id"] = lid
        ids_dossier.append(lid)
        fiche = par_id.get(lid, {"id": lid})
        for champ in CHAMPS_LOC:
            if loc.get(champ):
                fiche[champ] = loc[champ]
        locs = set(fiche.get("locations", []))
        if ref:
            locs.add(ref)
        fiche["locations"] = sorted(locs)
        if lid not in par_id:
            loc_reg.append(fiche)
            par_id[lid] = fiche
            print(f"Locataire cree dans le registre : {lid}")
        else:
            print(f"Locataire complete dans le registre : {lid}")

    _save(REGISTRE / "locataires.json", loc_reg)

    # Contrat retenu -> historique
    contrat = donnees.get("contrat") or {}
    loyer = contrat.get("loyer_hc_retenu") or contrat.get("loyer_hc_propose")
    charges = contrat.get("charges_retenues") or contrat.get("charges_proposees")
    if ref and loyer:
        contrats = _load(REGISTRE / "contrats.json")
        contrats.append({
            "bien": ref,
            "locataire_id": ids_dossier[0] if ids_dossier else None,
            "colocataires": ids_dossier if len(ids_dossier) > 1 else None,
            "loyer_hc": loyer,
            "charges": charges,
            "date_debut": contrat.get("date_effet"),
            "date_fin": None,
        })
        _save(REGISTRE / "contrats.json", contrats)
        print(f"Contrat enregistre pour {ref} : loyer HC {loyer} € + charges {charges} €")
    else:
        print("Aucun contrat enregistre (ref ou loyer manquant).", file=sys.stderr)

    donnees.setdefault("meta", {})["statut"] = "valide"
    dpath.write_text(json.dumps(donnees, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Dossier {args.slug} marque 'valide'.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
