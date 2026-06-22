#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Conversion unique d'une fiche NETPLY : modèle de puissance (SCALE/EXP)  ->  modèle
polynomial (POLY a·v²+b·v+c) avec repères /*PDC-NETAIR-START/END*/ injectables ensuite.
Sauvegarde l'original en .bak. N'écrit rien si un motif attendu n'est pas trouvé.
"""
import os, sys, shutil
from coeffs_pdc import poly_block_netply   # bloc POLY construit depuis DONNEES_PDC

DOSSIER = os.path.dirname(os.path.abspath(__file__))
FICHE = os.path.join(DOSSIER, "Fiche technique NETPLY v4.html")

# (old, new, nb attendu)
def edits():
    POLY = poly_block_netply()   # texte JS multi-lignes (avec \n littéraux)
    A_old = ("const SCALE = {\\n      g4: { 48: 55, 98: 38 },   // G4 · Coarse 65%\\n"
             "      m5: { 48: 78, 98: 54 },   // M5 · ePM10 50%\\n    };\\n"
             "    const EXP = { g4: 1.65, m5: 1.62 };")
    A_new = ("/*PDC-NETAIR-START*/\\n    const POLY = {\\n" + POLY +
             "    };\\n    /*PDC-NETAIR-END*/\\n"
             "    const pdc = (co, v) => Math.max(0, co.a*v*v + co.b*v + co.c);")
    C_old = ("const curve = (sc, ex) => {\\n      const pts = [];\\n"
             "      for (let v = 0; v <= Vmax - 1e-9; v += 0.1) {\\n"
             "        const p = sc * Math.pow(v / Vnom, ex);\\n"
             "        pts.push(mapX(v).toFixed(1) + ',' + mapY(p).toFixed(1));\\n      }\\n"
             "      // point final exact à la limite de plage\\n"
             "      pts.push(mapX(Vmax).toFixed(1) + ',' + mapY(sc * Math.pow(Vmax / Vnom, ex)).toFixed(1));\\n"
             "      return 'M' + pts.join(' L');\\n    };")
    C_new = ("const curve = (co) => {\\n      const pts = [];\\n"
             "      for (let v = 0; v <= Vmax - 1e-9; v += 0.1) {\\n"
             "        const p = pdc(co, v);\\n"
             "        pts.push(mapX(v).toFixed(1) + ',' + mapY(p).toFixed(1));\\n      }\\n"
             "      pts.push(mapX(Vmax).toFixed(1) + ',' + mapY(pdc(co, Vmax)).toFixed(1));\\n"
             "      return 'M' + pts.join(' L');\\n    };")
    e = [
      (A_old, A_new, 1),
      ("const scale = SCALE[eff][s.thick];\\n    const exp = EXP[eff];",
       "const co = POLY[eff][s.thick];", 1),
      (C_old, C_new, 1),
      ("curve(SCALE.g4[48], EXP.g4)", "curve(POLY.g4[48])", 1),
      ("curve(SCALE.g4[98], EXP.g4)", "curve(POLY.g4[98])", 1),
      ("curve(SCALE.m5[48], EXP.m5)", "curve(POLY.m5[48])", 1),
      ("curve(SCALE.m5[98], EXP.m5)", "curve(POLY.m5[98])", 1),
      ("mapY(SCALE.g4[48] * Math.pow(vr, EXP.g4))", "mapY(pdc(POLY.g4[48], vr))", 1),
      ("mapY(SCALE.g4[98] * Math.pow(vr, EXP.g4))", "mapY(pdc(POLY.g4[98], vr))", 1),
      ("mapY(SCALE.m5[48] * Math.pow(vr, EXP.m5))", "mapY(pdc(POLY.m5[48], vr))", 1),
      ("mapY(SCALE.m5[98] * Math.pow(vr, EXP.m5))", "mapY(pdc(POLY.m5[98], vr))", 1),
      ("fr(SCALE.g4[48])", "fr(pdc(POLY.g4[48], Vnom))", 1),
      ("fr(SCALE.g4[98])", "fr(pdc(POLY.g4[98], Vnom))", 1),
      ("fr(SCALE.m5[48])", "fr(pdc(POLY.m5[48], Vnom))", 1),
      ("fr(SCALE.m5[98])", "fr(pdc(POLY.m5[98], Vnom))", 1),
      ("const dpInitNum = scale * Math.pow(velNum / Vnom, exp);",
       "const dpInitNum = pdc(co, velNum);", 1),
    ]
    return e

def main():
    txt = open(FICHE, encoding="utf-8").read()
    if "/*PDC-NETAIR-START*/" in txt:
        sys.exit("Fiche déjà convertie (repères présents). Utilise injecter_pdc.py pour mettre à jour.")
    for old, new, n in edits():
        c = txt.count(old)
        if c != n:
            sys.exit(f"ABANDON — motif trouvé {c}× (attendu {n}) : {old[:60]!r}…")
        txt = txt.replace(old, new)
    for resid in ("SCALE.", "SCALE[", "const SCALE", "EXP.g4", "EXP.m5", "EXP[eff]",
                  "const EXP", "const scale", "const exp "):
        assert resid not in txt, f"Résidu non remplacé : {resid}"
    assert "/*PDC-NETAIR-START*/" in txt and "const pdc = (co, v)" in txt
    shutil.copy(FICHE, FICHE + ".bak")
    open(FICHE, "w", encoding="utf-8").write(txt)
    print("Fiche convertie au modèle polynomial. Sauvegarde : Fiche technique NETPLY v4.html.bak")

if __name__ == "__main__":
    main()
