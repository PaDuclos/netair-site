#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
lecture_courbes.py — courbes débit / perte de charge, normalisées pour le catalogue.

Les 18 fiches ne rangent pas leurs courbes de la même façon. Trois formes coexistent :

  1. `classes` {low, high}      — 12 produits ; polynômes par épaisseur (48 / 98 mm)
  2. `courbes` + `series`       —  5 produits ; une liste de courbes par classe et longueur
  3. `classes_list` + `multi_classe` — NETPAK S CILIA

Ce module les ramène à une seule forme. Il ne recalcule rien de son côté : il
importe `force_origin` et `AREF` du générateur de fiches, si bien que le catalogue
et les fiches tracent la même courbe à partir des mêmes coefficients. Corriger un
polynôme dans un JSON corrige les deux.

Règle de sélection — **le catalogue trace ce que la fiche affiche par défaut** :
  · forme 1 → les deux classes, à la plus petite épaisseur (une seule si elles
    sont identiques, cas des produits mono-classe) ;
  · forme 2 → les courbes listées dans `courbes_affichees` ;
  · forme 3 → la classe `eff_default`, à la plus petite épaisseur.

Physique (identique aux fiches) :
    v (m/s)   = (Q / 3600) / surface frontale
    ΔP (Pa)   = a·v² + b·v          après passage forcé par l'origine
"""

import json
import os
import sys

ICI = os.path.dirname(os.path.abspath(__file__))
GEN = os.path.abspath(os.path.join(ICI, "..", "Generateur"))
sys.path.insert(0, GEN)
from generer import AREF, force_origin  # noqa: E402

# Valeurs par défaut du générateur de fiches (generer.py) : ne pas les diverger.
VMAX_DEFAUT, PMAX_DEFAUT, DEBIT_NOM_DEFAUT = 3.17, 120, 3400

# Couleurs de la charte pour distinguer deux courbes.
COULEURS = ("#0F3261", "#0897A5", "#0070C8")


def _premiere_epaisseur(poly):
    """La plus petite variante disponible, en clé de texte ('48' avant '98')."""
    return sorted(poly, key=lambda k: int(k))[0]


def _mm(valeur):
    """Épaisseur en français : 4.5 → « 4,5 mm »."""
    txt = f"{valeur:g}".replace(".", ",")
    return f"{txt} mm"


def _epaisseur_reelle(cl, cle_poly):
    """L'épaisseur à AFFICHER.

    Les clés « 48 » / « 98 » des polynômes sont une convention interne du gabarit
    des fiches (deux variantes d'épaisseur), pas toujours des millimètres réels :
    NETPLAN se décline de 8 à 25 mm, NETFIL fait 4,5 mm. Quand la classe porte un
    champ `epaisseur`, c'est lui qui dit la vérité ; sinon la clé est bien
    l'épaisseur réelle (cas de NETPLY, 48 et 98 mm).
    """
    return _mm(cl["epaisseur"]) if "epaisseur" in cl else _mm(int(cle_poly))


def _courbes_brutes(d):
    """→ [(libellé, a, b, c)] selon la forme du produit, sans rien recalculer."""
    # Forme 2 — liste de courbes (NETBAG S, NETCEL V AZUR/NIVAL, NETPAK S AZUR/LUMEN)
    if d.get("series") and d.get("courbes"):
        cdef = d.get("classes_def", {})
        affichees = d.get("courbes_affichees") or []
        choisies = [c for c in d["courbes"] if c.get("cls") in affichees] or d["courbes"][:1]
        return [(f"{cdef.get(c['cls'], {}).get('label', c.get('cls', '')).upper()}"
                 f" · {c['len']} mm", c["a"], c["b"], c.get("c", 0.0))
                for c in choisies]

    # Forme 3 — classes_list (NETPAK S CILIA)
    if d.get("multi_classe") and d.get("classes_list"):
        liste = d["classes_list"]
        defaut = d.get("eff_default")
        cl = next((c for c in liste if c.get("id") == defaut), liste[0])
        ep = _premiere_epaisseur(cl["poly"])
        p = cl["poly"][ep]
        return [(f"{cl['label']} · {_epaisseur_reelle(cl, ep)}",
                 p["a"], p["b"], p.get("c", 0.0))]

    # Forme 1 — classes {low, high}
    if "classes" in d:
        out, vues = [], set()
        for cle in ("low", "high"):
            cl = d["classes"].get(cle)
            if not cl or "poly" not in cl:
                continue
            ep = _premiere_epaisseur(cl["poly"])
            p = cl["poly"][ep]
            signature = (cl.get("label"), p["a"], p["b"], p.get("c", 0.0))
            if signature in vues:          # produits mono-classe : low == high
                continue
            vues.add(signature)
            out.append((f"{cl.get('label', '')} · {_epaisseur_reelle(cl, ep)}",
                        p["a"], p["b"], p.get("c", 0.0)))
        return out

    return []


def lire_courbes(slug, produits_dir=None):
    """→ dict prêt à tracer, ou None si le produit n'a pas de courbe exploitable."""
    dossier = produits_dir or os.path.join(GEN, "produits")
    with open(os.path.join(dossier, f"{slug}.json"), encoding="utf-8") as f:
        d = json.load(f)

    # Trois courbes au maximum : au-delà, la légende ne tient plus dans le cadre
    # réservé sur la page produit, et le graphique devient illisible à cette taille.
    brutes = _courbes_brutes(d)[:3]
    if not brutes:
        return None

    vmax = d.get("vmax", VMAX_DEFAUT)
    aref = d.get("aref", AREF)          # NETCEL V LAM a une surface frontale à lui
    debit_nom = d.get("debit_nom", DEBIT_NOM_DEFAUT)
    debit_max = d.get("axe_debit_max") or vmax * aref * 3600

    courbes, plafond = [], 0.0
    for i, (label, a, b, c) in enumerate(brutes):
        a2, b2, _ = force_origin(a, b, c, vmax)   # même lissage que les fiches
        points = []
        for k in range(61):
            v = vmax * k / 60
            dp = a2 * v * v + b2 * v
            points.append((v * aref * 3600, max(0.0, dp)))
        plafond = max(plafond, points[-1][1])
        v_nom = (debit_nom / 3600) / aref
        courbes.append({
            "label": label,
            "couleur": COULEURS[i % len(COULEURS)],
            "points": points,
            "dp_nom": max(0.0, a2 * v_nom * v_nom + b2 * v_nom),
        })

    # L'échelle des fiches sert de base ; on la relève si une courbe la dépasse,
    # pour ne jamais tronquer un tracé.
    pmax = max(d.get("pmax", PMAX_DEFAUT), plafond * 1.06)
    return {
        "courbes": courbes,
        "debit_max": debit_max,
        "debit_nom": debit_nom if debit_nom <= debit_max else None,
        "pmax": pmax,
    }


if __name__ == "__main__":
    import lecture_produits
    for s in lecture_produits.slugs_disponibles():
        c = lire_courbes(s)
        if not c:
            print(f"{s:18} ❌ aucune courbe")
            continue
        libelles = " | ".join(f"{k['label']} → {k['dp_nom']:.0f} Pa" for k in c["courbes"])
        print(f"{s:18} Q≤{c['debit_max']:.0f} m³/h  ΔP≤{c['pmax']:.0f} Pa   {libelles}")
