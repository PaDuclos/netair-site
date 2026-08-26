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
    """Courbe débit / perte de charge, pleine largeur, légende en colonne à droite.

    Dessinée en SVG : aucune dépendance, et le tracé reste net à l'impression quel
    que soit l'agrandissement. Le cadre est calé sur la page, pas sur le nombre de
    courbes — un graphique élastique viendrait heurter le tableau en dessous.
    """
    if not c:
        return ""
    # Repère en unités de viewBox : 680 unités = 170 mm, soit 1 unité = 0,25 mm.
    X0, X1, Y0, Y1 = 56, 452, 18, 222
    LEG = 474                                   # abscisse de la colonne légende
    qmax, pmax = c["debit_max"], c["pmax"]
    n = len(c["courbes"])

    def px(q):
        return X0 + (q / qmax) * (X1 - X0)

    def py(p):
        return Y1 - (p / pmax) * (Y1 - Y0)

    pas_q, pas_p = _pas_joli(qmax, 5), _pas_joli(pmax, 5)
    grille, graduations = [], []
    k = pas_q
    while k <= qmax + 1e-6:
        grille.append(f'<line x1="{px(k):.1f}" y1="{Y0}" x2="{px(k):.1f}" y2="{Y1}"/>')
        graduations.append(f'<text x="{px(k):.1f}" y="{Y1 + 17}" text-anchor="middle" '
                           f'class="g">{k:,.0f}</text>'.replace(",", " "))
        k += pas_q
    k = pas_p
    while k <= pmax + 1e-6:
        grille.append(f'<line x1="{X0}" y1="{py(k):.1f}" x2="{X1}" y2="{py(k):.1f}"/>')
        graduations.append(f'<text x="{X0 - 8}" y="{py(k) + 4.5:.1f}" text-anchor="end" '
                           f'class="g">{k:,.0f}</text>'.replace(",", " "))
        k += pas_p

    # Légende : deux lignes par entrée quand les courbes sont peu nombreuses (la
    # place ne manque pas, et des étiquettes comme « F9 + charbon actif · 520 mm »
    # ne tiennent pas sur une ligne) ; une seule ligne, resserrée, au-delà.
    LARG_LEG = 676 - (LEG + 27)
    deux_lignes = n <= 4
    if deux_lignes:
        pas_leg, taille = 34, 13
    else:
        pas_leg = 20 if n <= 9 else 18
        # Largeur approchée d'une capitale Helvetica : ~0,52 × le corps. On réduit
        # le corps juste ce qu'il faut pour que l'étiquette la plus longue passe.
        long_max = max(len(k["classe"]) + len(k["epaisseur"]) + 3 for k in c["courbes"])
        long_val = max(len(f"{k['dp_nom']:.0f} Pa") for k in c["courbes"])
        taille = max(8.5, min(13, (LARG_LEG - 6) / (0.52 * (long_max + long_val))))
    depart = Y0 + 8

    traces, legende = [], []
    for i, courbe in enumerate(c["courbes"]):
        pts = " ".join(f"{px(q):.1f},{py(p):.1f}" for q, p in courbe["points"])
        traces.append(f'<polyline points="{pts}" fill="none" '
                      f'stroke="{courbe["couleur"]}" stroke-width="2.6" '
                      f'stroke-linejoin="round" stroke-linecap="round"/>')
        y = depart + i * pas_leg
        trait = (f'<line x1="{LEG}" y1="{y}" x2="{LEG + 20}" y2="{y}" '
                 f'stroke="{courbe["couleur"]}" stroke-width="2.6"/>')
        if deux_lignes:
            detail = courbe["epaisseur"]
            if detail:
                detail += "  —  "
            legende.append(
                trait
                + f'<text x="{LEG + 27}" y="{y + 4}" class="l">'
                  f'{e(courbe["classe"])}</text>'
                + f'<text x="{LEG + 27}" y="{y + 19}" class="v">'
                  f'{e(detail)}{courbe["dp_nom"]:.0f} Pa</text>')
        else:
            etiquette = courbe["classe"]
            if courbe["epaisseur"]:
                etiquette += " · " + courbe["epaisseur"]
            legende.append(
                trait
                + f'<text x="{LEG + 27}" y="{y + 4}" class="l" '
                  f'style="font-size:{taille:.1f}px">{e(etiquette)}</text>'
                + f'<text x="676" y="{y + 4}" class="v" text-anchor="end" '
                  f'style="font-size:{taille:.1f}px">{courbe["dp_nom"]:.0f} Pa</text>')

    nominal = ""
    if c["debit_nom"]:
        x = px(c["debit_nom"])
        # Étiquette retenue dans le cadre : centrée telle quelle, elle en sortait
        # quand le débit nominal est proche du bord.
        xl = min(max(x, X0 + 44), X1 - 44)
        nominal = (f'<line x1="{x:.1f}" y1="{Y0}" x2="{x:.1f}" y2="{Y1}" '
                   f'stroke="{TEAL}" stroke-width="1.2" stroke-dasharray="4 3" opacity=".8"/>'
                   f'<text x="{xl:.1f}" y="{Y0 - 5}" text-anchor="middle" class="n">'
                   f'{c["debit_nom"]:,.0f} m³/h nominal</text>'.replace(",", " "))
        for courbe in c["courbes"]:
            nominal += (f'<circle cx="{x:.1f}" cy="{py(courbe["dp_nom"]):.1f}" r="3.4" '
                        f'fill="{courbe["couleur"]}"/>')

    return f"""<svg class="pr-svg" viewBox="0 0 680 268" role="img"
     aria-label="Courbe débit / perte de charge">
  <style>
    .g{{font:13px Helvetica,Arial,sans-serif;fill:#4A5E7A}}
    .l{{font:13px Helvetica,Arial,sans-serif;fill:#0F3261;font-weight:600}}
    .v{{font:13px Helvetica,Arial,sans-serif;fill:#4A5E7A}}
    .n{{font:12px Helvetica,Arial,sans-serif;fill:{TEAL};font-weight:600}}
    .t{{font:12.5px Helvetica,Arial,sans-serif;fill:#4A5E7A}}
  </style>
  <g stroke="#E2E8F0" stroke-width="1">{''.join(grille)}</g>
  <line x1="{X0}" y1="{Y1}" x2="{X1}" y2="{Y1}" stroke="#94A3B8" stroke-width="1.4"/>
  <line x1="{X0}" y1="{Y0}" x2="{X0}" y2="{Y1}" stroke="#94A3B8" stroke-width="1.4"/>
  {''.join(graduations)}
  <text x="{X1}" y="{Y1 + 36}" text-anchor="end" class="t">Débit (m³/h)</text>
  <text x="20" y="{(Y0 + Y1) / 2}" class="t"
        transform="rotate(-90 20 {(Y0 + Y1) / 2})" text-anchor="middle">ΔP (Pa)</text>
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
.pr-photo-zone {{ position: absolute; top: 57mm; left: 20mm; width: 56mm; height: 56mm;
                 background: #fff; border: 1px solid var(--border); display: flex;
                 align-items: center; justify-content: center; overflow: hidden; }}
/* Fond BLANC, jamais gris : la moitié des photos ont elles-mêmes un fond blanc, et
   sur un fond de carte gris elles dessinaient un rectangle blanc bien visible. */
.pr-photo-zone img {{ max-width: 88%; max-height: 88%; object-fit: contain; }}
.pr-desc {{ position: absolute; top: 57mm; left: 82mm; right: 20mm;
           font-size: 8.8pt; line-height: 1.5; color: #26364d; }}
.pr-pts {{ position: absolute; top: 119mm; left: 20mm; right: 20mm; }}
.pr-pts-liste {{ display: flex; flex-wrap: wrap; gap: 1.6mm 4mm; margin-top: 2.5mm; }}
.pr-pt {{ font-size: 8.5pt; color: #26364d; padding-left: 4.5mm; position: relative;
         width: calc(33.33% - 2.7mm); }}
.pr-pt::before {{ content: ""; position: absolute; left: 0; top: 1.4mm;
                 width: 2.4mm; height: 2.7mm; background: var(--teal);
                 clip-path: polygon(25% 0%, 75% 0%, 100% 50%, 75% 100%, 25% 100%, 0% 50%); }}
.pr-courbe {{ position: absolute; top: 140mm; left: 20mm; right: 20mm; }}
.pr-svg {{ width: 170mm; display: block; margin-top: 2mm; }}
.pr-specs {{ position: absolute; top: 216mm; left: 20mm; right: 20mm; }}
.pr-specs-cols {{ display: flex; gap: 6mm; margin-top: 2.5mm; }}
table.specs {{ width: 100%; border-collapse: collapse; }}
table.specs td {{ padding: 1.2mm 2.5mm; font-size: 7pt; vertical-align: top;
                 border-bottom: 1px solid var(--border); line-height: 1.3; }}
table.specs td:first-child {{ width: 44%; font-weight: 600; color: var(--navy); }}
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

    # Caractéristiques sur deux colonnes : en une seule, le tableau ne laissait
    # pas la place d'un graphique lisible. La coupe se fait sur la HAUTEUR estimée
    # et non sur le nombre de lignes — quelques valeurs longues tiennent sur deux
    # ou trois lignes et déséquilibreraient un partage à la moitié.
    hauteurs = [1 + max(len(a), 0) // 26 + len(b) // 42 for a, b in p["specs"]]
    total, cumul, coupe = sum(hauteurs), 0, len(p["specs"])
    for i, h in enumerate(hauteurs):
        if cumul + h > total / 2:
            coupe = i if cumul >= total / 2 - h / 2 else i + 1
            break
        cumul += h
    coupe = max(1, min(coupe, len(p["specs"]) - 1))
    colonnes = "".join(
        "<table class=\"specs\">" + "".join(
            f"<tr><td>{e(a)}</td><td>{e(b)}</td></tr>" for a, b in bloc)
        + "</table>"
        for bloc in (p["specs"][:coupe], p["specs"][coupe:]) if bloc)

    bloc_courbe = (f'<div class="pr-courbe"><div class="label">'
                   f'Perte de charge — toutes classes</div>'
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
  <div class="pr-desc">{e(p['description'])}</div>
  <div class="pr-pts"><div class="label">Points clés</div>
    <div class="pr-pts-liste">{points}</div></div>
  {bloc_courbe}
  <div class="pr-specs"><div class="label">Caractéristiques</div>
    <div class="pr-specs-cols">{colonnes}</div></div>
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
# Limites mesurées sur le gabarit de page produit : au-delà, le bloc déborde sur
# le suivant. Relevées après le passage au grand graphique et aux caractéristiques
# sur deux colonnes (17/08/2026). Le plus long descriptif de la gamme, NETCARB
# AZUR, tient à 752 caractères — la marge est mince, et les NETCARB doivent encore
# être réécrits.
LIMITES = {"description": 760, "points_cles": 9, "specs": 18}


def controler_tenue(produits, courbes=None):
    """Prévient si un produit risque de déborder de sa page, plutôt que de sortir
    un PDF abîmé sans rien dire."""
    alertes = []
    for p in produits.values():
        if len(p["description"]) > LIMITES["description"]:
            alertes.append(f"{p['nom']} : descriptif de {len(p['description'])} "
                           f"caractères (max ≈ {LIMITES['description']}) — le bloc "
                           f"peut déborder, vérifier la page produit")
        if len(p["points_cles"]) > LIMITES["points_cles"]:
            alertes.append(f"{p['nom']} : {len(p['points_cles'])} points clés "
                           f"(max {LIMITES['points_cles']}) — le bloc peut déborder")
        if len(p["specs"]) > LIMITES["specs"]:
            alertes.append(f"{p['nom']} : {len(p['specs'])} caractéristiques "
                           f"(max {LIMITES['specs']}) — le bloc peut déborder")
    for slug, c in (courbes or {}).items():
        for etiquette in (c or {}).get("conflits", []):
            alertes.append(
                f"{produits[slug]['nom']} : deux courbes différentes portaient la "
                f"même étiquette « {etiquette} » — la donnée source déclare une "
                f"épaisseur unique pour deux polynômes distincts")
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

    courbes = {sl: lecture_courbes.lire_courbes(sl) for sl in slugs}
    corps = [page_couverture(contenu["COUVERTURE"], img),
             page_edito(contenu["EDITO"], img),
             page_sommaire(sections, pages_fam, pages_prod, produits, 3),
             page_normes(contenu["NORMES"], 4)]
    for i, s in enumerate(sections, 1):
        corps.append(page_section(s, i, produits, pages_prod, pages_fam[s["slug"]]))
        for sl in s["produits"]:
            corps.append(page_produit(produits[sl], s,
                                      image_data_uri(produits[sl]["photo"], 620),
                                      pages_prod[sl], courbes[sl]))
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
    return (len(corps), page_dos_num, len(slugs), len(sections),
            controler_tenue(produits, courbes))


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
        print(f"⚠️  {a}")
    if nb_pages != dernier:
        print(f"⚠️  incohérence de pagination : {nb_pages} pages rendues, "
              f"numérotation jusqu'à {dernier}.")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
