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
| NETMETAL | 🟡 | ΔP > 2,38 m/s non mesurée · ~~classe~~ ✅ G2/G3 (déc. PA) |
| NETFIL | 🟡 | épaisseur/profondeur · ~~G3/G4~~ ✅ G3 confirmé (PA) |
| NETFIBRE | 🟡 | courbes G2/G3/M5 à mesurer · ~~T°~~ ✅ 60 °C confirmé (PA) · **⚠️ TARIF (site B2) : G3 panneau = 0,015 €/dm² dans l'Excel = 5,7× moins cher que G4 (0,0856) → 1,51 € vs 8,57 € pour un 592×592. Jugé erroné (déc. PA 30/06) → G3 retiré de l'offre boutique (`classesExclues`). À corriger/supprimer à la SOURCE (Excel) après vérif R&D, puis ré-exporter.** |
| NETBAG S | 🟡 | Anomalie M5 550/650 · G4 intégré specs (Coarse 65%, courbe à mesurer) · 287×592 & humidité · photo · **⚠️ TARIF (site B2, MAJ 30/06) : le code Excel « 11 » étiqueté « NETBAG S » est EN FAIT AZUR (déc. PA : profondeur 292, dim 287/490/592×592, M5→F9). Reste le code 17 (poches 360-600 mm, F7/F8/F9/M6, ~7-11 €) = candidat NETBAG réel, à confirmer au retravail de l'Excel. Tant que non tranché → NETBAG S reste « sur devis ».** |
| NETPAK S AZUR | 🟡 | **⚠️ TARIF (site B2, 30/06) : = catégorie Excel 11 (mal étiquetée « NETBAG S » dans l'Excel → À RENOMMER en AZUR). Branché à l'achat (3 dim 287/490/592×592×292, M5→F9, prix). Fiche : parois « Polystyrène » → « Plastique » (déc. PA). Vérifier que M5/M6 sont bien standard pour AZUR (fiche disait « F7/F8/F9, M6 sur demande »).** |
| NETPAK S LUMEN | 🟡 | **⚠️ TARIF (site B2, 30/06) : l'Excel n'a que 2 dimensions (287×592, 592×592) — il MANQUE le 490×592 (3ᵉ format standard, déc. PA) → à AJOUTER dans l'Excel puis ré-exporter (apparaîtra tout seul). Fiche MAJ : efficacités M5→F9 ajoutées, cadre « plastique ». Classes M5→F9 gardées (déc. PA).** |
| NETBAG (G4 préfiltration) | ⬜ | Courbe G4 à mesurer |
| NETPAK S CILIA | 🟡 | F9 ép.48 = F8+10 Pa (suspect) · F8 ép.98 7ᵉ pt extrapolé · F7 GREENTEX croisement ép.48/98 · photo |
| NETPAK S AZUR | 🟡 | F8 = F9×0,95 (dérivé) · M6 non mesurée · surface média n.c. · photo |
| NETPAK S LUMEN | 🟡 | Variantes fournisseurs 2024-25 (MFILTER/FILTECH) · surface média n.c. · photo (Titanair visible) |
| NETPAK S BORA | 🟡 | GREENTEX ePM1 50% retenu (variante HPE 55% non tracée) · courbe lue sur image · surface n.c. · photo |
| NETPAK S DUO | 🟡 | ✅ créée (F7 GREENTEX + CA, ep48) · capacité charbon (grammage) à préciser R&D · A4 p2 OK · photo |
| NETCEL V LAM | 🟡 | ✅ créée (HEPA H14, flux laminaire, A4 OK) · capacité/colmatage à confirmer · photo HEPA |
| NETCEL V NIVAL | 🟡 | E10 & H14 sans courbe (H14 = copie H13) · 610×610 sur moteur 592 · photo |
| NETCEL V AZUR | 🟡 | H13 extrapolé >2400 m³/h · curseur débit init 3400 (calc OK 2400) · photo = idem NETPAK AZUR · nom à valider |
| NETCARB CILIA | 🟡 | ✅ créée (charbon actif, ISO 10121, 2 épaisseurs) · classe LD/MD/HD à déterminer par essai · capacité/durée de vie gaz R&D · photo (grains) |
| NETCARB AZUR | 🟡 | ✅ créée (charbon dièdre, mono-classe 292) · courbe 2020 QL-CARB (piège 2023 F7=F8 écarté) · classe LD/MD/HD & capacité R&D · photo blend placeholder |
| NETCARB NIVAL | 🟡 | ✅ créée (polydièdre, mono 292) · ⚠ courbe ΔP partagée AZUR (V-CARB sans courbe propre → R&D) · parois polyester à confirmer · photo Q-carb (code visible→remplacer) |
| NETCARB BAG | 🟡 | ✅ créée (poches souples F9 + charbon imprégné, COMBINÉ colmatant) · HR n.c. · capacité/classe 10121 R&D · photo forme NETBAG (média à reshooter) |

---

## 🔧 À INTÉGRER DANS LE CALCULATEUR (retravail Excel — déc. PA 30/06)

> **Principe figé : le configurateur du site ne référence QUE le calculateur.** Tout ce que le
> configurateur doit afficher (épaisseur, efficacité, dimensions, cadre) doit vivre dans l'Excel ;
> le site le lit après ré-export. Une seule source, mises à jour faciles, pas de divergence fiche↔site.
> Tant qu'une info manque dans l'Excel, le site a une **rustine temporaire** (flaggée) ou n'affiche rien.

À ajouter / corriger dans `Calculateur_Netair.xlsx` puis ré-exporter :
- [ ] **RENOMMAGE PRODUIT (01/07) : NETPAK V LAM → NETCEL V LAM** (code 14, famille HEPA). Fait partout côté site/fiche/docs/code ; **reste à changer le nom de gamme dans les 4 classeurs Excel** (`Calculateur_Netair.xlsx` + `.xltm`, `Gamme_References_Netair.xlsx`, `Bibliotheque_Fiches_Techniques_Netair.xlsx`, `DONNEES_PDC_Netair.xlsx`) via Rechercher-Remplacer « NETPAK V LAM » → « NETCEL V LAM », **puis ré-exporter** `tables.json` (le code 14 ne change pas). FDS à renommer aussi (`FDS_NETPAK_V_LAM` → `FDS_NETCEL_V_LAM`).
- [ ] **Renommer** la catégorie **11** « NETBAG S » → **AZUR** (mal étiquetée).
- [ ] **NETBAG S** : retrouver/figer son vrai code (≈ 17 ?) ; tant que non tranché → reste sur devis.
- [ ] **NETPAK S LUMEN** : ajouter la 3ᵉ dimension **490×592** (n'a que 287×592 / 592×592).
- [ ] **NETFIBRE** : corriger le **G3 panneau** (0,015 €/dm² erroné) → rustine `classesExclues:["G3"]` à retirer ensuite.
- [ ] **NETCEL V LAM** : ne garder que **H14** au tarif si c'est la seule classe vendue (sinon retirer la rustine `classesIncluses`).
- [ ] **Produits sur devis** (NETMETAL, DUO, NETCARB AZUR/NIVAL/BAG, BORA) : les **saisir dans le calculateur** avec leurs **épaisseurs/classes/dimensions** (marqués sur devis, sans prix) → le configurateur affichera alors ces champs tout seuls.
- [ ] **NETPAK S BORA** : épaisseur **100 mm** (actuellement rustine `epaisseursDevis:[100]` côté site → à porter dans l'Excel).
- [ ] **EXPÉDITION — sémantique des codes (doc PA 01/07, à garder en tête)** : l'onglet expédition contient des **départements** (01→95, Corse 2A/2B, tous tarifés) **et** des **modes d'expédition** qui ne sont PAS des départements : `00` = mise à disposition (retrait sur place), `C20`/`C30`/`C40` = Colissimo à 20/30/40 € (choix humain selon **taille/poids estimés** du/des filtre(s)). **Livraison limitée à la France métropolitaine + Corse** (pas de DROM/outre-mer). Côté site : le menu du panier ne propose **que les 96 départements métropole+Corse** (les modes d'expédition et l'outre-mer en sont exclus).
- [ ] **PORT COLISSIMO/CHRONOPOST — piste MISE DE CÔTÉ (déc. PA 01/07)** : après cadrage (règles transporteurs : Colissimo max 30 kg / L+l+h ≤ 150 cm / longueur ≤ 100 cm ; Chronopost max 30 kg / L+2l+2h ≤ 300 cm / poids volumétrique = L×l×h÷5000 ; poids média dispo dans `Poids_filtres`), **décision : on reste au port par département, TOUT en palette**. À reprendre plus tard si on veut proposer le colis (avec **choix client** palette/Colissimo/Chronopost quand éligible) — il manquera alors : paliers de prix négociés PA (poids→20/30/40 €), **poids du cadre** (les kg/m² ne couvrent que le média), marge d'emballage.
- [ ] **MINIMUM DE FACTURATION 80 € HT (déc. PA 01/07) — à porter dans l'Excel** : sous **80 € HT de produits** (hors port), la **commande boutique est bloquée** (message « Montant minimum de commande : 80 € HT »). Actuellement **rustine centralisée** (`MIN_COMMANDE_HT` dans `site/src/lib/boutique.ts`, importée par le panier ET la page produit qui affiche « Commande minimum : 80 € HT ») → **à ajouter aux `Paramètres unitaires` de l'Excel** (comme le franco 750 €), puis lire dans `tables.json` après ré-export. S'applique à la **boutique uniquement** (le devis n'a pas de minimum).
- [ ] **CADRE = info TARIFAIRE** (déc. PA : **le cadre change le prix**). Donc chaque variante de cadre = un **code (ligne tarif) séparé** dans le calculateur, avec son prix. Le configurateur proposera alors les cadres et **basculera le code/prix** selon le cadre choisi (≠ aujourd'hui où le cadre est neutre côté prix → à brancher quand l'Excel le structure).

---

## Transverse (toute la gamme)

- [ ] **Photos produit Netair** : toutes les fiches créées utilisent une **photo Titanair détourée
      en placeholder** → remplacer par des photos réelles du produit Netair.
- [ ] **RÉGÉNÉRATION AUTO DES FICHES (01/07) — décision déploiement à trancher.** Les fiches se
      régénèrent automatiquement au build/dev (`prebuild`/`predev` → `regen-fiches.sh` → `generer_tous.py`)
      tant que **python3** est présent. Les fiches HTML de `site/public/fiches-techniques/` sont
      **committées** (fallback si python absent). ⚠️ Au moment du **déploiement** (hébergeur), trancher :
      soit **committer les fiches régénérées avec chaque édition de JSON** (workflow), soit garantir
      **python3 au build de déploiement** (et éventuellement gitignore les fiches = artefacts). Sans objet
      tant que le site n'est pas hébergé.
- [x] **Page 2 A4 — mono-classe : RÉGLÉ** via option `compact_p2` (marges p2 + graphe 84 %).
      NETPLAN, NETMETAL, NETFIL, NETFIBRE → page 2 = 1123 px (≤ A4). Identité NETPLY OK.
- [ ] **🟠 Débordement A4 — état remesuré le 16/07/2026 (8 fiches sur 18).** Mesure faite au navigateur
      (hauteur réelle des blocs `.a4` ; limite A4 = 1123 px = 297 mm). **La liste du 22/06 était inexacte :**
      NETPAK S BORA ne déborde pas (1123/1123) ; NETCEL V AZUR, NETCEL V NIVAL, NETCARB CILIA et
      NETCARB AZUR débordent sans y figurer.

      | Fiche | Page 1 | Page 2 | `compact_p2` |
      |---|---|---|---|
      | NETPLY | 1299 (+47 mm) | 1344 → **1223 après ajout de `compact_p2` le 16/07** (+26 mm) | ✅ ajouté 16/07 |
      | NETBAG S | 1286 | 1458 | ❌ absent |
      | NETPAK S AZUR | 1229 | 1375 | ❌ absent |
      | NETPAK S LUMEN | 1169 | 1375 | ❌ absent |
      | NETCEL V AZUR | 1123 ✅ | 1375 | ❌ absent |
      | NETCEL V NIVAL | 1123 ✅ | 1375 | ❌ absent |
      | NETCARB CILIA | 1123 ✅ | 1167 | ✅ présent (insuffisant) |
      | NETCARB AZUR | 1129 | 1123 ✅ | ✅ présent (limite) |

      **Constat clé : `compact_p2` manque simplement sur 6 fiches** (NETBAG S, NETPAK S AZUR / LUMEN,
      NETCEL V AZUR / NIVAL — NETPLY corrigé le 16/07). Les 10 fiches conformes tombent *exactement*
      sur 1123 px : le gabarit est bien réglé, mais **il n'a aucun garde-fou** — un contenu trop long
      pousse la page sans alerte.

      **Décision PA (16/07/2026) : viser 2 pages, pas 3** (contrairement à l'orientation du 22/06).
      Motif : ces fiches doivent finir en PDF + catalogue HTML/PDF.

      **✅ NETPLY RÉGLÉ le 16/07/2026** — page 1 : 343,8 → **289,4 mm** (marge 7,6) ; page 2 : 355,6 →
      **290,1 mm** (marge 6,9). Deux leviers, tous deux opt-in par produit, gabarit non modifié :
      - `dims_fusionnees` : le tableau dimensions listait chaque section **deux fois** (une par classe)
        alors que la géométrie est identique → 11 lignes → 6, soit **−31 mm**. Vrai doublon supprimé.
      - `compact_fort` : colonne photo 70 → 52 mm, marges de blocs 6 → 4 mm, interligne du calculateur
        13 → 5 px, graphe 84 → 68 %, cadre de courbe resserré. Vérifié à l'écran : graphe toujours
        lisible (le blanc autour de la courbe a payé, pas la courbe).

      **Deux erreurs d'analyse à ne pas refaire** (16/07) :
      - les « 33 mm de vide sous la photo » **ne sont pas récupérables** : la grille est à 2 colonnes,
        sa hauteur est imposée par la colonne texte (93 mm) ; la photo (60 mm) est juste centrée dedans.
        Le seul levier est la **largeur** de la colonne photo, qui fait refluer le texte.
      - le débordement de la **page 2 n'est pas du gaspillage** : c'est le coût des sélecteurs de classe
        et d'épaisseur, que les fiches mono-classe n'affichent pas. Mesuré vs NETPLAN : calculateur
        +17,6 mm, courbe +7,3 mm (légende de 4 courbes), sélecteur « Afficher : » +5,6 mm.

      **Restent 7 fiches à traiter** : NETBAG S (1286/1458), NETPAK S AZUR (1229/1375), NETPAK S LUMEN
      (1169/1375), NETCEL V AZUR (—/1375), NETCEL V NIVAL (—/1375), NETCARB CILIA (—/1167), NETCARB AZUR
      (1129/—). Pour les 5 sans `compact_p2`, commencer par l'ajouter (≈ −33 mm) avant tout autre levier.
      ⚠️ `compact_fort` suppose 2 classes distinctes et le gabarit standard : ne pas l'appliquer en
      aveugle (il lève une erreur s'il manque compact_p1/compact_p2, mais ne vérifie pas le reste).
- [ ] **🔴 Références du tableau « Dimensions » non conformes à `CODIFICATION_PRODUITS.md`** (constaté sur
      NETPLY le 16/07/2026, **à vérifier sur les 17 autres**). La fiche génère
      `NETPLY-Coarse 65%-G4-592x592x48` alors que la règle impose `NETPLY-G4-592x592x48` :
      *« on utilise la classe EN 779 dans le code. La classe EN 16890 (ePM1 65%…) figure dans la désignation
      et la fiche technique, **pas dans le code article** »*. La fiche insère en plus un espace et un `%`
      dans un code produit. **Le configurateur du site, lui, respecte la règle** (`NETPLY-G4-592x592x48-A`)
      → **le client lit deux références différentes pour le même filtre** selon le support. Corriger le
      générateur, pas les JSON. (Noter aussi : les exemples de `CODIFICATION_PRODUITS.md` utilisent des
      épaisseurs 46/96 mm là où les fiches utilisent 48/98 — à trancher.)
- [ ] **Alignements de gamme créés par le retravail de NETPLY (16/07/2026)** — NETPLY est désormais seul
      conforme, les autres suivront à leur passage :
      - **« Surface média » → « Surface filtrante »** : 11 fiches encore en « Surface média »
        (netcel-v-azur, netcel-v-nival, netfibre, netcel-v-lam, netpak-s-azur, netpak-s-bora,
        netpak-s-cilia, netpak-s-duo, netplan, netpak-s-lumen). Le gabarit écrit déjà
        « S. filtrante (m²) » et « Surface filtrante = … » sur la même page.
      - **Ordre des normes** : NETPLAN, NETMETAL, NETFIL, NETFIBRE affichent **EN 779 avant ISO 16890**,
        contrairement à la règle actée « ISO primaire » (que les badges respectent). PA a confirmé
        le 16/07 : **ISO d'abord**.
- [ ] **Tirets cadratins « — » : 76 occurrences dans les 18 JSON** (18 sous-titres, 37 caractéristiques,
      12 points clés, 9 descriptifs). **PA n'en veut pas** (« ça fait réponse IA », 16/07/2026). Retirés
      des points clés et du descriptif de NETPLY. Restent les sous-titres (`Filtre plissé — Préfiltre
      synthétique`, 18/18) et les caractéristiques (ligne ΔP : `… — EN 13053`), où le tiret sépare deux
      champs plutôt qu'il ne fait du style. Le point médian `·` est déjà le séparateur maison ailleurs.
      **Chantier de charte à trancher, non ouvert.**
- [ ] **Humidité relative max.** : harmoniser/confirmer (100 % retenu par défaut sur média synthétique).
- [ ] **Pieds de page** : numéros de fiche figés OK ; vérifier version/date à chaque révision.
- [ ] **Classe G4 (Coarse, ADD +50)** sur les familles poches/poches rigides : annoncée commercialement,
      rarement mesurée → à mesurer au cas par cas.
- [ ] **Étiquette énergétique Eurovent 4/21** : spec prête et sourcée (Camfil/AFPRO) →
      `SPEC_ETIQUETTE_ENERGETIQUE.md`. **À implémenter** (badge indicatif figé 3400 m³/h, +10 %,
      tables ePM1/2,5/10, Coarse exclu). En attente de validation du design.

---

## Fiches créées — données à compléter

### NETPLY ✅
- [ ] Photo définitive Netair (actuel : TITAPLY EC détouré).

**Contenu retravaillé et validé par PA le 16/07/2026** (descriptif · points clés · caractéristiques).
Arbitrages et divergences à analyser — *ne pas les rouvrir sans PA* :

- [ ] **🟠 Incohérence gamme — le G3.** `Gamme_References_Netair.xlsx` annonce **G3 / G4 / M5** pour NETPLY ;
      la fiche ne présente que **G4 et M5**. **Décision PA (16/07/2026) : G3 retiré, « pas de marché »** —
      alors qu'une heure plus tôt il souhaitait le citer pour ne pas perdre un client vers un confrère.
      **→ le xlsx est désormais en avance sur la réalité : à trancher avec Cowork** (corriger le xlsx,
      ou réintroduire le G3). Aucune courbe ΔP mesurée pour le G3 de toute façon.
- [ ] **🟠 La classe M5 ne vient pas du même produit que le G4.** G4 = **TITAPLY EC** (FT 2018-020 v3 ep48,
      FT 2018-025 v2 ep98). M5 = **PRISME PLY** (FT 2019-032 ep48, FT 2019-033 ep98) — un *autre* produit
      Titanair. Les deux fiches concordent sur les specs (60 °C, M1, surface 2×/3×), mais NETPLY agrège
      bien **deux produits sources**. À confirmer côté fournisseur que la gamme Netair est cohérente.
- [ ] **🔴 « Sans couture ni colle » contredit les 4 fiches Titanair 2018**, qui portent toutes
      **« LUT / BOND : OUI »**. La formule vient du doc commercial *Titaply EC 2013*. **PA a tranché
      le 16/07 en tant que fabricant : c'est exact**, formulé « par un **assemblage** sans couture ni colle »
      (c'est le montage entre grilles qui est concerné, pas le média). À faire confirmer par le fournisseur
      si une preuve écrite est un jour nécessaire.
- [ ] **🔴 « Incinérable : Média : oui · Cadre acier : non » n'est sourcé nulle part** — absent des 4 fiches
      2018. **Confirmé par PA le 16/07.** Seule fiche des 18 à porter cette ligne, alors que NETPLAN a
      lui aussi média + cadre acier → à harmoniser.
- [x] **« Démontable / tri sélectif » RETIRÉ (16/07/2026).** Chez Titanair, la déconstruction repose sur des
      **bouchons de tri brevetés** (*« EXCLUSIVITÉ Groupe TITANAIR »*, doc 2013). Le NETPLY n'est **pas**
      démontable ; PA a précisé que seule la **séparation média / cadre acier** est vraie. Ne jamais
      réintroduire « démontable » ni « éco-conception » (notion juridiquement encadrée).
- [x] **« Sans fibre de verre » sourcé** : `Gamme_References_Netair.xlsx` → FIBRE = SYNTHÉTIQUE,
      TYPE FIBRE = **POLYESTER**. Le taux (100 % ?) n'est pas documenté → écrit « (polyester) » sans
      pourcentage, contrairement à NETFIL qui affiche « 100% polyester » (sourcé, lui).
- [ ] **Surface filtrante 2× (48 mm) / 3× (98 mm)** : confirmé sur les 4 fiches sources, en G4 comme en M5.
      Le descriptif annonce « 2 à 3 fois la surface frontale ».
- [ ] **Tableau dimensions : que du 48 mm** (5 sections). PA (16/07) : *« le standard est ce qui est tenu
      en stock, le gros du marché est en 48 mm ; le 98 mm est une épaisseur standard mais pas tenu en
      stock »*. → note à ajouter sous le tableau ; **bloc dimensions pas encore revu avec PA**.

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
- [x] **Classe G4 intégrée** (23/06/2026, décision PA : specs/gamme **sans courbe**) — Coarse 65% (G4), poche **380 mm**, ADD +50, badges/sous-titre/description/specs mis à jour. ⚠ **Courbe ΔP G4 toujours à mesurer** (aucune donnée TITABAG/FORMULE_PDC ; non tracée au graphe, « sur demande »).
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
Compact miniplis (équiv. TITAPAK S PRISME A). Multi-classes **M5→F9 × ép. 48/98**, fiche **3 pages** (moteur `multi_classe`).
Données ΔP **réelles** : M5/M6/F8/F9 = **TITAPAK S HPE PRISME A 2018** ; **F7 = TITAPAK S GR PRISME A** (GREENTEX, ePM1 50%).
Polynômes : `DONNEES_PDC` l.38-47.

- [ ] **🟠 F9 ép. 48 mm = F8 ép. 48 mm + 10 Pa EXACTEMENT** (33=23+10, 53=43+10, … sur les 7 points) → offset/copie suspecte dans l'Excel Titanair (en ép. 98, F8≠F9 proprement). **À trancher par une mesure R&D du F9 ép. 48.**
- [ ] **F8 ép. 98 mm — 7ᵉ point extrapolé** : 6 points mesurés (0,79→2,78 m/s) ; le point à 3,17 m/s (≈ 137 Pa) est calculé par le polynôme → à mesurer.
- [ ] **F7 (GREENTEX) — croisement ép. 48/ép. 98 à haute vitesse** : au-delà de ~2 m/s la courbe ép. 98 repasse **au-dessus** de l'ép. 48 (ep48 12·20·30·40·51·63·76 / ep98 10·19·29·40·52·67·86), contraire à l'attendu (plus épais = plus de surface = ΔP plus basse). Présent tel quel dans la fiche source GR PRISME A → à confirmer en R&D.
- [ ] **F7 (GREENTEX) ΔP < M5/M6** : média basse résistance → la courbe F7 passe sous M5/M6. Cohérent avec la techno GREENTEX mais à confirmer (mélange HPE/GR dans une même fiche).
- [ ] **Surface média m²/m²** : le tableau dimensions affiche les valeurs HPE (11,68 m² ép. 48 / 23,87 ép. 98 @592×592) comme représentatives ; le F7 GREENTEX diffère (12,55 / 25,65 m²) → préciser si on distingue par classe.
- [ ] **Photo** : TITAPAK PRISME A HD (© A. Périer) détourée sur blanc = placeholder → photo produit Netair.

### NETPAK S AZUR 🟡
Compact polydièdre rigide (équiv. TITAPAK SV-GD). Multi-classes **F7/F8/F9** (ePM1, moteur `series`), profondeur 292.
Données ΔP **réelles** : caches Excel SV-GD 2018 (F7/F9) + FORMULE_PDC. Polynômes : `DONNEES_PDC` l.48-51.

- [ ] **🟠 F8 (ePM1 70 %) = F9 × 0,95 EXACTEMENT** (18=round(19×0,95), … sur les 7 points) → courbe **dérivée, non mesurée** (même type de piège que CILIA F9=F8+10 et NETBAG M5). Affichée normalement sur **décision dirigeant**, mais **à mesurer en R&D**.
- [ ] **M6 ePM2,5 50 %** annoncée (livret DEHS) mais **aucune courbe 2018** → mise en specs/badges seulement (« sur demande ») → courbe à mesurer.
- [ ] **Surface média développée non communiquée** (n.c.) par Titanair → à obtenir/mesurer pour le tableau dimensions.
- [ ] **Largeurs 490/287** : F9 mesuré en 490 ; F7/F8 en 490/287 non mesurés (extrapolés du 592).
- [ ] **Photo** : SV-GD réelle (© A. Périer) légèrement nettoyée = placeholder → photo produit Netair.

### NETPAK S LUMEN 🟡
Compact polydièdre **rechargeable** (équiv. TITAPAK S QUARTZ, argument RSE). Multi-classes **F7/F8/F9** (ePM1, moteur `series`), profondeur 292.
Données ΔP **réelles** : courbes vectorielles PDF QUARTZ 2018 (FT 2019-041), **cohérentes F7<F8<F9** (pas de piège). Polynômes : `DONNEES_PDC` l.52-54.

- [ ] **Variantes fournisseurs 2024-25** : FORMULE_PDC contient des courbes MFILTER (2024) et FILTECH (2024-25) **différentes** des fiches 2018 → le média a peut-être changé. **Priorité fiches 2018** retenue ; à reconfirmer avec le média actuel.
- [ ] **% ePM1** : le livret annonce F7 60 % / F9 90 % ; les fiches 2018 disent **55 % / 80 %** (retenu) → à clarifier.
- [ ] **Surface média développée non communiquée** (n.c.) → à obtenir.
- [ ] **Largeur 287** : non mesurée indépendamment (extrapolée du 592).
- [ ] **Photo** : Quartz.jpg (concept recharge) — **marque « Titanair » visible** sur la cassette → à remplacer en priorité par photo produit Netair.

### NETPAK S BORA 🟡
Panneau compact à brides 100 mm (équiv. TITAPAK S DSK). **Mono-classe F7 GREENTEX (ePM1 50 %)** — décision PA.
Données ΔP **réelles** lues sur l'image `GR DSK F7.png`, recoupées FORMULE_PDC. Polynôme : `DONNEES_PDC` l.55.

- [ ] **Variante HPE ePM1 55 %** : les specs pointées étaient HPE 55 % mais la seule courbe exploitable est GREENTEX 50 % → BORA fait en GREENTEX. Si on veut une fiche HPE 55 %, **courbe HPE à récupérer** (image/PDF non vectoriel).
- [ ] **Courbe lue à l'œil** sur image (±2-3 Pa) ; recoupée FORMULE_PDC (5,83·v²+13,44·v−2,24) → à confirmer par les points mesurés exacts.
- [ ] **Plage mesurée ≤ 3100 m³/h** (panneau 100 mm) ; débit nominal fixé à 3000. ΔP > 3100 non mesurée.
- [ ] **Séparateur** : fiche HPE indique « INT » + colle « OUI », alors que le DSK est annoncé « sans séparateur de colle » (livret) → à clarifier.
- [ ] **Surface média n.c.** · **Photo** : TITAPAK S DSK réelle nettoyée = placeholder → photo produit Netair.

### NETCEL V NIVAL 🟡
Filtre absolu HEPA polydièdre (équiv. TITACEL V), 610×610×292, surface 40 m². **Mode HEPA** (ΔP finale = 2×init, EN 1822 ; pas d'étiquette Eurovent).
Courbe **H13** réelle (cache Excel) : `DONNEES_PDC` l.56. Fit 9,44·v²+75,31·v−1,20 (R²≈1).

- [ ] **E10 — courbe à ajouter** : Excel sans cache, extraction PDF échouée → mentionné en specs/gamme mais sans courbe.
- [ ] **🟠 H14 — courbe à ajouter** : la courbe H14 source (TITAPAK V CU H14) est une **copie exacte du H13** `[39,85,137,189,250,316]` (impossible : H14 doit être plus résistant) → non utilisée. Vraie courbe H14 **à mesurer**.
- [ ] **610×610 sur moteur série calibré 592×592** : axe vitesse + annotation « 592×592 » cosmétiquement décalés (le couple débit↔ΔP reste juste). À corriger si on généralise le moteur aux cadres 610.
- [ ] **Photo** : TITACEL V.png réelle nettoyée = placeholder → photo produit Netair.

### NETCEL V AZUR 🟡
Filtre absolu HEPA multidièdre (équiv. TITAPAK V-GD), 592×592×292, surface 24 m² (H13). **Mode HEPA** (ΔP finale = 2×init).
Courbes **E10 + H13** réelles (caches Excel) : `DONNEES_PDC` l.57-58.

- [ ] **H13 extrapolé > 2400 m³/h** (1,9 m/s) : mesuré jusqu'à 2400 ; au-delà la courbe est calculée par le polynôme → à mesurer si usage haut débit.
- [ ] **🟠 Curseur débit s'initialise à 3400** alors que le calcul utilise bien `debit_nom` (2400) — le moteur série ne synchronise pas l'attribut `value` du slider quand debit_nom ≠ 3400. Décalage cosmétique au chargement → à corriger dans le moteur série.
- [ ] **Photo = même polydièdre SV-GD que NETPAK S AZUR** → trouver/faire une photo distincte du V-GD HEPA.
- [ ] **Nom « AZUR »** partagé avec NETPAK S AZUR (familles différentes, OK par convention) → confirmer.

### NETCARB CILIA 🟡
Filtre **compact à charbon actif** (filtration moléculaire), équiv. PRISME CARB. **PAS de classe particulaire** (filtre de gaz) → cadre **ISO 10121**.
ΔP **réelles** (caches Excel `CARB/PRISME CARB 48.xlsx` & `98.xlsx`, YGLA 2017, cohérentes 48 > 98) : `DONNEES_PDC` l.59-60.
Polynômes 7 pts grille standard : 48 mm 4,851·v²+14,299·v−1,143 ; 98 mm 5,458·v²+10,995·v−2,500 (R²≈1). ΔP@3400 ≈ 73 / 67 Pa.
Moteur : nouveaux drapeaux `deux_epaisseurs` (1 famille × 2 épaisseurs) + `dp_final_mode:const` (non colmatant) + `ref_simple` (code `NETCARB-CILIA-LxHxP`). Identité NETPLY revérifiée OK.

- [ ] **🟠 Classe ISO 10121-3 (LD/MD/HD + %)** : non fournie par Titanair (fiche < 2022) → marquée « à déterminer par essai ». **À mesurer / faire certifier** (essai GPACD ISO 10121-2) avant toute revendication de classe.
- [ ] **Capacité d'adsorption / durée de vie** : 15 % en masse (charge max., donnée Titanair) ; durée de vie réelle = fonction de la charge polluante → **à préciser R&D** (grammage/type de charbon).
- [ ] **T° 40 °C / HR 50 %** : limites propres au charbon (≠ média synthétique 60 °C) — confirmer sur média Netair.
- [ ] **Surface média** : tableau = surface **frontale** (le miniplis charbon développe davantage ; surface développée non communiquée par le fournisseur).
- [ ] **Page 2** : 1167 px (≈ +44 px / A4) — léger débord, **bien inférieur** aux fiches multi-courbes déjà tolérées (NETPLY 1344, AZUR 1375). Laissé tel quel (cohérent décision PA 22/06).
- [ ] **Photo** : `CARB.png` (grains de charbon) aplatie sur blanc = placeholder → visuel produit Netair (cellule PRISME CARB).

### NETCARB AZUR 🟡
Filtre **poches rigides / dièdre à charbon actif** (filtration moléculaire), équiv. SV-GD CARB. **Mono-classe** (1 épaisseur 292 mm).
Courbe **2020 « QL-CARB »** (`DONNEES_PDC` l.61) : 8,073·v²+13,383·v+2,929 (R²=0,999), ΔP@3400 ≈ 98 Pa.
Drapeaux moteur : `mono_classe` + `dp_final_mode:const` + `ref_simple`.

- [ ] **🟠 Piège source écarté** : dans le dossier SV GD CARB, les fichiers `…F7 2023.xlsx` et `…F8 2023.xlsx` sont des **copies exactes** du `…2023.xlsx` base `[22,38,56,77,101,128,155]` (la classe combinée n'y change pas la ΔP) **et dépassent l'axe Y 0-120 de la fiche 2018** → 2023 **non retenue**. Courbe **2020 QL-CARB** conservée (cohérente fiche officielle 2018). À reconfirmer si le média actuel a changé depuis 2020.
- [ ] **Classe ISO 10121-3 (LD/MD/HD)** : non fournie → à déterminer par essai (idem CILIA).
- [ ] **Capacité d'adsorption** : **non communiquée** par Titanair (≠ CILIA qui donnait 15 %) → à préciser R&D.
- [ ] **T° 40 °C** retenue (efficacité d'adsorption, choix PA) alors que la **fiche 2018 indique 80 °C** (tenue structure polyester) → l'adsorption chute > 40 °C. HR max **70 %**.
- [ ] **Option combinée F7/F9 + charbon** : annoncée (doc 2015) mais ΔP combinée non fiable (fichiers 2023 copiés) → courbe combinée à mesurer si commercialisée.
- [ ] **ΔP réelle ~97-102 Pa** sur les 3 tailles (même régime ≈ 2,7 m/s) ; le doc 2015 arrondissait à **85 Pa** (écarté).
- [ ] **Photo** : `CARB_BLEND.png` (charbon + alumine permanganate) sur blanc = placeholder → visuel produit Netair (dièdre SV-GD).

### NETCARB NIVAL 🟡
Filtre **polydièdre à charbon actif** (filtration moléculaire), équiv. **V-CARB** (forme « V », cf. NETCEL V NIVAL). **Mono-classe** 292 mm, nominal **3000**.
Drapeaux : `mono_classe` + `dp_final_mode:const` + `ref_simple`.

- [ ] **🔴 Aucune courbe ΔP V-CARB mesurée** (doc 2018 = « 85 Pa » plat ; aucun Excel V-CARB/TITACEL CARB). **Décision PA (23/06)** : réutiliser la courbe du **pack charbon 292 mm de SV-GD/QL-CARB** (= AZUR, `DONNEES_PDC` l.62 ↔ l.61), assumée **« partagée »**. → **Courbe propre au V-CARB à mesurer R&D** (priorité si on distingue commercialement AZUR et NIVAL).
- [ ] **Redondance AZUR ↔ NIVAL** : aérodynamiquement quasi identiques (même pack charbon). À trancher : garder 2 SKU distincts (formes dièdre vs polydièdre) ou fusionner ? (question gamme/naming).
- [ ] **Parois polyester** : non précisé dans le doc V-CARB → repris de SV-GD CARB par cohérence → **à confirmer**.
- [ ] **Classe ISO 10121-3 & capacité d'adsorption** : à déterminer/préciser R&D (idem famille).
- [ ] **Photo** : `Q-carb.jpg` (forme polydièdre charbon) — **code « Q-carb » visible** → à remplacer en priorité par visuel produit Netair (cf. pattern LUMEN).

### NETCARB BAG 🟡
**Poches souples F9 (ePM1 80 %) à charbon actif imprégné** — **COMBINÉ** particules + gaz (≠ charbon grains), équiv. TITABAG F9 CARB. **Mono-classe**, profondeur 520 mm.
Courbe **réelle** (`DONNEES_PDC` l.63) : 9,172·v²+64,135·v−10,429 (R²≈1), ΔP@3400 ≈ 229 Pa. Drapeaux : `mono_classe` + `ref_simple` (PAS `dp_final_mode:const`).

- [ ] **Filtre COLMATANT** : c'est d'abord un F9 (média synthétique imprégné) → règle ΔP **ePM +100** appliquée (la fiche dit « 2× PDC initiale »). Ne PAS confondre avec les charbons en grains (non colmatants).
- [ ] **Classe ISO 10121-3** (volet moléculaire de l'imprégnation) : très inférieure à un lit de grains → à déterminer/qualifier R&D (l'imprégnation capte odeurs/COV légers, pas un traitement gaz lourd).
- [ ] **Capacité d'adsorption 15 %** (donnée fiche) ; durée de vie gaz selon charge → R&D.
- [ ] **Humidité relative max. non communiquée** par la fiche 2021 → omise (à préciser).
- [ ] **Surface média** : poches souples ≈ 5 m² (ordre de grandeur d'après NETBAG F9 ; exacte non communiquée pour la version imprégnée).
- [ ] **Photo** : forme poches souples (placeholder `netbag-s`) — le média imprégné réel est **plus sombre** → à reshooter en visuel produit Netair.

---

## Fiches à créer — données à rassembler

> Pour chacune : descriptif (à reformuler), specs (fiches 2018), courbe ΔP (cache Excel ou tracé vectoriel
> PDF), polynôme (DONNEES_PDC), dimensions, photo. Réfs Titanair dans la Bibliothèque.

### Poches rigides / compacts — famille NETPAK (noms ⚠ à valider)

### HEPA / T.H.E — famille NETCEL
_(NIVAL et AZUR créées — voir ci-dessus)_

### Charbon actif — famille NETCARB (noms validés PA 23/06/2026)
- [x] **NETCARB CILIA** (compact CA) — réf. PRISME CARB → **créée** (voir ci-dessus)
- [x] **NETCARB AZUR** (dièdre CA) — réf. SV GD CARB → **créée** (voir ci-dessous)
- [x] **NETCARB NIVAL** (polydièdre CA) — réf. V-CARB → **créée** (voir ci-dessous)
- [x] **NETCARB BAG** (poches CA imprégné) — réf. TITABAG F9 CARB → **créée** (voir ci-dessous)

**Famille NETCARB : 4/4 fiches créées ✅** (CILIA, AZUR, NIVAL = charbon grains/moléculaire pur ; BAG = combiné F9+charbon colmatant).

**Paradigme charbon (acté CILIA) à réappliquer :** filtration **moléculaire** (gaz), **pas** ISO 16890 → cadre **ISO 10121** (-1/-2 essai, **-3:2022 classes LD/MD/HD** vs O₃/SO₂/NO₂/toluène). Titanair (fiches < 2022) ne donne **aucune classe LD/MD/HD** → ne pas inventer. Feu **NA**, T° **40 °C**, HR **50 %**. ΔP **non colmatante** (`dp_final_mode:const`) : remplacement à saturation (capacité ≈ 15 % masse) — pas la règle ePM +100. Drapeaux moteur dédiés : `deux_epaisseurs`, `dp_final_mode:const`, `ref_simple`.

---

## Réglé ✅
_(déplacer ici les lignes traitées, avec date)_
