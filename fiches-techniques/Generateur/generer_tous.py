#!/usr/bin/env python3
"""
generer_tous.py — régénère TOUTES les fiches techniques depuis les JSON produits.

Boucle sur `produits/*.json` (hors `_gabarit_ref.json`, ancre du test d'identité)
et appelle `generer.py` pour chacun → fiches dans `Fiches_Netair/` + synchro vers
`site/public/fiches-techniques/`.

But : garder les fiches TOUJOURS alignées sur les données produit (source unique =
le JSON). Lancé automatiquement avant la construction et l'aperçu du site (scripts
npm `prebuild` / `predev`, via `site/scripts/regen-fiches.sh`), donc plus aucune
commande manuelle à retenir. `generer.py` étant déterministe, régénérer sans
changement ne produit aucune différence (pas de bruit git).

Usage : python3 generer_tous.py
"""
import os
import sys
import glob
import subprocess

ROOT = os.path.dirname(os.path.abspath(__file__))
GENERER = os.path.join(ROOT, "generer.py")
PRODUITS = os.path.join(ROOT, "produits")


def main() -> None:
    jsons = sorted(
        p for p in glob.glob(os.path.join(PRODUITS, "*.json"))
        if os.path.basename(p) != "_gabarit_ref.json"
    )
    if not jsons:
        print("generer_tous : aucun JSON produit trouvé.")
        return

    echecs = []
    for j in jsons:
        r = subprocess.run([sys.executable, GENERER, j], capture_output=True, text=True)
        if r.returncode != 0:
            echecs.append(os.path.basename(j))
            print(f"❌ {os.path.basename(j)}\n{r.stderr.strip()}")

    ok = len(jsons) - len(echecs)
    print(f"📄 Fiches techniques régénérées : {ok}/{len(jsons)}")
    if echecs:
        print("❌ Échecs : " + ", ".join(echecs))
        sys.exit(1)


if __name__ == "__main__":
    main()
