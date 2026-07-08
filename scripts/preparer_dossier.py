#!/usr/bin/env python3
"""Prepare un dossier locataire a partir d'un email transfere (.eml).

Deballe l'email : sauvegarde le corps du message et toutes les pieces jointes
(photos de la piece d'identite, etc.) dans dossiers/<slug>/pieces/.

Aucune dependance externe (bibliotheque standard uniquement).

Usage:
    python3 scripts/preparer_dossier.py inbox/mon_email.eml
    python3 scripts/preparer_dossier.py inbox/mon_email.eml --nom "Dupont Marie"

Ensuite, Claude (skill "nouveau-locataire") lit les pieces et remplit la fiche.
"""
import argparse
import email
import email.policy
import json
import re
import sys
import unicodedata
from datetime import datetime, timezone
from pathlib import Path

RACINE = Path(__file__).resolve().parent.parent
DOSSIERS = RACINE / "dossiers"


def slugifier(texte: str) -> str:
    """Transforme un texte en identifiant de dossier sur (sans accents/espaces)."""
    texte = unicodedata.normalize("NFKD", texte).encode("ascii", "ignore").decode()
    texte = re.sub(r"[^\w\s-]", "", texte).strip().lower()
    texte = re.sub(r"[\s_-]+", "-", texte)
    return texte or "locataire"


def extraire_corps(msg) -> str:
    """Recupere le corps texte de l'email (prefere text/plain, sinon strip HTML)."""
    if msg.is_multipart():
        for partie in msg.walk():
            if partie.get_content_type() == "text/plain" and not partie.get_filename():
                return partie.get_content()
        for partie in msg.walk():
            if partie.get_content_type() == "text/html" and not partie.get_filename():
                html = partie.get_content()
                return re.sub(r"<[^>]+>", " ", html)
        return ""
    contenu = msg.get_content()
    if msg.get_content_type() == "text/html":
        return re.sub(r"<[^>]+>", " ", contenu)
    return contenu


def _nom_unique(pieces: Path, nom_sur: str) -> str:
    """Evite d'ecraser une piece existante (colocation : plusieurs emails)."""
    cible = pieces / nom_sur
    if not cible.exists():
        return nom_sur
    tige, ext = Path(nom_sur).stem, Path(nom_sur).suffix
    n = 2
    while (pieces / f"{tige}_{n}{ext}").exists():
        n += 1
    return f"{tige}_{n}{ext}"


def preparer(chemin_eml: Path, nom_force: str | None, dossier_cible: str | None) -> Path:
    with chemin_eml.open("rb") as f:
        msg = email.message_from_binary_file(f, policy=email.policy.default)

    expediteur = str(msg.get("From", ""))
    objet = str(msg.get("Subject", ""))
    date_env = str(msg.get("Date", ""))
    corps = extraire_corps(msg)

    # Cible : dossier existant (--dossier, ex: colocation) sinon deduit du nom/objet/expediteur
    slug = slugifier(dossier_cible) if dossier_cible else slugifier(nom_force or objet or expediteur or "locataire")
    dossier = DOSSIERS / slug
    pieces = dossier / "pieces"
    ajout = dossier.exists()
    pieces.mkdir(parents=True, exist_ok=True)

    # Sauvegarde des pieces jointes (sans ecraser en mode ajout)
    jointes = []
    for partie in msg.walk():
        nom_fichier = partie.get_filename()
        if not nom_fichier:
            continue
        donnees = partie.get_payload(decode=True)
        if donnees is None:
            continue
        nom_sur = _nom_unique(pieces, Path(nom_fichier).name)  # anti-traversal + anti-collision
        (pieces / nom_sur).write_bytes(donnees)
        jointes.append(nom_sur)

    # Corps de l'email : email.txt, puis email_2.txt, email_3.txt... en mode ajout
    n = 1
    cible_corps = dossier / "email.txt"
    while cible_corps.exists():
        n += 1
        cible_corps = dossier / f"email_{n}.txt"
    cible_corps.write_text(
        f"De: {expediteur}\nObjet: {objet}\nDate: {date_env}\n\n{corps}\n",
        encoding="utf-8",
    )

    # meta.json : accumule les emails et les pieces (colocation multi-emails)
    meta_path = dossier / "meta.json"
    meta = json.loads(meta_path.read_text(encoding="utf-8")) if meta_path.exists() else {
        "emails": [], "pieces_jointes": [], "statut": "a_traiter"
    }
    meta.setdefault("emails", [])
    meta.setdefault("pieces_jointes", [])
    meta["emails"].append({
        "source_email": chemin_eml.name, "expediteur": expediteur,
        "objet": objet, "date_email": date_env, "corps_fichier": cible_corps.name,
        "pieces": jointes,
    })
    meta["pieces_jointes"] += jointes
    meta["prepare_le"] = datetime.now(timezone.utc).isoformat(timespec="seconds")
    meta_path.write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")

    return dossier, jointes, ajout


def main() -> int:
    parseur = argparse.ArgumentParser(description="Deballe un email transfere en dossier locataire.")
    parseur.add_argument("eml", type=Path, help="Chemin vers le fichier .eml transfere")
    parseur.add_argument("--nom", help="Force le nom du dossier (ex: 'Dupont Marie')")
    parseur.add_argument("--dossier", help="Rattacher a un dossier existant (colocation, 2e email). Ex: t2-rivoli-coloc")
    args = parseur.parse_args()

    if not args.eml.exists():
        print(f"Erreur : fichier introuvable : {args.eml}", file=sys.stderr)
        return 1

    dossier, jointes, ajout = preparer(args.eml, args.nom, args.dossier)
    action = "Email rattache au dossier" if ajout else "Dossier prepare"
    print(f"{action} : {dossier.relative_to(RACINE)}")
    print(f"  Pieces jointes de cet email ({len(jointes)}) : {', '.join(jointes) or 'aucune'}")
    print()
    if ajout:
        print("Colocation : ce dossier regroupe plusieurs emails.")
    print("Etape suivante : demandez a Claude de traiter ce dossier")
    print(f'  → skill "nouveau-locataire" sur {dossier.name}')
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
