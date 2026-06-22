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
| NETPAK S BORA/CILIA/AZUR/LUMEN | ⬜ | Tout (descriptif, ΔP, dimensions) · **noms à valider** |
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

- [ ] **Anomalie M5 — 550 vs 650** : 550 mm donne ΔP @3400 ≈ 48 Pa (5,11 m²) < 650 mm 65 Pa (6,10 m²) →
      physiquement impossible (plus de surface = moins de ΔP). Une des deux courbes est suspecte (graphe
      réutilisé/mal calé). **Provisoire** : les deux affichées, M5 550 marquée « à valider » (pointillé).
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

---

## Fiches à créer — données à rassembler

> Pour chacune : descriptif (à reformuler), specs (fiches 2018), courbe ΔP (cache Excel ou tracé vectoriel
> PDF), polynôme (DONNEES_PDC), dimensions, photo. Réfs Titanair dans la Bibliothèque.

### Poches rigides / compacts — famille NETPAK (noms ⚠ à valider)
- [ ] **NETPAK S BORA** (compact à brides / DSK) — réf. TITAPAK S D.S.K
- [ ] **NETPAK S CILIA** (prisme miniplis) — réf. TITAPAK S PRISME
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
