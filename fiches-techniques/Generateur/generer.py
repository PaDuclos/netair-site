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
from decimal import Decimal, ROUND_HALF_UP

ROOT = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.join(ROOT, "gabarit_base.html")


# ---------------------------------------------------------------- helpers ----
def fr_surface(L, H):
    """Surface filtrante = 2 × (L × H) en m², format français '0,70'."""
    val = Decimal(2 * L * H) / Decimal(1_000_000)
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
    rows = []
    i = 0  # index global (striping continu sur toutes les lignes de données)

    def emit(dim, cls):
        nonlocal i
        i += 1
        grey = (i % 2 == 0)  # ligne 1 blanche, ligne 2 grise, …
        tr = ' style="background:#F2F6FB;"' if grey else ""
        L, H, P = dim["L"], dim["H"], dim["P"]
        surface = fr_surface(L, H)
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
    for dim in d["dimensions"]:      # …puis toutes les lignes classe haute
        emit(dim, high)

    rows.append(
        '<tr style="background:#E6F5F7;">'
        '<td style="padding:4px 7px; font-weight:700; color:#0F3261;" '
        'colspan="7">Sur mesure</td>'
        '<td style="padding:4px 7px; color:#5A6573; font-style:italic;">'
        'sur demande — délai à confirmer</td></tr>'
    )
    return "\n".join("              " + r for r in rows)


def build_scale_block(low, high):
    """Bloc de constantes JS (#10). Reproduit l'espacement exact du gabarit."""
    return (
        "  var SCALE = {            // ΔP initiale (Pa) à 3400 m³/h sur 592×592 (≈ 2,69 m/s)\n"
        f"    g4: {{ 48: {low['scale48']}, 98: {low['scale98']} }},   // {low['label']} · {low['iso']}\n"
        f"    m5: {{ 48: {high['scale48']}, 98: {high['scale98']} }}    // {high['label']} · {high['iso']}\n"
        "  };\n"
        f"  var EXP  = {{ g4: {low['exp']}, m5: {high['exp']} }};          // exposant de la loi ΔP ∝ v^exp\n"
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
    for eid, txt in (("legG4a", f"{lab_low} — 48 mm"), ("legG4b", f"{lab_low} — 98 mm"),
                     ("legM5a", f"{lab_high} — 48 mm"), ("legM5b", f"{lab_high} — 98 mm")):
        html = sub1(html, r'(id="' + eid + r'"[^>]*>.*?</span>)(.*?)(</div>)',
                    lambda m, t=txt: m.group(1) + t + m.group(3), flags=re.DOTALL)
    html = sub1(html, r'(id="btnEffG4"[^>]*>)([^<]*)(</button>)',
                lambda m: m.group(1) + f'{low["iso"]} ({low["label"]})' + m.group(3))
    html = sub1(html, r'(id="btnEffM5"[^>]*>)([^<]*)(</button>)',
                lambda m: m.group(1) + f'{high["iso"]} ({high["label"]})' + m.group(3))

    # --- #10b constantes JS (SCALE / EXP / ADD / RULE)
    html = sub1(html, r"  var SCALE = \{.*?var RULE = \{[^\n]*\};",
                lambda m: build_scale_block(low, high), flags=re.DOTALL)

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

    if out is None:
        out = os.path.join(ROOT, f"Fiche technique {d['nom']}.html")
    elif not os.path.isabs(out):
        out = os.path.join(ROOT, out)

    with open(out, "w", encoding="utf-8") as f:
        f.write(result)

    # contrôle photo
    photo_path = os.path.join(ROOT, "assets", d["photo"])
    warn = "" if os.path.exists(photo_path) else "  ⚠️ photo absente de assets/ !"
    print(f"✅ {os.path.basename(out)} généré.{warn}")


if __name__ == "__main__":
    main()
