#!/usr/bin/env python3
"""
generate_golden.py — Génère les « vecteurs dorés » du moteur de prix (Bloc B1, T8).

Le JUGE indépendant : on rejoue la GÉOMÉTRIE VALIDÉE du calculateur de référence
(`DEVIS AUTO/src/cost_calculator.py`, validée sur de vrais devis) MAIS avec la charge
corrigée pour coller à la VRAIE formule Excel (`Calculateur_Netair.xltm`, onglet
« Devis interne », colonne « CL : % du Prix d'achat ») :

    CL% = XLOOKUP(code ; gammes ; « Frais de livraison » ; 0)   → 0 si la case est vide
    PRU HT = ROUND( (1 + CL%) × assemblage_géométrique ; 2 )
    PTU HT = PRU HT × Ratio prix tarif                          ← prix boutique

⚠️ La réplique Python brute appliquait un défaut de 0,10 sur les cases vides (bug) :
on le NEUTRALISE ici en peuplant `gamme_cl` pour TOUS les codes (0 si vide), exactement
comme la formule Excel.

Sortie : site/tests/pricing/golden-vectors.json — pour chaque entrée, le coût (PRU) et le
prix tarif (PTU) ATTENDUS, qui serviront à vérifier le moteur TypeScript au centime (T9).

Usage : python3 generate_golden.py
"""

import decimal
import json
import math
import sys
from pathlib import Path
from types import SimpleNamespace


def excel_round(x, n=0):
    """Arrondi « comme Excel » : moitié AWAY FROM ZERO (≠ round() Python = pair le plus proche)."""
    if not isinstance(x, (int, float)):
        return x
    quant = decimal.Decimal(1).scaleb(-n)  # 10^-n
    return float(decimal.Decimal(repr(x)).quantize(quant, rounding=decimal.ROUND_HALF_UP))

SCRIPT_DIR = Path(__file__).resolve().parent
TABLES_JSON = SCRIPT_DIR / "../src/lib/pricing/data/tables.json"
XLSX = (
    SCRIPT_DIR / "../../../../BLOC1_Gamme_Produits/Grille_Couts_Internes/Calculateur_Netair.xlsx"
).resolve()
COST_CALC_DIR = (SCRIPT_DIR / "../../../../DEVIS AUTO/src").resolve()
OUT = SCRIPT_DIR / "../tests/pricing/golden-vectors.json"


def milieu(lo, hi):
    """Une valeur sûrement à l'intérieur de [lo, hi]. Borne « infinie » → représentant fixe."""
    if hi is None or hi >= 1_000_000:
        return 500 if (lo is None or lo <= 1) else round(lo)
    return round((lo + hi) / 2)


def qty_palier(qmin, qmax):
    """Une quantité représentative dans le palier [qmin, qmax] (≥ 1)."""
    return max(int(qmin), 1)


def main():
    tables_data = json.loads(TABLES_JSON.read_text(encoding="utf-8"))
    gammes = {g["code"]: g for g in tables_data["gammes"]}

    if not XLSX.exists():
        sys.exit(f"ERREUR : Excel introuvable : {XLSX}")
    sys.path.insert(0, str(COST_CALC_DIR))
    import cost_calculator as cc  # type: ignore

    # Le calculateur de référence arrondit via round() Python (pair le plus proche) ;
    # Excel arrondit moitié-vers-le-haut. On aligne sur Excel pour la vérité-terrain.
    cc.round = excel_round  # type: ignore[attr-defined]

    tables = cc._charger_tables(XLSX)
    if not tables:
        sys.exit("ERREUR : tables non chargées par cost_calculator")

    # Charge corrigée : TOUS les codes, 0 si « Frais de livraison » vide (= formule Excel).
    tables["gamme_cl"] = {
        code: (g["frais_livraison"] if isinstance(g.get("frais_livraison"), (int, float)) else 0.0)
        for code, g in gammes.items()
    }

    def pru(code, L, H, P, classe, q):
        fn = cc._CALCULATEURS.get(code)
        if fn is None:
            return None
        ligne = SimpleNamespace(
            code_gamme=code, largeur_mm=L, longueur_mm=H, epaisseur_mm=P,
            classe_filtration=classe, nom_gamme="", quantite=q,
        )
        try:
            return fn(ligne, tables)
        except Exception:
            return None

    # Candidats : on balaie les lignes réelles des grilles (cases déjà tarifées).
    candidats = []  # (code, L, H, P, classe, q)

    def ajouter_depuis(rows, has_dim):
        for r in rows:
            code = r.get("code")
            g = gammes.get(code)
            if not g or g["methode"] == "sur_devis" or code not in cc._CALCULATEURS:
                continue
            prix = r.get("prix", {})
            classes = [c for c, v in prix.items() if isinstance(v, (int, float)) and v > 0]
            if not classes:
                continue
            P = r["ep"] if isinstance(r.get("ep"), (int, float)) else g.get("ep_defaut") or 48
            q = qty_palier(r["qmin"], r["qmax"])
            if has_dim:
                L = milieu(r["pd_min"], r["pd_max"])
                H = milieu(r["gd_min"], r["gd_max"])
            else:
                # grille surface : pas de dimensions → représentant qui tombe dans la tranche
                surf = (r["surf_min"] + min(r["surf_max"], 50)) / 2  # dm²
                cote = max(round((surf * 10000) ** 0.5), 1)  # mm, carré équivalent
                L = H = cote
            for classe in classes:
                candidats.append((code, L, H, P, classe, q))

    ajouter_depuis(tables_data["prix_l_et_l"], has_dim=True)
    ajouter_depuis(tables_data["prix_surface"], has_dim=False)

    vecteurs = []
    vus = set()
    for code, L, H, P, classe, q in candidats:
        cle = (code, L, H, P, classe, q)
        if cle in vus:
            continue
        vus.add(cle)
        cout = pru(code, L, H, P, classe, q)
        if cout is None:
            continue
        ratio = gammes[code]["ratio"]
        prix = excel_round(cout * ratio, 2)
        vecteurs.append({
            "codeGamme": code,
            "largeur_mm": L,
            "hauteur_mm": H,
            "profondeur_mm": P,
            "classe": classe,
            "quantite": q,
            "coutAttendu": cout,
            "prixAttendu": prix,
        })

    # ── Hors-format (> 50 dm²) : la référence Python NE le gère pas → on applique la
    #    VRAIE formule Excel (lue dans « Devis interne »), validée sur prix réels :
    #    NETPLY 900×600 = 37,67 € · 1000×600 = 46,03 €.
    #    base = Prix_Surface(50) + Prix_Surface_HF × (⌈surface⌉ − 50) ; puis renfort + charge + ratio.
    def getparam(lib):
        for p in tables_data["params"]:
            if p["libelle"] == lib:
                return p["valeur"]
        return 0

    def surf_val(code, ep, surf, q, cl):
        for r in tables_data["prix_surface"]:
            if r["code"] == code and r["ep"] == ep and r["surf_min"] <= surf <= r["surf_max"] and r["qmin"] <= q <= r["qmax"]:
                v = r["prix"].get(cl)
                return v if isinstance(v, (int, float)) and v > 0 else None
        return None

    def hf_val(code, ep, q, cl):
        for r in tables_data["prix_surface_hf"]:
            if r["code"] == code and r["ep"] == ep and r["qmin"] <= q <= r["qmax"]:
                v = r["prix"].get(cl)
                return v if isinstance(v, (int, float)) and v > 0 else None
        return None

    Q_HF = 10
    for g in gammes.values():
        if g["methode"] != "A":
            continue
        code, nom = g["code"], g["nom"]
        charge = g["frais_livraison"] if isinstance(g.get("frais_livraison"), (int, float)) else 0.0
        plan = "PLAN" in nom.upper()
        r_ext = getparam("NETPLAN renfort extérieur :" if plan else "TITAPLY renfort extérieur :")
        r_int = getparam("NETPLAN renfort intérieur :" if plan else "TITAPLY renfort intérieur :")
        eps = sorted({r["ep"] for r in tables_data["prix_surface"] if r["code"] == code and isinstance(r["ep"], int)})
        for ep in eps:
            for L, H in [(900, 600), (1000, 600), (900, 700)]:
                surf = L * H / 10000
                if surf <= 50:
                    continue
                petite, grande = min(L, H), max(L, H)
                renfort = r_int if petite > 850 else (r_ext if (grande > 800 or surf > 50) else 0)
                for cl in ["G2", "G3", "G4", "M5", "M6"]:
                    s50 = surf_val(code, ep, 50, Q_HF, cl)
                    hf = hf_val(code, ep, Q_HF, cl)
                    if s50 is None or hf is None:
                        continue
                    base = s50 + hf * (math.ceil(surf) - 50)
                    pru = excel_round((1 + charge) * (renfort + base), 2)
                    ptu = excel_round(pru * g["ratio"], 2)
                    cle = (code, L, H, ep, cl, Q_HF)
                    if cle in vus:
                        continue
                    vus.add(cle)
                    vecteurs.append({
                        "codeGamme": code, "largeur_mm": L, "hauteur_mm": H, "profondeur_mm": ep,
                        "classe": cl, "quantite": Q_HF, "coutAttendu": pru, "prixAttendu": ptu,
                    })

    vecteurs.sort(key=lambda v: (int(v["codeGamme"]), v["largeur_mm"], v["hauteur_mm"], v["classe"], v["quantite"]))

    # Garde anti-divergence : on fige l'empreinte de l'export. Si tables.json change,
    # le test golden échouera tant que ces vecteurs n'auront pas été régénérés (T9 / §7).
    meta = json.loads((TABLES_JSON.parent / "tables.meta.json").read_text(encoding="utf-8"))
    sortie = {
        "tables_sha256": meta.get("tables_sha256"),
        "version_excel": meta.get("version_excel"),
        "nb": len(vecteurs),
        "vecteurs": vecteurs,
    }
    OUT.write_text(json.dumps(sortie, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    par_gamme = {}
    for v in vecteurs:
        par_gamme[v["codeGamme"]] = par_gamme.get(v["codeGamme"], 0) + 1
    print(f"OK — {len(vecteurs)} vecteurs dorés → {OUT}")
    print("Par gamme (code : nb) :")
    for code in sorted(par_gamme, key=int):
        print(f"  {code:>4} {gammes[code]['nom'][:22]:22s} : {par_gamme[code]}")


if __name__ == "__main__":
    main()
