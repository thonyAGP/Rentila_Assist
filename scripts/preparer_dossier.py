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


def preparer(chemin_eml: Path, nom_force: str | None) -> Path:
    with chemin_eml.open("rb") as f:
        msg = email.message_from_binary_file(f, policy=email.policy.default)

    expediteur = str(msg.get("From", ""))
    objet = str(msg.get("Subject", ""))
    date_env = str(msg.get("Date", ""))
    corps = extraire_corps(msg)

    # Nom du dossier : force par l'utilisateur, sinon deduit de l'objet ou de l'expediteur
    base_nom = nom_force or objet or expediteur or "locataire"
    slug = slugifier(base_nom)
    dossier = DOSSIERS / slug
    pieces = dossier / "pieces"
    pieces.mkdir(parents=True, exist_ok=True)

    # Sauvegarde des pieces jointes
    jointes = []
    for partie in msg.walk():
        nom_fichier = partie.get_filename()
        if not nom_fichier:
            continue
        donnees = partie.get_payload(decode=True)
        if donnees is None:
            continue
        nom_sur = Path(nom_fichier).name  # anti-traversal
        cible = pieces / nom_sur
        cible.write_bytes(donnees)
        jointes.append(nom_sur)

    # Sauvegarde du corps + metadonnees
    (dossier / "email.txt").write_text(
        f"De: {expediteur}\nObjet: {objet}\nDate: {date_env}\n\n{corps}\n",
        encoding="utf-8",
    )

    meta = {
        "source_email": chemin_eml.name,
        "expediteur": expediteur,
        "objet": objet,
        "date_email": date_env,
        "pieces_jointes": jointes,
        "prepare_le": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "statut": "a_traiter",
    }
    (dossier / "meta.json").write_text(
        json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    return dossier


def main() -> int:
    parseur = argparse.ArgumentParser(description="Deballe un email transfere en dossier locataire.")
    parseur.add_argument("eml", type=Path, help="Chemin vers le fichier .eml transfere")
    parseur.add_argument("--nom", help="Force le nom du dossier (ex: 'Dupont Marie')")
    args = parseur.parse_args()

    if not args.eml.exists():
        print(f"Erreur : fichier introuvable : {args.eml}", file=sys.stderr)
        return 1

    dossier = preparer(args.eml, args.nom)
    meta = json.loads((dossier / "meta.json").read_text(encoding="utf-8"))
    print(f"Dossier prepare : {dossier.relative_to(RACINE)}")
    print(f"  Pieces jointes ({len(meta['pieces_jointes'])}) : {', '.join(meta['pieces_jointes']) or 'aucune'}")
    print(f"  Corps de l'email : {dossier.relative_to(RACINE)}/email.txt")
    print()
    print("Etape suivante : demandez a Claude de traiter ce dossier")
    print(f'  → skill "nouveau-locataire" sur {dossier.name}')
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
