# CHECKLIST — Données techniques & livrables des fiches Netair

> Tracker **transverse** des éléments **manquants / à valider / à compléter** sur l'ensemble
> de la gamme (pas seulement NETBAG). À tenir à jour à chaque fiche, en parallèle de la
> **Bibliothèque** (registre des versions) et de **DONNEES_PDC** (ΔP / polynômes R&D).
> À lire avec `PROCESS.md`. Cocher au fil de l'eau ; déplacer une ligne réglée vers « Réglé ✅ ».

Légende statut fiche : ✅ validée · 🟡 créée (données à compléter) · ⬜ à créer.

---

## Vue d'ensemble

| Réf. | Statut | Manques / à valider clés |
|---|:--:|---|
| NETPLY | ✅ | Photo finale Netair (placeholder détouré) |
| NETPLAN | 🟡 | Photo · ΔP extrapolée > 2 m/s à confirmer |
| NETMETAL | 🟡 | Photo · ΔP > 2,38 m/s non mesurée · classe G3 vs doc 2015 (G1-G2) |
| NETFIL | 🟡 | Photo · épaisseur/profondeur · révision G3/G4 à trancher |
| NETFIBRE | 🟡 | Photo · courbes G2/G3/M5 à mesurer · T° harmonisée à confirmer |
| NETBAG S | 🟡 | Anomalie M5 550/650 · G4 non mesuré · 287×592 & humidité · photo |
| NETBAG (G4 préfiltration) | ⬜ | Courbe G4 à mesurer |
| NETPAK S CILIA | 🟡 | F9 ép.48 = F8+10 Pa (suspect) · F8 ép.98 7ᵉ pt extrapolé · F7 GREENTEX croisement ép.48/98 · photo |
| NETPAK S BORA/AZUR/LUMEN | ⬜ | Tout (descriptif, ΔP, dimensions) · **noms à valider** |
| NETPAK S DUO (combiné) | ⬜ | Tout · nom à valider |
| NETPAK V LAM (laminaire H14) | ⬜ | Tout · pas de nom signature (volontaire) |
| NETCEL V AZUR / NIVAL | ⬜ | Tout · NIVAL nom validé, AZUR à valider |
| NETCARB CILIA/AZUR/NIVAL/BAG | ⬜ | Tout · noms à valider (sauf BAG) |

---

## Transverse (toute la gamme)

- [ ] **Photos produit Netair** : toutes les fiches créées utilisent une **photo Titanair détourée
      en placeholder** → remplacer par des photos réelles du produit Netair.
- [ ] **Humidité relative max.** : harmoniser/confirmer (100 % retenu par défaut sur média synthétique).
- [ ] **Pieds de page** : numéros de fiche figés OK ; vérifier version/date à chaque révision.
- [ ] **Classe G4 (Coarse, ADD +50)** sur les familles poches/poches rigides : annoncée commercialement,
      rarement mesurée → à mesurer au cas par cas.

---

## Fiches créées — données à compléter

### NETPLY ✅
- [ ] Photo définitive Netair (actuel : TITAPLY EC détouré).

### NETPLAN 🟡
- [ ] **Photo** Netair (placeholder).
- [ ] **ΔP > 2 m/s** : extrapolée au-delà de la plage mesurée (fiche 2018 ≤ 2 m/s) → à confirmer.
- [ ] Gamme G2/G3 annoncée (ép. 8–25) : seul G4 (ép. 25) tracé.

### NETMETAL 🟡
- [ ] **Photo** Netair (placeholder Titanair).
- [ ] **ΔP > 2,38 m/s** non mesurée (fit 5 pts 0,79–2,38 m/s).
- [ ] **Classe** : doc 2015 annonçait G1-G2, fiches 2018 G3/Coarse 50% (retenu) → confirmer le positionnement gamme.
- [ ] Variantes galva (KMZ) / inox 304 (KMXCA) : courbes propres si commercialisées.

### NETFIL 🟡
- [ ] **Photo** Netair (placeholder « blanc-sur-blanc »).
- [ ] **Épaisseur 20 mm / profondeur ≈ 4,5 mm** (Ø fil cadre) à valider.
- [ ] **Révision Titanair** : descriptif 2015 G2/G3 · fiche v2_2020 G3 · v3_2023 G4 → **G3 retenu**, à confirmer.
- [ ] Domaine basse vitesse (≤ 1,5 m/s) hors grille débits standard de DONNEES_PDC.

### NETFIBRE 🟡
- [ ] **Photo** Netair (placeholder Titanair détouré).
- [ ] **Courbes G2 / G3 / M5 à mesurer** (seul G4 tracé ; 1 point doc 2013 : G2 10 / G3 24 / M5 125 Pa @1,5 m/s).
- [ ] Courbe G4 = **identique à NETPLAN** (probable graphe Excel réutilisé) — recoupée doc 2013, à confirmer en R&D.
- [ ] **T° 60 °C** harmonisée (sources Titanair divergentes 80 / 100 °C).

### NETBAG S 🟡
Données ΔP **réelles** extraites des courbes vectorielles des PDF TITABAG 2018 (recalées sur axes ;
contrôle : F9 p500 reproduit 38/58/81/105/134/166/199 Pa). Détail polynômes : `DONNEES_PDC` l.28-37.

Matrice classe × profondeur de poche **mesurée** :

| Classe | ISO 16890 | 380 | 500 | 550 | 650 |
|---|---|:--:|:--:|:--:|:--:|
| M5 | ePM10 50% | ✅ | — | ⚠️ | ✅ |
| M6 | ePM2,5 50% | ✅ | — | — | — |
| F7 | ePM1 55% | ✅ | — | ✅ | ✅ |
| F8 | ePM1 70% | ✅ | ✅ | — | — |
| F9 | ePM1 80% | — | ✅ | — | — |

Surface média (cadre 592×592) : 380 → 3,46 m² · 500 = 550 → 5,11 m² · 650 → 6,10 m².

- [ ] **🔴 ANOMALIE M5 — courbes 550 mm / 650 mm incohérentes** (priorité — à mesurer en R&D)
      - **Principe** : poche plus profonde = plus de surface média = ΔP plus basse à débit égal.
        Surfaces M5 : 380 → 3,46 m² · 550 → 5,11 m² · 650 → 6,10 m². Ordre ΔP attendu : **380 > 550 > 650**.
      - **Mesuré (ΔP @3400 m³/h)** : 380 = **82 Pa** ✓ · 550 = **48 Pa** · 650 = **65 Pa** → le **650 (plus de
        surface) est PLUS résistant que le 550** : physiquement impossible. À chaque débit, la courbe 650 est
        au-dessus de la 550 alors qu'elle devrait être en-dessous.
      - **Ce n'est pas une erreur d'extraction** : dans les PDF Titanair, l'axe Y est calé sur le pic de chaque
        courbe → M5 550 axe à **70 Pa**, M5 650 axe à **100 Pa**. La source d'origine est elle-même incohérente
        (même type de piège que G3 = copie du G4 sur TITAPLAN).
      - **Hypothèse la plus probable** : **étiquettes 550 ↔ 650 interverties** (ou graphe copié-collé mal
        réétiqueté). Si on inverse : 550 = 65 Pa, 650 = 48 Pa → ordre **82 > 65 > 48**, cohérent. (Le F7 est, lui,
        cohérent : 550 = 105 Pa, 650 = 101 Pa.)
      - **Décision actée (22/06/2026)** : on **garde la donnée brute en l'état**, sans supposition. Les 2 courbes
        sont affichées, **M5 550 en pointillé « à valider »** (fiche + légende), note « ⚠ À VALIDER » dans
        `DONNEES_PDC` l.29. **À trancher par une mesure banc R&D** (M5 550 et 650) → puis MAJ DONNEES_PDC + fiche.
- [ ] **Classe G4** (préfiltration) annoncée (livret/plaquette) mais **aucune fiche 2018** → courbe à mesurer.
- [ ] **Combinaisons classe × longueur manquantes** : M5/M6/F7 en 500 ; M6/F8/F9 en 550/650 ; F9 en 380/550/650 ;
      M6 en 500/550/650 (cf. matrice).
- [ ] **Longueur 300 / 600 mm** (livret_2023) vs **380/550/650** (fiches 2018) : nomenclature à clarifier.
- [ ] **Dimensions 287×592** : cadre standard mais **surface média non fournie** (≈ 0,485 × valeur 592×592) → à mesurer.
- [ ] **Humidité relative max.** non spécifiée sur fiches 2018 (mise à 100 % par cohérence).
- [ ] **Nombre de poches** par cadre (selon longueur/classe) : non documenté.
- [ ] **Option « préfiltre intégré au cœur »** (livret_2023) : décider si commercialisée.
- [ ] **M6 / F7 / F8 (380 mm)** : terme `c` négatif (1ᵉʳ point bas-débit tassé) → léger pied de courbe < 0 (borné 0).
- [ ] **Photo** : `TITABAG/Titabag.jpg` détourée = placeholder → photo produit Netair.

### NETPAK S CILIA 🟡
Compact mini-plis (équiv. TITAPAK S PRISME A). Multi-classes **M5→F9 × ép. 48/98**, fiche **3 pages** (moteur `multi_classe`).
Données ΔP **réelles** : M5/M6/F8/F9 = **TITAPAK S HPE PRISME A 2018** ; **F7 = TITAPAK S GR PRISME A** (GREENTEX, ePM1 50%).
Polynômes : `DONNEES_PDC` l.38-47.

- [ ] **🟠 F9 ép. 48 mm = F8 ép. 48 mm + 10 Pa EXACTEMENT** (33=23+10, 53=43+10, … sur les 7 points) → offset/copie suspecte dans l'Excel Titanair (en ép. 98, F8≠F9 proprement). **À trancher par une mesure R&D du F9 ép. 48.**
- [ ] **F8 ép. 98 mm — 7ᵉ point extrapolé** : 6 points mesurés (0,79→2,78 m/s) ; le point à 3,17 m/s (≈ 137 Pa) est calculé par le polynôme → à mesurer.
- [ ] **F7 (GREENTEX) — croisement ép. 48/ép. 98 à haute vitesse** : au-delà de ~2 m/s la courbe ép. 98 repasse **au-dessus** de l'ép. 48 (ep48 12·20·30·40·51·63·76 / ep98 10·19·29·40·52·67·86), contraire à l'attendu (plus épais = plus de surface = ΔP plus basse). Présent tel quel dans la fiche source GR PRISME A → à confirmer en R&D.
- [ ] **F7 (GREENTEX) ΔP < M5/M6** : média basse résistance → la courbe F7 passe sous M5/M6. Cohérent avec la techno GREENTEX mais à confirmer (mélange HPE/GR dans une même fiche).
- [ ] **Surface média m²/m²** : le tableau dimensions affiche les valeurs HPE (11,68 m² ép. 48 / 23,87 ép. 98 @592×592) comme représentatives ; le F7 GREENTEX diffère (12,55 / 25,65 m²) → préciser si on distingue par classe.
- [ ] **Photo** : TITAPAK PRISME A HD (© A. Périer) détourée sur blanc = placeholder → photo produit Netair.

---

## Fiches à créer — données à rassembler

> Pour chacune : descriptif (à reformuler), specs (fiches 2018), courbe ΔP (cache Excel ou tracé vectoriel
> PDF), polynôme (DONNEES_PDC), dimensions, photo. Réfs Titanair dans la Bibliothèque.

### Poches rigides / compacts — famille NETPAK (noms ⚠ à valider)
- [ ] **NETPAK S BORA** (compact à brides / DSK) — réf. TITAPAK S D.S.K
- [ ] **NETPAK S AZUR** (polydièdre) — réf. TITAPAK SV GD
- [ ] **NETPAK S LUMEN** (polydièdre rechargeable, argument RSE) — réf. TITAPAK S QUARTZ
- [ ] **NETPAK S DUO** (particulaire + charbon actif) — réf. PRISME DUO
- [ ] **NETPAK V LAM** (laminaire H14, pas de nom signature — volontaire) — réf. TITAPAK V LAM

### HEPA / T.H.E — famille NETCEL
- [ ] **NETCEL V AZUR** (multidièdre E10/H13) — réf. TITAPAK V GD · nom à valider
- [ ] **NETCEL V NIVAL** (polydièdre E10→H14) — réf. TITACEL V · nom validé

### Charbon actif — famille NETCARB (noms ⚠ à valider sauf BAG)
- [ ] **NETCARB CILIA** (compact CA) — réf. PRISME CARB
- [ ] **NETCARB AZUR** (multidièdre CA) — réf. SV GD CARB
- [ ] **NETCARB NIVAL** (polydièdre CA) — réf. TITACEL CARB
- [ ] **NETCARB BAG** (poches CA imprégné) — réf. à préciser · nom validé

---

## Réglé ✅
_(déplacer ici les lignes traitées, avec date)_
