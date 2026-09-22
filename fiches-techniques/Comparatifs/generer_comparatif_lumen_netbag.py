#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Plaquette comparative énergétique — NETPAK S LUMEN F7 vs NETBAG S F7 (poches 380 mm).

2 pages A4 paysage :
  1. LUMEN seul  vs  poches souples seules
  2. LUMEN seul  vs  poches souples + préfiltre G4 (le LUMEN s'utilise sans préfiltre)

Toutes les valeurs sont RECALCULÉES à partir des mêmes polynômes ΔP que les fiches
techniques (Generateur/produits/*.json) et de la même méthode que leur calculateur
énergétique : aucun chiffre n'est saisi à la main.

    ΔP(v)   = a·v² + b·v          (polynôme lissé passant par l'origine)
    ΔP fin  = min(ΔP ini + ADD ; 3 × ΔP ini)          EN 13053
    ΔP moy  = (ΔP ini + ΔP fin) / 2 × 0,85
    P       = (Q/3600) × ΔP moy / η
    kWh     = P/1000 × heures

Pour changer les hypothèses commerciales, modifier le bloc « hypothèses » ci-dessous
puis relancer : python3 generer_comparatif_lumen_netbag.py
"""

import base64
import os
import sys

ICI = os.path.dirname(os.path.abspath(__file__))
GEN = os.path.abspath(os.path.join(ICI, "..", "Generateur"))
sys.path.insert(0, GEN)
from generer import force_origin, AREF  # noqa: E402  (réutilise le lissage des fiches)

RACINE = os.path.abspath(os.path.join(ICI, "..", "..", "..", ".."))
LOGO = os.path.join(RACINE, "Identite_Visuelle", "Finaux",
                    "Netair_logo_couleur_fond-transparent.png")

# ------------------------------------------------------------------ hypothèses
# Valeurs par défaut = celles du calculateur énergétique des fiches techniques Netair.
Q = 3400.0        # m³/h — débit nominal d'une cellule 592 × 592
ETA = 0.55        # rendement global du moto-ventilateur
HEURES = 6000.0   # 24 h × 250 j
PRIX = 0.18       # €/kWh
FE_CO2 = 0.079    # kg CO₂/kWh — mix électrique France
CELLULES = (4, 8, 12)

NAVY, TEAL, BLUE = "#0F3261", "#0897A5", "#0070C8"
SLATE, SLATE_F, ORANGE = "#94A3B8", "#5A6B80", "#B45309"
# Vert « écologique » validé par PA pour le LUMEN (dérogation assumée à la charte).
GREEN, GREEN_D, GREEN_L = "#1B8046", "#14532D", "#E9F5EE"


# ------------------------------------------------------------------- physique
def etage(coeffs, vmax, add, profondeur):
    """Un étage de filtration : ΔP initiale / finale / moyenne au point nominal."""
    a, b, _ = force_origin(coeffs[0], coeffs[1], coeffs[2], vmax)
    v = (Q / 3600) / AREF
    ini = a * v * v + b * v
    fin = min(ini + add, ini * 3)
    return {"a": a, "b": b, "ini": ini, "fin": fin,
            "moy": (ini + fin) / 2 * 0.85, "prof": profondeur}


def cumul(etages):
    """Ligne de filtration complète : les ΔP des étages s'additionnent."""
    m = sum(x["moy"] for x in etages)
    kwh = (Q / 3600) * m / ETA / 1000 * HEURES
    return {"ini": sum(x["ini"] for x in etages), "fin": sum(x["fin"] for x in etages),
            "moy": m, "kwh": kwh, "eur": kwh * PRIX, "co2": kwh * FE_CO2}


# Polynômes bruts des fiches (produits/netbag-s.json, netpak-s-lumen.json, netply.json)
BAG = etage((9.10, 43.96, -9.79), 3.17, 100, 380)
LUM = etage((8.87, 2.54, -0.71), 3.5667, 100, 292)
PRE = etage((5.38, 9.76, -2.14), 3.17, 50, 48)

S1_REF, S1_NET = cumul([BAG]), cumul([LUM])
S2_REF, S2_NET = cumul([BAG, PRE]), cumul([LUM])


def ecart(ref, net):
    return {"kwh": ref["kwh"] - net["kwh"], "eur": ref["eur"] - net["eur"],
            "co2": ref["co2"] - net["co2"], "pct": (1 - net["kwh"] / ref["kwh"]) * 100}


D1, D2 = ecart(S1_REF, S1_NET), ecart(S2_REF, S2_NET)


# --------------------------------------------------------------------- format
def fr(x, dec=0):
    return f"{x:,.{dec}f}".replace(",", " ").replace(".", ",")


def b64(chemin):
    with open(chemin, "rb") as f:
        return base64.b64encode(f.read()).decode()


# ------------------------------------------------------------------- schémas
# Coupes horizontales, profondeurs tracées à la même échelle sur les deux schémas.
ECH = 0.30          # px par mm de profondeur
X0, TOP, BOT = 40, 14, 128


def _flux(coul, xs=6, n=4):
    """Flèches d'air entrant."""
    o = []
    for i in range(n):
        y = TOP + 12 + i * (BOT - TOP - 24) / (n - 1)
        o.append(f'<line x1="{xs}" y1="{y:.1f}" x2="{X0 - 14}" y2="{y:.1f}" stroke="{coul}" '
                 f'stroke-width="1.6" opacity=".75"/>')
        o.append(f'<path d="M{X0 - 15} {y - 3.6:.1f}l7 3.6-7 3.6z" fill="{coul}" opacity=".75"/>')
    return "".join(o)


def _cote(prof, coul, txt):
    y = BOT + 16
    return (f'<line x1="{X0}" y1="{y}" x2="{X0 + prof:.1f}" y2="{y}" stroke="{coul}" '
            f'stroke-width="1"/>'
            f'<line x1="{X0}" y1="{y - 4}" x2="{X0}" y2="{y + 4}" stroke="{coul}" stroke-width="1.4"/>'
            f'<line x1="{X0 + prof:.1f}" y1="{y - 4}" x2="{X0 + prof:.1f}" y2="{y + 4}" '
            f'stroke="{coul}" stroke-width="1.4"/>'
            f'<text x="{X0 + prof / 2:.1f}" y="{y + 15}" text-anchor="middle" font-size="11"'
            f' font-weight="700" fill="{coul}" font-family="\'IBM Plex Mono\',monospace">{txt}</text>')


def schema_poches(w=250, h=168):
    """Filtre à poches souples vu en coupe : poches en fuseau, profondeur à l'échelle."""
    prof, n = BAG["prof"] * ECH, 7
    pas = (BOT - TOP) / n
    p = []
    for i in range(n):
        yc = TOP + pas / 2 + i * pas
        dy = pas * 0.40
        p.append(
            f'<path d="M{X0} {yc - dy:.1f} '
            f'C{X0 + prof * .35:.1f} {yc - dy * 1.02:.1f},{X0 + prof * .80:.1f} {yc - dy * .55:.1f},'
            f'{X0 + prof:.1f} {yc - dy * .16:.1f} '
            f'Q{X0 + prof + 3:.1f} {yc:.1f},{X0 + prof:.1f} {yc + dy * .16:.1f} '
            f'C{X0 + prof * .80:.1f} {yc + dy * .55:.1f},{X0 + prof * .35:.1f} {yc + dy * 1.02:.1f},'
            f'{X0} {yc + dy:.1f} Z" fill="#EBD5DB" stroke="{SLATE_F}" stroke-width="1.15"/>')
    return f"""<svg viewBox="0 0 {w} {h}" width="100%" role="img"
     aria-label="Coupe d'un filtre à poches souples, profondeur 380 mm">
  {_flux(NAVY)}{''.join(p)}
  <rect x="{X0 - 7}" y="{TOP - 3}" width="7" height="{BOT - TOP + 6}" rx="1" fill="#334155"/>
  {_cote(prof, NAVY, "380 mm")}
</svg>"""


def schema_diedre(w=250, h=168):
    """Polydièdre rechargeable vu en coupe : panneaux en V, profondeur à l'échelle."""
    prof, n = LUM["prof"] * ECH, 4          # 4 dièdres = 8 panneaux
    pas = (BOT - TOP) / n
    zig, plis = [], []
    for i in range(n):
        y = TOP + i * pas
        for k, (ya, yb) in enumerate(((y, y + pas / 2), (y + pas / 2, y + pas))):
            xa, xb = (X0, X0 + prof) if k == 0 else (X0 + prof, X0)
            zig.append(f'<line x1="{xa}" y1="{ya:.1f}" x2="{xb}" y2="{yb:.1f}" stroke="{GREEN_D}" '
                       f'stroke-width="6.5" stroke-linecap="round"/>')
            for j in range(1, 12):          # hachures fines = plis du média
                t = j / 12
                px, py = xa + (xb - xa) * t, ya + (yb - ya) * t
                plis.append(f'<line x1="{px - 1.7:.1f}" y1="{py - 1.7:.1f}" x2="{px + 1.7:.1f}" '
                            f'y2="{py + 1.7:.1f}" stroke="#8FCBA6" stroke-width="1"/>')
    return f"""<svg viewBox="0 0 {w} {h}" width="100%" role="img"
     aria-label="Coupe d'un filtre polydièdre rechargeable, profondeur 292 mm">
  {_flux(GREEN)}{''.join(zig)}{''.join(plis)}
  <rect x="{X0 - 7}" y="{TOP - 3}" width="7" height="{BOT - TOP + 6}" rx="1" fill="#334155"/>
  <rect x="{X0 + prof:.1f}" y="{TOP - 3}" width="5" height="{BOT - TOP + 6}" rx="1" fill="#334155"
        opacity=".55"/>
  {_cote(prof, GREEN, "292 mm")}
</svg>"""


def schema_poches_prefiltre(w=250, h=168):
    """Les deux étages de la solution classique : préfiltre plissé + poches."""
    prof, n = BAG["prof"] * ECH * .82, 7
    pp = PRE["prof"] * ECH * 3.2                     # 48 mm : épaissi pour rester lisible
    x1 = X0 + pp + 14
    pas = (BOT - TOP) / n
    p = []
    for i in range(n):
        yc = TOP + pas / 2 + i * pas
        dy = pas * 0.40
        p.append(
            f'<path d="M{x1} {yc - dy:.1f} '
            f'C{x1 + prof * .35:.1f} {yc - dy * 1.02:.1f},{x1 + prof * .80:.1f} {yc - dy * .55:.1f},'
            f'{x1 + prof:.1f} {yc - dy * .16:.1f} '
            f'Q{x1 + prof + 3:.1f} {yc:.1f},{x1 + prof:.1f} {yc + dy * .16:.1f} '
            f'C{x1 + prof * .80:.1f} {yc + dy * .55:.1f},{x1 + prof * .35:.1f} {yc + dy * 1.02:.1f},'
            f'{x1} {yc + dy:.1f} Z" fill="#EBD5DB" stroke="{SLATE_F}" stroke-width="1.1"/>')
    zz, npl = [], 22
    hp = (BOT - TOP) / npl
    for j in range(npl):
        y = TOP + j * hp
        zz.append(f'<path d="M{X0} {y:.1f}L{X0 + pp:.1f} {y + hp / 2:.1f}L{X0} {y + hp:.1f}" '
                  f'fill="none" stroke="{ORANGE}" stroke-width="1.6"/>')
    return f"""<svg viewBox="0 0 {w} {h}" width="100%" role="img"
     aria-label="Coupe d'une ligne préfiltre plissé plus filtre à poches souples">
  {_flux(NAVY, 2, 4)}
  {''.join(zz)}
  <rect x="{X0 - 6}" y="{TOP - 3}" width="6" height="{BOT - TOP + 6}" rx="1" fill="#334155"/>
  {''.join(p)}
  <rect x="{x1 - 6}" y="{TOP - 3}" width="6" height="{BOT - TOP + 6}" rx="1" fill="#334155"/>
  <text x="{X0 + pp / 2:.1f}" y="{BOT + 16}" text-anchor="middle" font-size="8.5"
        font-weight="700" fill="{ORANGE}">PRÉFILTRE</text>
  <text x="{x1 + prof / 2:.1f}" y="{BOT + 16}" text-anchor="middle" font-size="8.5"
        font-weight="700" fill="{NAVY}">POCHES SOUPLES</text>
  <text x="{(X0 + x1 + prof) / 2:.1f}" y="{BOT + 30}" text-anchor="middle" font-size="10.5"
        font-weight="700" fill="{NAVY}" font-family="'IBM Plex Mono',monospace">48 + 380 mm</text>
</svg>"""


# --------------------------------------------------------------- courbes ΔP
def courbes(w=740, h=190):
    ox, oy, iw, ih = 52, 10, w - 66, h - 40
    qmax, pmax = 4000.0, 320.0
    mx = lambda q: ox + q / qmax * iw
    my = lambda p: oy + ih - min(p, pmax) / pmax * ih

    def pts(etages):
        out = []
        for i in range(81):
            q = qmax * i / 80
            v = (q / 3600) / AREF
            out.append(f"{mx(q):.1f},{my(sum(e['a'] * v * v + e['b'] * v for e in etages)):.1f}")
        return " ".join(out)

    g = []
    for p in range(0, int(pmax) + 1, 80):
        y = my(p)
        g.append(f'<line x1="{ox}" y1="{y:.1f}" x2="{ox + iw}" y2="{y:.1f}" stroke="#EDF1F6"/>'
                 f'<text x="{ox - 7}" y="{y + 3.5:.1f}" text-anchor="end" font-size="9" '
                 f'fill="#9aa6b4" font-family="\'IBM Plex Mono\',monospace">{p}</text>')
    for q in range(0, 4001, 1000):
        x = mx(q)
        g.append(f'<line x1="{x:.1f}" y1="{oy}" x2="{x:.1f}" y2="{oy + ih}" stroke="#EDF1F6"/>'
                 f'<text x="{x:.1f}" y="{oy + ih + 14}" text-anchor="middle" font-size="9" '
                 f'fill="#9aa6b4" font-family="\'IBM Plex Mono\',monospace">{fr(q)}</text>')

    tr = "".join(
        f'<polyline points="{p}" fill="none" stroke="{c}" stroke-width="{2.1 if d else 2.7}"'
        + (f' stroke-dasharray="{d}"' if d else "") + ' stroke-linejoin="round"/>'
        for p, c, d in ((pts([BAG, PRE]), ORANGE, "6 3"), (pts([BAG]), NAVY, None),
                        (pts([LUM]), GREEN, None)))
    xn = mx(Q)
    marks = "".join(f'<circle cx="{xn:.1f}" cy="{my(v):.1f}" r="4" fill="{c}" stroke="#fff" '
                    f'stroke-width="1.8"/>'
                    for v, c in ((S2_REF["ini"], ORANGE), (BAG["ini"], NAVY), (LUM["ini"], GREEN)))
    return f"""<svg viewBox="0 0 {w} {h}" width="100%" role="img">
  {''.join(g)}
  <line x1="{xn:.1f}" y1="{oy}" x2="{xn:.1f}" y2="{oy + ih}" stroke="{NAVY}" stroke-width="1"
        stroke-dasharray="3 3" opacity=".45"/>
  <text x="{xn - 6:.1f}" y="{oy + 10}" text-anchor="end" font-size="8.5" font-weight="700"
        fill="{NAVY}" opacity=".7" font-family="'IBM Plex Mono',monospace">{fr(Q)} m³/h</text>
  {tr}{marks}
  <line x1="{ox}" y1="{oy}" x2="{ox}" y2="{oy + ih}" stroke="{NAVY}" stroke-width="1.3"/>
  <line x1="{ox}" y1="{oy + ih}" x2="{ox + iw}" y2="{oy + ih}" stroke="{NAVY}" stroke-width="1.3"/>
  <text x="{ox - 38}" y="{oy + ih / 2}" font-size="8.5" font-weight="700" fill="{NAVY}"
        transform="rotate(-90 {ox - 38} {oy + ih / 2})" text-anchor="middle"
        letter-spacing=".08em">ΔP (Pa)</text>
  <text x="{ox + iw}" y="{h - 3}" text-anchor="end" font-size="8.5" font-weight="700"
        fill="{NAVY}" letter-spacing=".08em">DÉBIT (m³/h)</text>
</svg>"""


# --------------------------------------------------------------------- icônes
def ico(kind, coul):
    s = f'stroke="{coul}" stroke-width="1.9" fill="none" stroke-linecap="round" ' \
        'stroke-linejoin="round"'
    d = {
        "kwh": f'<path d="M14 2 5 14h7l-1 8 9-12h-7z" {s}/>',
        "co2": f'<path d="M6 16a4 4 0 0 1 .6-8 5.5 5.5 0 0 1 10.5 1.4A3.6 3.6 0 0 1 17 16z" {s}/>'
               f'<text x="12" y="21.5" text-anchor="middle" font-size="7.5" font-weight="700"'
               f' fill="{coul}" font-family="Arial">CO₂</text>',
        "eur": f'<circle cx="12" cy="12" r="9" {s}/>'
               f'<path d="M15.5 8.4a4.6 4.6 0 0 0-6.4 3.6 4.6 4.6 0 0 0 6.4 3.6M7.4 10.8h5.4'
               f'M7.4 13.4h5.4" {s}/>',
    }[kind]
    return f'<svg viewBox="0 0 24 24" width="26" height="26" role="presentation">{d}</svg>'


# ----------------------------------------------------------------------- HTML
def colonne(titre, sous, schema, e, coul, fond, sombre=False):
    cl = "sol sol--net" if sombre else "sol"
    return f"""<div class="{cl}">
  <div class="sol__hd" style="background:{fond}">
    <div class="sol__t">{titre}</div><div class="sol__s">{sous}</div>
  </div>
  <div class="sol__sch">{schema}</div>
  <div class="sol__conso" style="background:{fond}">
    <div class="sol__lbl">Consommation énergétique annuelle</div>
    <div class="sol__big">{fr(e['kwh'])} <i>kWh</i></div>
    <div class="sol__dp">
      <span>ΔP initiale <b>{fr(e['ini'])} Pa</b></span>
      <span>ΔP finale <b>{fr(e['fin'])} Pa</b></span>
      <span class="on">ΔP moyenne <b>{fr(e['moy'])} Pa</b></span>
    </div>
  </div>
  <div class="sol__pied">
    <span>{ico('co2', coul)}<i>Émissions</i><b>{fr(e['co2'])} kg/an</b></span>
    <span>{ico('eur', coul)}<i>Coût annuel</i><b>{fr(e['eur'])} €</b></span>
  </div>
</div>"""


def bloc_gains(ref, net, d, titre):
    return f"""<div class="gain">
  <div class="gain__hd">{titre}</div>
  <div class="gain__l">
    {ico('kwh', GREEN)}
    <div><b>{fr(d['kwh'])} kWh</b><span>d'énergie économisée par an</span>
      <em>{fr(ref['kwh'])} kWh &rarr; {fr(net['kwh'])} kWh, soit &minus;{fr(d['pct'])} %</em></div>
  </div>
  <div class="gain__l">
    {ico('co2', GREEN)}
    <div><b>{fr(d['co2'])} kg</b><span>de CO₂ en moins par an</span>
      <em>{fr(ref['co2'])} kg &rarr; {fr(net['co2'])} kg rejetés</em></div>
  </div>
  <div class="gain__l">
    {ico('eur', GREEN)}
    <div><b>{fr(d['eur'])} €</b><span>d'économie annuelle</span>
      <em>{fr(ref['eur'])} € &rarr; {fr(net['eur'])} € de facture électrique</em></div>
  </div>
  <div class="gain__bd">&minus;{fr(d['pct'])} % d'énergie consommée</div>
</div>"""


CSS = f"""
*{{margin:0;padding:0;box-sizing:border-box}}
:root{{--navy:{NAVY};--teal:{TEAL};--bg:#F8FAFC;--muted:#ECF1F4;--border:#E2E8F0;--sub:#4A5E7A}}
body{{font-family:'Instrument Sans','Helvetica Neue',Arial,sans-serif;color:var(--navy);
background:#dfe5ec;-webkit-print-color-adjust:exact;print-color-adjust:exact}}
.page{{width:297mm;height:210mm;background:#fff;margin:0 auto 8mm;padding:9mm 11mm 7mm;
display:flex;flex-direction:column;overflow:hidden}}
.hd{{display:flex;align-items:center;justify-content:space-between;
border-bottom:1px solid var(--border);padding-bottom:6px}}
.hd img{{height:30px}}
.lbl{{font-size:8px;font-weight:700;letter-spacing:.15em;text-transform:uppercase;color:var(--teal);
text-align:right}}
.hd__d{{font-size:8.5px;color:#9aa6b4;font-family:'IBM Plex Mono',monospace;text-align:right;
margin-top:2px}}
h1{{font-size:20px;font-weight:700;letter-spacing:-.02em;text-align:center;margin-top:9px}}
h1 b{{color:{GREEN}}}h1 u{{text-decoration:none;color:var(--sub);font-weight:600}}
.hypo{{text-align:center;font-size:9.5px;color:var(--sub);margin-top:4px;line-height:1.45}}
.hypo b{{color:var(--navy);font-weight:700;font-family:'IBM Plex Mono',monospace}}
.hypo strong{{color:var(--navy);font-weight:700}}
.tri{{display:grid;grid-template-columns:1fr .84fr 1fr;gap:8px;margin-top:9px;flex:1;
min-height:0}}
.sol{{border:1.4px solid var(--border);border-radius:10px;overflow:hidden;display:flex;
flex-direction:column;background:#fff}}
.sol--net{{border-color:{GREEN};box-shadow:0 2px 12px rgba(27,128,70,.13)}}
.sol__hd{{padding:7px 10px;text-align:center;color:#fff}}
.sol__t{{font-size:14px;font-weight:700;letter-spacing:-.01em}}
.sol__s{{font-size:9px;opacity:.85;margin-top:1px;line-height:1.35}}
.sol__sch{{padding:5px 8px 2px;flex:1;display:flex;align-items:stretch;min-height:0}}
.sol__sch svg{{width:100%;height:100%;max-height:100%}}
.sol__conso{{color:#fff;padding:7px 10px 8px;text-align:center}}
.sol__lbl{{font-size:8px;font-weight:700;letter-spacing:.09em;text-transform:uppercase;
opacity:.8}}
.sol__big{{font-family:'IBM Plex Mono',monospace;font-size:30px;font-weight:700;line-height:1.1;
margin-top:1px}}
.sol__big i{{font-style:normal;font-size:14px;font-weight:500;opacity:.85}}
.sol__dp{{display:flex;justify-content:center;gap:9px;margin-top:5px;font-size:8.5px;
opacity:.9;flex-wrap:wrap}}
.sol__dp b{{font-family:'IBM Plex Mono',monospace;font-weight:700}}
.sol__dp .on{{background:rgba(255,255,255,.16);border-radius:3px;padding:0 5px}}
.sol__pied{{display:flex;border-top:1px solid var(--border)}}
.sol__pied span{{flex:1;display:flex;align-items:center;gap:6px;padding:7px 9px}}
.sol__pied span+span{{border-left:1px solid var(--border)}}
.sol__pied i{{font-style:normal;font-size:8px;font-weight:700;letter-spacing:.05em;
text-transform:uppercase;color:#8494a8}}
.sol__pied b{{font-family:'IBM Plex Mono',monospace;font-size:13px;margin-left:auto}}
.gain{{background:{GREEN_L};border:1.4px solid {GREEN};border-radius:10px;display:flex;
flex-direction:column;overflow:hidden}}
.gain__hd{{background:{GREEN};color:#fff;padding:7px 10px;text-align:center;font-size:11.5px;
font-weight:700;letter-spacing:.02em;line-height:1.3}}
.gain__l{{display:flex;gap:9px;align-items:flex-start;padding:9px 12px;flex:1;
border-bottom:1px solid rgba(27,128,70,.20)}}
.gain__l svg{{flex:none;margin-top:2px}}
.gain__l b{{display:block;font-family:'IBM Plex Mono',monospace;font-size:25px;font-weight:700;
line-height:1.05;color:{GREEN_D}}}
.gain__l span{{display:block;font-size:10px;font-weight:700;margin-top:1px;color:var(--navy)}}
.gain__l em{{display:block;font-style:normal;font-size:8.5px;color:#5f7a6b;margin-top:3px;
line-height:1.4}}
.gain__bd{{background:{GREEN};color:#fff;text-align:center;padding:7px;font-size:16px;
font-weight:700;font-family:'IBM Plex Mono',monospace}}
.bas{{display:grid;grid-template-columns:1fr;gap:8px;margin-top:8px}}
.bas2{{display:grid;grid-template-columns:1.05fr 1fr;gap:8px;margin-top:8px}}
.box{{border:1px solid var(--border);border-radius:9px;padding:8px 11px 9px;background:#fff}}
h2{{font-size:10px;font-weight:700;letter-spacing:.1em;text-transform:uppercase;
border-left:3.5px solid var(--teal);padding-left:8px;margin-bottom:5px}}
.leg{{display:flex;gap:15px;font-size:8.5px;font-weight:600;color:var(--sub);
justify-content:center;margin-top:2px}}
.leg span{{display:flex;align-items:center;gap:5px}}
.leg em{{width:15px;height:3px;border-radius:2px;font-style:normal}}
table.ech{{width:100%;border-collapse:collapse;font-size:9.5px}}
table.ech th{{background:#E8EEF6;font-size:8px;font-weight:700;letter-spacing:.06em;
text-transform:uppercase;padding:5px 7px;text-align:right;border-bottom:1px solid var(--border)}}
table.ech th:first-child{{text-align:left}}
table.ech td{{padding:5px 7px;text-align:right;border-bottom:1px solid #EEF2F6;
font-family:'IBM Plex Mono',monospace}}
table.ech td:first-child{{text-align:left;font-family:'Instrument Sans',Arial,sans-serif;
font-weight:600}}
table.ech tbody tr:nth-child(even){{background:#E6F5F7}}
table.ech .win{{color:var(--teal);font-weight:700}}
.args{{display:grid;grid-template-columns:1fr 1fr;gap:6px}}
.arg{{border:1px solid var(--border);border-radius:7px;padding:7px 9px;background:#FAFCFD}}
.arg b{{display:block;font-size:9.5px;font-weight:700;margin-bottom:2px}}
.arg span{{font-size:8.5px;line-height:1.45;color:var(--sub)}}
.hyp{{font-size:7.5px;line-height:1.5;color:#8a97a8;margin-top:7px;border-top:1px solid
var(--border);padding-top:6px}}
.hyp b{{font-size:7.5px;font-weight:700;letter-spacing:.09em;text-transform:uppercase;
color:var(--teal)}}
.ft{{display:flex;justify-content:space-between;font-size:7px;color:#a5b0bd;margin-top:5px}}
@page{{size:A4 landscape;margin:0}}
@media print{{body{{background:#fff}}.page{{margin:0;break-after:page;page-break-after:always}}
.page:last-child{{break-after:auto;page-break-after:auto}}}}
"""


def entete(sur):
    return f"""<div class="hd">
  <img src="data:image/png;base64,{b64(LOGO)}" alt="Netair">
  <div><div class="lbl">Comparatif énergétique</div><div class="hd__d">{sur}</div></div>
</div>"""


def pied(n):
    return f"""<div class="ft">
  <span>NETAIR — SASU · SIREN 107 397 648 R.C.S. Lyon</span>
  <span>NETPAK S LUMEN vs filtre à poches souples — page {n}/2</span></div>"""


HYPO_LIGNE = (f"Comparaison à efficacité identique <b>F7 — ISO ePM1 55 %</b> · cellule "
              f"<b>592 × 592 mm</b> · débit <b>{fr(Q)} m³/h</b> · <b>{fr(HEURES)} h</b> de "
              f"fonctionnement par an · électricité <b>{str(PRIX).replace('.', ',')} €/kWh</b>")

HYP_DETAIL = f"""<div class="hyp"><b>Méthode et hypothèses</b> — Puissance absorbée
P = (Q/3600) × ΔP<sub>moyenne</sub> / η, avec η = {int(ETA * 100)} % (rendement global du
moto-ventilateur) ; énergie = P × {fr(HEURES)} h. ΔP finale conforme <b style="color:#8a97a8">
EN 13053</b> : min(ΔP initiale + 50 Pa [Coarse] ou + 100 Pa [ePM] ; 3 × ΔP initiale) ;
ΔP moyenne = 0,85 × (ΔP initiale + ΔP finale)/2. Facteur d'émission
{str(FE_CO2).replace('.', ',')} kg CO₂/kWh (mix électrique France). Les pertes de charge sont
issues des courbes mesurées des fiches techniques Netair, média propre, au débit nominal d'une
cellule 592 × 592 mm. Valeurs indicatives établies pour comparer deux solutions de même
efficacité ; elles ne constituent pas un engagement contractuel de consommation.</div>"""


def page1():
    return f"""<div class="page">
{entete('Scénario 1 &mdash; filtre seul, sans préfiltre')}
<h1>Optimisez votre filtration d'air : <b>NETPAK S LUMEN F7</b> <u>vs</u> poches souples F7</h1>
<div class="hypo">{HYPO_LIGNE}</div>
<div class="tri">
{colonne("Solution classique", "Poches souples F7 &middot; profondeur 380 mm",
         schema_poches(), S1_REF, NAVY, NAVY)}
{bloc_gains(S1_REF, S1_NET, D1, "Gains écologiques et financiers<br>avec le NETPAK S LUMEN")}
{colonne("NETPAK S LUMEN", "Polydièdre rechargeable F7 &middot; profondeur 292 mm",
         schema_diedre(), S1_NET, GREEN, GREEN, True)}
</div>
<div class="bas"><div class="box">
  <h2>Perte de charge selon le débit d'air</h2>
  {courbes()}
  <div class="leg">
    <span><em style="background:{NAVY}"></em>Poches souples F7 &middot; 380 mm</span>
    <span><em style="background:{ORANGE}"></em>Poches souples + préfiltre G4 <i
      style="font-style:normal;color:#a5b0bd">&mdash; voir page 2</i></span>
    <span><em style="background:{GREEN}"></em>NETPAK S LUMEN F7 &middot; 292 mm</span>
  </div>
</div></div>
{pied(1)}
</div>"""


def page2():
    lignes = "".join(
        f"<tr><td>{n} cellules</td><td>{fr(S2_REF['kwh'] * n)}</td>"
        f"<td class='win'>{fr(S2_NET['kwh'] * n)}</td>"
        f"<td class='win'>&minus;{fr(D2['eur'] * n)} €</td>"
        f"<td class='win'>&minus;{fr(D2['co2'] * n)} kg</td></tr>" for n in CELLULES)
    return f"""<div class="page">
{entete('Scénario 2 &mdash; ligne complète, préfiltre compris')}
<h1>Le vrai match : <u>deux étages de filtration contre</u> <b>un seul</b></h1>
<div class="hypo">Un filtre à poches souples est protégé par un préfiltre, dont la perte de
charge s'ajoute à la sienne. Le <strong>NETPAK S LUMEN s'utilise sans préfiltre</strong> : la comparaison
porte donc sur la ligne de filtration complète.</div>
<div class="tri">
{colonne("Solution classique", "Préfiltre G4 48 mm <b>+</b> poches souples F7 380 mm",
         schema_poches_prefiltre(), S2_REF, NAVY, NAVY)}
{bloc_gains(S2_REF, S2_NET, D2, "Gains écologiques et financiers<br>avec le NETPAK S LUMEN")}
{colonne("NETPAK S LUMEN", "Polydièdre rechargeable F7 &middot; sans préfiltre",
         schema_diedre(), S2_NET, GREEN, GREEN, True)}
</div>
<div class="bas2">
  <div class="box"><h2>À l'échelle d'une centrale de traitement d'air</h2>
    <table class="ech"><thead><tr><th>Centrale</th><th>Poches + préfiltre<br>kWh/an</th>
      <th>NETPAK S LUMEN<br>kWh/an</th><th>Économie / an</th><th>CO₂ évité / an</th></tr></thead>
      <tbody>{lignes}</tbody></table>
    <p style="font-size:8px;color:#9aa6b4;margin-top:6px;line-height:1.45">Une cellule = 592 × 592 mm au débit nominal de {fr(Q)} m³/h. Le gain est strictement proportionnel au nombre de cellules équipées.</p></div>
  <div class="box"><h2>Ce que vous gagnez aussi</h2>
    <div class="args">
      <div class="arg"><b>Un étage de filtration en moins</b><span>Plus de préfiltre à acheter,
        stocker ni remplacer : la maintenance ne porte que sur un produit.</span></div>
      <div class="arg"><b>Support conservé, cassettes remplacées</b><span>Le LUMEN est
        rechargeable : seules les cassettes filtrantes sont changées, le support reste en place —
        d'où un volume de déchets nettement réduit.</span></div>
      <div class="arg"><b>Encombrement réduit</b><span>292 mm au lieu de 48 + 380 mm : un caisson
        entier libéré sur la ligne de traitement.</span></div>
      <div class="arg"><b>Sans fibre de verre</b><span>Média papier polypropylène, classement au
        feu M1, 60 °C et 100 % d'humidité relative sans condensation.</span></div>
    </div></div>
</div>
{HYP_DETAIL}
{pied(2)}
</div>"""


HTML = f"""<!doctype html>
<html lang="fr"><head><meta charset="utf-8">
<title>Comparatif énergétique — NETPAK S LUMEN vs filtre à poches souples</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Instrument+Sans:wght@400;500;600;700&family=IBM+Plex+Mono:wght@400;500;700&display=swap" rel="stylesheet">
<style>{CSS}</style></head><body>{page1()}{page2()}</body></html>"""


if __name__ == "__main__":
    dest = os.path.join(ICI, "Comparatif_energetique_LUMEN_vs_NETBAG.html")
    with open(dest, "w", encoding="utf-8") as f:
        f.write(HTML)
    print(f"→ {dest}")
    for lib, r, n, d in (("Scénario 1 — sans préfiltre", S1_REF, S1_NET, D1),
                         ("Scénario 2 — avec préfiltre", S2_REF, S2_NET, D2)):
        print(f"{lib:30} ΔP moy {fr(r['moy'])} → {fr(n['moy'])} Pa | "
              f"{fr(r['kwh'])} → {fr(n['kwh'])} kWh/an "
              f"(-{fr(d['pct'], 1)} % · -{fr(d['eur'])} € · -{fr(d['co2'])} kg CO2)")
