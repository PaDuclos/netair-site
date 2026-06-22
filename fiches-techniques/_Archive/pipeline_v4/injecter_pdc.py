#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Injecte les coefficients polynomiaux de DONNEES_PDC_Netair.xlsx dans la fiche
technique (entre les repères /*PDC-NETAIR-START*/ … /*PDC-NETAIR-END*/).

À lancer après chaque mise à jour des ΔP mesurées dans DONNEES_PDC.
    python3 injecter_pdc.py
"""
import os, re, sys, shutil
from coeffs_pdc import poly_block_netply

DOSSIER = os.path.dirname(os.path.abspath(__file__))
FICHE = os.path.join(DOSSIER, "Fiche technique NETPLY v4.html")
PAT = re.compile(r"/\*PDC-NETAIR-START\*/.*?/\*PDC-NETAIR-END\*/", re.S)

def main():
    txt = open(FICHE, encoding="utf-8").read()
    if not PAT.search(txt):
        sys.exit("Repères /*PDC-NETAIR-…*/ absents — lance d'abord retrofit_fiche_pdc.py.")
    bloc = "/*PDC-NETAIR-START*/\\n    const POLY = {\\n" + poly_block_netply() + "    };\\n    /*PDC-NETAIR-END*/"
    new = PAT.sub(lambda m: bloc, txt, count=1)
    if new == txt:
        print("Aucun changement (coefficients déjà à jour).")
        return
    shutil.copy(FICHE, FICHE + ".bak")
    open(FICHE, "w", encoding="utf-8").write(new)
    print("Coefficients NETPLY injectés dans la fiche.")
    print(poly_block_netply().replace("\\n", "\n"))

if __name__ == "__main__":
    main()
