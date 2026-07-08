# État des lieux

L'état des lieux (entrée ou sortie) arrive sous forme de **PDF**. Le workflow l'exploite
comme une pièce du dossier.

## Ce que le projet extrait du PDF
- **Type** : entrée ou sortie.
- **Bien** concerné (adresse / désignation tels qu'écrits dans le PDF).
- **Noms des locataires** figurant sur le document.
- **Date** de l'état des lieux.

Ces champs vont dans `donnees.json` → `etat_des_lieux`, et le PDF est rangé dans `pieces/`
sous le nom `etat_des_lieux[_entree|_sortie].pdf`.

## Vérifications à la validation
- Le **bien** extrait correspond bien à la location traitée (`config/logement.yaml`).
- Les **noms** correspondent aux locataires du dossier.
- Le PDF est **signé** par les deux parties (à confirmer visuellement).

## Entrée vs sortie
- **Entrée** : établi à la remise des clés ; fait partie des pièces avant/à la signature.
- **Sortie** : établi au départ du locataire ; sert de comparaison pour le dépôt de garantie.
  Ce workflow se concentre sur l'entrée ; la sortie utilise la même extraction (type =
  `sortie`) pour archivage dans les pièces.
