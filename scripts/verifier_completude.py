#!/usr/bin/env python3
"""Verifie la completude d'un dossier et produit le recapitulatif "A VALIDER".

Compare les pieces recues (donnees.json -> pieces[]) aux pieces requises
(config/pieces_requises.yaml). Ecrit dossiers/<slug>/recapitulatif.md avec :
  - l'inventaire des pieces rangees,
  - la checklist de completude (present / manquant),
  - le statut Visale et etat des lieux,
  - le verdict final : CONTRAT PRET A SIGNER ou liste des pieces manquantes.

Renvoie le code de sortie 0 si pret, 2 si des pieces obligatoires manquent.

Usage:
    python3 scripts/verifier_completude.py dupont-marie
"""
import argparse
import json
import sys
from pathlib import Path

RACINE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RACINE / "scripts"))
from remplir_templates import charger_yaml  # reutilise le loader YAML  # noqa: E402

LIBELLES_PIECE = {
    "piece_identite": "Pièce d'identité",
    "visale": "Garantie Visale",
    "certificat_scolarite": "Certificat de scolarité",
    "attestation_assurance": "Attestation d'assurance habitation",
    "etat_des_lieux": "État des lieux",
    "rib": "RIB",
    "justificatif_revenus": "Justificatif de revenus",
    "autre": "Autre",
}


def piece_requises_defaut():
    return [
        {"type": "piece_identite", "libelle": "Pièce d'identité", "par_locataire": True, "obligatoire": True},
        {"type": "visale", "libelle": "Garantie Visale", "par_locataire": False, "obligatoire": True},
        {"type": "attestation_assurance", "libelle": "Attestation d'assurance habitation", "par_locataire": False, "obligatoire": True},
    ]


def nom_locataire(loc: dict) -> str:
    return " ".join(x for x in [loc.get("prenoms"), loc.get("nom")] if x) or "(sans nom)"


def main() -> int:
    p = argparse.ArgumentParser(description="Verifie la completude d'un dossier.")
    p.add_argument("slug")
    args = p.parse_args()

    dossier = RACINE / "dossiers" / args.slug
    donnees_path = dossier / "donnees.json"
    if not donnees_path.exists():
        print(f"Erreur : {donnees_path} introuvable.", file=sys.stderr)
        return 1
    donnees = json.loads(donnees_path.read_text(encoding="utf-8"))

    conf = charger_yaml(RACINE / "config" / "pieces_requises.yaml")
    requises = conf.get("pieces", []) if isinstance(conf, dict) else []
    if not requises:
        requises = piece_requises_defaut()

    locataires = donnees.get("locataires", []) or []
    pieces = donnees.get("pieces", []) or []
    types_presents = [pc.get("type") for pc in pieces]

    # Etudiant ? -> certificat de scolarite devient bloquant
    est_etudiant = any(
        (pc.get("type") == "certificat_scolarite") for pc in pieces
    ) or any((loc.get("statut") == "Etudiant") for loc in locataires)

    lignes_check = []
    manquantes_obligatoires = []
    for r in requises:
        t = r["type"]
        libelle = r.get("libelle", LIBELLES_PIECE.get(t, t))
        oblig = bool(r.get("obligatoire", True))
        if t == "certificat_scolarite" and est_etudiant:
            oblig = True
        if r.get("par_locataire") and locataires:
            for loc in locataires:
                nom = nom_locataire(loc)
                present = any(
                    pc.get("type") == t and (pc.get("locataire") in (None, nom) or nom in str(pc.get("locataire")))
                    for pc in pieces
                )
                coche = "✅" if present else ("❌" if oblig else "⬜")
                lignes_check.append(f"| {libelle} — {nom} | {'obligatoire' if oblig else 'facultatif'} | {coche} |")
                if oblig and not present:
                    manquantes_obligatoires.append(f"{libelle} ({nom})")
        else:
            present = t in types_presents
            coche = "✅" if present else ("❌" if oblig else "⬜")
            note = "obligatoire" if oblig else "facultatif"
            if t == "certificat_scolarite" and est_etudiant:
                note = "obligatoire (locataire étudiant)"
            lignes_check.append(f"| {libelle} | {note} | {coche} |")
            if oblig and not present:
                manquantes_obligatoires.append(libelle)

    pret = not manquantes_obligatoires

    # Inventaire des pieces
    lignes_inv = ["| Type | Fichier | Locataire |", "|---|---|---|"]
    for pc in pieces:
        lignes_inv.append(
            f"| {LIBELLES_PIECE.get(pc.get('type'), pc.get('type'))} | `{pc.get('fichier')}` | {pc.get('locataire') or '—'} |"
        )
    if not pieces:
        lignes_inv.append("| _aucune piece rangee_ | | |")

    visale = donnees.get("visale") or {}
    edl = donnees.get("etat_des_lieux") or {}
    meta = donnees.get("meta") or {}
    incertains = meta.get("champs_incertains") or []

    verdict = (
        "## ✅ CONTRAT PRÊT À SIGNER\nToutes les pièces obligatoires sont présentes."
        if pret else
        "## ⏳ Dossier incomplet\nPièces obligatoires manquantes :\n"
        + "\n".join(f"- {m}" for m in manquantes_obligatoires)
    )

    recap = f"""# À VALIDER — Dossier {args.slug}

> Récapitulatif automatique. **Rien n'est finalisé sans votre validation.**

## Locataire(s)
{chr(10).join('- ' + nom_locataire(l) for l in locataires) or '_aucun_'}

## Pièces rangées dans `pieces/`
{chr(10).join(lignes_inv)}

## Checklist de complétude
| Pièce | Statut requis | Présente ? |
|---|---|---|
{chr(10).join(lignes_check)}

## Garantie Visale
- Code visa : **{visale.get('code_visa') or '⚠️ à compléter'}**
- Validité : {visale.get('validite_debut') or '?'} → {visale.get('validite_fin') or '?'}
- Activation : {visale.get('statut_activation') or 'a_activer'} → voir `visale_activation.md`

## État des lieux
- Type : {edl.get('type') or '—'} · Bien : {edl.get('bien') or '—'} · Date : {edl.get('date') or '—'}
- Locataires au PDF : {', '.join(edl.get('locataires') or []) or '—'}

## Champs incertains à revérifier
{chr(10).join('- ' + c for c in incertains) or '_aucun_'}

{verdict}

---
*Confiance globale : {meta.get('confiance_globale') or '?'}. Documents : `fiche_locataire.md`, `visale_activation.md`.*
"""
    (dossier / "recapitulatif.md").write_text(recap, encoding="utf-8")
    print(f"Ecrit : {(dossier / 'recapitulatif.md').relative_to(RACINE)}")
    print("Verdict :", "CONTRAT PRET A SIGNER" if pret else f"INCOMPLET ({len(manquantes_obligatoires)} piece(s) manquante(s))")
    return 0 if pret else 2


if __name__ == "__main__":
    raise SystemExit(main())
