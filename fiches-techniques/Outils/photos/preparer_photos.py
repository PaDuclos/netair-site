#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
preparer_photos.py — prépare les photos produit Netair pour les trois supports.

À partir d'une photo sur fond blanc, produit deux fichiers :
  · <cible>.jpg          fond blanc conservé, redimensionné — fiches techniques
  · detour/<cible>.png   fond rendu transparent — vignettes du site et catalogue

Pourquoi deux versions : sur le site, les vignettes de gamme et les cartes produit
posent l'image sur un HALO DE COULEUR (dégradé turquoise/bleu). Une photo à fond
blanc y dessine un rectangle blanc. Les fiches techniques, elles, sont sur fond
blanc et se contentent du JPEG.

Le détourage procède par REMPLISSAGE DEPUIS LES BORDS, jamais par seuil global :
seuls les pixels clairs RELIÉS au bord de l'image sont effacés. C'est ce qui permet
de garder intact un média filtrant blanc au centre du produit — un simple seuil sur
la luminosité le rendrait transparent lui aussi.

Aucune dépendance : `sips` (fourni avec macOS) pour lire et redimensionner, le reste
en Python. Tenté d'abord en Swift, abandonné : le compilateur de ce Mac et son SDK
ne sont pas accordés (Command Line Tools).

Usage : python3 preparer_photos.py [--taille 1200] [--seuil 232]
"""

import argparse
import json
import os
import struct
import subprocess
import sys
import tempfile
import zlib

ICI = os.path.dirname(os.path.abspath(__file__))
CORRESPONDANCE = os.path.join(ICI, "correspondance.json")
SORTIE = os.path.join(ICI, "_sortie")


def sips(*args):
    r = subprocess.run(["sips", *args], capture_output=True)
    return r.returncode == 0


def lire_bmp(chemin):
    """BMP 24 bits non compressé → (pixels RVB à plat, largeur, hauteur)."""
    d = open(chemin, "rb").read()
    if d[:2] != b"BM":
        raise ValueError("ce n'est pas un BMP")
    debut = struct.unpack("<I", d[10:14])[0]
    w, h = struct.unpack("<ii", d[18:26])
    bits = struct.unpack("<H", d[28:30])[0]
    if bits != 24:
        raise ValueError(f"BMP {bits} bits non géré")
    haut_en_bas = h < 0
    h = abs(h)
    pas = (w * 3 + 3) // 4 * 4            # les lignes BMP sont calées sur 4 octets
    px = bytearray(w * h * 3)
    for y in range(h):
        src = debut + (y if haut_en_bas else h - 1 - y) * pas
        ligne = d[src:src + w * 3]
        px[y * w * 3:(y + 1) * w * 3] = ligne
    return px, w, h                        # attention : ordre BGR


def masque_de_fond(px, w, h, seuil):
    """True = pixel de fond, c.-à-d. clair ET relié à un bord de l'image."""
    clair = bytearray(w * h)
    for i in range(w * h):
        o = i * 3
        if px[o] >= seuil and px[o + 1] >= seuil and px[o + 2] >= seuil:
            clair[i] = 1
    fond = bytearray(w * h)
    pile = []
    for x in range(w):
        for i in (x, (h - 1) * w + x):
            if clair[i] and not fond[i]:
                fond[i] = 1
                pile.append(i)
    for y in range(h):
        for i in (y * w, y * w + w - 1):
            if clair[i] and not fond[i]:
                fond[i] = 1
                pile.append(i)
    while pile:
        i = pile.pop()
        x = i % w
        if x > 0 and clair[i - 1] and not fond[i - 1]:
            fond[i - 1] = 1; pile.append(i - 1)
        if x < w - 1 and clair[i + 1] and not fond[i + 1]:
            fond[i + 1] = 1; pile.append(i + 1)
        if i >= w and clair[i - w] and not fond[i - w]:
            fond[i - w] = 1; pile.append(i - w)
        if i < (h - 1) * w and clair[i + w] and not fond[i + w]:
            fond[i + w] = 1; pile.append(i + w)
    return fond


def alpha_adouci(fond, w, h):
    """Transparence partielle sur le contour : sans ça la découpe fait un escalier."""
    a = bytearray(255 if not f else 0 for f in fond)
    for i in range(w * h):
        if fond[i]:
            continue
        x = i % w
        n = 0
        if x > 0 and fond[i - 1]: n += 1
        if x < w - 1 and fond[i + 1]: n += 1
        if i >= w and fond[i - w]: n += 1
        if i < (h - 1) * w and fond[i + w]: n += 1
        if n:
            a[i] = 255 - n * 48
    return a


def ecrire_png_rvba(chemin, px_bgr, alpha, w, h):
    """PNG 8 bits RVBA, écrit à la main (zlib + CRC), sans bibliothèque."""
    lignes = bytearray()
    for y in range(h):
        lignes.append(0)                                   # filtre « aucun »
        base = y * w * 3
        for x in range(w):
            o = base + x * 3
            lignes += bytes((px_bgr[o + 2], px_bgr[o + 1], px_bgr[o], alpha[y * w + x]))

    def bloc(typ, data):
        c = typ + data
        return struct.pack(">I", len(data)) + c + struct.pack(">I", zlib.crc32(c) & 0xFFFFFFFF)

    with open(chemin, "wb") as f:
        f.write(b"\x89PNG\r\n\x1a\n")
        f.write(bloc(b"IHDR", struct.pack(">IIBBBBB", w, h, 8, 6, 0, 0, 0)))
        f.write(bloc(b"IDAT", zlib.compress(bytes(lignes), 9)))
        f.write(bloc(b"IEND", b""))


def preparer(source, cible_jpg, cible_png, taille, seuil, tmp, taille_png=None):
    # 1. version fond blanc — un simple redimensionnement suffit
    if not sips("-Z", str(taille), "-s", "format", "jpeg",
                "-s", "formatOptions", "86", source, "--out", cible_jpg):
        return None
    # 2. version détourée
    bmp = os.path.join(tmp, "t.bmp")
    if not sips("-Z", str(taille_png or taille), "-s", "format", "bmp", source, "--out", bmp):
        return None
    px, w, h = lire_bmp(bmp)
    fond = masque_de_fond(px, w, h, seuil)
    part = sum(fond) * 100 // (w * h)
    ecrire_png_rvba(cible_png, px, alpha_adouci(fond, w, h), w, h)
    return w, h, part


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--taille", type=int, default=1200,
                    help="côté le plus long du JPEG, en pixels")
    ap.add_argument("--taille-detour", type=int, default=900,
                    help="côté le plus long du PNG détouré ; il ne s'affiche jamais "
                         "au-delà de ~400 px sur le site, inutile de le charger plus")
    ap.add_argument("--seuil", type=int, default=232,
                    help="à partir de quelle clarté un pixel est considéré comme du fond")
    a = ap.parse_args()

    corr = json.load(open(CORRESPONDANCE, encoding="utf-8"))
    src_dir = corr["dossier_source"]
    os.makedirs(os.path.join(SORTIE, "detour"), exist_ok=True)
    tmp = tempfile.mkdtemp()

    print(f"{'produit':17} {'photo source':18} {'taille détourée':18} "
          f"{'seuil':9} fond effacé")
    alertes = []
    for p in corr["produits"]:
        source = os.path.join(src_dir, p["photo"])
        if not os.path.exists(source):
            alertes.append(f"{p['produit']} : photo introuvable → {p['photo']}")
            continue
        base = os.path.splitext(p["cible"])[0]
        # Seuil réglable produit par produit : une matière blanche (média fibreux)
        # est presque aussi claire que le fond, et un seuil trop bas mord dedans.
        seuil = p.get("seuil", a.seuil)
        r = preparer(source, os.path.join(SORTIE, p["cible"]),
                     os.path.join(SORTIE, "detour", base + ".png"), a.taille, seuil, tmp,
                     a.taille_detour)
        if not r:
            alertes.append(f"{p['produit']} : conversion impossible")
            continue
        w, h, part = r
        # Un fond effacé anormalement petit ou grand trahit une photo qui ne se
        # découpe pas proprement : on le signale plutôt que de le laisser passer.
        drapeau = "  ⚠️ à regarder" if part < 12 or part > 70 else ""
        print(f"  {p['produit']:17} {p['photo']:18} détourée {w}x{h:<9} "
              f"seuil {seuil:3d}  fond {part:3d} %{drapeau}")
        if drapeau:
            alertes.append(f"{p['produit']} : fond effacé à {part} %, découpe à vérifier")

    print(f"\n→ {SORTIE}")
    for x in alertes:
        print(f"⚠️  {x}")
    return 1 if alertes else 0


if __name__ == "__main__":
    sys.exit(main())
