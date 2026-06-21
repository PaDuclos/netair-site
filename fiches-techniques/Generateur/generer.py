#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Générateur de fiches techniques Netair — "génération par données".

Principe : on part du GABARIT NETPLY validé (gabarit_base.html) — jamais retapé —
et on ne remplace QUE les zones variables décrites dans le README de handoff
(zones #1 à #10). Le style et toute la logique JS (calculateur, courbe, survol)
restent strictement identiques au caractère près.

Usage :
    python3 generer.py produits/netxxx.json
    python3 generer.py produits/netxxx.json --out "Fiche technique NETXXX.html"

Le .json décrit un produit (voir produits/netply.json comme modèle de référence).
Test d'identité : régénérer netply.json doit reproduire gabarit_base.html à l'octet près.
"""

import json
import re
import sys
import os
import shutil
from decimal import Decimal, ROUND_HALF_UP

ROOT = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.join(ROOT, "gabarit_base.html")


# ---------------------------------------------------------------- helpers ----
def fr_surface(L, H, facteur=2):
    """Surface filtrante = facteur × (L × H) en m², format français '0,70'.
    facteur=2 pour les plissés (NETPLY), facteur=1 pour les filtres plans (frontale)."""
    val = Decimal(facteur * L * H) / Decimal(1_000_000)
    val = val.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    return f"{val}".replace(".", ",")


def fr_debit(n):
    """Débit avec séparateur de milliers insécable : 3400 -> '3&nbsp;400'."""
    return f"{n:,}".replace(",", "&nbsp;")


def sub1(html, pattern, repl, flags=0):
    """Remplacement unique avec garde-fou (lève si l'ancre est introuvable)."""
    new, n = re.subn(pattern, repl, html, count=1, flags=flags)
    if n == 0:
        raise RuntimeError(f"Ancre introuvable : {pattern[:70]}…")
    return new


def lit(s):
    """Échappe les antislash/backref pour une chaîne de remplacement re.sub."""
    return s.replace("\\", "\\\\")


# --------------------------------------------------------- fragments HTML ----
def build_points_cles(points):
    SPAN = ('<span style="width:8px; height:8px; background:#0897A5; '
            'display:inline-block; flex:none;"></span>')
    rows = []
    for p in points:
        rows.append(
            f'<div style="display:flex; align-items:center; gap:8px;">{SPAN}{p}</div>'
        )
    return "\n".join("              " + r for r in rows)


def build_specs(specs):
    rows = []
    for i, (k, v) in enumerate(specs, start=1):
        grey = (i % 2 == 1)  # première ligne grise, puis alternance
        tr = ' style="background:#F2F6FB;"' if grey else ""
        kstyle = "padding:6px 12px; font-weight:700; color:#0F3261;"
        if i == 1:
            kstyle = "padding:6px 12px; font-weight:700; color:#0F3261; width:40%;"
        rows.append(
            f'<tr{tr}><td style="{kstyle}">{k}</td>'
            f'<td style="padding:6px 12px; color:#3a4654;">{v}</td></tr>'
        )
    return "\n".join("              " + r for r in rows)


def build_dimensions(d):
    nom = d["nom"]
    low, high = d["classes"]["low"], d["classes"]["high"]
    mono = d.get("mono_classe", False)
    facteur = d.get("surface_facteur", 2)
    rows = []
    i = 0  # index global (striping continu sur toutes les lignes de données)

    def emit(dim, cls):
        nonlocal i
        i += 1
        grey = (i % 2 == 0)  # ligne 1 blanche, ligne 2 grise, …
        tr = ' style="background:#F2F6FB;"' if grey else ""
        L, H, P = dim["L"], dim["H"], dim["P"]
        surface = fr_surface(L, H, facteur)
        debit = fr_debit(dim["debit"])
        eff = f'{cls["iso"]} ({cls["label"]})'
        ref = f'{nom}-{cls["iso"]}-{cls["label"]}-{L}x{H}x{P}'
        c = "padding:4px 7px;"
        cref = ("padding:4px 7px; font-family:'IBM Plex Mono',monospace; "
                "color:#0F3261;")
        rows.append(
            f'<tr{tr}>'
            f'<td style="{c}">{L}</td>'
            f'<td style="{c}">{H}</td>'
            f'<td style="{c}">{P}</td>'
            f'<td style="{c}">{surface}</td>'
            f'<td style="{c}">{debit}</td>'
            f'<td style="{c}">{cls["dp"]}</td>'
            f'<td style="{c}">{eff}</td>'
            f'<td style="{cref}">{ref}</td>'
            f'</tr>'
        )

    for dim in d["dimensions"]:      # toutes les lignes classe basse…
        emit(dim, low)
    if not mono:                     # …puis classe haute (sauf fiche mono-classe)
        for dim in d["dimensions"]:
            emit(dim, high)

    rows.append(
        '<tr style="background:#E6F5F7;">'
        '<td style="padding:4px 7px; font-weight:700; color:#0F3261;" '
        'colspan="7">Sur mesure</td>'
        '<td style="padding:4px 7px; color:#5A6573; font-style:italic;">'
        'sur demande — délai à confirmer</td></tr>'
    )
    return "\n".join("              " + r for r in rows)


def _co(co):
    """Formate un jeu de coefficients {a,b,c} comme dans le gabarit."""
    return f"{{ a: {co['a']}, b: {co['b']}, c: {co['c']} }}"


AREF = 0.592 * 0.592   # surface frontale de référence (m²)


def _frnum(x):
    """Nombre format français : 2 -> '2', 1.5 -> '1,5', 0.5 -> '0,5'."""
    return f"{x:g}".replace(".", ",")


def _mapx(v, vmax):
    return 52 + (v / vmax) * 528


def build_gridlines(vmax, vnom):
    """Graduations verticales (0,5 / 1 / …) + ligne pointillée du point nominal."""
    out, v = [], 0.5
    while v < vmax - 1e-9:
        x = f"{_mapx(v, vmax):.1f}"
        out.append(f'<line x1="{x}" y1="16" x2="{x}" y2="250" stroke="#EDF1F6" stroke-width="1"></line>')
        v += 0.5
    xn = f"{_mapx(vnom, vmax):.1f}"
    out.append(f'<line x1="{xn}" y1="16" x2="{xn}" y2="250" stroke="#0F3261" '
               f'stroke-width="1" stroke-dasharray="2 3" opacity="0.4"></line>')
    return "\n".join("            " + l for l in out)


def build_xlabels(vmax):
    """Étiquettes de l'axe vitesse : 0, 0,5, … (centrées) puis Vmax (aligné à droite)."""
    out, v = [], 0.0
    base = ('font-family="\'IBM Plex Mono\',monospace" font-size="11" fill="#5A6573"')
    while v < vmax - 1e-9:
        x = "52" if v == 0 else f"{_mapx(v, vmax):.1f}"
        out.append(f'<text x="{x}" y="265" text-anchor="middle" {base}>{_frnum(v)}</text>')
        v += 0.5
    out.append(f'<text x="580" y="265" text-anchor="end" {base}>{_frnum(vmax)}</text>')
    return "\n".join("            " + l for l in out)


def build_poly_block(low, high):
    """Bloc de constantes JS — polynômes ΔP = a·v² + b·v + c. Espacement exact du gabarit."""
    return (
        "  var POLY = {\n"
        f"    g4: {{ 48: {_co(low['poly']['48'])}, 98: {_co(low['poly']['98'])} }},   // {low['label']} · {low['iso']}\n"
        f"    m5: {{ 48: {_co(high['poly']['48'])}, 98: {_co(high['poly']['98'])} }}    // {high['label']} · {high['iso']}\n"
        "  };\n"
        f"  var ADD  = {{ g4: {low['add']},   m5: {high['add']} }};           // EN 13053 : +50 Pa (Coarse) / +100 Pa (ePM)\n"
        f"  var RULE = {{ g4: '{low['rule']}', m5: '{high['rule']}' }};"
    )


# ----------------------------------------------------------------- moteur ----
def generer(d, html):
    nom = d["nom"]
    slug = d["slug"]
    low, high = d["classes"]["low"], d["classes"]["high"]

    # --- #1 nom produit : title, thumbnail, en-tête P1 (40px), en-tête P2 (22px)
    html = html.replace("<title>Fiche technique NETPLY — Netair</title>",
                        f"<title>Fiche technique {nom} — Netair</title>")
    html = html.replace('letter-spacing="2">NETPLY</text>',
                        f'letter-spacing="2">{nom}</text>')
    html = html.replace('letter-spacing:-.6px; text-align:center;">NETPLY</div>',
                        f'letter-spacing:-.6px; text-align:center;">{nom}</div>')
    html = html.replace('letter-spacing:-.3px;">NETPLY</div>',
                        f'letter-spacing:-.3px;">{nom}</div>')

    # --- #2 sous-titre
    html = html.replace(">Filtre plissé — Préfiltre synthétique</div>",
                        f">{d['soustitre']}</div>")

    # --- #3 badges normes (P1 ×3 puis P2 ×3)
    b1 = d["badges_p1"]
    b2 = d["badges_p2"]
    html = html.replace(">ISO 16890 : Coarse 65% / ePM10 50%</div>", f">{b1[0]}</div>")
    html = html.replace(">EN 779 : G4 / M5</div>", f">{b1[1]}</div>")
    html = html.replace('border:1.5px solid #C9D7E8;">EN 13053</div>',
                        f'border:1.5px solid #C9D7E8;">{b1[2]}</div>')
    html = html.replace(">ISO 16890 : Coarse 65% → ePM10 50%</div>", f">{b2[0]}</div>")
    html = html.replace(">EN 779 : G4 → M5</div>", f">{b2[1]}</div>")
    html = html.replace('border:1.5px solid #C9D7E8; white-space:nowrap;">EN 13053</div>',
                        f'border:1.5px solid #C9D7E8; white-space:nowrap;">{b2[2]}</div>')

    # --- #4 photo (src + alt) puis identifiants d'éléments (slug)
    html = html.replace('src="assets/netply-photo.jpg" alt="Filtre NETPLY"',
                        f'src="assets/{d["photo"]}" alt="{d["photo_alt"]}"')
    for tok in ("netply-photo", "netply-img", "netply-ph", "netply-file"):
        html = re.sub(r"\b" + tok + r"\b", f"{slug}-" + tok.split("-", 1)[1], html)

    # --- #5 description
    html = sub1(html, r"(text-wrap:pretty;\">)(.*?)(</p>)",
                lambda m: m.group(1) + d["description"] + m.group(3), flags=re.DOTALL)

    # --- #6 points clés
    html = sub1(html, r"(color:#27313e;\">\n)(.*?)(\n            </div>)",
                lambda m: m.group(1) + build_points_cles(d["points_cles"]) + m.group(3),
                flags=re.DOTALL)

    # --- #7 caractéristiques techniques
    html = sub1(
        html,
        r"(<!-- Caractéristiques techniques -->.*?<tbody>\n)(.*?)(\n            </tbody>)",
        lambda m: m.group(1) + build_specs(d["specs"]) + m.group(3),
        flags=re.DOTALL)

    # --- #8 dimensions & références
    no_dim = d.get("no_dimensions", False)
    if no_dim:
        # produit sans dimensions standard : on retire tout le bloc (titre + table + note)
        html = sub1(
            html,
            r"\n        <!-- Dimensions -->\n        <div style=\"margin-top:8mm;\">.*?\n        </div>",
            lambda m: "",
            flags=re.DOTALL)
    else:
        html = sub1(
            html,
            r"(<!-- Dimensions -->.*?<tbody>\n)(.*?)(\n            </tbody>)",
            lambda m: m.group(1) + build_dimensions(d) + m.group(3),
            flags=re.DOTALL)

    # --- #9 pied de page (n°, version, date — P1 et P2)
    html = html.replace("Fiche n° FT-NETPLY-001", f"Fiche n° {d['fiche']['num']}")
    vd = f"{d['fiche']['version']} — {d['fiche']['date']}"
    html = html.replace("v1.0 — 20/06/2026 — Page 1/2", f"{vd} — Page 1/2")
    html = html.replace("v1.0 — 20/06/2026 — Page 2/2", f"{vd} — Page 2/2")

    # --- #10a libellés courbe/calculateur (cases, légende, boutons)
    lab_low = f'{low["label"]} · {low["iso"]}'
    lab_high = f'{high["label"]} · {high["iso"]}'
    html = sub1(html, r'(id="cbG4"[^>]*>\s*).*?(\s*</label>)',
                lambda m: m.group(1) + lab_low + m.group(2), flags=re.DOTALL)
    html = sub1(html, r'(id="cbM5"[^>]*>\s*).*?(\s*</label>)',
                lambda m: m.group(1) + lab_high + m.group(2), flags=re.DOTALL)
    mono = d.get("mono_classe", False)
    ep = low.get("epaisseur")
    leg_low_a = f"{lab_low} — {_frnum(ep)} mm" if mono else f"{lab_low} — 48 mm"
    for eid, txt in (("legG4a", leg_low_a), ("legG4b", f"{lab_low} — 98 mm"),
                     ("legM5a", f"{lab_high} — 48 mm"), ("legM5b", f"{lab_high} — 98 mm")):
        html = sub1(html, r'(id="' + eid + r'"[^>]*>.*?</span>)(.*?)(</div>)',
                    lambda m, t=txt: m.group(1) + t + m.group(3), flags=re.DOTALL)
    html = sub1(html, r'(id="btnEffG4"[^>]*>)([^<]*)(</button>)',
                lambda m: m.group(1) + f'{low["iso"]} ({low["label"]})' + m.group(3))
    html = sub1(html, r'(id="btnEffM5"[^>]*>)([^<]*)(</button>)',
                lambda m: m.group(1) + f'{high["iso"]} ({high["label"]})' + m.group(3))

    # --- #10b constantes JS (POLY / ADD / RULE)
    html = sub1(html, r"  var POLY = \{.*?var RULE = \{[^\n]*\};",
                lambda m: build_poly_block(low, high), flags=re.DOTALL)

    # --- plage de vitesse / débit nominal (optionnel ; NETPLY garde les défauts du gabarit)
    if "vmax" in d:
        vmax = d["vmax"]
        dnom = d.get("debit_nom", 3400)
        vnom = (dnom / 3600) / AREF
        # constantes JS
        html = html.replace("var Vmax = 3.17;", f"var Vmax = {vmax};")
        html = html.replace("var Vnom = (3400 / 3600) / Aref;",
                            f"var Vnom = ({dnom} / 3600) / Aref;")
        html = html.replace("fr(v / Vnom * 3400)", f"fr(v / Vnom * {dnom})")
        # débit par défaut du calculateur
        html = html.replace('id="inDebit" min="500" max="6000" step="50" value="3400"',
                            f'id="inDebit" min="500" max="6000" step="50" value="{dnom}"')
        html = html.replace("debit: 3400,", f"debit: {dnom},")
        # axe X : graduations, point nominal, étiquettes, annotation
        html = sub1(html, r"(<!-- vertical gridlines -->\n)(.*?)(\n            <!-- 4 courbes)",
                    lambda m: m.group(1) + build_gridlines(vmax, vnom) + m.group(3), flags=re.DOTALL)
        html = sub1(html, r"(<!-- x tick labels -->\n)(.*?)(\n            <!-- axis titles)",
                    lambda m: m.group(1) + build_xlabels(vmax) + m.group(3), flags=re.DOTALL)
        annot = f"{vnom:.1f}".replace(".", ",") + f" m/s ≈ {dnom} m³/h · 592×592"
        xn = f"{_mapx(vnom, vmax):.1f}"
        html = sub1(html, r'(<text x=")[\d.]+(" y="11"[^>]*>)[^<]*(</text>)',
                    lambda m: m.group(1) + xn + m.group(2) + annot + m.group(3))

    # --- échelle de l'axe Y / perte de charge (optionnel ; NETPLY garde 120 Pa)
    if "pmax" in d:
        pmax = d["pmax"]
        # mapY : borne haute de l'axe (250 px = 0 Pa, 16 px = pmax)
        html = html.replace("return 250 - (Math.min(p, 120) / 120) * 234;",
                            f"return 250 - (Math.min(p, {pmax}) / {pmax}) * 234;")
        # 5 graduations Y (x="46") : 0, pmax/4, pmax/2, 3·pmax/4, pmax
        yticks = (("254", 0), ("195.5", 1), ("137", 2), ("78.5", 3), ("20", 4))
        for ypos, k in yticks:
            val = pmax * k / 4
            lab = _frnum(round(val, 1)) if abs(val - round(val)) > 1e-9 else str(int(round(val)))
            html = sub1(html, r'(x="46" y="' + re.escape(ypos) + r'"[^>]*>)[^<]*(</text>)',
                        lambda m, l=lab: m.group(1) + l + m.group(2))

    # --- note sous le tableau dimensions (optionnelle ; sans objet si bloc retiré)
    if "note_dimensions" in d and not no_dim:
        html = sub1(html, r'(margin-top:6px; line-height:1\.45;">)(.*?)(</div>)',
                    lambda m: m.group(1) + d["note_dimensions"] + m.group(3),
                    flags=re.DOTALL)

    # --- mode mono-classe : 1 seule courbe, sans toggle classe/épaisseur
    if mono:
        css = ("\n<style>/* fiche mono-classe : 1 courbe, sans sélecteur */\n"
               "#pathG498,#cG498,#tG498,#legG4b,#legM5a,#legM5b,"
               "#hd2,#hh2,#ht2,#hd3,#hh3,#ht3,#hd4,#hh4,#ht4{display:none!important;}\n"
               "</style>\n</head>")
        html = html.replace("</head>", css, 1)
        # masquer le sélecteur Classe d'efficacité + Épaisseur
        html = html.replace('grid-template-columns:1.7fr 1fr; gap:12px;">',
                            'grid-template-columns:1.7fr 1fr; gap:12px; display:none;">')
        # masquer la ligne de contrôles « Afficher : … »
        html = html.replace('display:flex; align-items:center; gap:18px; margin-top:7px;">',
                            'align-items:center; gap:18px; margin-top:7px; display:none;">')

    # --- page 1 compacte (par produit) : réduit les marges verticales pour
    #     faire tenir un contenu plus dense sur l'A4, sans toucher les autres fiches.
    if d.get("compact_p1"):
        html = html.replace("margin:9mm 0 7mm 0;", "margin:6mm 0 5mm 0;")           # filet en-tête P1
        html = html.replace('<div style="margin-top:9mm;">', '<div style="margin-top:6mm;">')   # Caractéristiques
        html = html.replace('<div style="margin-top:8mm;">', '<div style="margin-top:6mm;">')   # Dimensions

    return html


def main():
    args = [a for a in sys.argv[1:]]
    if not args:
        print("Usage : python3 generer.py produits/netxxx.json [--out fichier.html]")
        sys.exit(1)
    json_path = args[0]
    out = None
    if "--out" in args:
        out = args[args.index("--out") + 1]

    with open(json_path, encoding="utf-8") as f:
        d = json.load(f)
    with open(BASE, encoding="utf-8") as f:
        html = f.read()

    result = generer(d, html)

    # Par défaut, la fiche finale va dans le dossier livrables Fiches_Netair/.
    if out is None:
        out = os.path.join(ROOT, "..", "Fiches_Netair", f"Fiche technique {d['nom']}.html")
    elif not os.path.isabs(out):
        out = os.path.join(ROOT, out)
    out = os.path.abspath(out)
    outdir = os.path.dirname(out)
    os.makedirs(outdir, exist_ok=True)

    with open(out, "w", encoding="utf-8") as f:
        f.write(result)

    # Copier la photo à côté de la fiche (assets/) pour un livrable autonome.
    src_photo = os.path.join(ROOT, "assets", d["photo"])
    if os.path.exists(src_photo):
        dst_assets = os.path.join(outdir, "assets")
        os.makedirs(dst_assets, exist_ok=True)
        if os.path.abspath(src_photo) != os.path.join(dst_assets, d["photo"]):
            shutil.copy(src_photo, os.path.join(dst_assets, d["photo"]))
        warn = ""
    else:
        warn = "  ⚠️ photo absente de Generateur/assets/ !"
    print(f"✅ {os.path.basename(out)} → {os.path.relpath(outdir)}{warn}")


if __name__ == "__main__":
    main()
