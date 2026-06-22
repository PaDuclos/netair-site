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
        f'<button id="be_{c}" style="flex:1;">{cdef[c]["label"]}</button>' for c in present)
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
        surf = f'{s["surface"]:.2f}'.replace(".", ",")
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
      var be = $('be_' + ORDER[i]); if (be) be.setAttribute('style', BTN + (state.eff === ORDER[i] ? ON : OFF));
    }
    buildLenBtns();

    var cs = curSeries(), co = cs.co, add = CLS[cs.cls].add, rule = CLS[cs.cls].rule;
    var areaNum = (Math.max(50, state.flen) / 1000) * (Math.max(50, state.fwid) / 1000);
    var velNum = (state.debit / 3600) / areaNum;
    var dpInit = pdc(co, velNum), dpFinal = Math.min(dpInit + add, dpInit * 3), dpAvg = (dpInit + dpFinal) / 2;
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

    # --- page 1 compacte
    if d.get("compact_p1"):
        html = html.replace("margin:9mm 0 7mm 0;", "margin:6mm 0 5mm 0;")
        html = html.replace('<div style="margin-top:9mm;">', '<div style="margin-top:6mm;">')
        html = html.replace('<div style="margin-top:8mm;">', '<div style="margin-top:6mm;">')

    return html


# ----------------------------------------------------------------- moteur ----
def generer(d, html):
    if d.get("series"):
        return generer_series(d, html)
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
