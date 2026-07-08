#!/usr/bin/env python3
"""Calcule le tableau d'amortissement d'un bien (logique LMNP, par composants).

Amortissement lineaire par composant, avec prorata temporis la premiere annee.
Le bati est decompose (gros oeuvre, facade, installations, agencements) ; le terrain
n'est pas amortissable ; mobilier et travaux ont leur propre base et duree.

Entree : config/biens_fiscal.json (ou --fichier), bloc du bien <REF>.
Sortie : tableau annuel (par poste, total, cumule, valeur nette comptable restante).

> Rappel fiscal : en LMNP au reel, l'amortissement deductible ne peut pas creer ni
> aggraver un deficit ; l'excedent est reportable sans limite de duree. Ce script calcule
> le tableau theorique ; la limitation au resultat se fait a la declaration.

Bibliotheque standard uniquement.

Usage:
    python3 scripts/amortissement.py T2-RIVOLI
    python3 scripts/amortissement.py T2-RIVOLI --horizon 30 --sortie amortissement.md --json amort.json
"""
import argparse
import json
import sys
from pathlib import Path

RACINE = Path(__file__).resolve().parent.parent


def prorata_annee1(date_debut: str) -> tuple[int, float]:
    """Renvoie (annee de debut, fraction de la 1re annee) a partir de 'AAAA-MM-JJ'."""
    try:
        an, mois, _ = (int(x) for x in date_debut.split("-"))
    except (ValueError, AttributeError):
        return (0, 1.0)
    mois_restants = 12 - (mois - 1)  # du mois de debut a decembre inclus
    return (an, mois_restants / 12)


def serie_poste(base: float, duree: int, date_debut: str) -> dict[int, float]:
    """Montants annuels d'amortissement d'un poste {annee: montant}."""
    if not base or not duree:
        return {}
    an1, frac = prorata_annee1(date_debut)
    if an1 == 0:
        return {}
    annuel = base / duree
    serie: dict[int, float] = {}
    reste = base
    annee = an1
    # 1re annee au prorata
    m = round(min(annuel * frac, reste), 2)
    serie[annee] = m
    reste = round(reste - m, 2)
    # annees pleines
    while reste > 0.005:
        annee += 1
        m = round(min(annuel, reste), 2)
        serie[annee] = m
        reste = round(reste - m, 2)
    return serie


def construire_postes(bien: dict) -> list[dict]:
    """Construit la liste des postes amortissables (bati decompose + mobilier + travaux)."""
    postes = []
    prix = (bien.get("prix_acquisition") or 0) + (bien.get("frais_acquisition") or 0)
    terrain_pct = bien.get("quote_part_terrain_pct") or 0
    base_bati = prix * (1 - terrain_pct / 100)
    date_bati = bien.get("date_acquisition") or bien.get("date_mise_en_location")

    for comp in bien.get("composants", []):
        base = comp.get("base")
        if base is None and comp.get("pct_du_bati") is not None:
            base = base_bati * comp["pct_du_bati"] / 100
        postes.append({
            "libelle": comp.get("libelle", "Composant"),
            "base": round(base or 0, 2),
            "duree": comp.get("duree"),
            "date_debut": comp.get("date_debut") or date_bati,
        })
    for grp in ("mobilier", "travaux"):
        for it in bien.get(grp, []):
            postes.append({
                "libelle": it.get("libelle", grp.capitalize()),
                "base": round(it.get("base") or 0, 2),
                "duree": it.get("duree"),
                "date_debut": it.get("date_debut") or date_bati,
            })
    return postes, round(base_bati, 2), round(prix * terrain_pct / 100, 2)


def main() -> int:
    p = argparse.ArgumentParser(description="Tableau d'amortissement LMNP d'un bien.")
    p.add_argument("ref", help="Reference du bien (ex: T2-RIVOLI)")
    p.add_argument("--fichier", type=Path, default=RACINE / "config" / "biens_fiscal.json")
    p.add_argument("--horizon", type=int, default=30, help="Nombre d'annees affichees")
    p.add_argument("--sortie", type=Path, help="Ecrit un tableau Markdown")
    p.add_argument("--json", dest="json_out", type=Path, help="Ecrit le detail JSON")
    args = p.parse_args()

    if not args.fichier.exists():
        print(f"Erreur : {args.fichier} introuvable (copiez biens_fiscal.example.json).", file=sys.stderr)
        return 1
    data = json.loads(args.fichier.read_text(encoding="utf-8"))
    biens = data.get("biens", data) if isinstance(data, dict) else data
    bien = next((b for b in biens if b.get("ref") == args.ref), None)
    if not bien:
        print(f"Erreur : bien '{args.ref}' absent de {args.fichier.name}.", file=sys.stderr)
        return 1

    postes, base_bati, base_terrain = construire_postes(bien)
    series = [serie_poste(x["base"], x["duree"], x["date_debut"]) for x in postes]
    total_base = sum(x["base"] for x in postes)

    annees = sorted({a for s in series for a in s})
    if annees:
        annees = list(range(annees[0], min(annees[0] + args.horizon, annees[-1] + 1)))

    lignes = []
    cumul = 0.0
    for an in annees:
        annuel = round(sum(s.get(an, 0) for s in series), 2)
        cumul = round(cumul + annuel, 2)
        vnc = round(total_base - cumul, 2)
        lignes.append({"annee": an, "annuel": annuel, "cumule": cumul, "vnc": vnc})

    # affichage console
    print(f"Bien {args.ref} — base amortissable {total_base:.0f} € "
          f"(bâti {base_bati:.0f} €, terrain non amortissable {base_terrain:.0f} €)")
    print(f"Postes : " + ", ".join(f"{x['libelle']} {x['base']:.0f}€/{x['duree']}ans" for x in postes))
    print(f"{'Année':>6} | {'Amort. annuel':>13} | {'Cumulé':>10} | {'VNC restante':>12}")
    for l in lignes:
        print(f"{l['annee']:>6} | {l['annuel']:>11.2f} € | {l['cumule']:>8.2f} € | {l['vnc']:>10.2f} €")

    detail = {
        "ref": args.ref, "base_amortissable": total_base, "base_bati": base_bati,
        "base_terrain": base_terrain, "postes": postes, "tableau": lignes,
        "taxe_fonciere": bien.get("taxe_fonciere"),
        "charges_eau_annuelle": bien.get("charges_eau_annuelle"),
    }
    if args.json_out:
        args.json_out.write_text(json.dumps(detail, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"\nJSON : {args.json_out}")
    if args.sortie:
        md = [f"# Tableau d'amortissement — {args.ref}", "",
              f"Base amortissable : **{total_base:.0f} €** (bâti {base_bati:.0f} €, "
              f"terrain non amortissable {base_terrain:.0f} €)", "",
              "| Poste | Base | Durée |", "|---|---|---|"]
        md += [f"| {x['libelle']} | {x['base']:.0f} € | {x['duree']} ans |" for x in postes]
        md += ["", "| Année | Amort. annuel | Cumulé | VNC restante |", "|---|---|---|---|"]
        md += [f"| {l['annee']} | {l['annuel']:.2f} € | {l['cumule']:.2f} € | {l['vnc']:.2f} € |" for l in lignes]
        md += ["", "> Amortissement linéaire par composants, prorata temporis la 1re année.",
               "> En LMNP réel, l'amortissement déductible ne peut créer/aggraver un déficit (excédent reportable)."]
        args.sortie.write_text("\n".join(md), encoding="utf-8")
        print(f"Markdown : {args.sortie}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
