# CHECKLIST — NETBAG S (poches souples)

> Suivi des éléments **manquants / à valider** de la fiche NETBAG S.
> Source Titanair : `Titanair/Fiches techniques 2018/TITABAG/` (PDF + Excel) ·
> descriptif `Documentation/DOCUMENTATION 2015/livret_2023.pdf` p.9.
> Données ΔP extraites des **courbes vectorielles** des PDF (recalées sur les axes ;
> méthode validée : F9 p500 reproduit 38/58/81/105/134/166/199 Pa).

## Données ΔP disponibles (mesurées) — matrice classe × longueur de poche

Débit testé : 1000 → 4000 m³/h (pas 500). v = débit / 3600 / 0,3505 (frontale 592×592).
Polynôme `ΔP = a·v² + b·v + c` (R² ≈ 1 partout).

| Classe | ISO 16890 | 380 mm | 500 mm | 550 mm | 650 mm |
|---|---|:--:|:--:|:--:|:--:|
| M5 | ePM10 50% | ✅ | — | ⚠️ | ✅ |
| M6 | ePM2,5 50% | ✅ | — | — | — |
| F7 | ePM1 55% | ✅ | — | ✅ | ✅ |
| F8 | ePM1 70% | ✅ | ✅ | — | — |
| F9 | ePM1 80% | — | ✅ | — | — |

Surface média (fiches 2018, cadre 592×592) : 380 → 3,46 m² · 500 = 550 → 5,11 m² · 650 → 6,10 m².

## ⚠️ Anomalies / pièges (à trancher)

- [ ] **M5 — 550 vs 650 incohérent** : 550 mm donne ΔP @3400 ≈ **48 Pa** (5,11 m²) alors que
      650 mm (plus de surface, 6,10 m²) donne **65 Pa** → physiquement impossible (plus de média
      devrait baisser la ΔP). L'une des deux courbes M5 est suspecte (probable graphe Excel
      réutilisé/mal calé). **Décision provisoire** : les deux affichées, M5 550 marquée « À VALIDER ».
      → vérifier sur banc R&D quelle courbe est la bonne.
- [ ] **M6 / F7 / F8 (380 mm)** : terme `c` négatif (le 1ᵉʳ point bas-débit semble tassé) →
      léger « pied » de courbe sous 0 (borné à 0 à l'affichage). Sans effet dans la zone
      d'exploitation, mais à reconfirmer si un point basse-vitesse est mesuré.

## Données manquantes (à compléter ultérieurement)

- [ ] **Classe G4** (préfiltration) annoncée dans la gamme (livret_2023 + plaquette) mais
      **aucune fiche 2018** → pas de courbe. Annoncée en specs/badges, à mesurer.
- [ ] **Combinaisons classe × longueur non mesurées** : M5/M6/F7 en 500 ; M6/F8/F9 en 550/650 ;
      F9 en 380/550/650 ; M6 en 500/550/650. (cf. matrice ci-dessus.)
- [ ] **Longueur 300 mm** : annoncée au livret_2023 (300/380/500/600) mais fiches 2018 = 380/500/550/650.
      Écart de nomenclature longueurs à clarifier (300/600 vs 550/650).
- [ ] **Dimensions 287×592** : cadre standard (livret) mais **surface média non fournie** par les
      fiches 2018 → à mesurer (estimation ≈ 0,485 × valeur 592×592). Non incluse au tableau pour l'instant.
- [ ] **Humidité relative max.** : non spécifiée sur les fiches 2018 TITABAG (mise à 100 % par
      cohérence gamme synthétique — à confirmer).
- [ ] **Nombre de poches** par cadre (selon longueur/classe) : non documenté → à renseigner au tableau.
- [ ] **Option « préfiltre intégré au cœur »** (livret_2023) : à décider si on la commercialise (NETBAG).

## Livrable / présentation

- [ ] **Photo** : `Titanair/Photos Filtres/TITABAG/Titabag.jpg` (poche rose, cadre noir, fond blanc) =
      **placeholder** détouré → à remplacer par une photo produit Netair.
- [ ] Vérifier que la **courbe multi-classes** (jusqu'à 10 tracés) reste lisible sur l'A4 imprimé.

## Décisions actées

- Courbe + calculateur : **toutes les classes M5→F9** avec **toutes les longueurs mesurées**
  (cases à cocher par classe pour filtrer). Manquant → cette checklist.
- ΔP finale recommandée (specs) = `min(ΔP initiale + 100 Pa ; 3 × ΔP initiale) — EN 13053`
  (toutes les classes de poches sont **ePM** → ADD = +100 Pa). G4 (Coarse, +50) ajouté quand mesuré.
- T° de service **60 °C** (acc. 65 °C/1 h), feu **M1**, séparateurs **thermosoudés**, **sans colle**
  (fiches 2018). Cadre **acier galvanisé** (option **polypropylène** — livret).
