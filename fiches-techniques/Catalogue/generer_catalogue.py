#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
generer_catalogue.py — construit le catalogue produits Netair (HTML + PDF).

    python3 generer_catalogue.py

Assemble trois sources et n'en invente aucune :
  · `Generateur/produits/*.json`  → tout ce qui décrit un produit
  · `site/src/lib/familles.ts`    → tout ce qui décrit une famille
  · `contenu_catalogue.md`        → couverture, édito, page normes, 4e de couverture

Le PDF est imprimé par Google Chrome en mode sans fenêtre : même moteur de rendu
que l'aperçu à l'écran, donc ce qu'on voit est ce qui sort. Aucune retouche
manuelle n'intervient entre la donnée et le PDF.

Design : hexagones, découpes en diagonale et photographie de nature, repris de la
présentation commerciale de Pierre-Alain ; couleurs et typographie de la charte
« Precision Blanche ».
"""

import base64
import html
import math
import os
import re
import shutil
import subprocess
import sys
from datetime import date

import lecture_courbes
import lecture_familles
import lecture_produits

ICI = os.path.dirname(os.path.abspath(__file__))
ASSETS = os.path.join(ICI, "assets")
CACHE = os.path.join(ICI, ".cache_images")
CONTENU = os.path.join(ICI, "contenu_catalogue.md")
SORTIE_HTML = os.path.join(ICI, "Catalogue_Netair.html")
SORTIE_PDF = os.path.join(ICI, "Catalogue_Netair.pdf")

CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"

NAVY, TEAL, BLUE = "#0F3261", "#0897A5", "#0070C8"

MOIS = ("janvier février mars avril mai juin juillet "
        "août septembre octobre novembre décembre").split()


def e(s):
    """Échappement HTML — les données produit sont du texte brut, jamais du balisage."""
    return html.escape(str(s), quote=False)


# ------------------------------------------------------------ contenu manuel --
def lire_contenu():
    """Parse `contenu_catalogue.md` : blocs `## NOM`, champs `cle: valeur`."""
    with open(CONTENU, encoding="utf-8") as f:
        texte = f.read()

    blocs, courant, champ = {}, None, None
    for ligne in texte.splitlines():
        if ligne.startswith("## "):
            courant = ligne[3:].strip()
            blocs[courant], champ = {}, None
            continue
        if courant is None or ligne.strip() in ("---", ""):
            if champ and courant and ligne.strip() == "":
                blocs[courant][champ] += "\n"
            continue
        if ligne.startswith(">"):
            continue
        m = re.match(r"^([a-z_]+)\s*:\s*(.*)$", ligne)
        if m:
            champ = m.group(1)
            blocs[courant][champ] = m.group(2)
        elif champ:
            blocs[courant][champ] += "\n" + ligne

    for bloc in blocs.values():
        for k in bloc:
            bloc[k] = bloc[k].strip()
    for requis in ("COUVERTURE", "EDITO", "NORMES", "DOS"):
        if requis not in blocs:
            raise RuntimeError(f"contenu_catalogue.md : bloc « {requis} » absent.")
    return blocs


def paragraphes(texte):
    """Texte libre → paragraphes HTML."""
    return "".join(f"<p>{e(p.strip())}</p>"
                   for p in re.split(r"\n\s*\n", texte) if p.strip())


# ---------------------------------------------------------------- images ------
def image_data_uri(chemin, largeur_max=1400):
    """Image réduite pour l'impression puis embarquée en base64 (fichier autoportant).

    Un PNG reste un PNG : le JPEG n'a pas de canal alpha, et le convertir ferait
    perdre la transparence des logos — le logo blanc deviendrait un bloc blanc, et
    la charte interdit tout fond blanc derrière le logo.
    """
    if not os.path.exists(chemin):
        raise RuntimeError(f"image introuvable : {chemin}")
    transparent = chemin.lower().endswith(".png")
    fmt = "png" if transparent else "jpeg"
    os.makedirs(CACHE, exist_ok=True)
    cible = os.path.join(CACHE, f"{largeur_max}-{os.path.basename(chemin)}.{fmt}")
    if not os.path.exists(cible) or os.path.getmtime(cible) < os.path.getmtime(chemin):
        cmd = ["sips", "-Z", str(largeur_max), "-s", "format", fmt]
        if not transparent:
            cmd += ["-s", "formatOptions", "80"]
        r = subprocess.run(cmd + [chemin, "--out", cible], capture_output=True)
        if r.returncode != 0 or not os.path.exists(cible):
            cible = chemin  # sips indisponible : on embarque l'original
    with open(cible, "rb") as f:
        b64 = base64.b64encode(f.read()).decode()
    return f"data:image/{fmt};base64,{b64}"


# ------------------------------------------------- courbe perte de charge -----
def _pas_joli(etendue, cibles=4):
    """Un pas de graduation lisible (1, 2, 2,5 ou 5 × puissance de dix)."""
    if etendue <= 0:
        return 1
    base = etendue / cibles
    mag = 10 ** math.floor(math.log10(base))
    for m in (1, 2, 2.5, 5, 10):
        if base <= m * mag:
            return m * mag
    return 10 * mag


def svg_courbe(c):
    """Courbe débit / perte de charge, en SVG (aucune dépendance, imprimable)."""
    if not c:
        return ""
    X0, X1, Y0, Y1 = 46, 286, 14, 200        # cadre de tracé, en unités viewBox
    qmax, pmax = c["debit_max"], c["pmax"]

    def px(q):
        return X0 + (q / qmax) * (X1 - X0)

    def py(p):
        return Y1 - (p / pmax) * (Y1 - Y0)

    pas_q, pas_p = _pas_joli(qmax), _pas_joli(pmax)
    grille, graduations = [], []
    k = pas_q
    while k <= qmax + 1e-6:
        grille.append(f'<line x1="{px(k):.1f}" y1="{Y0}" x2="{px(k):.1f}" y2="{Y1}"/>')
        graduations.append(f'<text x="{px(k):.1f}" y="{Y1 + 14}" text-anchor="middle" '
                           f'class="g">{k:,.0f}</text>'.replace(",", " "))
        k += pas_q
    k = pas_p
    while k <= pmax + 1e-6:
        grille.append(f'<line x1="{X0}" y1="{py(k):.1f}" x2="{X1}" y2="{py(k):.1f}"/>')
        graduations.append(f'<text x="{X0 - 6}" y="{py(k) + 3.5:.1f}" text-anchor="end" '
                           f'class="g">{k:,.0f}</text>'.replace(",", " "))
        k += pas_p

    traces, legende = [], []
    for i, courbe in enumerate(c["courbes"]):
        pts = " ".join(f"{px(q):.1f},{py(p):.1f}" for q, p in courbe["points"])
        traces.append(f'<polyline points="{pts}" fill="none" '
                      f'stroke="{courbe["couleur"]}" stroke-width="2.2" '
                      f'stroke-linejoin="round" stroke-linecap="round"/>')
        y = 240 + i * 12
        legende.append(
            f'<line x1="{X0}" y1="{y}" x2="{X0 + 16}" y2="{y}" '
            f'stroke="{courbe["couleur"]}" stroke-width="2.2"/>'
            f'<text x="{X0 + 22}" y="{y + 3.5}" class="l">{e(courbe["label"])}'
            f'  —  {courbe["dp_nom"]:.0f} Pa</text>')

    nominal = ""
    if c["debit_nom"]:
        x = px(c["debit_nom"])
        # Quand le debit nominal est proche du bord, on retient l'etiquette a
        # l'interieur du cadre : centree telle quelle, elle sortait du dessin.
        xl = min(max(x, X0 + 34), X1 - 34)
        nominal = (f'<line x1="{x:.1f}" y1="{Y0}" x2="{x:.1f}" y2="{Y1}" '
                   f'stroke="{TEAL}" stroke-width="1" stroke-dasharray="3 3" opacity=".75"/>'
                   f'<text x="{xl:.1f}" y="{Y0 - 3}" text-anchor="middle" class="n">'
                   f'{c["debit_nom"]:,.0f} m³/h nominal</text>'.replace(",", " "))
        for courbe in c["courbes"]:
            nominal += (f'<circle cx="{x:.1f}" cy="{py(courbe["dp_nom"]):.1f}" r="3" '
                        f'fill="{courbe["couleur"]}"/>')

    # Hauteur FIGÉE quel que soit le nombre de courbes : le tableau des
    # caractéristiques est à une position fixe plus bas, un graphique élastique
    # viendrait le heurter (constaté sur NETBAG S et ses trois courbes).
    return f"""<svg class="pr-svg" viewBox="0 0 296 274" role="img"
     aria-label="Courbe débit / perte de charge">
  <style>
    .g{{font:9px Helvetica,Arial,sans-serif;fill:#4A5E7A}}
    .l{{font:9.5px Helvetica,Arial,sans-serif;fill:#0F3261;font-weight:600}}
    .n{{font:8.5px Helvetica,Arial,sans-serif;fill:{TEAL};font-weight:600}}
    .t{{font:9px Helvetica,Arial,sans-serif;fill:#4A5E7A}}
  </style>
  <g stroke="#E2E8F0" stroke-width="1">{''.join(grille)}</g>
  <line x1="{X0}" y1="{Y1}" x2="{X1}" y2="{Y1}" stroke="#94A3B8" stroke-width="1.2"/>
  <line x1="{X0}" y1="{Y0}" x2="{X0}" y2="{Y1}" stroke="#94A3B8" stroke-width="1.2"/>
  {''.join(graduations)}
  <text x="{X1}" y="{Y1 + 28}" text-anchor="end" class="t">Débit (m³/h)</text>
  <text x="{X0 - 34}" y="{(Y0 + Y1) / 2}" class="t"
        transform="rotate(-90 {X0 - 34} {(Y0 + Y1) / 2})" text-anchor="middle">ΔP (Pa)</text>
  {nominal}{''.join(traces)}{''.join(legende)}
</svg>"""


# ------------------------------------------------------------------ styles ----
def feuille_de_style():
    return f"""
@page {{ size: A4 portrait; margin: 0; }}
* {{ box-sizing: border-box; margin: 0; padding: 0; }}
:root {{
  --navy: {NAVY}; --teal: {TEAL}; --blue: {BLUE};
  --bg: #F8FAFC; --muted: #ECF1F4; --border: #E2E8F0; --sub: #4A5E7A;
}}
body {{
  font-family: "Helvetica Neue", Helvetica, Arial, sans-serif;
  color: var(--navy); background: #6b7280; -webkit-font-smoothing: antialiased;
}}
.page {{
  position: relative; width: 210mm; height: 297mm; overflow: hidden;
  background: #fff; margin: 0 auto 6mm; page-break-after: always;
}}
.page:last-child {{ page-break-after: auto; }}
@media print {{
  body {{ background: #fff; }}
  .page {{ margin: 0; box-shadow: none; }}
  * {{ -webkit-print-color-adjust: exact; print-color-adjust: exact; }}
}}

/* --- motifs communs ------------------------------------------------------ */
.hex {{ clip-path: polygon(25% 0%, 75% 0%, 100% 50%, 75% 100%, 25% 100%, 0% 50%); }}
.hex-v {{ clip-path: polygon(50% 0%, 100% 25%, 100% 75%, 50% 100%, 0% 75%, 0% 25%); }}
.label {{
  text-transform: uppercase; letter-spacing: .12em; font-weight: 700;
  font-size: 7.5pt; color: var(--teal);
}}
/* Les renvois du sommaire, des pages de gamme et de la synthèse sont des liens
   internes : cliquables dans le PDF, mais rigoureusement invisibles à l'impression. */
a {{ color: inherit; text-decoration: none; }}
.lame {{ border-left: 4px solid var(--teal); padding-left: 6mm; }}

/* --- couverture ---------------------------------------------------------- */
.cv-bande {{ position: absolute; top: 0; right: 0; width: 88mm; height: 297mm;
            background: var(--blue); clip-path: polygon(38% 0, 100% 0, 100% 100%, 0 100%); }}
.cv-bande2 {{ position: absolute; top: 0; right: 0; width: 60mm; height: 118mm;
             background: var(--navy); clip-path: polygon(52% 0, 100% 0, 100% 100%, 0 100%); }}
.cv-photo {{ position: absolute; top: 48mm; right: 12mm; width: 96mm; height: 162mm;
            object-fit: cover; }}
.cv-logo {{ position: absolute; top: 20mm; left: 20mm; width: 52mm; }}
.cv-titre {{ position: absolute; top: 126mm; left: 20mm; width: 72mm;
            font-size: 30pt; font-weight: 700; line-height: 1.12; letter-spacing: -.01em; }}
.cv-sous {{ position: absolute; top: 172mm; left: 20mm; font-size: 14pt;
           color: var(--blue); font-weight: 600; }}
.cv-accroche {{ position: absolute; bottom: 34mm; left: 20mm; font-size: 10.5pt;
               color: var(--sub); font-style: italic; }}
.cv-mention {{ position: absolute; bottom: 20mm; left: 20mm; font-size: 8pt; color: var(--sub); }}
.cv-filet {{ position: absolute; bottom: 28mm; left: 20mm; width: 34mm;
            height: 3px; background: var(--teal); }}

/* --- édito --------------------------------------------------------------- */
.ed-photo {{ position: absolute; top: 0; left: 0; width: 92mm; height: 297mm;
            object-fit: cover; clip-path: polygon(0 0, 100% 0, 74% 100%, 0 100%); }}
.ed-voile {{ position: absolute; top: 0; left: 0; width: 92mm; height: 297mm;
            background: linear-gradient(180deg, rgba(15,50,97,.55), rgba(15,50,97,.78));
            clip-path: polygon(0 0, 100% 0, 74% 100%, 0 100%); }}
.ed-hex {{ position: absolute; top: 122mm; left: 22mm; width: 30mm; height: 34mm;
          background: rgba(255,255,255,.14); border: 1px solid rgba(255,255,255,.4); }}
.ed-logo {{ position: absolute; top: 22mm; left: 18mm; width: 44mm; }}
.ed-corps {{ position: absolute; top: 62mm; left: 104mm; width: 86mm; }}
.ed-titre {{ font-size: 21pt; font-weight: 700; line-height: 1.15; margin: 3mm 0 7mm; }}
.ed-corps p {{ font-size: 10pt; line-height: 1.62; color: #26364d; margin-bottom: 4.5mm; }}
.ed-sign {{ position: absolute; bottom: 34mm; left: 104mm; width: 86mm;
           padding-top: 4mm; border-top: 1px solid var(--border);
           font-size: 9pt; color: var(--sub); }}

/* --- en-tête de page courante -------------------------------------------- */
.tete {{ position: absolute; top: 0; left: 0; width: 210mm; height: 26mm;
        background: var(--navy); clip-path: polygon(0 0, 100% 0, 100% 62%, 0 100%); }}
.tete-txt {{ position: absolute; top: 8mm; left: 20mm; color: #fff;
            font-size: 12.5pt; font-weight: 700; }}
.tete-num {{ position: absolute; top: 9.5mm; right: 20mm; color: rgba(255,255,255,.75);
            font-size: 8pt; letter-spacing: .1em; text-transform: uppercase; }}
.pied {{ position: absolute; bottom: 12mm; left: 20mm; right: 20mm;
        display: flex; justify-content: space-between; align-items: center;
        font-size: 7.5pt; color: var(--sub);
        border-top: 1px solid var(--border); padding-top: 3mm; }}

/* --- sommaire ------------------------------------------------------------ */
.so-corps {{ position: absolute; top: 42mm; left: 20mm; right: 20mm; }}
.so-fam {{ margin-bottom: 5.5mm; }}
.so-tete {{ display: flex; align-items: center; gap: 5mm; margin-bottom: 2mm; }}
.so-hex {{ width: 11mm; height: 12.5mm; background: var(--blue); color: #fff;
          display: flex; align-items: center; justify-content: center;
          font-size: 11pt; font-weight: 700; flex: none; }}
.so-nom {{ font-size: 12.5pt; font-weight: 700; }}
.so-page {{ margin-left: auto; font-size: 10pt; color: var(--blue); font-weight: 700; }}
.so-liste {{ margin-left: 17mm; }}
.so-item {{ display: flex; font-size: 9pt; color: #26364d; padding: .7mm 0;
           border-bottom: 1px dotted var(--border); }}
.so-item span:last-child {{ margin-left: auto; color: var(--sub); }}

/* --- page normes --------------------------------------------------------- */
.no-corps {{ position: absolute; top: 44mm; left: 20mm; right: 20mm; }}
.no-corps p {{ font-size: 9.5pt; line-height: 1.6; color: #26364d; margin-bottom: 4mm; }}
table.normes {{ width: 100%; border-collapse: collapse; margin: 6mm 0 4mm; }}
table.normes th {{ background: var(--navy); color: #fff; font-size: 8pt;
                  text-transform: uppercase; letter-spacing: .08em;
                  padding: 3.2mm 3.5mm; text-align: left; }}
table.normes td {{ padding: 3mm 3.5mm; font-size: 9pt; border-bottom: 1px solid var(--border); }}
table.normes tr:nth-child(even) td {{ background: #E6F5F7; }}
table.normes td:first-child {{ font-weight: 700; color: var(--navy); width: 26%; }}
table.normes td:last-child {{ color: var(--sub); width: 30%; }}
.no-note {{ font-size: 8pt; color: var(--sub); line-height: 1.5; font-style: italic; }}
.no-encadre {{ margin-top: 8mm; background: var(--navy); color: #fff;
              padding: 6mm 7mm; font-size: 10.5pt; line-height: 1.5; font-weight: 600; }}
.no-encadre::before {{ content: ""; display: block; width: 22mm; height: 3px;
                      background: var(--teal); margin-bottom: 3.5mm; }}

/* --- page de section ------------------------------------------------------ */
/* La diagonale sépare un haut marine d'un bas blanc. Tout ce qui est au-dessus
   d'elle s'écrit en blanc, tout ce qui est en dessous en marine — les positions
   ci-dessous sont calées sur ses deux bords (195 mm à gauche, 147 mm à droite). */
.se-fond {{ position: absolute; inset: 0; background: var(--navy); }}
.se-diag {{ position: absolute; bottom: 0; left: 0; width: 210mm; height: 150mm;
           background: #fff; clip-path: polygon(0 32%, 100% 0, 100% 100%, 0 100%); }}
.se-motif {{ position: absolute; width: 46mm; height: 52mm; background: rgba(255,255,255,.055); }}
.se-num {{ position: absolute; top: 40mm; left: 20mm; width: 26mm; height: 29mm;
          background: var(--teal); color: #fff; display: flex;
          align-items: center; justify-content: center; font-size: 20pt; font-weight: 700; }}
.se-titre {{ position: absolute; top: 80mm; left: 20mm; right: 24mm; color: #fff;
            font-size: 27pt; font-weight: 700; line-height: 1.12; }}
.se-tag {{ position: absolute; top: 46mm; left: 54mm; color: #fff; font-size: 8pt;
          border: 1px solid rgba(255,255,255,.45); padding: 2mm 4mm;
          text-transform: uppercase; letter-spacing: .1em; }}
.se-texte {{ position: absolute; top: 112mm; left: 20mm; width: 110mm;
            font-size: 10pt; line-height: 1.62; color: rgba(255,255,255,.88); }}
.se-liste {{ position: absolute; top: 202mm; left: 20mm; right: 20mm; }}
.se-item {{ display: flex; align-items: baseline; gap: 4mm; padding: 2.6mm 0;
           border-bottom: 1px solid var(--border); }}
.se-ref {{ font-weight: 700; font-size: 10pt; width: 42mm; }}
.se-desc {{ font-size: 8.5pt; color: var(--sub); flex: 1; }}
.se-pg {{ font-size: 9pt; color: var(--blue); font-weight: 700; }}

/* --- page produit --------------------------------------------------------- */
.pr-tete {{ position: absolute; top: 18mm; left: 20mm; right: 20mm; }}
.pr-nom {{ font-size: 23pt; font-weight: 700; line-height: 1.05; }}
.pr-sous {{ font-size: 10.5pt; color: var(--sub); margin-top: 1.5mm; }}
.pr-ref {{ position: absolute; top: 1mm; right: 0; text-align: right;
          font-size: 7.5pt; color: var(--sub); line-height: 1.5; }}
.pr-badges {{ position: absolute; top: 46mm; left: 20mm; right: 20mm;
             display: flex; gap: 2.5mm; flex-wrap: wrap; }}
.pr-badge {{ background: var(--muted); color: var(--navy); font-size: 7.5pt;
            font-weight: 600; padding: 1.8mm 3.5mm; border-left: 2px solid var(--teal); }}
.pr-photo-zone {{ position: absolute; top: 58mm; left: 20mm; width: 74mm; height: 46mm;
                 background: var(--muted); display: flex;
                 align-items: center; justify-content: center; overflow: hidden; }}
.pr-photo-zone img {{ max-width: 86%; max-height: 86%; object-fit: contain; }}
.pr-courbe {{ position: absolute; top: 110mm; left: 20mm; width: 74mm; }}
.pr-svg {{ width: 74mm; display: block; margin-top: 2mm; }}
.pr-desc {{ position: absolute; top: 58mm; left: 104mm; right: 20mm;
           font-size: 9pt; line-height: 1.55; color: #26364d; }}
.pr-pts {{ position: absolute; top: 136mm; left: 104mm; right: 20mm; }}
.pr-pts-liste {{ margin-top: 3mm; }}
.pr-pt {{ font-size: 8.5pt; color: #26364d; padding-left: 4.5mm; position: relative;
         padding-bottom: 1.6mm; }}
.pr-pt::before {{ content: ""; position: absolute; left: 0; top: 1.4mm;
                 width: 2.4mm; height: 2.7mm; background: var(--teal);
                 clip-path: polygon(25% 0%, 75% 0%, 100% 50%, 75% 100%, 25% 100%, 0% 50%); }}
.pr-specs {{ position: absolute; top: 187mm; left: 20mm; right: 20mm; }}
table.specs {{ width: 100%; border-collapse: collapse; margin-top: 2.5mm; }}
table.specs td {{ padding: 1.25mm 3mm; font-size: 7.5pt; vertical-align: top;
                 border-bottom: 1px solid var(--border); line-height: 1.3; }}
table.specs td:first-child {{ width: 38%; font-weight: 600; color: var(--navy); }}
table.specs td:last-child {{ color: #26364d; }}
table.specs tr:nth-child(even) td {{ background: #E6F5F7; }}

/* --- synthèse ------------------------------------------------------------- */
.sy-corps {{ position: absolute; top: 38mm; left: 15mm; right: 15mm; }}
table.synth {{ width: 100%; border-collapse: collapse; }}
table.synth th {{ background: var(--navy); color: #fff; font-size: 7pt;
                 text-transform: uppercase; letter-spacing: .08em;
                 padding: 2.4mm 3mm; text-align: left; }}
table.synth td {{ padding: 1.55mm 3mm; font-size: 7.5pt; border-bottom: 1px solid var(--border);
                 vertical-align: top; line-height: 1.35; }}
table.synth tr:nth-child(even) td {{ background: #E6F5F7; }}
.sy-fam td {{ background: var(--muted) !important; font-weight: 700;
             font-size: 7.5pt; color: var(--navy);
             text-transform: uppercase; letter-spacing: .08em; }}
.sy-ref {{ font-weight: 700; color: var(--navy); }}

/* --- dos ------------------------------------------------------------------ */
.do-fond {{ position: absolute; inset: 0; background: var(--navy); }}
.do-diag {{ position: absolute; top: 0; right: 0; width: 96mm; height: 297mm;
           background: rgba(255,255,255,.045); clip-path: polygon(42% 0, 100% 0, 100% 100%, 0 100%); }}
.do-hex {{ position: absolute; top: 58mm; right: 26mm; width: 54mm; height: 60mm;
          background: rgba(255,255,255,.05); border: 1px solid rgba(255,255,255,.34); }}
.do-gammes {{ position: absolute; top: 148mm; left: 22mm; width: 104mm; }}
.do-gammes .label {{ color: var(--teal); }}
.do-gamme {{ color: rgba(255,255,255,.9); font-size: 9.5pt; padding: 1.7mm 0;
            border-bottom: 1px solid rgba(255,255,255,.14); display: flex; }}
.do-gamme span {{ margin-left: auto; color: rgba(255,255,255,.5); font-size: 8pt; }}
.do-logo {{ position: absolute; top: 46mm; left: 22mm; width: 56mm; }}
.do-accroche {{ position: absolute; top: 84mm; left: 22mm; color: rgba(255,255,255,.82);
               font-size: 11pt; font-style: italic; }}
.do-texte {{ position: absolute; top: 108mm; left: 22mm; width: 92mm; color: #fff;
            font-size: 10.5pt; line-height: 1.65; }}
.do-filet {{ position: absolute; top: 100mm; left: 22mm; width: 30mm; height: 3px;
            background: var(--teal); }}
.do-coord {{ position: absolute; bottom: 52mm; left: 22mm; color: #fff;
            font-size: 10pt; line-height: 1.85; }}
.do-coord .k {{ color: rgba(255,255,255,.55); display: inline-block; width: 20mm;
               font-size: 7.5pt; text-transform: uppercase; letter-spacing: .1em; }}
.do-mentions {{ position: absolute; bottom: 30mm; left: 22mm; right: 22mm;
               color: rgba(255,255,255,.62); font-size: 7.5pt; line-height: 1.7;
               border-top: 1px solid rgba(255,255,255,.2); padding-top: 4mm; }}
"""


# --------------------------------------------------------------- fabriques ----
def page_couverture(c, img):
    return f"""<section class="page" id="p1">
  <div class="cv-bande"></div><div class="cv-bande2"></div>
  <img class="cv-photo hex-v" src="{img['couverture']}" alt="">
  <img class="cv-logo" src="{img['logo']}" alt="Netair">
  <div class="cv-titre">{e(c['titre'])}</div>
  <div class="cv-sous">{e(c['sous_titre'])}</div>
  <div class="cv-accroche">{e(c['accroche'])}</div>
  <div class="cv-filet"></div>
  <div class="cv-mention">{e(c['mention_bas'])}</div>
</section>"""


def page_edito(c, img):
    return f"""<section class="page" id="p2">
  <img class="ed-photo" src="{img['foret']}" alt="">
  <div class="ed-voile"></div>
  <div class="ed-hex hex-v"></div>
  <img class="ed-logo" src="{img['logo_blanc']}" alt="Netair">
  <div class="ed-corps">
    <div class="label">Présentation</div>
    <h1 class="ed-titre">{e(c['titre'])}</h1>
    {paragraphes(c['texte'])}
  </div>
  <div class="ed-sign">{e(c.get('signature', ''))}</div>
</section>"""


def page_sommaire(sections, pages_fam, pages_prod, produits, num):
    blocs = []
    for i, s in enumerate(sections, 1):
        items = "".join(
            f'<a class="so-item" href="#p{pages_prod[sl]}">'
            f'<span>{e(produits[sl]["nom"])} — '
            f'{e(produits[sl]["soustitre"])}</span><span>{pages_prod[sl]}</span></a>'
            for sl in s["produits"])
        pf = pages_fam[s["slug"]]
        blocs.append(f"""<div class="so-fam">
      <a class="so-tete" href="#p{pf}"><div class="so-hex hex">{i}</div>
        <div class="so-nom">{e(s['titre'])}</div>
        <div class="so-page">p. {pf}</div></a>
      <div class="so-liste">{items}</div></div>""")
    return f"""<section class="page" id="p{num}">
  <div class="tete"></div><div class="tete-txt">Sommaire</div>
  <div class="tete-num">Catalogue produits</div>
  <div class="so-corps">{''.join(blocs)}</div>
  <div class="pied"><span>Netair — Catalogue produits</span><span>{num}</span></div>
</section>"""


def page_normes(c, num):
    lignes = ""
    for ligne in c["tableau"].splitlines():
        if not ligne.strip():
            continue
        cols = [x.strip() for x in ligne.split("|")]
        lignes += "<tr>" + "".join(f"<td>{e(x)}</td>" for x in cols) + "</tr>"
    return f"""<section class="page" id="p{num}">
  <div class="tete"></div><div class="tete-txt">{e(c['titre'])}</div>
  <div class="tete-num">Repères</div>
  <div class="no-corps">
    {paragraphes(c['intro'])}
    <table class="normes"><thead><tr>
      <th>Catégorie</th><th>Particules visées</th><th>Équivalence EN 779</th>
    </tr></thead><tbody>{lignes}</tbody></table>
    <div class="no-note">{e(c['note_tableau'])}</div>
    <div class="no-encadre">{e(c['encadre'])}</div>
  </div>
  <div class="pied"><span>Netair — Catalogue produits</span><span>{num}</span></div>
</section>"""


def page_section(s, i, produits, pages_prod, num):
    items = "".join(
        f'<a class="se-item" href="#p{pages_prod[sl]}">'
        f'<div class="se-ref">{e(produits[sl]["nom"])}</div>'
        f'<div class="se-desc">{e(produits[sl]["soustitre"])}</div>'
        f'<div class="se-pg">p. {pages_prod[sl]}</div></a>'
        for sl in s["produits"])
    tag = f'<div class="se-tag">{e((s["norme"] + " · " if s["norme"] else "") + s["tag"])}</div>' \
        if s["tag"] else ""
    return f"""<section class="page" id="p{num}">
  <div class="se-fond"></div>
  <div class="se-motif hex-v" style="top:-14mm;right:18mm;"></div>
  <div class="se-motif hex-v" style="top:14mm;right:52mm;"></div>
  <div class="se-diag"></div>
  <div class="se-num hex-v">{i}</div>{tag}
  <h1 class="se-titre">{e(s['titre'])}</h1>
  <div class="se-texte">{e(s['texte'])}</div>
  <div class="se-liste">
    <div class="label" style="margin-bottom:2.5mm;">
      {len(s['produits'])} référence{'s' if len(s['produits']) > 1 else ''}</div>
    {items}</div>
  <div class="pied"><span>Netair — {e(s['titre'])}</span><span>{num}</span></div>
</section>"""


def page_produit(p, famille, img, num, courbe):
    badges = "".join(f'<div class="pr-badge">{e(b)}</div>' for b in p["badges"])
    points = "".join(f'<div class="pr-pt">{e(pt)}</div>' for pt in p["points_cles"])
    specs = "".join(f"<tr><td>{e(a)}</td><td>{e(b)}</td></tr>" for a, b in p["specs"])
    bloc_courbe = (f'<div class="pr-courbe"><div class="label">Perte de charge</div>'
                   f'{svg_courbe(courbe)}</div>') if courbe else ""
    return f"""<section class="page" id="p{num}">
  <div class="pr-tete">
    <div class="pr-ref">{e(p['fiche_num'])}<br>{e(p['version'])} · {e(p['date'])}</div>
    <div class="label">{e(famille['titre'])}</div>
    <h1 class="pr-nom">{e(p['nom'])}</h1>
    <div class="pr-sous">{e(p['soustitre'])}</div>
  </div>
  <div class="pr-badges">{badges}</div>
  <div class="pr-photo-zone"><img src="{img}" alt="{e(p['photo_alt'])}"></div>
  {bloc_courbe}
  <div class="pr-desc">{e(p['description'])}</div>
  <div class="pr-pts"><div class="label">Points clés</div>
    <div class="pr-pts-liste">{points}</div></div>
  <div class="pr-specs"><div class="label">Caractéristiques</div>
    <table class="specs">{specs}</table></div>
  <div class="pied"><span>Netair — {e(p['nom'])}</span><span>{num}</span></div>
</section>"""


def page_synthese(sections, produits, pages_prod, num):
    lignes = ""
    for s in sections:
        lignes += f'<tr class="sy-fam"><td colspan="4">{e(s["titre"])}</td></tr>'
        for sl in s["produits"]:
            p = produits[sl]
            lignes += (f'<tr><td class="sy-ref">'
                       f'<a href="#p{pages_prod[sl]}">{e(p["nom"])}</a></td>'
                       f'<td>{e(p["soustitre"])}</td>'
                       f'<td>{e(p["efficacite"])}</td>'
                       f'<td><a href="#p{pages_prod[sl]}">{pages_prod[sl]}</a></td></tr>')
    return f"""<section class="page" id="p{num}">
  <div class="tete"></div><div class="tete-txt">Synthèse de la gamme</div>
  <div class="tete-num">{len(produits)} références</div>
  <div class="sy-corps">
    <table class="synth"><thead><tr>
      <th style="width:26%">Référence</th><th style="width:32%">Type</th>
      <th style="width:34%">Efficacité</th><th style="width:8%">Page</th>
    </tr></thead><tbody>{lignes}</tbody></table>
  </div>
  <div class="pied"><span>Netair — Catalogue produits</span><span>{num}</span></div>
</section>"""


def page_dos(c, img, sections, num):
    coord = ""
    for cle, libelle in (("adresse", "Adresse"), ("email", "Email"), ("site", "Web")):
        if c.get(cle):
            coord += f'<div><span class="k">{libelle}</span>{e(c[cle])}</div>'
    # Les gammes du dos sont lues, pas recopiées : renommer une famille sur le site
    # la renomme ici à la régénération suivante.
    gammes = "".join(
        f'<div class="do-gamme">{e(s["titre"])}'
        f'<span>{len(s["produits"])} réf.</span></div>' for s in sections)
    return f"""<section class="page" id="p{num}">
  <div class="do-fond"></div><div class="do-diag"></div>
  <div class="do-hex hex-v"></div>
  <img class="do-logo" src="{img['logo_blanc']}" alt="Netair">
  <div class="do-accroche">{e(c['accroche'])}</div>
  <div class="do-filet"></div>
  <div class="do-texte">{e(c['texte']).replace(chr(10), '<br>')}</div>
  <div class="do-gammes"><div class="label">Nos gammes</div>{gammes}</div>
  <div class="do-coord">{coord}</div>
  <div class="do-mentions">{e(c['mentions'])}<br>{e(c['pied'])}</div>
</section>"""


# ------------------------------------------------------------------ montage ---
# Limites mesurées sur le gabarit de page produit (17/08/2026) : au-delà, le bloc
# déborde sur le suivant. Le plus long descriptif de la gamme, NETCARB AZUR, tient
# à 752 caractères — la marge est mince, et les NETCARB doivent encore être réécrits.
LIMITES = {"description": 760, "points_cles": 6, "specs": 14}


def controler_tenue(produits):
    """Prévient si un produit risque de déborder de sa page, plutôt que de sortir
    un PDF abîmé sans rien dire."""
    alertes = []
    for p in produits.values():
        if len(p["description"]) > LIMITES["description"]:
            alertes.append(f"{p['nom']} : descriptif de {len(p['description'])} "
                           f"caractères (max ≈ {LIMITES['description']})")
        if len(p["points_cles"]) > LIMITES["points_cles"]:
            alertes.append(f"{p['nom']} : {len(p['points_cles'])} points clés "
                           f"(max {LIMITES['points_cles']})")
        if len(p["specs"]) > LIMITES["specs"]:
            alertes.append(f"{p['nom']} : {len(p['specs'])} caractéristiques "
                           f"(max {LIMITES['specs']})")
    return alertes


def substituer(texte, valeurs):
    for cle, val in valeurs.items():
        texte = texte.replace("{" + cle + "}", str(val))
    return texte


def construire():
    slugs = lecture_produits.slugs_disponibles()
    produits = {s: lecture_produits.lire(s) for s in slugs}
    sections = lecture_familles.plan_du_catalogue(slugs)
    contenu = lire_contenu()

    aujourd_hui = date.today()
    valeurs = {
        "nb_produits": len(slugs),
        "nb_familles": len(sections),
        "date_edition": f"{aujourd_hui.day} {MOIS[aujourd_hui.month - 1]} {aujourd_hui.year}",
    }
    for bloc in contenu.values():
        for k in bloc:
            bloc[k] = substituer(bloc[k], valeurs)

    # Pagination : couverture, édito, sommaire, normes, puis (section + produits),
    # puis synthèse et dos. On la calcule d'abord pour que le sommaire soit juste.
    n, pages_fam, pages_prod = 5, {}, {}
    for s in sections:
        pages_fam[s["slug"]] = n
        n += 1
        for sl in s["produits"]:
            pages_prod[sl] = n
            n += 1
    page_synth, page_dos_num = n, n + 1

    img = {
        "logo": image_data_uri(os.path.join(ASSETS, "netair-logo.png"), 900),
        "logo_blanc": image_data_uri(os.path.join(ASSETS, "netair-logo-blanc.png"), 900),
        "couverture": image_data_uri(os.path.join(ASSETS, "couverture-montagne.jpg"), 1500),
        "foret": image_data_uri(os.path.join(ASSETS, "ambiance-foret.jpg"), 1300),
    }

    corps = [page_couverture(contenu["COUVERTURE"], img),
             page_edito(contenu["EDITO"], img),
             page_sommaire(sections, pages_fam, pages_prod, produits, 3),
             page_normes(contenu["NORMES"], 4)]
    for i, s in enumerate(sections, 1):
        corps.append(page_section(s, i, produits, pages_prod, pages_fam[s["slug"]]))
        for sl in s["produits"]:
            corps.append(page_produit(produits[sl], s,
                                      image_data_uri(produits[sl]["photo"], 1100),
                                      pages_prod[sl], lecture_courbes.lire_courbes(sl)))
    corps.append(page_synthese(sections, produits, pages_prod, page_synth))
    corps.append(page_dos(contenu["DOS"], img, sections, page_dos_num))

    html_doc = f"""<!DOCTYPE html>
<html lang="fr"><head><meta charset="utf-8">
<title>Netair — Catalogue produits</title>
<style>{feuille_de_style()}</style>
</head><body>
{''.join(corps)}
</body></html>"""

    with open(SORTIE_HTML, "w", encoding="utf-8") as f:
        f.write(html_doc)
    return len(corps), page_dos_num, len(slugs), len(sections), controler_tenue(produits)


def imprimer_pdf():
    """Impression PDF par Chrome — même moteur que l'aperçu, donc même rendu."""
    if not os.path.exists(CHROME):
        print("⚠️  Google Chrome introuvable : PDF non produit (le HTML, lui, est à jour).")
        return False
    ancien = os.path.getmtime(SORTIE_PDF) if os.path.exists(SORTIE_PDF) else 0
    r = subprocess.run(
        [CHROME, "--headless=new", "--disable-gpu", "--no-pdf-header-footer",
         "--virtual-time-budget=20000",
         f"--print-to-pdf={SORTIE_PDF}", f"file://{SORTIE_HTML}"],
        capture_output=True, text=True)
    if not os.path.exists(SORTIE_PDF) or os.path.getmtime(SORTIE_PDF) <= ancien:
        print("❌ Chrome n'a pas produit le PDF.\n" + (r.stderr or "")[-600:])
        return False
    return True


def main():
    nb_pages, dernier, nb_prod, nb_fam, alertes = construire()
    print(f"📘 Catalogue_Netair.html — {nb_pages} pages "
          f"({nb_prod} produits, {nb_fam} familles)")
    if imprimer_pdf():
        taille = os.path.getsize(SORTIE_PDF) / 1_048_576
        print(f"📄 Catalogue_Netair.pdf — {taille:.1f} Mo")
    for a in alertes:
        print(f"⚠️  {a} — vérifier la page produit, le bloc peut déborder.")
    if nb_pages != dernier:
        print(f"⚠️  incohérence de pagination : {nb_pages} pages rendues, "
              f"numérotation jusqu'à {dernier}.")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
