import json, glob, re, os

V_REF = (3400/3600) / (0.592*0.592)
FACTEUR_COLMATAGE = 1.10
COEF_W = 11.328
SEUILS = {
 "ePM1":  {0:[800,900,1050,1400,2000],1:[850,950,1100,1450,2050],2:[950,1100,1250,1550,2150],3:[1050,1250,1450,1800,2400],4:[1200,1400,1550,1900,2500]},
 "ePM2,5":{0:[700,800,950,1300,1900],1:[750,850,1000,1350,1950],2:[800,900,1050,1400,2000],3:[900,1000,1200,1500,2100],4:[1000,1100,1300,1600,2200]},
 "ePM10": {0:[450,550,650,750,1100],1:[500,600,700,850,1200],2:[600,700,800,900,1300],3:[700,800,900,1000,1400],4:[800,900,1050,1400,1500]},
}
LETTRES = ["A+","A","B","C","D"]
def bande(e): return 0 if e<=55 else 1 if e<=65 else 2 if e<=75 else 3 if e<=85 else 4
def parse_iso(iso):
    m=re.match(r"ePM(10|2,5|1)\s+(\d+)",iso)
    return ("ePM"+m.group(1),int(m.group(2))) if m else (None,None)
def classe(grp,eff,W):
    for i,s in enumerate(SEUILS[grp][bande(eff)]):
        if W<=s: return LETTRES[i]
    return "E"
def dpr(a,b,c): return a*V_REF**2+b*V_REF+c
def emit(rows,sub,iso,a,b,c):
    grp,eff=parse_iso(iso)
    if grp is None: return False
    dpi=dpr(a,b,c); W=COEF_W*dpi*FACTEUR_COLMATAGE
    rows.append((sub,iso,dpi,W,classe(grp,eff,W))); return True

def traiter(d):
    rows,exclus=[],[]
    if d.get("series"):
        cd=d["classes_def"]
        for c in d["courbes"]:
            iso=cd[c["cls"]]["iso"]; sub=f'{cd[c["cls"]]["label"]} {c.get("len","")}mm'.strip()
            if not emit(rows,sub,iso,c["a"],c["b"],c["c"]): exclus.append((sub,iso))
    elif "classes_list" in d:
        for cl in d["classes_list"]:
            for ep,p in cl["poly"].items():
                sub=f'{cl["label"]} {ep}mm'; iso=cl["iso"]
                if not emit(rows,sub,iso,p["a"],p["b"],p["c"]): exclus.append((sub,iso))
    elif "classes" in d:
        for lvl in ("low","high"):
            cl=d["classes"].get(lvl)
            if not cl: continue
            for ep,p in cl["poly"].items():
                sub=f'{cl["label"]} {ep}mm'; iso=cl["iso"]
                if not emit(rows,sub,iso,p["a"],p["b"],p["c"]): exclus.append((cl["label"],iso))
    return rows,exclus

print(f"Point de calcul : v = {V_REF:.4f} m/s  (3400 m³/h, cadre 592×592)  |  ΔP moy = ΔP propre +10%  |  W = 11,328 × ΔP moy\n")
classes,exclus_all={},{}
for fp in sorted(glob.glob("produits/*.json")):
    if os.path.basename(fp).startswith("_"): continue
    d=json.load(open(fp)); r,e=traiter(d)
    if r: classes[d["nom"]]=r
    if e: exclus_all[d["nom"]]=exclus_all.get(d["nom"],[])+e

print("="*78); print("FILTRES AVEC ÉTIQUETTE ÉNERGÉTIQUE (estimation indicative)"); print("="*78)
for nom,rows in classes.items():
    print(f"\n■ {nom}")
    # dédoublonne lignes identiques (low/high mêmes poly)
    seen=set()
    for sub,iso,dpi,W,cl in rows:
        key=(sub,round(dpi))
        if key in seen: continue
        seen.add(key)
        print(f"   {sub:14s} | {iso:11s} | ΔP {dpi:5.0f} Pa  →  W {W:5.0f} kWh/an  →  classe {cl}")

print("\n"+"="*78); print("FILTRES NON CLASSÉS (hors périmètre Eurovent 4/21)"); print("="*78)
for nom,e in exclus_all.items():
    print(f"   {nom:18s} → {', '.join(sorted(set(i for _,i in e)))}")
