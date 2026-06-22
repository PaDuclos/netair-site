# PROCESS — Fabrication des fiches techniques Netair

> Méthode validée sur **NETPLAN** (juin 2026). À lire au début de chaque session
> avant de créer/modifier une fiche. Outils : `Generateur/` → livrables `Fiches_Netair/`.

## Principe

L'utilisateur ne manipule pas le générateur : il donne ses consignes, Claude Code
édite un `.json` et lance le script. Le **gabarit n'est jamais retouché à la main par
produit** ; on ne change que les **zones variables** via `produits/<slug>.json`.
Garantie : régénérer `produits/_gabarit_ref.json` reproduit `gabarit_base.html` à
l'octet près (test d'identité — à relancer après toute modif du moteur ou du gabarit).
`produits/netply.json` est la **fiche produit NETPLY officielle** (≠ l'ancre `_gabarit_ref.json`).

## Règles d'or

1. **Proposer avant d'agir.** Présenter la prochaine étape, attendre validation.
2. **Questions = choix cliquables** (jamais en texte libre).
3. **Données réelles uniquement.** Ne jamais inventer de valeur certifiée ; **marquer
   « À VALIDER »** ce qui est estimé. Interroger l'utilisateur dès qu'une donnée
   manque ou que les sources se contredisent.
4. **Reformuler** les textes Titanair (descriptif) — ne jamais copier mot pour mot.
5. **Vérifier au navigateur** (preview) chaque fiche : 0 erreur JS, valeurs ΔP/courbe/
   calculateur, photo, tient sur l'A4. Fournir une preuve (capture).
6. **Commit + push** sur la branche `feature/generateur-fiches` après validation.

## Étapes pour une nouvelle fiche

1. **Identifier le produit** : `Bibliotheque_Fiches_Techniques_Netair.xlsx` +
   `Gamme_References_Netair.xlsx` (BLOC1). Noter la **réf. Titanair** équivalente.
2. **Rassembler les sources réelles** dans `Titanair/` :
   - *Descriptif* → `Documentation/DOCUMENTATION 2015/<produit>.pdf` (à reformuler).
   - *Specs + courbe ΔP* → `Fiches techniques 2018/<PRODUIT>/` (PDF + Excel).
     Les points ΔP exacts sont dans le **cache du graphe Excel** (`xl/charts/chart1.xml`).
   - *Polynôme ΔP* → recouper `FORMULE_PDC.xlsx` ; source de vérité des coefficients =
     `DONNEES_PDC_Netair.xlsx`.
   - *Photo* → `Photos Filtres/<PRODUIT>/` → **détourer sur blanc pur**
     (composantes connexes depuis les bords, seuil sous le métal).
3. **Contrôler la qualité des sources** (cf. Pièges) avant d'utiliser une valeur.
4. **Caler la structure avec l'utilisateur** (questions cliquables) : nb de classes,
   mono-classe ?, épaisseur(s), **plage de vitesse (Vmax)**, **point/débit nominal**,
   dimensions standard à retenir.
5. **Remplir `produits/<slug>.json`** (zones variables seulement).
6. **Mettre à jour les sources de vérité** : coefficients dans `DONNEES_PDC`,
   ligne produit dans `Bibliotheque` (statut, version, nom de fichier, classes).
7. **Générer** : `cd Generateur && python3 generer.py produits/<slug>.json`
   → sort dans `Fiches_Netair/` avec la photo.
8. **Vérifier** au navigateur (valeurs + rendu + A4) et **relancer le test d'identité**
   NETPLY si le moteur/gabarit a changé.
9. **Commit + push.**

## Modèle ΔP (validé)

Calculateur = **polynôme `ΔP = a·v² + b·v + c`** (mesures R&D), source `DONNEES_PDC`.
Constantes énergétiques conservées du gabarit (CO₂ 0,079 kg/kWh, prix 0,18 €, 250 j).

## Règle ΔP finale recommandée (spec) — IMPÉRATIVE

ΔP finale recommandée = **min( ΔP initiale + ADD ; 3 × ΔP initiale )** — EN 13053, où **ADD dépend de la classe** :

| Classe | ADD |
|---|---|
| **Coarse** (G / grossier) | **+ 50 Pa** |
| **ePM10 · ePM2,5 · ePM1** | **+ 100 Pa** |

C'est **exactement** la logique du calculateur énergétique (constante `ADD = { Coarse: 50, ePM: 100 }` dans le moteur).
Le **texte de la ligne specs doit refléter la (les) classe(s) réelle(s) de la fiche** :

- Fiche **mono-Coarse** (NETFIBRE, NETPLAN, NETMETAL, NETFIL) :
  `"min(ΔP initiale + 50 Pa ; 3 × ΔP initiale) — EN 13053"`
- Fiche **multi-classes Coarse + ePM** (NETPLY v6 : G4 Coarse + M5 ePM10) :
  `"min(ΔP initiale + 50 Pa [Coarse] / + 100 Pa [ePM] ; 3 × ΔP initiale) — EN 13053"`
- Fiche **ePM seule** (à venir : NETBAG S, NETPAK…) : `+ 100 Pa`.

**Ne jamais** mettre les valeurs absolues des fiches Titanair (ex. 250 Pa EN 779 / 200 Pa ISO) : elles dépendent
du débit et contredisent le calculateur.

## Réglages disponibles par produit (clés du JSON)

| Clé | Effet |
|---|---|
| `classes.low/high.poly` | polynômes a/b/c par épaisseur (48/98) |
| `classes.*.dp` | ΔP de référence du tableau dimensions (= polynôme au point nominal) |
| `mono_classe` | fiche à 1 seule classe (1 courbe, sélecteurs masqués) |
| `surface_facteur` | surface filtrante : `2` (plissé) ou `1` (plan, frontale) |
| `vmax` | vitesse max de la courbe (axe X reconstruit auto) |
| `pmax` | échelle haute de l'axe Y / ΔP (défaut 120 Pa ; graduations 0…pmax auto) |
| `debit_nom` | débit nominal → point nominal, annotation, défaut calculateur |
| `classes.*.epaisseur` | épaisseur réelle (légende, libellés) |
| `note_dimensions` | note sous le tableau dimensions |
| `compact_p1` | réduit les marges verticales de la page 1 (contenu dense qui doit tenir sur l'A4), par produit |
| `series` (+ `courbes`, `classes_def`, `classes_order`, `eff0`, `len0`) | **mode multi-classes opt-in** (N courbes classe × longueur ; calculateur à sélecteur classe × longueur ; cases par classe). Chemin **legacy 2×2 inchangé** sans cette clé → test d'identité NETPLY préservé. Utilisé par NETBAG S. |
| `multi_classe` (+ `classes_list`, `dimensions_multi`, `velocities`, `eff_default`) | **mode multi-classes « compact » opt-in** → `generer_multi`. **Sélecteur 5 classes**, 2 courbes (classe choisie en 48/98) à la fois, fiche **3 pages** (P1 desc/specs · P2 dimensions + tableau ΔP complet + courbe · P3 calculateur), surface m²/m², réfs cadre `-A`/`-P`. Chemin 2×2 inchangé. Utilisé par NETPAK S CILIA. ⚠️ proche de `series` — à fusionner un jour. |

## Pièges identifiés (à surveiller partout)

- **Graphes Excel copiés-collés** : la courbe G3 de TITAPLAN était une copie du G4
  (vérifié via le cache). Toujours contrôler la cohérence avant d'utiliser.
- **Sources contradictoires** (plaquette 2013 vs fiche 2018 vs FORMULE_PDC) →
  **priorité aux fiches techniques 2018**.
- **Surface** : filtre plan = frontale (×1) ; plissé = ×2.
- **Plage de vitesse propre à chaque produit** (NETPLAN : max 2 m/s, nominal 1,5).
- **Extrapolation** au-delà de la plage mesurée → la signaler et, si possible,
  caler le point nominal **dans** la plage mesurée.

## Checklist de validation (à faire confirmer par l'utilisateur)

- [ ] Correspondance EN 779 ↔ ISO 16890 (classes et %)
- [ ] Source de la courbe ΔP + vitesse nominale
- [ ] Épaisseurs et dimensions standard (retirer les non-standard)
- [ ] Photo (détourée blanc pur)
- [ ] Specs sensibles : classement feu, températures, humidité
- [ ] Pied de page : n° de fiche, version, date

## État d'avancement

- **NETPLY** — fiche officielle `Fiche technique NETPLY.html` (v1.0), d'après TITAPLY EC :
  specs réelles (acier galvanisé, sans couture ni colle), éco-conception générique, photo
  détourée, `compact_p1`. Source = `produits/netply.json`. Ancre du test d'identité =
  `produits/_gabarit_ref.json`. (l'ancienne fiche placeholder est dans `_Archive/divers/`)
- **NETPLAN** — mono-classe G4, polynôme, 0-2 m/s, nominal 1,5 m/s (ΔP nom ≈ 42 Pa) ✅
- **NETMETAL** — mono-classe G3 / Coarse 50% (équiv. TITAMETAL KMZ/A alu, ép. 48), polynôme
  7,34·v²+2,44·v+5,57 (fit 5 pts 0,79–2,38 m/s), Vmax 2,4 · nominal 1,5 m/s (1900 m³/h) ✅
  — doc 2015 disait G1-G2 → priorité fiche 2018 ; photo placeholder Titanair à remplacer ;
  ΔP au-delà de 2,38 m/s non mesurée.
- **NETFIL** — mono-classe G3 / Coarse 50% (équiv. TITAFIL, filtre cousu), polynôme
  3,99·v²+7,24·v+0,97 (fit 6 pts 0,16–1,5 m/s, fiche v2_2020), Vmax 1,5 · nominal 1,0 m/s (1260 m³/h) ✅
  — 3 révisions Titanair (G3 2020 / G4 2023) → G3 retenu (cohérent gamme) ; épaisseur 20 mm et
  photo placeholder à valider ; domaine basse vitesse hors grille débits de DONNEES_PDC.
- **NETFIBRE** — mono-classe G4 / Coarse 65% (réf. TITAFIBRE, fiche 2018 FT 2018-030, ép. 20 mm), polynôme
  14·v²+1,8·v+8 (fit 4 pts courbe fiche 2018, R²≈0,998), Vmax 2 · nominal 1,5 m/s (1900 m³/h, ΔP≈42 Pa) ✅
  — média synthétique densité croissante vendu en **panneau découpé sur mesure** (média aussi en rouleau 20×2 m) →
  `no_dimensions:true`, `surface_facteur:1`, mention découpe/rouleau dans le descriptif. Courbe G4 **identique à NETPLAN**
  (probable graphe Excel réutilisé) mais recoupée par doc 2013 (ΔP init G4 38 Pa @1,5 m/s) → retenue en la signalant.
  Gamme complète G2→M5 annoncée (specs+sous-titre) mais courbes G2/G3/M5 **à mesurer** (doc 2013 : G2 10/G3 24/M5 125 Pa @1,5 m/s).
  Photo Titanair détourée sur blanc (rouleau+panneaux) — placeholder à remplacer par photo Netair.
- **NETBAG S** — poches souples, fiche **MULTI-CLASSES** (1ʳᵉ utilisation du moteur `series`). 10 courbes ΔP
  **réelles** extraites des **courbes vectorielles** des PDF `TITABAG` 2018 (recalées sur les axes ; contrôle :
  F9 p500 reproduit 38/58/81/105/134/166/199 Pa). Classes M5/M6/F7/F8/F9 × profondeurs 380/500/550/650 mm,
  surface média réelle par ligne (3,46–6,10 m²), polynômes auto (LINEST) dans `DONNEES_PDC` l.28-37. Toutes ePM
  → ADD +100 Pa. Vmax 3,17 · nominal 3400 m³/h · axe Y 240 Pa. Descriptif reformulé du `livret_2023` p.9.
  **Anomalie** M5 550 mm (ΔP < 650 mm, incohérent) → marquée « à valider » (courbe pointillée). G4 annoncé
  (gamme) mais non mesuré. Manques suivis dans **`CHECKLIST.md`** (tracker global, section NETBAG S). Photo Titabag détourée = placeholder.
- **NETPAK S CILIA** — filtre **compact à mini-plis** (équiv. TITAPAK S PRISME A), **MULTI-CLASSES** (moteur `multi_classe`) ✅
  Fiche **3 pages** : P1 desc/specs · P2 dimensions + **tableau ΔP complet** + courbe · P3 calculateur. **Sélecteur 5 classes**
  M5·M6·F7·F8·F9 ; classe choisie tracée en **48 mm (navy) + 98 mm (teal pointillé)** ; calculateur piloté par la classe + toggle
  épaisseur. Source = **PRISME A HPE 2018** (fiches 2018, ep48+ep98, caches Excel) — courbes distinctes, ΔP croissante, ep98<ep48.
  **10 polynômes** ajustés R²≈1 (DONNEES_PDC l.38-47). **Surface m²/m²** (≈33 ep48 / ≈68 ep98, dimension-indépendante car courbe
  en vitesse) + absolus en tableau dims (11,68 / 23,87 m² @592×592). **Cadre** acier galvanisé (**-A**) / plastique (**-P**), même ΔP.
  **PIÈGES** : (1) PRISME P : F8=F9 (copier-collé) → écarté, PRISME A où F8≠F9 ; (2) PRISME A **ep48 : F9 = F8 + 10 Pa exact**
  (offset suspect, À VALIDER) ; (3) F8 ep98 = 6 pts, 7e (≈137 Pa @3,17) extrapolé. Vmax 3,17 · nominal 3400 m³/h · axe Y 200 Pa.
  Nom validé par PA via skill `netair-naming` (CILIA = cils vibratiles, pas de chevauchement PRISME). Photo PLACEHOLDER à remplacer.
- Suivants : NETPAK S BORA/AZUR/LUMEN/DUO, NETCEL…, NETCARB… (cf. Bibliothèque / CHECKLIST)
