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
    """Graduations verticales (0,5 / 1 / …) + ligne pointillée du point nominal.
    Pas de 0,1 m/s pour les très basses plages (HEPA laminaire, Vmax ≤ 1)."""
    step = 0.1 if vmax <= 1 else 0.5
    out, v = [], step
    while v < vmax - 1e-9:
        x = f"{_mapx(v, vmax):.1f}"
        out.append(f'<line x1="{x}" y1="16" x2="{x}" y2="250" stroke="#EDF1F6" stroke-width="1"></line>')
        v += step
    xn = f"{_mapx(vnom, vmax):.1f}"
    out.append(f'<line x1="{xn}" y1="16" x2="{xn}" y2="250" stroke="#0F3261" '
               f'stroke-width="1" stroke-dasharray="2 3" opacity="0.4"></line>')
    return "\n".join("            " + l for l in out)


def build_xlabels(vmax):
    """Étiquettes de l'axe vitesse : 0, 0,5, … (centrées) puis Vmax (aligné à droite)."""
    out, v = [], 0.0
    base = ('font-family="\'IBM Plex Mono\',monospace" font-size="11" fill="#5A6573"')
    step = 0.1 if vmax <= 1 else 0.5
    margin = 0.06 if vmax <= 1 else 0.3   # on s'arrête avant Vmax pour ne pas chevaucher son étiquette
    while v < vmax - margin:
        x = "52" if v == 0 else f"{_mapx(v, vmax):.1f}"
        out.append(f'<text x="{x}" y="265" text-anchor="middle" {base}>{_frnum(v)}</text>')
        v += step
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


# ============================================================ moteur SÉRIES ==
# Mode multi-classes opt-in (clé "series" du JSON). N courbes (classe × longueur
# de poche), calculateur à sélecteur classe × longueur. Le chemin legacy (2 classes
# × 2 épaisseurs, NETPLY / _gabarit_ref) est INCHANGÉ → test d'identité préservé.

def _serie_key(s):
    return f'{s["cls"]}_{s["len"]}'


def build_series_checkboxes(d):
    cdef = d["classes_def"]; order = d["classes_order"]; series = d["courbes"]
    primary = {}
    for s in series:
        primary.setdefault(s["cls"], s["color"])
    rows = ['        <div style="display:flex; align-items:center; gap:14px; '
            'margin-top:7px; flex-wrap:wrap;">',
            '          <span style="font-size:11px; font-weight:600; color:#5A6573; '
            'white-space:nowrap;">Afficher :</span>']
    for cls in order:
        if cls not in primary:
            continue
        col = primary[cls]
        lab = f'{cdef[cls]["label"]} · {cdef[cls]["iso"]}'
        rows.append(
            '          <label style="display:inline-flex; align-items:center; gap:6px; '
            'cursor:pointer; font-size:11.5px; color:#3a4654; white-space:nowrap;">'
            f'<input type="checkbox" id="cb_{cls}" checked style="width:14px; height:14px; '
            f'accent-color:{col}; cursor:pointer;">{lab}</label>')
    rows.append('        </div>')
    return "\n".join(rows)


def build_series_paths(d):
    series = d["courbes"]
    out = ["            <!-- courbes multi-classes (générées) -->"]
    for s in series:
        k = _serie_key(s)
        dash = ' stroke-dasharray="5 4"' if s.get("dash") else ""
        out.append(
            f'            <path id="p_{k}" d="" fill="none" stroke="{s["color"]}" '
            f'stroke-width="2.1" stroke-linecap="round" stroke-linejoin="round"{dash}></path>')
    out.append('            <g id="fixedMarks">')
    for s in series:
        k = _serie_key(s)
        out.append(f'            <circle id="m_{k}" cx="0" cy="0" r="0" fill="{s["color"]}"></circle>')
    out.append('            </g>')
    return "\n".join(out)


def build_series_hover():
    return (
        '            <g id="hoverG" style="display:none;">\n'
        '              <line id="hvV" x1="0" y1="16" x2="0" y2="250" stroke="#0F3261" '
        'stroke-width="1" stroke-dasharray="3 3" opacity="0.4"></line>\n'
        '              <text id="hvel" x="0" y="244" text-anchor="middle" paint-order="stroke" '
        'stroke="#fff" stroke-width="3.5" stroke-linejoin="round" '
        'font-family="\'IBM Plex Mono\',monospace" font-size="10.5" font-weight="700" '
        'fill="#0F3261"></text>\n'
        '            </g>')


def build_series_legend(d):
    cdef = d["classes_def"]
    out = []
    for s in d["courbes"]:
        k = _serie_key(s)
        lab = f'{cdef[s["cls"]]["label"]} · {cdef[s["cls"]]["iso"]} — {s["len"]} mm'
        if s.get("avalider"):
            lab += " (à valider)"
        out.append(
            f'            <div id="lg_{k}" style="display:flex; align-items:center; gap:7px;">'
            f'<span style="width:22px; height:3px; background:{s["color"]}; '
            f'display:inline-block; border-radius:2px;"></span>{lab}</div>')
    return "\n".join(out)


def build_series_selector(d):
    cdef = d["classes_def"]; order = d["classes_order"]
    present = [c for c in order if any(s["cls"] == c for s in d["courbes"])]
    btns = "".join(
        f'<button id="be_{c}" style="flex:1; font-size:10px;">{cdef[c]["iso"]} ({cdef[c]["label"]})</button>' for c in present)
    return (
        '            <div style="display:grid; grid-template-columns:1fr; gap:10px;">\n'
        '              <div>\n'
        '                <div style="font-size:10px; font-weight:700; letter-spacing:.7px; '
        'text-transform:uppercase; color:#9aa6b4; margin-bottom:7px;">Classe d\'efficacité</div>\n'
        '                <div style="display:flex; background:#EEF3F9; border:1px solid #D5E0EF; '
        f'border-radius:9px; padding:3px; gap:3px;">{btns}</div>\n'
        '              </div>\n'
        '              <div>\n'
        '                <div style="font-size:10px; font-weight:700; letter-spacing:.7px; '
        'text-transform:uppercase; color:#9aa6b4; margin-bottom:7px;">Longueur de poche</div>\n'
        '                <div id="lenBtns" style="display:flex; background:#EEF3F9; '
        'border:1px solid #D5E0EF; border-radius:9px; padding:3px; gap:3px;"></div>\n'
        '              </div>\n'
        '            </div>')


def build_dimensions_series(d):
    nom = d["nom"]; cdef = d["classes_def"]; dnom = d.get("debit_nom", 3400)
    rows = []
    for i, s in enumerate(d["courbes"], start=1):
        grey = (i % 2 == 0)
        tr = ' style="background:#F2F6FB;"' if grey else ""
        cl = cdef[s["cls"]]
        L, H, P = 592, 592, s["len"]
        surf = f'{s["surface"]:.2f}'.replace(".", ",") if "surface" in s else "n.c."
        debit = fr_debit(dnom)
        eff = f'{cl["iso"]} ({cl["label"]})'
        ref = f'{nom}-{cl["iso"]}-{cl["label"]}-{L}x{H}x{P}'
        dp = f'{s["dp"]}*' if s.get("avalider") else f'{s["dp"]}'
        c = "padding:4px 7px;"
        cref = ("padding:4px 7px; font-family:'IBM Plex Mono',monospace; color:#0F3261;")
        rows.append(
            f'<tr{tr}><td style="{c}">{L}</td><td style="{c}">{H}</td><td style="{c}">{P}</td>'
            f'<td style="{c}">{surf}</td><td style="{c}">{debit}</td><td style="{c}">{dp}</td>'
            f'<td style="{c}">{eff}</td><td style="{cref}">{ref}</td></tr>')
    rows.append(
        '<tr style="background:#E6F5F7;">'
        '<td style="padding:4px 7px; font-weight:700; color:#0F3261;" colspan="7">Sur mesure</td>'
        '<td style="padding:4px 7px; color:#5A6573; font-style:italic;">'
        'sur demande — délai à confirmer</td></tr>')
    return "\n".join("              " + r for r in rows)


SERIES_JS = r"""<script>
(function () {
  "use strict";
  var SERIES = __SERIES__;
  var CLS    = __CLS__;
  var ORDER  = __ORDER__;
  var Vmax = __VMAX__, Pmax = __PMAX__, Dnom = __DNOM__;
  var HEPA = __HEPA__;
  var Aref = 0.592 * 0.592;
  var Vnom = (Dnom / 3600) / Aref;

  var state = { debit: Dnom, duree: 24, jours: 250, eta: 55, prix: 0.18,
                eff: __EFF0__, len: __LEN0__, disp: __DISP0__, flen: 592, fwid: 592 };

  var fr = function (n) { return Math.round(n).toLocaleString('fr-FR'); };
  var $  = function (id) { return document.getElementById(id); };
  var mapX = function (v) { return 52 + (v / Vmax) * 528; };
  var mapY = function (p) { return 250 - (Math.min(p, Pmax) / Pmax) * 234; };
  function pdc(co, v) { return Math.max(0, co.a * v * v + co.b * v + co.c); }
  function curve(co) {
    var pts = [], v;
    for (v = 0; v <= Vmax - 1e-9; v += 0.1) pts.push(mapX(v).toFixed(1) + ',' + mapY(pdc(co, v)).toFixed(1));
    pts.push(mapX(Vmax).toFixed(1) + ',' + mapY(pdc(co, Vmax)).toFixed(1));
    return 'M' + pts.join(' L');
  }
  function lengthsFor(cls) { var o = []; for (var i = 0; i < SERIES.length; i++) if (SERIES[i].cls === cls) o.push(SERIES[i].len); return o; }
  function curSeries() {
    var i; for (i = 0; i < SERIES.length; i++) if (SERIES[i].cls === state.eff && SERIES[i].len === state.len) return SERIES[i];
    for (i = 0; i < SERIES.length; i++) if (SERIES[i].cls === state.eff) return SERIES[i];
    return SERIES[0];
  }

  var ON  = 'background:#0897A5; color:#fff; box-shadow:0 1px 3px rgba(8,151,165,.4);';
  var OFF = 'background:transparent; color:#5A6573; box-shadow:none;';
  var BTN = 'flex:1; padding:7px 3px; border:none; border-radius:6px; font-size:10.5px; font-weight:600; cursor:pointer; font-family:inherit; transition:all .12s; white-space:nowrap; ';
  var BEB = 'flex:1; padding:7px 2px; border:none; border-radius:6px; font-size:9px; font-weight:600; cursor:pointer; font-family:inherit; transition:all .12s; white-space:nowrap; ';
  var BTL = 'padding:6px 10px; border:none; border-radius:6px; font-size:10.5px; font-weight:600; cursor:pointer; font-family:inherit; white-space:nowrap; ';

  var NS = 'http://www.w3.org/2000/svg';
  var hoverG = $('hoverG'), lanes = {};
  for (var i = 0; i < SERIES.length; i++) {
    var s = SERIES[i];
    var hh = document.createElementNS(NS, 'line');
    hh.setAttribute('x1', '52'); hh.setAttribute('stroke', s.color); hh.setAttribute('stroke-width', '1');
    hh.setAttribute('stroke-dasharray', '3 3'); hh.setAttribute('opacity', '0.3'); hh.style.display = 'none';
    var hd = document.createElementNS(NS, 'circle'); hd.setAttribute('r', '0'); hd.setAttribute('fill', s.color);
    var ht = document.createElementNS(NS, 'text');
    ht.setAttribute('text-anchor', 'start'); ht.setAttribute('paint-order', 'stroke'); ht.setAttribute('stroke', '#fff');
    ht.setAttribute('stroke-width', '3.2'); ht.setAttribute('stroke-linejoin', 'round');
    ht.setAttribute('font-family', "'IBM Plex Mono',monospace"); ht.setAttribute('font-size', '9.5');
    ht.setAttribute('font-weight', '600'); ht.setAttribute('fill', s.color);
    hoverG.appendChild(hh); hoverG.appendChild(hd); hoverG.appendChild(ht);
    lanes[s.k] = { hh: hh, hd: hd, ht: ht };
  }

  function buildLenBtns() {
    var cont = $('lenBtns'); cont.innerHTML = '';
    var ls = lengthsFor(state.eff);
    if (ls.indexOf(state.len) < 0) state.len = ls[0];
    ls.forEach(function (L) {
      var b = document.createElement('button');
      b.textContent = L + ' mm';
      b.setAttribute('style', BTL + (state.len === L ? ON : OFF));
      b.addEventListener('click', function () { state.len = L; render(); });
      cont.appendChild(b);
    });
  }

  function render() {
    var i, s;
    for (i = 0; i < SERIES.length; i++) {
      s = SERIES[i];
      var show = state.disp[s.cls] !== false;
      $('p_' + s.k).setAttribute('d', show ? curve(s.co) : '');
      var mc = $('m_' + s.k), yy = mapY(pdc(s.co, Vnom));
      mc.setAttribute('cx', mapX(Vnom).toFixed(1)); mc.setAttribute('cy', yy.toFixed(1)); mc.setAttribute('r', show ? 2.6 : 0);
      $('lg_' + s.k).style.opacity = show ? '1' : '0.25';
    }
    for (i = 0; i < ORDER.length; i++) {
      var cb = $('cb_' + ORDER[i]); if (cb) cb.checked = state.disp[ORDER[i]] !== false;
      var be = $('be_' + ORDER[i]); if (be) be.setAttribute('style', BEB + (state.eff === ORDER[i] ? ON : OFF));
    }
    buildLenBtns();

    var cs = curSeries(), co = cs.co, add = CLS[cs.cls].add, rule = CLS[cs.cls].rule;
    var areaNum = (Math.max(50, state.flen) / 1000) * (Math.max(50, state.fwid) / 1000);
    var velNum = (state.debit / 3600) / areaNum;
    var dpInit = pdc(co, velNum), dpFinal = HEPA ? dpInit * 2 : Math.min(dpInit + add, dpInit * 3), dpAvg = (dpFinal / 2) * 0.85;
    $('dpInit').textContent = fr(dpInit); $('dpFinal').textContent = fr(dpFinal); $('dpAvg').textContent = fr(dpAvg);
    $('effAdd').textContent = add; $('effRule').textContent = rule;
    $('area').textContent = areaNum.toLocaleString('fr-FR', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
    $('vel').textContent = velNum.toLocaleString('fr-FR', { minimumFractionDigits: 1, maximumFractionDigits: 1 });
    var heures = Math.round(state.duree * state.jours);
    $('debitVal').textContent = state.debit;
    $('dureeVal').textContent = state.duree.toLocaleString('fr-FR', { minimumFractionDigits: 0, maximumFractionDigits: 1 });
    $('joursVal').textContent = state.jours; $('heuresVal').textContent = fr(heures);
    $('heures2').textContent = fr(heures); $('heures3').textContent = fr(heures);
    $('etaVal').textContent = state.eta;
    $('prixVal').textContent = state.prix.toLocaleString('fr-FR', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
    var power = (state.debit / 3600) * dpAvg / (state.eta / 100), kwh = power / 1000 * heures;
    $('kwh').textContent = fr(kwh); $('cost').textContent = fr(kwh * state.prix); $('co2').textContent = fr(kwh * 0.079);
  }

  for (var c = 0; c < ORDER.length; c++) {
    (function (cls) {
      var cb = $('cb_' + cls);
      if (cb) cb.addEventListener('change', function () {
        var anyOther = false, k; for (k in state.disp) { if (k !== cls && state.disp[k] !== false) anyOther = true; }
        var cur = state.disp[cls] !== false;
        if (cur && !anyOther) { render(); return; }
        state.disp[cls] = !cur; render();
      });
      var be = $('be_' + cls);
      if (be) be.addEventListener('click', function () { state.eff = cls; render(); });
    })(ORDER[c]);
  }
  $('inLen').addEventListener('input', function (e) { state.flen = +e.target.value; render(); });
  $('inWid').addEventListener('input', function (e) { state.fwid = +e.target.value; render(); });
  $('inDebit').addEventListener('input', function (e) { state.debit = +e.target.value; render(); });
  $('inDuree').addEventListener('input', function (e) { state.duree = +e.target.value; render(); });
  $('inJours').addEventListener('input', function (e) { state.jours = +e.target.value; render(); });
  $('inEta').addEventListener('input', function (e) { state.eta = +e.target.value; render(); });
  $('inPrix').addEventListener('input', function (e) { state.prix = +e.target.value; render(); });

  var curveSvg = $('curveSvg'), fixedMarks = $('fixedMarks');
  function moveHover(evt) {
    var r = curveSvg.getBoundingClientRect();
    var x = (evt.clientX - r.left) / r.width * 600; x = Math.max(52, Math.min(580, x));
    var v = (x - 52) / 528 * Vmax;
    fixedMarks.style.display = 'none'; hoverG.style.display = '';
    $('hvV').setAttribute('x1', x.toFixed(1)); $('hvV').setAttribute('x2', x.toFixed(1));
    for (var i = 0; i < SERIES.length; i++) {
      var s = SERIES[i], L = lanes[s.k], show = state.disp[s.cls] !== false;
      if (!show) { L.hd.setAttribute('r', 0); L.hh.style.display = 'none'; L.ht.textContent = ''; continue; }
      var y = mapY(pdc(s.co, v));
      L.hd.setAttribute('cx', x.toFixed(1)); L.hd.setAttribute('cy', y.toFixed(1)); L.hd.setAttribute('r', 2.6);
      L.hh.style.display = ''; L.hh.setAttribute('x2', x.toFixed(1)); L.hh.setAttribute('y1', y.toFixed(1)); L.hh.setAttribute('y2', y.toFixed(1));
      L.ht.setAttribute('x', (x + 6).toFixed(1)); L.ht.setAttribute('y', (y + 3).toFixed(1)); L.ht.textContent = fr(pdc(s.co, v)) + ' Pa';
    }
    var hv = $('hvel'); hv.setAttribute('x', x.toFixed(1));
    hv.textContent = v.toLocaleString('fr-FR', { minimumFractionDigits: 2, maximumFractionDigits: 2 }) + ' m/s - ' + fr(v / Vnom * Dnom) + ' m³/h';
  }
  var hit = $('hoverHit'); hit.addEventListener('mousemove', moveHover);
  hit.addEventListener('mouseleave', function () { hoverG.style.display = 'none'; fixedMarks.style.display = ''; });

  render();
})();
</script>"""


def build_series_script(d):
    import json as _json
    series = [{"k": _serie_key(s), "cls": s["cls"], "len": s["len"],
               "co": {"a": s["a"], "b": s["b"], "c": s["c"]}, "color": s["color"]}
              for s in d["courbes"]]
    cls = {k: {"label": v["label"], "iso": v["iso"], "add": v["add"], "rule": v["rule"]}
           for k, v in d["classes_def"].items()}
    order = [c for c in d["classes_order"] if any(s["cls"] == c for s in d["courbes"])]
    disp0 = {c: True for c in order}
    js = SERIES_JS
    js = js.replace("__SERIES__", _json.dumps(series, ensure_ascii=False))
    js = js.replace("__CLS__", _json.dumps(cls, ensure_ascii=False))
    js = js.replace("__ORDER__", _json.dumps(order, ensure_ascii=False))
    js = js.replace("__VMAX__", repr(d.get("vmax", 3.17)))
    js = js.replace("__PMAX__", repr(d.get("pmax", 120)))
    js = js.replace("__DNOM__", str(d.get("debit_nom", 3400)))
    js = js.replace("__HEPA__", "true" if d.get("hepa") else "false")
    js = js.replace("__EFF0__", _json.dumps(d.get("eff0", order[0])))
    js = js.replace("__LEN0__", str(d.get("len0", d["courbes"][0]["len"])))
    js = js.replace("__DISP0__", _json.dumps(disp0))
    return js


def generer_series(d, html):
    nom = d["nom"]; slug = d["slug"]

    # #1 nom produit
    html = html.replace("<title>Fiche technique NETPLY — Netair</title>",
                        f"<title>Fiche technique {nom} — Netair</title>")
    html = html.replace('letter-spacing="2">NETPLY</text>', f'letter-spacing="2">{nom}</text>')
    html = html.replace('letter-spacing:-.6px; text-align:center;">NETPLY</div>',
                        f'letter-spacing:-.6px; text-align:center;">{nom}</div>')
    html = html.replace('letter-spacing:-.3px;">NETPLY</div>', f'letter-spacing:-.3px;">{nom}</div>')

    # #2 sous-titre
    html = html.replace(">Filtre plissé — Préfiltre synthétique</div>", f">{d['soustitre']}</div>")

    # #3 badges
    b1 = d["badges_p1"]; b2 = d["badges_p2"]
    html = html.replace(">ISO 16890 : Coarse 65% / ePM10 50%</div>", f">{b1[0]}</div>")
    html = html.replace(">EN 779 : G4 / M5</div>", f">{b1[1]}</div>")
    html = html.replace('border:1.5px solid #C9D7E8;">EN 13053</div>', f'border:1.5px solid #C9D7E8;">{b1[2]}</div>')
    html = html.replace(">ISO 16890 : Coarse 65% → ePM10 50%</div>", f">{b2[0]}</div>")
    html = html.replace(">EN 779 : G4 → M5</div>", f">{b2[1]}</div>")
    html = html.replace('border:1.5px solid #C9D7E8; white-space:nowrap;">EN 13053</div>',
                        f'border:1.5px solid #C9D7E8; white-space:nowrap;">{b2[2]}</div>')

    # #4 photo + slug
    html = html.replace('src="assets/netply-photo.jpg" alt="Filtre NETPLY"',
                        f'src="assets/{d["photo"]}" alt="{d["photo_alt"]}"')
    for tok in ("netply-photo", "netply-img", "netply-ph", "netply-file"):
        html = re.sub(r"\b" + tok + r"\b", f"{slug}-" + tok.split("-", 1)[1], html)

    # #5 description
    html = sub1(html, r"(text-wrap:pretty;\">)(.*?)(</p>)",
                lambda m: m.group(1) + d["description"] + m.group(3), flags=re.DOTALL)

    # #6 points clés
    html = sub1(html, r"(color:#27313e;\">\n)(.*?)(\n            </div>)",
                lambda m: m.group(1) + build_points_cles(d["points_cles"]) + m.group(3), flags=re.DOTALL)

    # #7 specs
    html = sub1(html, r"(<!-- Caractéristiques techniques -->.*?<tbody>\n)(.*?)(\n            </tbody>)",
                lambda m: m.group(1) + build_specs(d["specs"]) + m.group(3), flags=re.DOTALL)

    # #8 dimensions (lignes explicites par série)
    html = sub1(html, r"(<!-- Dimensions -->.*?<tbody>\n)(.*?)(\n            </tbody>)",
                lambda m: m.group(1) + build_dimensions_series(d) + m.group(3), flags=re.DOTALL)

    # #9 pied de page
    html = html.replace("Fiche n° FT-NETPLY-001", f"Fiche n° {d['fiche']['num']}")
    vd = f"{d['fiche']['version']} — {d['fiche']['date']}"
    html = html.replace("v1.0 — 20/06/2026 — Page 1/2", f"{vd} — Page 1/2")
    html = html.replace("v1.0 — 20/06/2026 — Page 2/2", f"{vd} — Page 2/2")

    # --- échelle Y (pmax) : étiquettes de graduation (le script série gère mapY)
    pmax = d.get("pmax", 120)
    for ypos, k in (("254", 0), ("195.5", 1), ("137", 2), ("78.5", 3), ("20", 4)):
        val = pmax * k / 4
        lab = _frnum(round(val, 1)) if abs(val - round(val)) > 1e-9 else str(int(round(val)))
        html = sub1(html, r'(x="46" y="' + re.escape(ypos) + r'"[^>]*>)[^<]*(</text>)',
                    lambda m, l=lab: m.group(1) + l + m.group(2))

    # --- bloc « Afficher : » (cases par classe)
    html = sub1(
        html,
        r'<div style="display:flex; align-items:center; gap:18px; margin-top:7px;">.*?</div>'
        r'(\n\n        <div style="margin-top:6mm; border:1px solid #E1E7EF;)',
        lambda m: build_series_checkboxes(d) + m.group(1), flags=re.DOTALL)

    # --- courbes + marqueurs nominaux (remplace les 4 paths + fixedMarks)
    html = sub1(html, r'            <!-- 4 courbes.*?\n(            <!-- axes -->)',
                lambda m: build_series_paths(d) + "\n" + m.group(1), flags=re.DOTALL)

    # --- groupe de survol (lanes créées par le JS)
    html = sub1(html, r'            <!-- survol interactif -->.*?\n(            <rect id="hoverHit")',
                lambda m: build_series_hover() + "\n" + m.group(1), flags=re.DOTALL)

    # --- légende (1 entrée par série)
    html = sub1(
        html,
        r'(margin-top:3mm; font-size:11px; color:#3a4654; flex-wrap:wrap;">\n)(.*?)'
        r'(\n            <div style="margin-left:auto; font-style:italic;)',
        lambda m: m.group(1) + build_series_legend(d) + m.group(3), flags=re.DOTALL)

    # --- sélecteur classe × longueur (remplace classe + épaisseur)
    html = sub1(
        html,
        r'            <div style="display:grid; grid-template-columns:1.7fr 1fr; gap:12px;">.*?'
        r'\n(            <div>\n              <div style="display:flex; gap:7px;">)',
        lambda m: build_series_selector(d) + "\n" + m.group(1), flags=re.DOTALL)

    # --- script principal (modèle N-séries)
    html = sub1(html, r'<script>\n\(function \(\) \{\n  "use strict";.*?\n  render\(\);\n\}\)\(\);\n</script>',
                lambda m: build_series_script(d), flags=re.DOTALL)

    # --- note sous le tableau dimensions (optionnelle)
    if "note_dimensions" in d:
        html = sub1(html, r'(margin-top:6px; line-height:1\.45;">)(.*?)(</div>)',
                    lambda m: m.group(1) + d["note_dimensions"] + m.group(3), flags=re.DOTALL)

    # --- mode HEPA : ΔP finale = 2 × initiale (au lieu de la règle ePM ; cf. EN 1822)
    if d.get("hepa"):
        html = html.replace(
            'ΔP finale = min(ΔP init + <span id="effAdd"></span> Pa ; ΔP init × 3) '
            '<span style="color:#b9c2cd;">— EN 13053 · <span id="effRule"></span></span>',
            'ΔP finale = 2 × ΔP initiale<span id="effAdd" style="display:none"></span> '
            '<span style="color:#b9c2cd;">— EN 1822 · <span id="effRule"></span></span>')

    # --- page 1 compacte
    if d.get("compact_p1"):
        html = html.replace("margin:9mm 0 7mm 0;", "margin:6mm 0 5mm 0;")
        html = html.replace('<div style="margin-top:9mm;">', '<div style="margin-top:6mm;">')
        html = html.replace('<div style="margin-top:8mm;">', '<div style="margin-top:6mm;">')

    return html


# ----------------------------------------------- multi-classes (NETPAK…) ----
# Couleurs fixes : 48 mm (navy, trait plein) / 98 mm (teal, pointillé). La classe
# est choisie via un sélecteur ; seules 2 courbes (la classe choisie) sont tracées.
C48 = "#0F3261"
C98 = "#0897A5"


def build_dp_table(d):
    """Tableau ΔP complet : chaque classe × (48/98 mm) × les vitesses mesurées (Pa)."""
    V = d["velocities"]
    head = "".join(
        f'<th style="padding:5px 6px; text-align:right; font-weight:600;">{_frnum(v)}</th>'
        for v in V)
    rows, i = [], 0
    for cls in d["classes_list"]:
        for ep in ("48", "98"):
            i += 1
            tr = ' style="background:#F2F6FB;"' if (i % 2 == 0) else ""
            tds = "".join(
                f'<td style="padding:2px 6px; text-align:right; '
                f"font-family:'IBM Plex Mono',monospace; color:#3a4654;\">{p}</td>"
                for p in cls["points"][ep])
            rows.append(
                f'<tr{tr}>'
                f'<td style="padding:2px 7px; font-weight:700; color:#0F3261;">{cls["label"]}</td>'
                f'<td style="padding:2px 7px; color:#5A6573; font-family:\'IBM Plex Mono\',monospace;">{cls["iso"]}</td>'
                f'<td style="padding:2px 7px; color:#5A6573;">{ep}&nbsp;mm</td>'
                f'{tds}</tr>')
    body = "\n".join("              " + r for r in rows)
    return (
        '        <!-- Perte de charge par classe -->\n'
        '        <div style="margin-top:6mm;">\n'
        '          <div style="display:flex; align-items:center; gap:10px;">\n'
        '            <span style="font-size:11px; font-weight:700; color:#0F3261; letter-spacing:1.2px; text-transform:uppercase; white-space:nowrap;">Perte de charge initiale par classe (Pa)</span>\n'
        '            <span style="flex:1; height:1px; background:#0F3261;"></span>\n'
        '          </div>\n'
        '          <table style="width:100%; border-collapse:collapse; font-size:9.5px; margin-top:7px; white-space:nowrap;">\n'
        '            <thead>\n'
        '              <tr style="background:#0F3261; color:#fff;">\n'
        '                <th style="padding:5px 7px; text-align:left; font-weight:600;">Classe</th>\n'
        '                <th style="padding:5px 7px; text-align:left; font-weight:600;">ISO 16890</th>\n'
        '                <th style="padding:5px 7px; text-align:left; font-weight:600;">Ép.</th>\n'
        f'                <th style="padding:5px 6px; text-align:center; font-weight:600;" colspan="{len(V)}">Vitesse d\'air (m/s)</th>\n'
        '              </tr>\n'
        '              <tr style="background:#1B4279; color:#fff;">\n'
        '                <th></th><th></th><th></th>\n'
        f'                {head}\n'
        '              </tr>\n'
        '            </thead>\n'
        '            <tbody>\n'
        f'{body}\n'
        '            </tbody>\n'
        '          </table>\n'
        '          <div style="font-size:10px; color:#8b97a6; margin-top:3px; line-height:1.4;">Valeurs ΔP initiales mesurées (média propre, air 20 °C) — fiches techniques 2018 (F7 = GREENTEX, basse résistance). F8 (98 mm) : dernier point extrapolé. ΔP finale recommandée = min(ΔP&nbsp;initiale&nbsp;+&nbsp;100&nbsp;Pa ; 3&nbsp;×&nbsp;ΔP&nbsp;initiale) — EN&nbsp;13053.</div>\n'
        '        </div>')


def build_dimensions_multi(d):
    """Tableau dimensions/surfaces (dimension-centré, indépendant de la classe)."""
    rows = []
    for i, dim in enumerate(d["dimensions_multi"], start=1):
        tr = ' style="background:#F2F6FB;"' if (i % 2 == 0) else ""
        c = "padding:4px 7px;"
        cref = ("padding:4px 7px; font-family:'IBM Plex Mono',monospace; color:#0F3261;")
        ref = f'NETPAK S CILIA · [classe] · {dim["L"]}×{dim["H"]}×{dim["P"]} · -A/-P'
        rows.append(
            f'<tr{tr}>'
            f'<td style="{c}">{dim["L"]}</td>'
            f'<td style="{c}">{dim["H"]}</td>'
            f'<td style="{c}">{dim["P"]}</td>'
            f'<td style="{c}">{dim["surface"]}</td>'
            f'<td style="{c}">{fr_debit(dim["debit"])}</td>'
            f'<td style="{c}">M5 → F9</td>'
            f'<td style="{cref}">{ref}</td>'
            f'</tr>')
    rows.append(
        '<tr style="background:#E6F5F7;">'
        '<td style="padding:4px 7px; font-weight:700; color:#0F3261;" colspan="6">Sur mesure</td>'
        '<td style="padding:4px 7px; color:#5A6573; font-style:italic;">sur demande — toute dimension</td></tr>')
    return "\n".join("              " + r for r in rows)


def build_multi_pagebreak(d, num):
    """Ferme la page courante (avec son pied de page n°), ouvre une nouvelle page A4
    avec un en-tête léger. Utilisé pour répartir la fiche multi-classes sur 3 pages."""
    f = d["fiche"]
    vd = f'{f["version"]} — {f["date"]}'
    b2 = d["badges_p2"]
    return f'''        </div>
      <!-- Footer P2 -->
      <div style="margin:0; background:#0F3261; color:#cdd9e8; height:10mm; display:flex; align-items:center; justify-content:space-between; padding:0 12mm; font-size:11px;">
        <span style="font-weight:600; color:#fff;">Netair SAS</span>
        <span style="font-family:'IBM Plex Mono',monospace; color:#9DB8D6; letter-spacing:.3px;">Fiche n° {f["num"]}</span>
        <span>{vd} — Page {num}/3</span>
      </div>
    </div>

    <!-- ============================ PAGE 3 ============================ -->
    <div class="a4">
      <div style="padding:13mm 12mm 0 12mm; flex:1; display:flex; flex-direction:column;">
        <!-- Header page 3 -->
        <div style="position:relative; display:flex; flex-direction:column; align-items:center; justify-content:center; min-height:42px; text-align:center;">
          <div style="font-size:22px; font-weight:700; color:#0F3261; line-height:1; letter-spacing:-.3px;">{d["nom"]}</div>
          <div style="font-size:12px; color:#5A6573; margin-top:3px; font-weight:500;">Calculateur énergétique</div>
          <div style="position:absolute; right:0; top:50%; transform:translateY(-50%); text-align:right;">
            <div style="display:flex; flex-direction:column; align-items:flex-end; gap:5px;">
              <div style="display:inline-block; background:#0F3261; color:#fff; font-size:9px; font-weight:600; padding:4px 9px; border-radius:20px; letter-spacing:.2px; white-space:nowrap;">{b2[0]}</div>
              <div style="display:inline-block; background:#0897A5; color:#fff; font-size:9px; font-weight:600; padding:4px 9px; border-radius:20px; letter-spacing:.2px; white-space:nowrap;">{b2[1]}</div>
              <div style="display:inline-block; background:#fff; color:#0F3261; font-size:9px; font-weight:600; padding:3px 9px; border-radius:20px; border:1.5px solid #C9D7E8; white-space:nowrap;">{b2[2]}</div>
            </div>
          </div>
        </div>
        <div style="height:2px; background:#0F3261; margin:7mm 0 7mm 0;"></div>
'''


def build_dimensions_block_multi(d):
    """Bloc « Dimensions & références » complet (titre + table 7 colonnes + note)."""
    return (
        '        <!-- Dimensions -->\n'
        '        <div style="margin-top:6mm;">\n'
        '          <div style="display:flex; align-items:center; gap:10px;">\n'
        '            <span style="font-size:11px; font-weight:700; color:#0F3261; letter-spacing:1.2px; text-transform:uppercase; white-space:nowrap;">Dimensions &amp; références standard</span>\n'
        '            <span style="flex:1; height:1px; background:#0F3261;"></span>\n'
        '          </div>\n'
        '          <table style="width:100%; border-collapse:collapse; font-size:10px; margin-top:7px; white-space:nowrap;">\n'
        '            <thead>\n'
        '              <tr style="background:#0F3261; color:#fff;">\n'
        '                <th style="padding:6px 7px; text-align:left; font-weight:600;">L (mm)</th>\n'
        '                <th style="padding:6px 7px; text-align:left; font-weight:600;">H (mm)</th>\n'
        '                <th style="padding:6px 7px; text-align:left; font-weight:600;">P (mm)</th>\n'
        '                <th style="padding:6px 7px; text-align:left; font-weight:600;">S. média (m²)</th>\n'
        '                <th style="padding:6px 7px; text-align:left; font-weight:600;">Débit nom. (m³/h)</th>\n'
        '                <th style="padding:6px 7px; text-align:left; font-weight:600;">Classes</th>\n'
        '                <th style="padding:6px 7px; text-align:left; font-weight:600;">Référence complète</th>\n'
        '              </tr>\n'
        '            </thead>\n'
        '            <tbody>\n'
        f'{build_dimensions_multi(d)}\n'
        '            </tbody>\n'
        '          </table>\n'
        f'          <div style="font-size:10px; color:#8b97a6; margin-top:6px; line-height:1.45;">{d["dim_note"]}</div>\n'
        '        </div>')


def build_multi_section(d):
    """Page 2 (dimensions + ΔP + courbe) + saut de page + page 3 (calculateur)."""
    classes = d["classes_list"]
    vmax = d["vmax"]
    pmax = d.get("pmax", 200)
    dnom = d.get("debit_nom", 3400)
    vnom = (dnom / 3600) / AREF
    selbtns = "\n              ".join(
        f'<button id="cls_{c["id"]}" type="button" style="flex:1; padding:7px 3px; border:none; border-radius:6px; font-size:11px; font-weight:600; cursor:pointer; font-family:inherit;">{c["label"]}</button>'
        for c in classes)
    # sélecteur d'efficacité PROPRE au calculateur (indépendant de la courbe)
    calcbtns = "\n                  ".join(
        f'<button id="ce_{c["id"]}" type="button" style="flex:1; padding:7px 2px; border:none; border-radius:6px; font-size:9px; font-weight:600; cursor:pointer; font-family:inherit; white-space:nowrap;">{c["iso"]} ({c["label"]})</button>'
        for c in classes)
    grid = build_gridlines(vmax, vnom)
    xlab = build_xlabels(vmax)
    yvals = [("254", 0), ("195.5", 1), ("137", 2), ("78.5", 3), ("20", 4)]
    ylab = "\n".join(
        f'            <text x="46" y="{yp}" text-anchor="end" font-family="\'IBM Plex Mono\',monospace" font-size="11" fill="#5A6573">{int(round(pmax * k / 4))}</text>'
        for yp, k in yvals)
    annot = _frnum(round(vnom, 1)) + f" m/s ≈ {dnom} m³/h · 592×592"
    xn = f"{_mapx(vnom, vmax):.1f}"
    dims_block = build_dimensions_block_multi(d)
    dp_block = build_dp_table(d)
    pagebreak = build_multi_pagebreak(d, 2)

    return f'''{dims_block}

{dp_block}

        <!-- Section courbe -->
        <div style="display:flex; align-items:center; gap:10px;">
          <span style="font-size:11px; font-weight:700; color:#0F3261; letter-spacing:1.2px; text-transform:uppercase; white-space:nowrap;">Courbe vitesse / perte de charge</span>
          <span style="flex:1; height:1px; background:#0F3261;"></span>
        </div>
        <div style="display:flex; align-items:center; gap:14px; margin-top:4px; flex-wrap:wrap;">
          <span style="font-size:11px; font-weight:600; color:#5A6573; white-space:nowrap;">Classe :</span>
          <div style="display:flex; background:#EEF3F9; border:1px solid #D5E0EF; border-radius:9px; padding:3px; gap:3px; min-width:230px;">
              {selbtns}
          </div>
          <span id="clsIso" style="font-size:11.5px; color:#0897A5; font-weight:600; font-family:'IBM Plex Mono',monospace;"></span>
        </div>

        <div style="margin-top:3mm; border:1px solid #E1E7EF; border-radius:8px; padding:3mm 6mm 2mm 4mm; background:#FCFDFE;">
          <svg id="curveSvg" viewBox="0 0 600 292" style="width:100%; height:auto; display:block;">
            <line x1="52" y1="16" x2="580" y2="16" stroke="#EDF1F6" stroke-width="1"></line>
            <line x1="52" y1="74.5" x2="580" y2="74.5" stroke="#EDF1F6" stroke-width="1"></line>
            <line x1="52" y1="133" x2="580" y2="133" stroke="#EDF1F6" stroke-width="1"></line>
            <line x1="52" y1="191.5" x2="580" y2="191.5" stroke="#EDF1F6" stroke-width="1"></line>
            <!-- vertical gridlines -->
{grid}
            <!-- 2 courbes : classe sélectionnée — 48 mm (navy plein) / 98 mm (teal pointillé) -->
            <path id="p98" d="" fill="none" stroke="{C98}" stroke-width="2.2" stroke-dasharray="5 3" stroke-linecap="round" stroke-linejoin="round"></path>
            <path id="p48" d="" fill="none" stroke="{C48}" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"></path>
            <g id="fixedMarks">
            <circle id="c48" cx="0" cy="0" r="0" fill="{C48}"></circle>
            <circle id="c98" cx="0" cy="0" r="0" fill="{C98}"></circle>
            <text id="t48" x="0" y="0" text-anchor="end" paint-order="stroke" stroke="#fff" stroke-width="3.5" stroke-linejoin="round" font-family="'IBM Plex Mono',monospace" font-size="10" font-weight="600" fill="{C48}"></text>
            <text id="t98" x="0" y="0" text-anchor="start" paint-order="stroke" stroke="#fff" stroke-width="3.5" stroke-linejoin="round" font-family="'IBM Plex Mono',monospace" font-size="10" font-weight="600" fill="{C98}"></text>
            </g>
            <!-- axes -->
            <line x1="52" y1="16" x2="52" y2="250" stroke="#0F3261" stroke-width="1.4"></line>
            <line x1="52" y1="250" x2="580" y2="250" stroke="#0F3261" stroke-width="1.4"></line>
            <!-- y tick labels -->
{ylab}
            <!-- x tick labels -->
{xlab}
            <!-- axis titles -->
            <text x="316" y="285" text-anchor="middle" font-family="'Instrument Sans',sans-serif" font-size="11.5" font-weight="600" fill="#0F3261">Vitesse d'air (m/s)</text>
            <text x="{xn}" y="11" text-anchor="middle" font-family="'Instrument Sans',sans-serif" font-size="9.5" font-weight="600" fill="#0F3261">{annot}</text>
            <text transform="rotate(-90 16 133)" x="16" y="133" text-anchor="middle" font-family="'Instrument Sans',sans-serif" font-size="11.5" font-weight="600" fill="#0F3261">Perte de charge (Pa)</text>
            <!-- survol interactif -->
            <g id="hoverG" style="display:none;">
              <line id="hvV" x1="0" y1="16" x2="0" y2="250" stroke="#0F3261" stroke-width="1" stroke-dasharray="3 3" opacity="0.4"></line>
              <line id="hh1" x1="52" y1="0" x2="0" y2="0" stroke="{C48}" stroke-width="1" stroke-dasharray="3 3" opacity="0.32"></line>
              <line id="hh2" x1="52" y1="0" x2="0" y2="0" stroke="{C98}" stroke-width="1" stroke-dasharray="3 3" opacity="0.32"></line>
              <circle id="hd1" r="0" fill="{C48}"></circle>
              <circle id="hd2" r="0" fill="{C98}"></circle>
              <text id="ht1" text-anchor="start" paint-order="stroke" stroke="#fff" stroke-width="3.5" stroke-linejoin="round" font-family="'IBM Plex Mono',monospace" font-size="10" font-weight="600" fill="{C48}"></text>
              <text id="ht2" text-anchor="start" paint-order="stroke" stroke="#fff" stroke-width="3.5" stroke-linejoin="round" font-family="'IBM Plex Mono',monospace" font-size="10" font-weight="600" fill="{C98}"></text>
              <text id="hvel" x="0" y="244" text-anchor="middle" paint-order="stroke" stroke="#fff" stroke-width="3.5" stroke-linejoin="round" font-family="'IBM Plex Mono',monospace" font-size="10.5" font-weight="700" fill="#0F3261"></text>
            </g>
            <rect id="hoverHit" x="52" y="16" width="528" height="234" fill="transparent" style="cursor:crosshair;"></rect>
          </svg>
          <div style="display:flex; gap:14px 18px; align-items:center; margin-top:1mm; font-size:11px; color:#3a4654; flex-wrap:wrap;">
            <div id="leg48" style="display:flex; align-items:center; gap:7px;"><span style="width:22px; height:3px; background:{C48}; display:inline-block; border-radius:2px;"></span><span id="leg48t"></span></div>
            <div id="leg98" style="display:flex; align-items:center; gap:7px;"><span style="width:22px; height:0; border-top:3px dashed {C98}; display:inline-block;"></span><span id="leg98t"></span></div>
            <div style="margin-left:auto; font-style:italic; color:#5A6573;">Média propre — air à 20 °C</div>
          </div>
        </div>
{pagebreak}
        <!-- Section calculateur -->
        <div style="display:flex; align-items:center; gap:10px; margin-top:7mm;">
          <span style="font-size:11px; font-weight:700; color:#0F3261; letter-spacing:1.2px; text-transform:uppercase; white-space:nowrap;">Calculateur énergétique</span>
          <span style="flex:1; height:1px; background:#0F3261;"></span>
        </div>
        <div style="font-size:12px; color:#5A6573; margin-top:5px; line-height:1.5;">Estimez la consommation du ventilateur liée à la perte de charge du filtre sur une année de fonctionnement. Choisissez la classe d'efficacité et l'épaisseur (indépendamment de la courbe), puis ajustez les paramètres.</div>

        <div style="display:grid; grid-template-columns:1fr 80mm; gap:7mm; margin-top:5mm; align-items:stretch;">
          <div style="display:flex; flex-direction:column; gap:11px; padding-top:1px;">
            <div style="display:grid; grid-template-columns:1.7fr 1fr; gap:12px;">
              <div>
                <div style="font-size:10px; font-weight:700; letter-spacing:.7px; text-transform:uppercase; color:#9aa6b4; margin-bottom:7px;">Classe d'efficacité</div>
                <div style="display:flex; background:#EEF3F9; border:1px solid #D5E0EF; border-radius:9px; padding:3px; gap:3px;">
                  {calcbtns}
                </div>
              </div>
              <div>
                <div style="font-size:10px; font-weight:700; letter-spacing:.7px; text-transform:uppercase; color:#9aa6b4; margin-bottom:7px;">Épaisseur</div>
                <div style="display:flex; background:#EEF3F9; border:1px solid #D5E0EF; border-radius:9px; padding:3px; gap:3px;">
                  <button id="btnThick48" type="button">48 mm</button>
                  <button id="btnThick98" type="button">98 mm</button>
                </div>
              </div>
            </div>
            <div>
              <div style="display:flex; gap:7px;">
                <div style="flex:1; background:#F7F9FC; border:1px solid #E4EBF3; border-radius:8px; padding:8px 6px; text-align:center;"><div style="font-size:8.5px; font-weight:700; letter-spacing:.4px; text-transform:uppercase; color:#9aa6b4;">ΔP initiale</div><div style="font-family:'IBM Plex Mono',monospace; font-size:14px; color:#0F3261; margin-top:3px;"><span id="dpInit"></span><span style="font-size:9px; color:#9aa6b4;"> Pa</span></div></div>
                <div style="flex:1; background:#F7F9FC; border:1px solid #E4EBF3; border-radius:8px; padding:8px 6px; text-align:center;"><div style="font-size:8.5px; font-weight:700; letter-spacing:.4px; text-transform:uppercase; color:#9aa6b4;">ΔP finale</div><div style="font-family:'IBM Plex Mono',monospace; font-size:14px; color:#0F3261; margin-top:3px;"><span id="dpFinal"></span><span style="font-size:9px; color:#9aa6b4;"> Pa</span></div></div>
                <div style="flex:1; background:#F7F9FC; border:1px solid #E4EBF3; border-radius:8px; padding:8px 6px; text-align:center;"><div style="font-size:8.5px; font-weight:700; letter-spacing:.4px; text-transform:uppercase; color:#0897A5;">ΔP moyenne</div><div style="font-family:'IBM Plex Mono',monospace; font-size:14px; color:#0897A5; font-weight:500; margin-top:3px;"><span id="dpAvg"></span><span style="font-size:9px; color:#9aa6b4;"> Pa</span></div></div>
              </div>
              <div style="font-size:9.5px; color:#9aa6b4; margin-top:7px; line-height:1.4;">ΔP finale = min(ΔP init + <span id="effAdd"></span> Pa ; ΔP init × 3) <span style="color:#b9c2cd;">— EN 13053 · <span id="effRule"></span></span></div>
            </div>
            <div>
              <div style="display:flex; justify-content:space-between; align-items:baseline; margin-bottom:6px;">
                <span style="font-size:12.5px; font-weight:600; color:#0F3261;">Dimensions du filtre <span style="font-weight:400; color:#8b97a6;">(mm)</span></span>
                <span style="font-family:'IBM Plex Mono',monospace; font-size:11.5px; color:#0897A5;"><span id="area"></span> m² · <span id="vel"></span> m/s</span>
              </div>
              <div style="display:flex; gap:10px; align-items:center;">
                <div style="flex:1; display:flex; align-items:center; gap:7px;">
                  <span style="font-size:11px; font-weight:600; color:#5A6573; width:12px;">L</span>
                  <input type="number" id="inLen" min="50" max="2000" value="592" style="width:100%; font-family:'IBM Plex Mono',monospace; font-size:13px; color:#0F3261; border:1.5px solid #C9D7E8; border-radius:6px; padding:7px 9px; outline:none; box-sizing:border-box;">
                </div>
                <span style="color:#8b97a6; font-size:13px;">×</span>
                <div style="flex:1; display:flex; align-items:center; gap:7px;">
                  <span style="font-size:11px; font-weight:600; color:#5A6573; width:14px;">H</span>
                  <input type="number" id="inWid" min="50" max="2000" value="592" style="width:100%; font-family:'IBM Plex Mono',monospace; font-size:13px; color:#0F3261; border:1.5px solid #C9D7E8; border-radius:6px; padding:7px 9px; outline:none; box-sizing:border-box;">
                </div>
              </div>
            </div>
            <div>
              <div style="display:flex; justify-content:space-between; align-items:baseline; margin-bottom:5px;">
                <span style="font-size:12.5px; font-weight:600; color:#0F3261;">Débit d'air</span>
                <span style="font-family:'IBM Plex Mono',monospace; font-size:12.5px; color:#0897A5; font-weight:500;"><span id="debitVal"></span> m³/h</span>
              </div>
              <input type="range" id="inDebit" min="500" max="6000" step="50" value="{dnom}" style="width:100%; accent-color:#0897A5;">
            </div>
            <div>
              <div style="display:flex; justify-content:space-between; align-items:baseline; margin-bottom:5px;">
                <span style="font-size:12.5px; font-weight:600; color:#0F3261;">Durée de fonctionnement</span>
                <span style="font-family:'IBM Plex Mono',monospace; font-size:12.5px; color:#0897A5; font-weight:500;"><span id="dureeVal"></span> h/jour</span>
              </div>
              <input type="range" id="inDuree" min="0" max="24" step="0.5" value="24" style="width:100%; accent-color:#0897A5;">
            </div>
            <div>
              <div style="display:flex; justify-content:space-between; align-items:baseline; margin-bottom:5px;">
                <span style="font-size:12.5px; font-weight:600; color:#0F3261;">Jours de fonctionnement</span>
                <span style="font-family:'IBM Plex Mono',monospace; font-size:12.5px; color:#0897A5; font-weight:500;"><span id="joursVal"></span> j/an · <span id="heuresVal"></span> h/an</span>
              </div>
              <input type="range" id="inJours" min="0" max="365" step="5" value="250" style="width:100%; accent-color:#0897A5;">
            </div>
            <div>
              <div style="display:flex; justify-content:space-between; align-items:baseline; margin-bottom:5px;">
                <span style="font-size:12.5px; font-weight:600; color:#0F3261;">Rendement moto-ventilateur</span>
                <span style="font-family:'IBM Plex Mono',monospace; font-size:12.5px; color:#0897A5; font-weight:500;"><span id="etaVal"></span> %</span>
              </div>
              <input type="range" id="inEta" min="30" max="85" step="1" value="55" style="width:100%; accent-color:#0897A5;">
            </div>
            <div>
              <div style="display:flex; justify-content:space-between; align-items:baseline; margin-bottom:5px;">
                <span style="font-size:12.5px; font-weight:600; color:#0F3261;">Prix de l'électricité</span>
                <span style="font-family:'IBM Plex Mono',monospace; font-size:12.5px; color:#0897A5; font-weight:500;"><span id="prixVal"></span> €/kWh</span>
              </div>
              <input type="range" id="inPrix" min="0.05" max="0.40" step="0.01" value="0.18" style="width:100%; accent-color:#0897A5;">
            </div>
          </div>

          <div style="background:#F6FAFD; border:1px solid #E1EAF3; border-radius:12px; padding:6mm; display:flex; flex-direction:column; justify-content:center; gap:5mm;">
            <div style="text-align:center;">
              <div style="font-size:10px; font-weight:700; letter-spacing:1.2px; text-transform:uppercase; color:#0897A5;">Coût énergétique</div>
              <div style="display:flex; align-items:baseline; justify-content:center; gap:6px; margin-top:8px; white-space:nowrap;"><span style="font-size:52px; font-weight:700; color:#0897A5; line-height:.9; font-variant-numeric:tabular-nums;" id="cost"></span><span style="font-size:18px; color:#0897A5; font-weight:600;">€</span></div>
              <div style="font-size:10px; color:#9aa6b4; margin-top:7px;">sur <span id="heures3"></span> h</div>
            </div>
            <div style="height:1px; background:#E1EAF3;"></div>
            <div style="text-align:center;">
              <div style="font-size:9.5px; font-weight:700; letter-spacing:1px; text-transform:uppercase; color:#8b97a6;">Consommation énergétique</div>
              <div style="margin-top:6px; white-space:nowrap;"><span style="font-size:30px; font-weight:700; color:#0F3261; font-variant-numeric:tabular-nums;" id="kwh"></span> <span style="font-size:12px; color:#9aa6b4;">kWh/an</span></div>
              <div style="font-size:9.5px; color:#9aa6b4; margin-top:4px;">sur <span id="heures2"></span> h/an</div>
            </div>
            <div style="height:1px; background:#E1EAF3;"></div>
            <div style="text-align:center;">
              <div style="font-size:11.5px; font-weight:700; letter-spacing:1px; text-transform:uppercase; color:#8b97a6;">Impact carbone</div>
              <div style="margin-top:6px; white-space:nowrap;"><span style="font-size:25px; font-weight:700; color:#0F3261; font-variant-numeric:tabular-nums;" id="co2"></span> <span style="font-size:13px; color:#9aa6b4;">kg CO₂/an</span></div>
            </div>
          </div>
        </div>

        <div style="margin-top:6mm; background:#F2F6FB; border-left:3px solid #0897A5; padding:9px 14px; font-size:10.5px; color:#5A6573; line-height:1.55;">
          <strong style="color:#0F3261;">Méthode :</strong> P = (Q ⁄ 3600) × ΔP ⁄ η &nbsp;·&nbsp; Énergie = P × heures de fonctionnement. Valeurs indicatives à but de comparaison — base CO₂ 0,079 kgCO₂/kWh — 79 g (mix électrique France). η = rendement global du moto-ventilateur.
        </div>'''


def build_multi_js(d):
    """Bloc <script> du composant interactif multi-classes."""
    classes = d["classes_list"]
    vmax = d["vmax"]
    pmax = d.get("pmax", 200)
    dnom = d.get("debit_nom", 3400)
    eff0 = d.get("eff_default", classes[0]["id"])

    def poly_entry(c):
        p = c["poly"]
        return (f"    {c['id']}: {{ 48: {_co(p['48'])}, 98: {_co(p['98'])} }}")
    poly = ",\n".join(poly_entry(c) for c in classes)
    add = ", ".join(f"{c['id']}: {c['add']}" for c in classes)
    rule = ", ".join(f"{c['id']}: '{c['rule']}'" for c in classes)
    lab = ", ".join(f"{c['id']}: '{c['label']}'" for c in classes)
    iso = ", ".join(f"{c['id']}: '{c['iso']}'" for c in classes)
    ids = ", ".join(f"'{c['id']}'" for c in classes)

    return f'''<script>
(function () {{
  "use strict";
  var POLY = {{
{poly}
  }};
  var ADD  = {{ {add} }};
  var RULE = {{ {rule} }};
  var LAB  = {{ {lab} }};
  var ISO  = {{ {iso} }};
  var IDS  = [{ids}];

  var Vmax = {_jsf(vmax)};
  var Pmax = {pmax};
  var Aref = 0.592 * 0.592;
  var Dnom = {dnom};
  var Vnom = (Dnom / 3600) / Aref;

  // eff = classe affichée sur la COURBE ; calcEff = classe du CALCULATEUR (indépendants)
  var state = {{ eff: '{eff0}', calcEff: '{eff0}', thick: 48, debit: {dnom}, duree: 24, jours: 250, eta: 55, prix: 0.18, len: 592, wid: 592 }};

  var fr = function (n) {{ return Math.round(n).toLocaleString('fr-FR'); }};
  var $  = function (id) {{ return document.getElementById(id); }};
  var mapX = function (v) {{ return 52 + (v / Vmax) * 528; }};
  var mapY = function (p) {{ return 250 - (Math.min(p, Pmax) / Pmax) * 234; }};
  function pdc(co, v) {{ return Math.max(0, co.a * v * v + co.b * v + co.c); }}
  function curve(co) {{
    var pts = [], v;
    for (v = 0; v <= Vmax - 1e-9; v += 0.1) pts.push(mapX(v).toFixed(1) + ',' + mapY(pdc(co, v)).toFixed(1));
    pts.push(mapX(Vmax).toFixed(1) + ',' + mapY(pdc(co, Vmax)).toFixed(1));
    return 'M' + pts.join(' L');
  }}

  var ON  = 'background:#0897A5; color:#fff; box-shadow:0 1px 3px rgba(8,151,165,.4);';
  var OFF = 'background:transparent; color:#5A6573; box-shadow:none;';
  var BTN = 'flex:1; padding:7px 3px; border:none; border-radius:6px; font-size:10.5px; font-weight:600; cursor:pointer; font-family:inherit; transition:all .12s; white-space:nowrap; ';
  var SEL = 'flex:1; padding:7px 3px; border:none; border-radius:6px; font-size:11px; font-weight:600; cursor:pointer; font-family:inherit; transition:all .12s; white-space:nowrap; ';
  var CEB = 'flex:1; padding:7px 2px; border:none; border-radius:6px; font-size:9px; font-weight:600; cursor:pointer; font-family:inherit; transition:all .12s; white-space:nowrap; ';

  function render() {{
    var eff = state.eff;          // courbe
    var ceff = state.calcEff;     // calculateur (indépendant)
    var co = POLY[ceff][state.thick];
    var co48 = POLY[eff][48], co98 = POLY[eff][98];

    var areaNum = (Math.max(50, state.len) / 1000) * (Math.max(50, state.wid) / 1000);
    var velNum = (state.debit / 3600) / areaNum;
    var dpInitNum = pdc(co, velNum);
    var dpFinalNum = Math.min(dpInitNum + ADD[ceff], dpInitNum * 3);
    var dpAvgNum = (dpFinalNum / 2) * 0.85;

    $('p48').setAttribute('d', curve(co48));
    $('p98').setAttribute('d', curve(co98));

    var mx = mapX(Vnom);
    function pt(cid, tid, yPa, dx, dy) {{
      var y = mapY(yPa), e = $(cid), t = $(tid);
      e.setAttribute('cx', mx.toFixed(1)); e.setAttribute('cy', y.toFixed(1)); e.setAttribute('r', 3.2);
      t.setAttribute('x', (mx + dx).toFixed(1)); t.setAttribute('y', (y + dy).toFixed(1)); t.textContent = fr(yPa) + ' Pa';
    }}
    pt('c48', 't48', pdc(co48, Vnom), -9, -8);
    pt('c98', 't98', pdc(co98, Vnom), 9, 14);

    // sélecteur de classe de la COURBE
    IDS.forEach(function (id) {{
      var b = $('cls_' + id);
      if (b) b.setAttribute('style', SEL + (id === eff ? ON : OFF));
      var c = $('ce_' + id);   // sélecteur d'efficacité du CALCULATEUR
      if (c) c.setAttribute('style', CEB + (id === ceff ? ON : OFF));
    }});
    $('clsIso').textContent = LAB[eff] + ' · ' + ISO[eff];
    $('leg48t').textContent = LAB[eff] + ' · ' + ISO[eff] + ' — 48 mm';
    $('leg98t').textContent = LAB[eff] + ' · ' + ISO[eff] + ' — 98 mm';

    $('btnThick48').setAttribute('style', BTN + (state.thick === 48 ? ON : OFF));
    $('btnThick98').setAttribute('style', BTN + (state.thick === 98 ? ON : OFF));

    $('dpInit').textContent = fr(dpInitNum);
    $('dpFinal').textContent = fr(dpFinalNum);
    $('dpAvg').textContent = fr(dpAvgNum);
    $('effAdd').textContent = ADD[ceff];
    $('effRule').textContent = RULE[ceff];

    $('area').textContent = areaNum.toLocaleString('fr-FR', {{ minimumFractionDigits: 2, maximumFractionDigits: 2 }});
    $('vel').textContent = velNum.toLocaleString('fr-FR', {{ minimumFractionDigits: 1, maximumFractionDigits: 1 }});

    var heuresNum = Math.round(state.duree * state.jours);
    $('debitVal').textContent = state.debit;
    $('dureeVal').textContent = state.duree.toLocaleString('fr-FR', {{ minimumFractionDigits: 0, maximumFractionDigits: 1 }});
    $('joursVal').textContent = state.jours;
    $('heuresVal').textContent = fr(heuresNum);
    $('heures2').textContent = fr(heuresNum);
    $('heures3').textContent = fr(heuresNum);
    $('etaVal').textContent = state.eta;
    $('prixVal').textContent = state.prix.toLocaleString('fr-FR', {{ minimumFractionDigits: 2, maximumFractionDigits: 2 }});

    var power = (state.debit / 3600) * dpAvgNum / (state.eta / 100);
    var kwhNum = power / 1000 * heuresNum;
    $('kwh').textContent = fr(kwhNum);
    $('cost').textContent = fr(kwhNum * state.prix);
    $('co2').textContent = fr(kwhNum * 0.079);
  }}

  IDS.forEach(function (id) {{
    var b = $('cls_' + id);
    if (b) b.addEventListener('click', function () {{ state.eff = id; render(); }});
    var c = $('ce_' + id);
    if (c) c.addEventListener('click', function () {{ state.calcEff = id; render(); }});
  }});
  $('btnThick48').addEventListener('click', function () {{ state.thick = 48; render(); }});
  $('btnThick98').addEventListener('click', function () {{ state.thick = 98; render(); }});
  $('inLen').addEventListener('input', function (e) {{ state.len = +e.target.value; render(); }});
  $('inWid').addEventListener('input', function (e) {{ state.wid = +e.target.value; render(); }});
  $('inDebit').addEventListener('input', function (e) {{ state.debit = +e.target.value; render(); }});
  $('inDuree').addEventListener('input', function (e) {{ state.duree = +e.target.value; render(); }});
  $('inJours').addEventListener('input', function (e) {{ state.jours = +e.target.value; render(); }});
  $('inEta').addEventListener('input', function (e) {{ state.eta = +e.target.value; render(); }});
  $('inPrix').addEventListener('input', function (e) {{ state.prix = +e.target.value; render(); }});

  var curveSvg = $('curveSvg'), fixedMarks = $('fixedMarks'), hoverG = $('hoverG');
  function moveHover(evt) {{
    var r = curveSvg.getBoundingClientRect();
    var x = (evt.clientX - r.left) / r.width * 600;
    x = Math.max(52, Math.min(580, x));
    var v = (x - 52) / 528 * Vmax;
    var eff = state.eff;
    fixedMarks.style.display = 'none';
    hoverG.style.display = '';
    $('hvV').setAttribute('x1', x.toFixed(1)); $('hvV').setAttribute('x2', x.toFixed(1));
    function lane(n, yPa, dy) {{
      var hd = $('hd' + n), hh = $('hh' + n), ht = $('ht' + n), y = mapY(yPa);
      hd.setAttribute('cx', x.toFixed(1)); hd.setAttribute('cy', y.toFixed(1)); hd.setAttribute('r', 3);
      hh.style.display = ''; hh.setAttribute('x2', x.toFixed(1)); hh.setAttribute('y1', y.toFixed(1)); hh.setAttribute('y2', y.toFixed(1));
      ht.setAttribute('x', (x + 7).toFixed(1)); ht.setAttribute('y', (y + dy).toFixed(1)); ht.textContent = fr(yPa) + ' Pa';
    }}
    lane(1, pdc(POLY[eff][48], v), -5);
    lane(2, pdc(POLY[eff][98], v), 13);
    var hv = $('hvel');
    hv.setAttribute('x', x.toFixed(1));
    hv.textContent = v.toLocaleString('fr-FR', {{ minimumFractionDigits: 2, maximumFractionDigits: 2 }}) + ' m/s - ' + fr(v / Vnom * Dnom) + ' m³/h';
  }}
  var hit = $('hoverHit');
  hit.addEventListener('mousemove', moveHover);
  hit.addEventListener('mouseleave', function () {{ hoverG.style.display = 'none'; fixedMarks.style.display = ''; }});

  render();
}})();
</script>'''


def _jsf(x):
    """Nombre pour le JS : 3.17 -> '3.17', 2 -> '2'."""
    return f"{x:g}"


def generer_multi(d, html):
    """Fiche multi-classes (NETPAK…) : sélecteur 5 classes, 2 courbes 48/98,
    tableau ΔP complet, surface m²/m², variantes cadre -A/-P. Remplacements
    chirurgicaux dans le gabarit ; le chemin 2-classes (NETPLY) reste intact."""
    nom = d["nom"]
    slug = d["slug"]

    # #1 nom produit
    html = html.replace("<title>Fiche technique NETPLY — Netair</title>",
                        f"<title>Fiche technique {nom} — Netair</title>")
    html = html.replace('letter-spacing="2">NETPLY</text>', f'letter-spacing="2">{nom}</text>')
    html = html.replace('letter-spacing:-.6px; text-align:center;">NETPLY</div>',
                        f'letter-spacing:-.6px; text-align:center;">{nom}</div>')
    html = html.replace('letter-spacing:-.3px;">NETPLY</div>', f'letter-spacing:-.3px;">{nom}</div>')

    # #2 sous-titre
    html = html.replace(">Filtre plissé — Préfiltre synthétique</div>", f">{d['soustitre']}</div>")

    # #3 badges
    b1 = d["badges_p1"]; b2 = d["badges_p2"]
    html = html.replace(">ISO 16890 : Coarse 65% / ePM10 50%</div>", f">{b1[0]}</div>")
    html = html.replace(">EN 779 : G4 / M5</div>", f">{b1[1]}</div>")
    html = html.replace('border:1.5px solid #C9D7E8;">EN 13053</div>', f'border:1.5px solid #C9D7E8;">{b1[2]}</div>')
    html = html.replace(">ISO 16890 : Coarse 65% → ePM10 50%</div>", f">{b2[0]}</div>")
    html = html.replace(">EN 779 : G4 → M5</div>", f">{b2[1]}</div>")
    html = html.replace('border:1.5px solid #C9D7E8; white-space:nowrap;">EN 13053</div>',
                        f'border:1.5px solid #C9D7E8; white-space:nowrap;">{b2[2]}</div>')

    # #4 photo + slug
    html = html.replace('src="assets/netply-photo.jpg" alt="Filtre NETPLY"',
                        f'src="assets/{d["photo"]}" alt="{d["photo_alt"]}"')
    for tok in ("netply-photo", "netply-img", "netply-ph", "netply-file"):
        html = re.sub(r"\b" + tok + r"\b", f"{slug}-" + tok.split("-", 1)[1], html)

    # #5 description
    html = sub1(html, r"(text-wrap:pretty;\">)(.*?)(</p>)",
                lambda m: m.group(1) + d["description"] + m.group(3), flags=re.DOTALL)

    # #6 points clés
    html = sub1(html, r"(color:#27313e;\">\n)(.*?)(\n            </div>)",
                lambda m: m.group(1) + build_points_cles(d["points_cles"]) + m.group(3), flags=re.DOTALL)

    # #7 specs
    html = sub1(html, r"(<!-- Caractéristiques techniques -->.*?<tbody>\n)(.*?)(\n            </tbody>)",
                lambda m: m.group(1) + build_specs(d["specs"]) + m.group(3), flags=re.DOTALL)

    # #8 dimensions : retirées de la page 1 (relocalisées en page 2 par build_multi_section)
    html = sub1(
        html,
        r"\n        <!-- Dimensions -->\n        <div style=\"margin-top:8mm;\">.*?\n        </div>",
        lambda m: "", flags=re.DOTALL)

    # #9 pied de page (fiche 3 pages : P1 = 1/3, le footer du gabarit P2 devient 3/3)
    html = html.replace("Fiche n° FT-NETPLY-001", f"Fiche n° {d['fiche']['num']}")
    vd = f"{d['fiche']['version']} — {d['fiche']['date']}"
    html = html.replace("v1.0 — 20/06/2026 — Page 1/2", f"{vd} — Page 1/3")
    html = html.replace("v1.0 — 20/06/2026 — Page 2/2", f"{vd} — Page 3/3")

    # remplacer toute la section courbe + calculateur (page 2)
    html = sub1(html,
                r"        <!-- Section courbe -->.*?rendement global du moto-ventilateur\.\s*</div>",
                lambda m: build_multi_section(d), flags=re.DOTALL)

    # remplacer le script principal du composant interactif
    html = sub1(html,
                r'<script>\n\(function \(\) \{\n  "use strict";.*?\n  render\(\);\n\}\)\(\);\n</script>',
                lambda m: build_multi_js(d), flags=re.DOTALL)

    # page 1 compacte
    if d.get("compact_p1"):
        html = html.replace("margin:9mm 0 7mm 0;", "margin:6mm 0 5mm 0;")
        html = html.replace('<div style="margin-top:9mm;">', '<div style="margin-top:6mm;">')
        html = html.replace('<div style="margin-top:8mm;">', '<div style="margin-top:6mm;">')

    return html


# ----------------------------------------------------------------- moteur ----
def generer(d, html):
    if d.get("series"):
        return generer_series(d, html)
    if d.get("multi_classe"):
        return generer_multi(d, html)
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
        aref = d.get("aref", AREF)            # HEPA : aire de réf. 610² ≠ 592²
        dim_ref = d.get("dim_ref", "592×592")
        vnom = (dnom / 3600) / aref
        # constantes JS
        html = html.replace("var Vmax = 3.17;", f"var Vmax = {vmax};")
        if d.get("aref"):
            html = html.replace("var Aref = 0.592 * 0.592;", f"var Aref = {aref};")
            # dimensions par défaut du calculateur = cellule réelle (ex. 610×610) au lieu de 592
            cl, cw = (re.split(r"[×x]", dim_ref) + ["592", "592"])[:2]
            html = html.replace('id="inLen" min="50" max="2000" value="592"',
                                f'id="inLen" min="50" max="2000" value="{cl}"')
            html = html.replace('id="inWid" min="50" max="2000" value="592"',
                                f'id="inWid" min="50" max="2000" value="{cw}"')
            html = html.replace("len: 592, wid: 592", f"len: {cl}, wid: {cw}")
        html = html.replace("var Vnom = (3400 / 3600) / Aref;",
                            f"var Vnom = ({dnom} / 3600) / Aref;")
        html = html.replace("fr(v / Vnom * 3400)", f"fr(v / Vnom * {dnom})")
        # débit par défaut du calculateur (+ plage du curseur, configurable)
        dmin = d.get("debit_min", 500); dmax = d.get("debit_max", 6000); dstep = d.get("debit_step", 50)
        html = html.replace('id="inDebit" min="500" max="6000" step="50" value="3400"',
                            f'id="inDebit" min="{dmin}" max="{dmax}" step="{dstep}" value="{dnom}"')
        html = html.replace("debit: 3400,", f"debit: {dnom},")
        # axe X : graduations, point nominal, étiquettes, annotation
        html = sub1(html, r"(<!-- vertical gridlines -->\n)(.*?)(\n            <!-- 4 courbes)",
                    lambda m: m.group(1) + build_gridlines(vmax, vnom) + m.group(3), flags=re.DOTALL)
        html = sub1(html, r"(<!-- x tick labels -->\n)(.*?)(\n            <!-- axis titles)",
                    lambda m: m.group(1) + build_xlabels(vmax) + m.group(3), flags=re.DOTALL)
        _prec = 2 if vmax <= 1 else 1     # HEPA basse vitesse : 2 décimales
        annot = f"{vnom:.{_prec}f}".replace(".", ",") + f" m/s ≈ {dnom} m³/h · {dim_ref}"
        xn = f"{_mapx(vnom, vmax):.1f}"
        html = sub1(html, r'(<text x=")[\d.]+(" y="11"[^>]*>)[^<]*(</text>)',
                    lambda m: m.group(1) + xn + m.group(2) + annot + m.group(3))

    # --- mode ΔP finale HEPA : 2 × ΔP initiale (EN 1822), au lieu de min(init+ADD ; 3×init)
    if d.get("dp_final_mode") == "x2":
        html = html.replace("var dpFinalNum = Math.min(dpInitNum + ADD[eff], dpInitNum * 3);",
                            "var dpFinalNum = dpInitNum * 2;")
        html = html.replace(
            'ΔP finale = min(ΔP init + <span id="effAdd"></span> Pa ; ΔP init × 3) <span style="color:#b9c2cd;">— EN 13053 · <span id="effRule"></span></span>',
            'ΔP finale = 2 × ΔP initiale<span id="effAdd" style="display:none;"></span> <span style="color:#b9c2cd;">— EN 1822 · <span id="effRule"></span></span>')

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

    # --- page 2 compacte (par produit) : courbe + calculateur sur une seule page A4.
    #     Réduit les marges de la page 2 et la taille du graphe, sans toucher le gabarit
    #     par défaut (NETPLY) ni le test d'identité.
    if d.get("compact_p2"):
        html = html.replace("margin:7mm 0 7mm 0;", "margin:4mm 0 4mm 0;")                       # filet en-tête P2
        html = html.replace('<div style="margin-top:6mm; border:1px solid #E1E7EF;',
                            '<div style="margin-top:3mm; border:1px solid #E1E7EF;')             # cadre courbe
        html = html.replace('display:flex; align-items:center; gap:18px; margin-top:7px;">',
                            'display:flex; align-items:center; gap:18px; margin-top:4px;">')     # ligne « Afficher : »
        html = html.replace('gap:10px; margin-top:9mm;">',
                            'gap:10px; margin-top:5mm;">')                                       # titre Calculateur
        html = html.replace('gap:7mm; margin-top:6mm; align-items:stretch;">',
                            'gap:7mm; margin-top:4mm; align-items:stretch;">')                   # grille calculateur
        html = html.replace('margin-top:7mm; background:#F2F6FB;',
                            'margin-top:4mm; background:#F2F6FB;')                               # note méthode
        html = html.replace('<svg id="curveSvg" viewBox="0 0 600 300" style="width:100%; height:auto; display:block;">',
                            '<svg id="curveSvg" viewBox="0 0 600 300" style="width:84%; height:auto; display:block; margin:0 auto;">')

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
