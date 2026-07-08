#!/usr/bin/env python3
"""Genere un CSV d'import Rentila (locataires) a partir de donnees.json.

Rentila permet d'importer des locataires via un modele CSV/Excel. Ce script produit ce CSV
en suivant la correspondance de colonnes definie dans config/rentila_import.yaml (a caler sur
l'en-tete exact du modele telecharge depuis votre compte Rentila).

Une ligne par locataire du dossier (gere la colocation).

Usage:
    python3 scripts/exporter_rentila_csv.py t2-rivoli-coloc
    python3 scripts/exporter_rentila_csv.py t2-rivoli-coloc --sortie import_rentila.csv
"""
import argparse
import csv
import json
import sys
from pathlib import Path

RACINE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RACINE / "scripts"))
from remplir_templates import charger_yaml  # noqa: E402


def main() -> int:
    p = argparse.ArgumentParser(description="Genere un CSV d'import locataires Rentila.")
    p.add_argument("slug")
    p.add_argument("--sortie", help="Fichier CSV de sortie (defaut: dossiers/<slug>/import_rentila.csv)")
    args = p.parse_args()

    dossier = RACINE / "dossiers" / args.slug
    donnees_path = dossier / "donnees.json"
    if not donnees_path.exists():
        print(f"Erreur : {donnees_path} introuvable.", file=sys.stderr)
        return 1
    donnees = json.loads(donnees_path.read_text(encoding="utf-8"))
    locataires = donnees.get("locataires", []) or []

    conf_path = RACINE / "config" / "rentila_import.yaml"
    if not conf_path.exists():
        print("Erreur : config/rentila_import.yaml manquant. "
              "Copiez l'exemple et calez les colonnes sur le modele Rentila.", file=sys.stderr)
        return 1
    conf = charger_yaml(conf_path)
    colonnes = conf.get("colonnes", [])
    delimiteur = conf.get("delimiteur", ";")
    if not colonnes:
        print("Erreur : aucune colonne dans config/rentila_import.yaml.", file=sys.stderr)
        return 1

    sortie = Path(args.sortie) if args.sortie else dossier / "import_rentila.csv"
    entetes = [c["colonne"] for c in colonnes]

    with sortie.open("w", newline="", encoding="utf-8-sig") as f:  # BOM pour Excel FR
        writer = csv.writer(f, delimiter=delimiteur)
        writer.writerow(entetes)
        for loc in locataires:
            ligne = []
            for c in colonnes:
                if "valeur" in c:
                    ligne.append(c["valeur"])
                else:
                    v = loc.get(c.get("champ"))
                    ligne.append("" if v is None else str(v))
            writer.writerow(ligne)

    print(f"CSV d'import genere : {sortie.relative_to(RACINE) if sortie.is_relative_to(RACINE) else sortie}")
    print(f"  {len(locataires)} locataire(s), {len(entetes)} colonne(s), delimiteur '{delimiteur}'")
    print("  → Verifiez les colonnes vs le modele Rentila, puis importez dans Rentila.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
