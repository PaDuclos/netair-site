# SPEC — Étiquette énergétique des fiches Netair (méthode Eurovent 4/21)

> **Statut : proposition à valider — RIEN n'est encore implémenté dans les fiches/le moteur.**
> Décisions déjà actées avec le dirigeant (juin 2026) : option **B** (badge indicatif),
> base **ΔP propre + 10 %**. Reste à valider ce document, puis à coder.

---

## 1. Pourquoi Eurovent 4/21 (et pas le système Titanair)

Le calculateur « classement énergétique » historique de Titanair était **faux** : la classe
**changeait quand on modifiait le débit d'air**. Or une classe énergétique doit être une
**propriété fixe du filtre**, mesurée à un point de référence normalisé.

**Eurovent 4/21 (2019)** est la référence du marché et corrige exactement ça :
la classe est **toujours évaluée au même point**, indépendamment de l'usage réel.

Réf. : Eurovent 4/21:2019 (4ᵉ éd., 25/11/2019) · cotation `RS4/C/001-2019` / `ECP-11-FIL-2020`.

---

## 2. Méthode de calcul (figée)

**Point de référence Eurovent (constantes, non modifiables) :**

| Paramètre | Valeur |
|---|---|
| Débit de référence `qV` | **0,944 m³/s = 3400 m³/h** |
| Cadre | **592 × 592 mm** (pleine taille, EN 15805) |
| Rendement ventilateur `η` | **0,50** (ηtot, EN 16798-3) |
| Temps de fonctionnement `T` | **6000 h/an** |

**Énergie annuelle :**
```
W = qV × ΔP_moyenne × T / (η × 1000)      [kWh/an]
  = 0,944 × ΔP_moyenne × 6000 / (0,5 × 1000)
  = 11,328 × ΔP_moyenne                    [ΔP en Pa]
```

> ⚠️ Ce **W** sert UNIQUEMENT à l'étiquette (point figé 3400 m³/h). Il est **distinct** du
> calculateur énergétique interactif de la fiche (qui reste un outil « et si… » avec curseurs).
> **La lettre de l'étiquette ne doit jamais bouger avec les curseurs.**

**ΔP moyenne — définition officielle Eurovent :** moyenne de la **courbe ΔP vs masse de
poussière** (essai de colmatage ISO 16890-3, poussière L2/AC Fine jusqu'à M10 = 400 g /
M2,5 = 250 g / M1 = 200 g, ou ΔP finale 300 Pa). **Nous n'avons pas cet essai.**

**ΔP moyenne — estimation Netair (faute d'essai de colmatage) :**
```
ΔP_moyenne_estimée = ΔP_initiale(3400 m³/h, air propre) × 1,10
```
Le facteur **+10 %** est calé sur l'exemple officiel Eurovent (ΔP moyenne ≈ +8 % vs initiale)
et **validé par recoupement** avec des poches réellement certifiées (catalogue AFPRO, cf. §6) :
concordance à **±1 classe**. → l'étiquette est donc **« indicative », non certifiée**.

---

## 3. Tables de seuils — classes A+ → E (AEC en kWh/an)

Source : catalogue AFPRO Filters 2021 (réf. Eurovent ECP-11-FIL-2020). Le filtre obtient la
**meilleure classe dont le seuil n'est pas dépassé** (W ≤ seuil), dans la ligne de son **% d'efficacité ISO**.

### ePM1
| Efficacité | A+ | A | B | C | D | E |
|---|--|--|--|--|--|--|
| 50 & 55 % | ≤ 800 | ≤ 900 | ≤ 1050 | ≤ 1400 | ≤ 2000 | > 2000 |
| 60 & 65 % | ≤ 850 | ≤ 950 | ≤ 1100 | ≤ 1450 | ≤ 2050 | > 2050 |
| 70 & 75 % | ≤ 950 | ≤ 1100 | ≤ 1250 | ≤ 1550 | ≤ 2150 | > 2150 |
| 80 & 85 % | ≤ 1050 | ≤ 1250 | ≤ 1450 | ≤ 1800 | ≤ 2400 | > 2400 |
| ≥ 90 % | ≤ 1200 | ≤ 1400 | ≤ 1550 | ≤ 1900 | ≤ 2500 | > 2500 |

### ePM2,5
| Efficacité | A+ | A | B | C | D | E |
|---|--|--|--|--|--|--|
| 50 & 55 % | ≤ 700 | ≤ 800 | ≤ 950 | ≤ 1300 | ≤ 1900 | > 1900 |
| 60 & 65 % | ≤ 750 | ≤ 850 | ≤ 1000 | ≤ 1350 | ≤ 1950 | > 1950 |
| 70 & 75 % | ≤ 800 | ≤ 900 | ≤ 1050 | ≤ 1400 | ≤ 2000 | > 2000 |
| 80 & 85 % | ≤ 900 | ≤ 1000 | ≤ 1200 | ≤ 1500 | ≤ 2100 | > 2100 |
| ≥ 90 % | ≤ 1000 | ≤ 1100 | ≤ 1300 | ≤ 1600 | ≤ 2200 | > 2200 |

### ePM10
| Efficacité | A+ | A | B | C | D | E |
|---|--|--|--|--|--|--|
| 50 & 55 % | ≤ 450 | ≤ 550 | ≤ 650 | ≤ 750 | ≤ 1100 | > 1100 |
| 60 & 65 % | ≤ 500 | ≤ 600 | ≤ 700 | ≤ 850 | ≤ 1200 | > 1200 |
| 70 & 75 % | ≤ 600 | ≤ 700 | ≤ 800 | ≤ 900 | ≤ 1300 | > 1300 |
| 80 & 85 % | ≤ 700 | ≤ 800 | ≤ 900 | ≤ 1000 | ≤ 1400 | > 1400 |
| ≥ 90 % | ≤ 800 | ≤ 900 | ≤ 1050 | ≤ 1400 | ≤ 1500 | > 1500 |

### Coarse (G3/G4) → **PAS de classe énergétique**
Eurovent 4/21 ne classe **que** les filtres fins (ePM1/ePM2,5/ePM10). Les préfiltres **Coarse**
(NETMETAL, NETFIL, NETPLAN, NETFIBRE) n'ont **pas** d'étiquette → badge « Préfiltre — non classé ».

> ✅ Tables **confirmées par Camfil** (leader du marché, brochure FR « Classement Eurovent 2019 »),
> **identiques à AFPRO** sur les 3 groupes — y compris ePM2,5 50-55 % (C ≤ 1300 / D ≤ 1900).
> L'ancienne valeur Interfilter (C ≤ 1200 / D ≤ 1700) était erronée/obsolète → écartée.

**Dimensions dérivées** : Camfil n'affiche **que le 592×592 comme dimension certifiée** ; les
dérivées (287×592, 490×592, 592×287…) reçoivent **la même classe** que le 592×592. → pour nos
fiches multi-dimensions, une seule classe par (classe × longueur), valable pour toutes les largeurs de cadre.

---

## 4. Design du badge (proposition)

- **Emplacement** : badge fixe en page 1, à côté des badges EN 779 / ISO 16890.
- **Libellé** : `Énergie ~ C` + sous-texte `méthode Eurovent 4/21 · 3400 m³/h`.
- **Mention obligatoire** (petit) : *« Estimation Netair (air propre +10 %) — non certifié Eurovent.
  Classe officielle = essai de colmatage ISO 16890-3. »*
- **Échelle couleur** A+ (vert) → E (rouge), façon étiquette électroménager.
- **Indépendant des curseurs** du calculateur interactif.
- **Fiches multi-classes** (NETBAG, NETPAK) : chaque couple (classe × longueur/épaisseur) a sa
  propre ΔP → sa propre classe. **Proposition** : ajouter une **colonne « Énergie »** au tableau
  « Dimensions & références » (1 lettre par ligne), + éventuellement un badge « phare » pour la
  config de référence. (À confirmer.)

---

## 5. Exemples calculés (méthode ci-dessus, ΔP propre +10 %)

| Filtre | Groupe ISO | ΔP init @3400 | ΔP moy (+10 %) | W (kWh/an) | Classe |
|---|---|--:|--:|--:|:--:|
| NETBAG F7 650 mm | ePM1 55 % | 101 | 111 | 1258 | **C** |
| NETBAG F8 500 mm | ePM1 70 % | 128 | 141 | 1595 | **D** |
| NETBAG F9 500 mm | ePM1 80 % | 158 | 174 | 1969 | **D** |
| NETBAG M5 380 mm | ePM10 50 % | 82 | 90 | 1022 | **D** |
| NETBAG M6 380 mm | ePM2,5 50 % | 156 | 172 | 1944 | **E** |

NB : à 3400 m³/h = 2,7 m/s sur **une seule cellule 592×592**, nos poches sont chargées → classes
moyennes. Les configurations **grande surface / multi-poches / 287×592** remontent en A/B. Le badge
**discrimine** donc bien les variantes (utile commercialement).

---

## 6. Calibration sur filtres réellement certifiés (AFPRO 2021)

Vérification de la méthode (ΔP propre +10 %) contre des poches AFPRO **certifiées Eurovent** :

| Filtre AFPRO (ePM10 70 %) | ΔP @3400 | Classe officielle | Notre estimation |
|---|--:|:--:|:--:|
| HQ55A6-3 (360 mm) | 135 | E | E ✅ |
| HQ55A6-6 (635 mm) | 75 | D | D ✅ |
| HQ55A8-6 (8 poches, 635) | 70 | C | C ✅ |

→ Concordance **±1 classe** (l'écart se creuse surtout en ePM2,5, où le colmatage réel est plus
marqué que +10 %). **Suffisant pour un badge « indicatif »** ; insuffisant pour revendiquer la
classe certifiée. (Un cas AFPRO interne est incohérent — 55 Pa noté D — non retenu.)

**Point de calage Camfil (étiquette réelle certifiée)** : *Opakfil ES 7 — ISO ePM1 60 %*,
AEC **838 kWh/an** → classe **A+** (ePM1 60-65 % : A+ ≤ 850). Rétro-calcul : ΔP moyenne ≈ 74 Pa
(838 / 11,33). Cohérent avec la méthode.

---

## 7. Limites & étapes pour passer de « indicatif » à « certifié »

- [ ] L'étiquette **indicative** ≠ étiquette **Eurovent certifiée** (marque déposée Eurovent Certita).
      Ne pas afficher le **logo Eurovent** sans certification.
- [ ] Pour le **réel** : obtenir les **courbes de colmatage ISO 16890-3** (mesure labo ou données
      fournisseurs Deltrian/Mfilters), puis viser la **certification** sur les produits phares.
- [ ] Affiner le **facteur de colmatage** par famille (poches souples vs compacts) une fois
      quelques courbes de colmatage réelles disponibles (le +10 % est une moyenne).
- [ ] Reconfirmer les seuils **ePM2,5** sur le RS4/C/001 officiel.

---

## 8. Sources

- Eurovent 4/21:2019 — PDF officiel (méthode, exemple, Annexe 1 sur le débit fixe) :
  https://www.eurovent.me/wp-content/uploads/publications-files/eurovent-rec-4-21-energy-efficiency-evaluation-of-air-filters-for-general-ventilation-purposes-fourth-edition-2019-en.pdf
- Tables de seuils complètes (3 groupes) — **catalogue AFPRO Filters 2021** (réf. ECP-11-FIL-2020)
  **ET brochure Camfil FR « Classement Eurovent 2019 »** (leader, tables identiques — confirmation croisée) :
  https://www.camfil.com/-/media/files/qbank/documents/__web/insight/standards-and-regulations/brochure-classement-eurovent-2019-fr.pdf
- Exemple d'étiquette certifiée (calage) : Camfil Opakfil ES 7, ePM1 60 %, 838 kWh/an → A+.
- Interfilter (seuils ePM1) · MANN+HUMMEL · TROX (paramètres de référence).
