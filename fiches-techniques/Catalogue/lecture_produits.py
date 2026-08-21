#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
lecture_produits.py — couche de lecture des données produit pour le catalogue.

Rôle unique : ouvrir les `Generateur/produits/*.json` (mêmes fichiers que les 18
fiches techniques) et en renvoyer une forme normalisée. Aucun texte produit n'est
écrit ici : tout est lu. Si une donnée attendue manque, on lève une erreur au lieu
de produire une page trouée en silence.

Le catalogue ne lit QUE les champs présents sur les 18 produits (audités le
17/08/2026) : nom, soustitre, description, points_cles, specs, photo, badges_p1,
fiche. Il n'ouvre volontairement pas les coefficients de perte de charge, qui
existent sous trois formes différentes selon les produits (`classes`, `series`,
`multi_classe`) : le catalogue n'en a pas besoin, et ne pas les lire supprime
d'emblée le risque de casser sur une des trois formes.
"""

import glob
import json
import os

ICI = os.path.dirname(os.path.abspath(__file__))
PRODUITS = os.path.abspath(os.path.join(ICI, "..", "Generateur", "produits"))
PHOTOS = os.path.abspath(os.path.join(ICI, "..", "Generateur", "assets"))
# Le site publie des versions DÉTOURÉES (PNG à fond transparent) des mêmes photos.
# On les préfère : posée sur un fond de carte, une photo à fond blanc dessine un
# rectangle blanc qui se voit (remarque de PA du 17/08/2026).
DETOUREES = os.path.abspath(
    os.path.join(ICI, "..", "..", "site", "public", "produits", "detour"))

# Ancre du test d'identité du générateur de fiches : ce n'est pas un produit.
EXCLUS = {"_gabarit_ref.json"}

REQUIS = ("slug", "nom", "soustitre", "description", "points_cles",
          "specs", "photo", "badges_p1", "fiche")


class DonneeManquante(RuntimeError):
    pass


def _exiger(d, fichier):
    """Refuse un produit incomplet plutôt que d'imprimer une page à trous."""
    for champ in REQUIS:
        if champ not in d or d[champ] in (None, "", [], {}):
            raise DonneeManquante(f"{fichier} : champ « {champ} » absent ou vide.")
    for sous in ("num", "version", "date"):
        if sous not in d["fiche"]:
            raise DonneeManquante(f"{fichier} : fiche.{sous} absent.")
    for s in d["specs"]:
        if len(s) != 2:
            raise DonneeManquante(f"{fichier} : spec mal formée → {s!r}")
    photo = os.path.join(PHOTOS, d["photo"])
    if not os.path.exists(photo):
        raise DonneeManquante(f"{fichier} : photo introuvable → {d['photo']}")


def _detouree(nom_fichier):
    """Le PNG détouré correspondant, s'il existe (14 produits sur 18 en ont un)."""
    png = os.path.join(DETOUREES, os.path.splitext(nom_fichier)[0] + ".png")
    return png if os.path.exists(png) else None


def _meilleure_photo(nom_fichier):
    """Le détouré si disponible, sinon la photo d'origine."""
    return _detouree(nom_fichier) or os.path.join(PHOTOS, nom_fichier)


def lire(slug):
    """Un produit, normalisé. `slug` = nom de fichier sans .json."""
    chemin = os.path.join(PRODUITS, f"{slug}.json")
    if not os.path.exists(chemin):
        raise DonneeManquante(f"produit inconnu : {slug}.json")
    with open(chemin, encoding="utf-8") as f:
        d = json.load(f)
    _exiger(d, f"{slug}.json")

    return {
        "slug": d["slug"],
        "nom": d["nom"],
        "soustitre": d["soustitre"],
        "description": d["description"],
        "points_cles": list(d["points_cles"]),
        "specs": [(str(a), str(b)) for a, b in d["specs"]],
        "badges": list(d["badges_p1"]),
        "photo": _meilleure_photo(d["photo"]),
        "photo_detouree": _detouree(d["photo"]) is not None,
        "photo_alt": d.get("photo_alt", d["nom"]),
        "fiche_num": d["fiche"]["num"],
        "version": d["fiche"]["version"],
        "date": d["fiche"]["date"],
        # Résumé d'efficacité du tableau de synthèse : les deux premiers badges,
        # repris mot pour mot. Aucune interprétation, donc rien qui puisse
        # diverger des fiches techniques.
        "efficacite": " · ".join(d["badges_p1"][:2]),
    }


def slugs_disponibles():
    """Tous les produits présents sur le disque, pour le contrôle d'exhaustivité."""
    return sorted(
        os.path.basename(p)[:-5]
        for p in glob.glob(os.path.join(PRODUITS, "*.json"))
        if os.path.basename(p) not in EXCLUS
    )


if __name__ == "__main__":
    slugs = slugs_disponibles()
    print(f"{len(slugs)} produits lisibles :\n")
    for s in slugs:
        p = lire(s)
        print(f"  {p['nom']:16} {p['version']:5} {p['date']:11} "
              f"{len(p['points_cles'])} pts · {len(p['specs'])} specs")
