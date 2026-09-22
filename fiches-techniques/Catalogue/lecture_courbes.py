#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
lecture_courbes.py — courbes débit / perte de charge, normalisées pour le catalogue.

Les 18 fiches ne rangent pas leurs courbes de la même façon. Trois formes coexistent :

  1. `classes` {low, high}           — 12 produits ; polynômes par épaisseur (48 / 98)
  2. `courbes` + `series`            —  5 produits ; une courbe par classe et longueur
  3. `classes_list` + `multi_classe` — NETPAK S CILIA

Ce module les ramène à une seule forme. Il ne recalcule rien de son côté : il
importe `force_origin` et `AREF` du générateur de fiches, si bien que le catalogue
et les fiches tracent la même courbe à partir des mêmes coefficients. Corriger un
polynôme dans un JSON corrige les deux.

**Toutes les classes du produit sont tracées** (décision PA du 17/08/2026).
Les courbes qui partagent exactement les mêmes coefficients sont fusionnées en un
seul tracé dont l'étiquette réunit les classes et épaisseurs concernées : sur la
plupart des produits, les deux « épaisseurs » du gabarit portent le même polynôme,
et dessiner deux traits superposés n'apprendrait rien.

Physique (identique aux fiches) :
    v (m/s) = (Q / 3600) / surface frontale
    ΔP (Pa) = a·v² + b·v          après passage forcé par l'origine
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

# Palette de repli, reprise de celle que les fiches portent déjà dans leurs JSON
# (NETBAG S en définit dix). Aucune teinte inventée.
PALETTE = ("#0F3261", "#0897A5", "#0070C8", "#6A4C93", "#C0392B",
           "#1B9E5A", "#3E66A6", "#036C77", "#A98FD0", "#6FCBD2")


def _mm(valeur):
    """Épaisseur en français : 4.5 → « 4,5 mm »."""
    return f"{valeur:g}".replace(".", ",") + " mm"


def _epaisseur_reelle(cl, cle_poly):
    """L'épaisseur à AFFICHER.

    Les clés « 48 » / « 98 » des polynômes sont une convention interne du gabarit
    des fiches (deux variantes), pas toujours des millimètres réels : NETPLAN se
    décline de 8 à 25 mm, NETFIL fait 4,5 mm, NETCEL V LAM 68 mm. Quand la classe
    porte un champ `epaisseur`, c'est lui qui dit la vérité ; sinon la clé est bien
    l'épaisseur réelle (cas de NETPLY, 48 et 98 mm).
    """
    return _mm(cl["epaisseur"]) if "epaisseur" in cl else _mm(int(cle_poly))


def _entrees(d):
    """Toutes les courbes → [(classe, épaisseur, clé brute, a, b, c, couleur)].

    La « clé brute » est le nom que porte la variante dans le JSON (48 / 98, ou la
    longueur de poche). Elle ne sert qu'à départager deux tracés que leurs
    étiquettes ne distinguent pas — voir le contrôle de collision plus bas.
    """
    # Forme 2 — liste de courbes, avec les couleurs choisies pour la fiche
    if d.get("series") and d.get("courbes"):
        cdef = d.get("classes_def", {})
        return [(cdef.get(c["cls"], {}).get("label", c.get("cls", "")).upper(),
                 _mm(c["len"]), str(c["len"]),
                 c["a"], c["b"], c.get("c", 0.0), c.get("color"))
                for c in d["courbes"]]

    # Forme 3 — classes_list (NETPAK S CILIA)
    if d.get("multi_classe") and d.get("classes_list"):
        return [(cl.get("label", ""), _epaisseur_reelle(cl, ep), ep,
                 p["a"], p["b"], p.get("c", 0.0), None)
                for cl in d["classes_list"]
                for ep, p in sorted(cl["poly"].items(), key=lambda kv: int(kv[0]))]

    # Forme 1 — classes {low, high}
    if "classes" in d:
        out = []
        for cle in ("low", "high"):
            cl = d["classes"].get(cle)
            if not cl or "poly" not in cl:
                continue
            for ep, p in sorted(cl["poly"].items(), key=lambda kv: int(kv[0])):
                out.append((cl.get("label", ""), _epaisseur_reelle(cl, ep), ep,
                            p["a"], p["b"], p.get("c", 0.0), None))
        return out

    return []


def _fusionner(entrees):
    """Regroupe les tracés identiques et réunit leurs étiquettes."""
    groupes = {}
    for classe, ep, cle, a, b, c, couleur in entrees:
        g = groupes.setdefault((round(a, 6), round(b, 6), round(c, 6)),
                               {"classes": [], "eps": [], "cles": [], "couleur": couleur})
        if cle not in g["cles"]:
            g["cles"].append(cle)
        if classe and classe not in g["classes"]:
            g["classes"].append(classe)
        if ep and ep not in g["eps"]:
            g["eps"].append(ep)
        if g["couleur"] is None:
            g["couleur"] = couleur
    return groupes


def lire_courbes(slug, produits_dir=None):
    """→ dict prêt à tracer, ou None si le produit n'a pas de courbe exploitable."""
    dossier = produits_dir or os.path.join(GEN, "produits")
    with open(os.path.join(dossier, f"{slug}.json"), encoding="utf-8") as f:
        d = json.load(f)

    groupes = _fusionner(_entrees(d))
    if not groupes:
        return None

    vmax = d.get("vmax", VMAX_DEFAUT)
    aref = d.get("aref", AREF)          # NETCEL V LAM a une surface frontale à lui
    debit_nom = d.get("debit_nom", DEBIT_NOM_DEFAUT)
    debit_max = d.get("axe_debit_max") or vmax * aref * 3600
    v_nom = (debit_nom / 3600) / aref

    courbes, plafond = [], 0.0
    for i, ((a, b, c), g) in enumerate(groupes.items()):
        a2, b2, _ = force_origin(a, b, c, vmax)   # même lissage que les fiches
        points = [((vmax * k / 60) * aref * 3600,
                   max(0.0, a2 * (vmax * k / 60) ** 2 + b2 * (vmax * k / 60)))
                  for k in range(61)]
        plafond = max(plafond, points[-1][1])
        courbes.append({
            "classe": " / ".join(g["classes"]),
            "epaisseur": " / ".join(g["eps"]),
            "cles": " / ".join(g["cles"]),
            "couleur": g["couleur"] or PALETTE[i % len(PALETTE)],
            "points": points,
            "dp_nom": max(0.0, a2 * v_nom * v_nom + b2 * v_nom),
        })
    courbes.sort(key=lambda k: k["dp_nom"])

    # Deux tracés différents ne doivent jamais porter la même étiquette : le
    # lecteur ne saurait pas lequel est lequel. Quand ça arrive, la donnée source
    # est en défaut (NETCARB CILIA déclare une épaisseur unique de 48 mm mais
    # porte deux polynômes distincts). On départage par la clé brute du JSON et
    # on remonte l'anomalie plutôt que d'inventer une épaisseur.
    conflits, vus = [], {}
    for k in courbes:
        etiquette = (k["classe"], k["epaisseur"])
        vus.setdefault(etiquette, []).append(k)
    for etiquette, groupe in vus.items():
        if len(groupe) > 1:
            conflits.append(" · ".join(x for x in etiquette if x))
            for k in groupe:
                k["epaisseur"] = f"variante {k['cles']}"

    # L'échelle des fiches sert de base ; on la relève si une courbe la dépasse,
    # pour ne jamais tronquer un tracé.
    pmax = max(d.get("pmax", PMAX_DEFAUT), plafond * 1.06)
    return {
        "courbes": courbes,
        "conflits": conflits,
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
        print(f"{s:18} {len(c['courbes']):2} courbe(s)  Q≤{c['debit_max']:.0f}  ΔP≤{c['pmax']:.0f}")
        for k in c["courbes"]:
            print(f"                     · {k['classe']:14} {k['epaisseur']:18} {k['dp_nom']:6.1f} Pa")
