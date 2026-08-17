#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
lecture_familles.py — lit la taxonomie des familles DANS LE FICHIER DU SITE.

Source unique : `site/src/lib/familles.ts`. Les noms de familles, leurs textes de
présentation, le rattachement des produits et leur ordre d'affichage y sont déjà
définis et validés pour le site vitrine. Le catalogue les relit au lieu d'en tenir
une seconde copie : une famille renommée sur le site suit dans le catalogue à la
régénération suivante, sans intervention.

C'est la leçon notée dans CLAUDE.md à propos de DEVIS AUTO (brique 4bis) : des
règles présentes à deux endroits divergent en silence. On ne crée donc pas de
deuxième table ici.

Nuance volontaire : sur le site un produit peut figurer dans plusieurs familles
(un client doit le retrouver partout où il le cherche). Sur un catalogue imprimé,
on retient la famille PRINCIPALE — la première de la liste, celle qui sert déjà de
fil d'Ariane aux fiches — pour que chaque produit soit imprimé une fois et une seule.
"""

import os
import re

ICI = os.path.dirname(os.path.abspath(__file__))
FAMILLES_TS = os.path.abspath(
    os.path.join(ICI, "..", "..", "site", "src", "lib", "familles.ts"))


class TaxonomieIllisible(RuntimeError):
    pass


def _bloc(source, debut):
    """Extrait le littéral qui suit `debut` jusqu'à sa fermeture équilibrée."""
    i = source.find(debut)
    if i < 0:
        raise TaxonomieIllisible(
            f"« {debut} » introuvable dans familles.ts — le fichier a changé de forme.")
    i += len(debut)
    ouvrant = source[i - 1]
    fermant = {"[": "]", "{": "}"}[ouvrant]
    prof, j = 1, i
    while j < len(source) and prof:
        if source[j] == ouvrant:
            prof += 1
        elif source[j] == fermant:
            prof -= 1
        j += 1
    return source[i:j - 1]


def _champs(bloc):
    """Les paires `cle: 'valeur'` d'une entrée, chaînes simples ou doubles quotes."""
    return {m.group(1): m.group(3)
            for m in re.finditer(r"(\w+):\s*(['\"])(.*?)\2", bloc, re.S)}


def _entrees(tableau):
    """Découpe un tableau JS en ses objets de premier niveau."""
    out, prof, debut = [], 0, None
    for k, c in enumerate(tableau):
        if c == "{":
            if prof == 0:
                debut = k + 1
            prof += 1
        elif c == "}":
            prof -= 1
            if prof == 0:
                out.append(tableau[debut:k])
    return out


def lire_taxonomie():
    """→ (familles ordonnées, principale par slug produit, ordre par slug produit)."""
    if not os.path.exists(FAMILLES_TS):
        raise TaxonomieIllisible(f"familles.ts introuvable : {FAMILLES_TS}")
    with open(FAMILLES_TS, encoding="utf-8") as f:
        src = f.read()

    familles = []
    for e in _entrees(_bloc(src, "export const FAMILLES: Famille[] = [")):
        c = _champs(e)
        if "slug" not in c or "titre" not in c:
            raise TaxonomieIllisible(f"famille sans slug/titre : {e[:80]}…")
        familles.append({
            "slug": c["slug"],
            "titre": c["titre"],
            "tag": c.get("tag", ""),
            "norme": c.get("norme", ""),
            "tag_en": c.get("tagEn", ""),
            # descLong est le texte long des pages famille du site ; desc est la
            # phrase courte des bulles. On préfère le long, on retombe sur le court.
            "texte": c.get("descLong") or c.get("desc", ""),
        })
    if not familles:
        raise TaxonomieIllisible("aucune famille lue dans familles.ts")

    rattachement = _bloc(src, "export const SLUG_FAMILLE: Record<string, string[]> = {")
    principale = {}
    for m in re.finditer(r"'?([\w-]+)'?\s*:\s*\[([^\]]*)\]", rattachement):
        listes = re.findall(r"'([\w-]+)'", m.group(2))
        if not listes:
            raise TaxonomieIllisible(f"produit sans famille : {m.group(1)}")
        principale[m.group(1)] = listes[0]

    ordre = {m.group(1): int(m.group(2)) for m in re.finditer(
        r"'?([\w-]+)'?\s*:\s*(\d+)",
        _bloc(src, "export const ORDRE_PRODUITS: Record<string, number> = {"))}

    return familles, principale, ordre


def plan_du_catalogue(slugs_disponibles):
    """Les sections du catalogue, dans l'ordre, chacune avec ses produits.

    Contrôle d'exhaustivité : un produit présent sur le disque mais rattaché à
    aucune famille fait échouer la génération. Un produit ne peut pas disparaître
    du catalogue en silence — ce qui arriverait au premier produit ajouté.
    """
    familles, principale, ordre = lire_taxonomie()

    inconnus = [s for s in slugs_disponibles if s not in principale]
    if inconnus:
        raise TaxonomieIllisible(
            "produits non rattachés à une famille dans site/src/lib/familles.ts : "
            + ", ".join(inconnus))

    sections = []
    for f in familles:
        dedans = sorted(
            (s for s in slugs_disponibles if principale[s] == f["slug"]),
            key=lambda s: (ordre.get(s, 999), s))
        if dedans:
            sections.append({**f, "produits": dedans})

    place = sum(len(s["produits"]) for s in sections)
    if place != len(slugs_disponibles):
        raise TaxonomieIllisible(
            f"{place} produits placés pour {len(slugs_disponibles)} disponibles.")
    return sections


if __name__ == "__main__":
    import lecture_produits
    for s in plan_du_catalogue(lecture_produits.slugs_disponibles()):
        print(f"\n{s['titre']}  [{s['slug']}]  {s['tag']}")
        print(f"   {s['texte'][:95]}…")
        for p in s["produits"]:
            print(f"   · {p}")
