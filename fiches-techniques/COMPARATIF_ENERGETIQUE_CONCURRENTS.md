# Comparatif énergétique Netair vs concurrents (méthode Eurovent 4/21)

> **Document d'analyse interne — comparaison technologique.** Établi le 27/06/2026.
> Classes **Netair** = estimation indicative (voir [`RESULTATS_ETIQUETTE_ENERGETIQUE.md`](RESULTATS_ETIQUETTE_ENERGETIQUE.md)).
> Classes **concurrents** = valeurs publiées par les fabricants (catalogues / pages produit), sourcées colonne par colonne ci-dessous.
>
> ⚠️ **Usage** : aide à la décision interne. Avant toute publication d'un comparatif (site, devis, plaquette),
> faire valider par `netair-juridique-fr` (la publicité comparative est encadrée — art. L122-1 s. C. conso.).
>
> ⚠️ **Limites de comparaison** : la classe énergie dépend fortement du **média** (fibre de verre vs synthétique),
> de la **profondeur** et de l'**efficacité ISO exacte** (qui diffère d'un fabricant à l'autre pour une même lettre EN 779).
> Les valeurs sont donc des **ordres de grandeur de gamme**, pas une équivalence modèle à modèle.

---

## 1. Filtres à poches souples (bag filters) — comparer avec **NETBAG S**

| Efficacité (EN 779 / ISO) | Média | **Netair NETBAG S** | Camfil Hi-Flo | AFPRO HQ85/ES | Deltrian KS |
|---|---|:---:|:---:|:---:|:---:|
| **F7** (ePM1 ~55-60 %) | — | **C** (650 mm) → E (380 mm) | **A+** (640 mm) → D (370 mm) | **A+** (ePM1 60 %) | **E** |
| **F8** (ePM1 70 %) | — | **D** (500 mm) → E (380 mm) | **A** (640 mm) → D | A+ (gamme premium) | **E** |
| **F9** (ePM1 80-85 %) | — | **D** (500 mm) | **C** (640 mm) → E (370 mm) | **A+** (HQ85/ES) | n.c. |
| **M5/M6** (ePM10/ePM2,5) | — | B (M5 550 mm) · E (M6) | n.c. | n.c. | **E** |
| **Type de média** | | **Synthétique** (sans fibre de verre) | **Fibre de verre** | **Fibre de verre** | **Synthétique** |

**Lecture clé** : les concurrents qui atteignent **A+** sur les poches (Camfil Hi-Flo, AFPRO HQ85/ES) le font avec un
**média fibre de verre** (très basse perte de charge). Les poches **synthétiques** — celles de **Netair NETBAG**
**et** de **Deltrian KS** — sont structurellement plus résistantes à l'air → classes C à E. **À média comparable
(synthétique), NETBAG se situe au niveau, voire au-dessus, du Deltrian KS** (souvent classé E).

---

## 2. Filtres compacts / poches rigides — comparer avec la gamme **NETPAK**

| Efficacité (EN 779 / ISO) | **Netair NETPAK** | Camfil Opakfil ES | AFPRO HPQ/ES | Deltrian RPV XL |
|---|:---:|:---:|:---:|:---:|
| **F7** (ePM1 50-60 %) | **A+** (AZUR, CILIA) · **A** (LUMEN) · B (BORA) | **A+** (ES 7, ePM1 60 %) | **A+** | **A** → C |
| **F8** (ePM1 70 %) | **B** (AZUR) · **A** (LUMEN) · C-D (CILIA) | A | A+ | A → C |
| **F9** (ePM1 80-85 %) | **A** (AZUR) · **A** (LUMEN) · C-D (CILIA) | A / B | A+ | **A** (RPV98-6XL, 97 Pa) → C |
| **Type de média** | Fibre synthétique / microfibre | Fibre de verre | Fibre de verre | Fibre de verre / nano |

**Lecture clé** : **c'est là que Netair est le plus fort.** Les compacts **NETPAK AZUR et LUMEN sont en A+/A**,
au niveau des meilleurs compacts premium du marché (Opakfil ES, HPQ/ES, RPV XL). La technologie compacte Netair
est **directement compétitive** avec les leaders. NETPAK CILIA est plus variable (A+ en F7 fin, jusqu'à C-D en F9).

---

## 3. Préfiltres / plissés (NETPLY, NETPLAN, NETMETAL, NETFIL, NETFIBRE)

- **NETPLY version M5 (ePM10 50 %)** : classe **D**. À titre indicatif, le Deltrian KS en ePM10 est classé **E** → Netair devant.
- Les versions **Coarse / G4** (NETPLY G4, NETPLAN, NETMETAL, NETFIL, NETFIBRE) ne reçoivent **aucune** classe Eurovent
  (la norme ne classe que les filtres fins ePM). Idem pour tous les préfiltres concurrents.

---

## 4. Enseignements stratégiques

1. **Force Netair = les compacts (NETPAK).** AZUR et LUMEN jouent dans la cour des A+/A premium. Argument commercial fort.
2. **Le média fait la classe.** Les A+ concurrents sur poches reposent sur la **fibre de verre**. Le choix Netair
   « **sans fibre de verre** » (média synthétique) est un **atout sanitaire/sécurité** mais coûte en classe énergie
   sur les poches → positionnement « air sain sans fibre de verre » plutôt que « champion énergie » sur la gamme poches.
3. **Comparaison loyale = à média égal.** Face à un Deltrian KS (synthétique), NETBAG tient la comparaison. Face à un
   Hi-Flo fibre de verre, l'argument se déplace sur la santé/sécurité, pas sur le kWh.
4. **Piste produit** : pour viser A+ sur les poches, il faudrait un média **microfibre/fibre de verre** ou une
   **poche plus profonde / plus de surface** (cf. NETBAG 550-650 mm déjà mieux classé).

---

## 5. Sources

**Netair** : calcul interne `Generateur/etiquette_energetique.py` (polynômes ΔP R&D), méthode Eurovent 4/21.

**Camfil**
- Hi-Flo (poches, fibre de verre) — classes A+→E selon profondeur : https://www.camfil.com/en/products/general-ventilation-filters/bag-filters/hi-flo/hi-flo-a--uf-_-6048
- Opakfil ES (compact) — ePM1 F7-F9, haute efficacité énergétique : https://www.camfil.com/en/products/general-ventilation-filters/compact-filters-(header-frame)/opakfil/opakfil-es-_-21770
- Opakfil ES 7, ePM1 60 %, 838 kWh/an → A+ (point de calage, cf. spec §6)
- Méthode Eurovent 4/21 : https://www.camfil.com/en/insights/standard-and-regulations/eurovent-4-21

**AFPRO Filters**
- HQ85/ES ePM1 A+ (poche, fibre de verre, ePM1 60 %) : https://www.afprofilters.com/product/hq85-es-a-bag-filter/
- HPQ/ES A+ (compact) : https://www.afprofilters.com/product/hpq-es-a-compact-filter/
- Catalogue produits 2022 : https://www.afprofilters.com/wp-content/uploads/2022/04/Product-catalog-EN-AFPRO-online-1.pdf

**Deltrian**
- KS (poches, média synthétique) — classes E en ePM10/ePM2,5/ePM1 : https://www.deltrian.com/filtration/product/ks-pocket-filters
- RPV XL (compact rigide) — classes A→C ; RPV98-6XL ePM1 85 %, 97 Pa, 1170 kWh/an → A : https://www.deltrian.com/filtration/product/compact-and-rigid-rpv-xl-filters
- RPV GT / SCG / 3V ST (compacts) : https://www.deltrian.com/filtration/products/compact-and-rigid-filters

> **Pour fiabiliser modèle par modèle** : base officielle **Eurovent Certified Performance** (eurovent-certification.com,
> programme FIL) — chaque modèle certifié y a sa classe énergie exacte.
