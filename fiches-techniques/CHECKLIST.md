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
| NETMETAL | 🟡 | ΔP > 2,38 m/s non mesurée · ~~classe~~ ✅ G2/G3 (déc. PA) · **contenu retravaillé v1.1 (17/07) — voir `_arbitrages_pad` de netmetal.json AVANT toute retouche** · **feu M0 : sourcé (4 fiches 2018) mais (a) classement français 1983 remplacé par les Euroclasses EN 13501-1 (A1) → basculer un jour, (b) PV d'essai à récupérer/refaire pour Netair si un BE le réclame** · **T° inox 304 sous-vendue : la fiche annonce 150 °C (valeur alu/galva) alors que KMX/CA donne 200 °C continu / 300 °C acc. — décision PA du 17/07 de garder une valeur unique prudente ; à rouvrir si l'inox se vend** · épaisseurs 10/15/20 mm et HR 100 % = confirmées PA en tant que fabricant, non sourcées · **ΔP finale recommandée RETIRÉE de la p1 (déc. PA 17/07) → seule des 18 fiches à déroger à la règle « impérative » du PROCESS ; le calculateur p2 applique pourtant toujours +50 Pa** · photo placeholder Titanair |
| NETFIL | 🟡 | **contenu retravaillé v1.1 (17/07) — voir `_arbitrages_pad` de netfil.json AVANT toute retouche** · ~~G3/G4~~ ✅ G3 confirmé (PA) · ~~ISO Coarse 50% « équivalence indicative »~~ ✅ **SOURCÉ** : 4e révision `TITAFIL.pdf` (non datée, SAS/APE 2825Z) porte « ISO 16890 : COARSE 50% » **en face du G3** ; le `_commentaire` affirmait le contraire → corrigé le 17/07 · ✅ **courbe G3 corroborée** par une 4e source jusqu'ici non exploitée (cache `TITAFIL 2013.xlsx` : 6/12/20/38 Pa à 0,5/1/1,5/2 m/s, vs 6,5/11,5/21 pour la v2_2020 retenue) · **🔴 ÉPAISSEUR 4,5 mm = DÉDUCTION, PAS UNE MESURE** : c'est le Ø du fil du cadre (doc 2015) ; un média cousu **sur** un fil de 4,5 mm fait nécessairement plus. Aucune fiche Titanair ne donne d'épaisseur (« DIMENSIONS EFFECTIVES : A DETERMINER »). Le chiffre est **affiché 3×** (légende de courbe + sélecteurs du calculateur) → **seul chiffre visible de la fiche ne provenant d'aucune mesure. À faire mesurer en R&D.** Maintenu par PA le 17/07 après signalement. ⚠️ `PROCESS.md` disait « 20 mm à valider » : **périmé** depuis le commit `2454fec` (22/06), corrigé le 17/07 · **T° 60 °C / acc. 65 °C = CONTRE les 4 fiches Titanair** (toutes à acc. 80 °C ; doc 2015 : 100 °C) — alignement délibéré sur la règle de gamme CLAUDE.md (même média = même T°) · **HR 100 % (sans condensation) = confirmée PA, NON SOURCÉE** (aucune fiche TITAFIL n'a de ligne humidité ; l'ancien 95 % ne venait d'aucune source non plus) · **VC uniquement, jamais CTA = déc. PA, CONTREDIT la doc 2015** (« comme filtre final » en « ventilo-convecteurs, unité de traitement d'air ») · **🔴 3 des 4 points clés = recopie de la rubrique « AVANTAGES DES FILTRES » de la plaquette Titanair 2015** (Faible encombrement / Construction renforcée / Toutes dimensions), et « Faible encombrement » + « Construction renforcée » sont des **jugements orphelins** depuis la réécriture du descriptif (rien sur la page ne les soutient) — **réserves de Claude exposées 3× et écartées par PA en connaissance de cause le 17/07** (une ligne « Épaisseur : 4,5 mm » a été ajoutée puis retirée à sa demande) · « 100% polyester » sourcé **uniquement par v3_2023**, la révision écartée pour sa classe (G4) · photo placeholder Titanair blanc-sur-blanc à remplacer |
| NETFIBRE | 🟡 | **contenu retravaillé v1.1 (17/07) — voir `_arbitrages_pad` de netfibre.json AVANT toute retouche** · ~~courbes G2/G3/M5 à mesurer~~ ✅ **SANS OBJET : gamme réduite à G4 SEUL (déc. PA 17/07)** — la seule courbe mesurée est la G4 ; les classes G2/G3/M5 ne sont plus annoncées (sous-titre et specs nettoyés) · ~~T°~~ ✅ 60 °C confirmé (PA) · **⚠️ TARIF ROULEAU (site B2, 17/07) : incohérence /m² relevée au configurateur — `20 m × 1 m` (20 m²) = 105,14 € soit 5,26 €/m², vs `10 m × 2 m` (20 m²) = 168,43 € soit 8,42 €/m² : +60 % pour la MÊME surface de média. Pire, passer de `10 m × 1 m` (103,69 €) à `20 m × 1 m` (105,14 €) ajoute 10 m² pour +1,45 €, et rend le 20×1 moins cher au m² que le 20×2 (5,74 €/m²). Prix issus de l'Excel (code 5, méthode E) → à VÉRIFIER/CORRIGER À LA SOURCE puis ré-exporter. ⚠️ RUSTINE (déc. PA 17/07) : la boutique ne propose plus qu'UN SEUL format, le **20 m × 2 m** (229,71 €, celui qu'annonce la fiche) ; les 4 autres (10×1, 20×1, 10×2, 30×2) sont retirés de la vente le temps de la vérif R&D → aucun prix douteux n'atteint le client, mais 4 formats réels ne sont plus vendables. À rouvrir après correction de l'Excel.** · **⚠️ TARIF G3 panneau (déc. PA 30/06) : 0,015 €/dm² = 5,7× moins cher que G4 (0,0856) → 1,51 € vs 8,57 € pour un 592×592. Jugé erroné → G3 retiré de l'offre (`classesExclues`). ⚠️ MAJ 17/07 : la gamme étant désormais G4 SEUL, le G3 n'a plus à exister dans l'Excel — la rustine devient DÉFINITIVE (ce n'est plus un prix à corriger, c'est une ligne à supprimer).** · **v1.2 (26/07) : vocabulaire « densité PROGRESSIVE » harmonisé sur la gamme (déc. PA, passe NETBAG S) + sous-titre simplifié « Média filtrant synthétique » — cf. `_arbitrages_pad` (8)** · photo placeholder Titanair à remplacer |
| NETBAG S | 🟡 | **contenu retravaillé v1.1 (26/07) — voir `_arbitrages_pad` de netbag-s.json AVANT toute retouche** · ~~sur devis~~ → **BOUTIQUE BRANCHÉE sur le code 17 (déc. PA 26/07)** : standard 380/550 chiffrés (32,34-36,20 € en 592×592), G4/M5 au menu sans prix (`classesSurDevis`), variante sur-mesure en devis · **divergence longueurs fiche (380/500/550/650) ↔ tarif (360/380/530/550/600) assumée — cf. § calculateur** · anomalie M5 550/650 (inchangée, R&D) · courbe G4 à mesurer · courbe/curseur bornés 4 000 (zéro extrapolation) · photo |
| NETPAK S AZUR | 🟡 | **⚠️ TARIF (site B2, 30/06) : = catégorie Excel 11 (mal étiquetée « NETBAG S » dans l'Excel → À RENOMMER en AZUR). Branché à l'achat (3 dim 287/490/592×592×292, M5→F9, prix). ~~Vérifier que M5/M6 sont bien standard~~ → TRANCHÉ le 17/07 (déc. PA) : fiche alignée sur **M5 → F9** (M5 sans source ni courbe, cf. § détaillé). Parois : « Plastique » partout — **ABS retiré le 18/07 (déc. PA, passe BORA), fiche v1.2 au registre, écart fiche↔configurateur résorbé**.** |
| NETPAK S LUMEN | 🟡 | **contenu retravaillé v1.1 (26/07) — voir `_arbitrages_pad` de netpak-s-lumen.json AVANT toute retouche** · ~~TARIF : ajouter le 490×592~~ → **CADUC (déc. PA 26/07) : les 2 formats sourcés SEULS (287×592, 592×592) — fiche = boutique = Excel, plus de divergence** · plage M5→F9 partout, stock affiché F7/F9 · courbe 4 500 m³/h (F7 seule cochée) · calculateur formats fixes façon AZUR · configurateur vérifié : prix inchangés au centime (relevé 52 lignes) |
| NETBAG (G4 préfiltration) | ⬜ | Courbe G4 à mesurer |
| NETPAK S CILIA | 🟡 | **contenu retravaillé v1.1 (23/07) — voir `_arbitrages_pad` de netpak-s-cilia.json AVANT toute retouche** · fiche **2 pages** (courbe à cases F7 seule cochée, dimensions en p.1) · **surfaces m²/m² corrigées** (l'ancien ≈33/68 était une double division — vraies valeurs 12,55/25,65, média F7) · **cellulose pelliculée (-C)** ajoutée (fiche + configurateur, à tarifer Excel) · étiquette F7 = ePM1 50 % partout (`etiquettesIso`) · F9 ép.48 = F8+10 Pa (suspect) · F8 ép.98 7ᵉ pt extrapolé · croisement F7 ép.48/98 · photo |
| NETPAK S AZUR | 🟡 | F8 = F9×0,95 (dérivé, réserve ROUVERTE 17/07) · M5 ET M6 sans courbe (M5 sans source) · courbe >4000 extrapolée · surface média n.c. · photo |
| NETPAK S LUMEN | 🟡 | Variantes fournisseurs 2024-25 (MFILTER/FILTECH) · surface média n.c. · courbe > 4 000 m³/h extrapolée · photo (Titanair visible) |
| NETPAK S BORA | 🟡 | **contenu retravaillé v1.1 (18/07) — voir `_arbitrages_pad` de netpak-s-bora.json AVANT toute retouche** · plage **G4 → F9** affichée (déc. PA — doc 2013 : M5/F7 seulement), courbe F7 seule · **F7 = ePM1 50 % partout** (média spécial ; étiquette configurateur corrigée via `etiquettesIso` — AZUR/CILIA à trancher à la resynchro) · variante haute efficacité 55% non tracée · courbe lue sur image · surface n.c. · photo |
| NETPAK S DUO | 🟡 | ✅ créée (F7 GREENTEX + CA, ep48) · capacité charbon (grammage) à préciser R&D · A4 p2 OK · photo |
| NETCEL V LAM | 🟡 | **contenu retravaillé v1.1 (04/08) — voir `_arbitrages_pad` de netcel-v-lam.json AVANT toute retouche** · **épaisseur 68 mm corrigée À LA SOURCE dans l'Excel tarifaire** (disait 69 → 0 prix à 68 ; prix inchangés au centime) · **boutique ouverte à E11/E12/H13/U15** (déc. PA) alors qu'**aucune n'a de courbe ΔP** et que **U15 = ULPA** · 6 formats sur les 17 tarifés · surface média retirée (ne valait que pour le 610×610) · **axe courbe en VITESSE** (écart assumé à la convention « axe débit ») · T° 80 °C vs 60 °C sur AZUR (cadre alu — T° d'AZUR à rouvrir) · hot melt à 80 °C et humidité 100 % non sourcés · ΔP 125 Pa mieux-disante que Camfil (140 Pa à 66 mm) · capacité/colmatage à confirmer · photo HEPA |
| NETCEL V NIVAL | 🟡 | E10 & H14 sans courbe (H14 = copie H13) · 610×610 sur moteur 592 · photo |
| NETCEL V AZUR | 🟡 | **contenu retravaillé v1.1 (02/08) — voir `_arbitrages_pad` de netcel-v-azur.json AVANT toute retouche** · **courbe H13 corrigée (axe débit +20 %, erreur détectée PA — DONNEES_PDC réaligné)** · plage E10 → H14 (H14 sur devis, à tarifer — action PA) · ~~curseur init 3400~~ ✅ corrigé moteur · boutique formats standard + classes EPA/HEPA seules (F8 à 12 € neutralisé) · surface retirée (à mesurer) · H13 extrapolé 3000-3500 sur courbe · photo = idem NETPAK AZUR · nom à valider |
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

### 🔴 BLOQUANT AVANT MISE EN LIGNE — la chaîne Excel → site est ROMPUE (constaté le 04/08/2026)

> **Ne PAS lancer `export_excel.py` avant d'avoir traité ce point : le site perdrait tous ses prix.**

Constat, en tentant de ré-exporter pour corriger l'épaisseur du code 14 (export **annulé et restauré**,
prix vérifiés identiques au centime). Un ré-export depuis `Calculateur_Netair.xltm` produirait aujourd'hui :

| Effet | Détail |
|---|---|
| **Plus aucun prix sur le site** | les ~20 gammes calculées (méthodes A→F) repassent toutes en `sur_devis` |
| **7 gammes supprimées** | codes 12, 101, 102, 103, 129, 130, 150 |
| **Retour de noms Titanair / anciens** | NETCARB AZUR → « EDELWEISS », NETCARB → « C-CARB », NETBAG S → « NETPAK S AZUR », NETPAK S DUO → « NETPAK S CILIA DUO », NETCARB CILIA → « NETPAK S CILIA P » |
| **Prix et poids modifiés** | 55 lignes L×l · 42 surface · 18 pièce · 14 surface HF · 9 poids |

Cause : le `tables.json` en service a été **exporté le 01/07 depuis un fichier aujourd'hui rangé dans
`_Archive/Calculateurs/BLOC1/Calculateur_Netair.xlsx`** (empreinte SHA-256 concordante). Depuis, tout le
travail de **renommage Netair** et d'**affectation des méthodes de calcul** ne vit **que dans `tables.json`**
et n'a jamais été reporté dans le classeur de référence `.xltm`.

- [ ] **Décider du sens de la resynchronisation** : soit reporter dans le `.xltm` ce qui n'existe que dans
      `tables.json` (noms, méthodes, 7 gammes), soit acter que `tables.json` devient la source et adapter
      le principe figé ci-dessus. **Tant que ce n'est pas tranché, toute correction tarifaire doit se faire
      par patch chirurgical des deux côtés** (méthode employée pour l'épaisseur du code 14, cf. plus bas).
- [ ] **Vérifier au passage** que `DEVIS AUTO/Calculateur_Netair.xltm` (exemplaire du pipeline) n'a pas
      divergé lui aussi — le LISEZ-MOI de `Grille_Couts_Internes/` signale déjà des empreintes distinctes.

À ajouter / corriger dans `Calculateur_Netair.xlsx` puis ré-exporter :
- [ ] **RENOMMAGE PRODUIT (01/07) : NETPAK V LAM → NETCEL V LAM** (code 14, famille HEPA). Fait partout côté site/fiche/docs/code ; **reste à changer le nom de gamme dans les 4 classeurs Excel** (`Calculateur_Netair.xlsx` + `.xltm`, `Gamme_References_Netair.xlsx`, `Bibliotheque_Fiches_Techniques_Netair.xlsx`, `DONNEES_PDC_Netair.xlsx`) via Rechercher-Remplacer « NETPAK V LAM » → « NETCEL V LAM », **puis ré-exporter** `tables.json` (le code 14 ne change pas). FDS à renommer aussi (`FDS_NETPAK_V_LAM` → `FDS_NETCEL_V_LAM`).
- [ ] **Renommer** la catégorie **11** « NETBAG S » → **AZUR** (mal étiquetée).
- [x] ~~**NETBAG S** : retrouver/figer son vrai code (≈ 17 ?)~~ → **TRANCHÉ (déc. PA 26/07/2026, passe v1.1) : code 17 branché en mode calcul** (identité corroborée par `ep_defaut` 380 typique des poches — le 11 homonyme est AZUR, à renommer, cf. ci-dessus). Restent à faire dans l'Excel :
- [ ] **🔴 BLOQUANT MISE EN LIGNE — confirmer l'identité du code 17 dans l'Excel source.** L'identité n'est corroborée que par des indices (`ep_defaut` 380, plage 360-600) ; les deux codes homonymes « NETBAG S » ont déjà piégé une fois (le 11 = AZUR). Depuis le 26/07 des **prix réels** partent au panier sur ce code : si le 17 désignait un autre produit, des prix faux atteindraient les clients. → Vérification à faire dans `Calculateur_Netair.xlsx` (onglet source du code 17) AVANT toute mise en production (exigence de la revue du 27/07).
- [ ] **NETBAG S — aligner les longueurs de poche du code 17 sur la fiche** : le tarif vend **360/380/530/550/600** mm, la fiche mesure **380/500/550/650**. La boutique ne propose que 380 et 550 (les seules mesurées ET tarifées). → **Tarifer le 500 et le 650** (courbes réelles sans prix) et **statuer sur le 360/530/600** (prix sans courbe ni mention fiche : vrais produits à documenter, ou lignes à purger).
- [ ] **NETBAG S — tarifer G4 et M5** (annoncés fiche, courbes M5 réelles, aucun prix au code 17) → en attendant ils partent en devis via `classesSurDevis` (rustine côté site).
- [ ] **🔴 NETCEL V AZUR — prix F8 490×592 ERRONÉ dans l'Excel (code 13) : 3,50 € au lieu de ~31,50 €** (grille : F8 = 24 € en 287, 33 € en 592 ; F9 490 = 31,50 €). Vendait un filtre à **12 € au lieu de ~108 €** en boutique. **Neutralisé le 02/08** : l'offre du produit est restreinte aux classes EPA/HEPA (`classesIncluses` E10-E12/H13) — le F8 n'est plus commandable sur cette page — mais **la cellule Excel reste fausse**, à corriger à la source puis ré-exporter. **Adresse pour PA** : famille « 3. Filtres HEPA / T.H.E. » · gamme code 13 (NETCEL V AZUR, grille L×l) · ligne ép. 292 / petite 490 / grande 592 · colonne F8 (constaté sur l'export `tables.json` du 01/07 — Excel « v1.0 — 25/06 » ; si l'Excel a été corrigé depuis, simple ré-export).
- [ ] **NETCEL V AZUR — statuer sur les classes particulaires M6→F9 de l'onglet 13** : tarifées dans l'Excel mais absentes de la fiche (filtre absolu). S'il existe un vrai multidièdre particulaire à vendre, c'est un AUTRE produit (page + fiche à créer) ; sinon purger ces colonnes de l'onglet 13.
- [x] ~~**🔴 NETCEL V AZUR — corriger la courbe H13 dans `DONNEES_PDC_Netair.xlsx`**~~ → **FAIT le 02/08/2026** (demande PA : la source de vérité devait suivre immédiatement). L'extraction du cache Excel avait **comprimé l'axe débit de 20 %** (couples 400→2400 au lieu de 500→3000 — erreur détectée par PA sur la fiche source PDF `SV-GD/TITAPAK V-GD 592 H13.pdf`). Ligne 58 : coefficients 31,8/119,76 → **20,3525/95,8058** (c −14,7 et R² 0,9993 inchangés), commentaire corrigé et daté ; ligne 57 (E10, données conformes) : ΔP@nominal 134 → **176** (nominal fiche passé à 3 000 m³/h). Fiche = JSON = DONNEES_PDC réalignés ; aucune autre ligne touchée, zip revalidé.
- [x] ~~**🟠 NETPAK S LUMEN — CRÉER L'OFFRE « RECHARGES »**~~ → **BRANCHÉE le 02/08/2026** (trou signalé
      PA le jour même ; le tarif existait en réalité déjà — **code 10 « RECHARGES NETPAK S LUMEN »** de
      l'Excel, repéré par PA, coeff 0,5 / ratio 4, lignes sans épaisseur). Page LUMEN : menu
      « Conditionnement » **Filtre complet / Recharge (cassettes seules)**, formats 287×592 et 592×592
      lus dans la grille, références `Recharge_NETPAK_S_LUMEN-<classe>-<format>` (format technique à
      tirets bas, déc. PA — nouveau mécanisme `refBase` par variante). Prix de vente vérifiés au centime
      (= grille × 4) : 287 M5-F7 **67,68 €** · F8/F9 82,08 € · 592 M5-F7 **80,64 €** · F8/F9 148,32 € ;
      490×592 → hors_fabrication ; le filtre complet (code 9) n'a pas bougé d'un centime (non-régression
      contre l'arbitrage (10) de la passe LUMEN). **Restent :** (a) confirmation PA de l'unité vendue
      (= jeu de cassettes pour UN cadre ?) ; (b) mention « recharges disponibles » sur la fiche LUMEN
      figée → bump v1.2 avec accord PA ; (c) suffixe `-CAS` de la codification NON utilisé dans la
      référence boutique (déc. PA : format `Recharge_…`) → à réconcilier avec CODIFICATION_PRODUITS.md
      au moment du catalogue Incwo. ⚠️ Vérifier ce point à chaque futur produit rechargeable.
- [ ] **NETCEL V AZUR — AJOUTER LE H14 AU TARIF (action PA, demandé le 02/08)** : plage fiche E10 → H14 (déc. fabricant) mais ni prix ni courbe aujourd'hui → part en devis via `classesSurDevis`. À faire : ajouter la colonne/valeurs H14 au code 13 dans `Calculateur_Netair.xlsx`, ré-exporter (il apparaîtra tout seul au menu avec prix, la rustine `classesSurDevis` sera alors à retirer). Courbe H14 à mesurer par ailleurs (réserve déjà ouverte sur NIVAL : la source H14 était une copie du H13).
- [x] ~~**NETPAK S LUMEN** : ajouter la 3ᵉ dimension **490×592**~~ → **CADUC (déc. PA 26/07/2026, passe v1.1) : LUMEN reste aux 2 formats sourcés (287×592 / 592×592), la fiche les affiche seuls — l'Excel est déjà correct tel quel.**
- [ ] **NETFIBRE — G3 panneau** : ~~corriger le tarif~~ → **SUPPRIMER la classe G3** de l'Excel : la gamme est G4 SEUL (déc. PA 17/07). La rustine `classesExclues:["G3"]` reste en place et devient définitive.
- [ ] **NETFIBRE — tarifs rouleau (code 5)** : incohérence au m² (cf. tableau ci-dessus) — `20 m × 1 m` à 5,26 €/m² vs `10 m × 2 m` à 8,42 €/m² pour 20 m² dans les deux cas ; +1,45 € seulement pour 10 m² de plus entre `10 m × 1 m` et `20 m × 1 m`. À vérifier en R&D puis corriger à la source. **Tant que ce n'est pas fait, seul le 20 m × 2 m est vendu (rustine `formats` à un seul élément dans `produits-gammes.ts`) → à rouvrir aux 5 formats une fois les tarifs fiables.**
- [x] ~~**NETCEL V LAM** : ne garder que **H14** au tarif si c'est la seule classe vendue~~ → **TRANCHÉ (déc. PA 04/08/2026) : l'offre est OUVERTE aux 5 classes tarifées** par l'onglet 14 (E11 · E12 · H13 · H14 · U15) ; `classesIncluses` les liste toutes et la fiche v1.1 annonce la plage E11 → U15. ⚠️ **Réserve ouverte ci-dessous** (courbes ΔP absentes pour 4 d'entre elles).
- [x] ~~**NETCEL V LAM — épaisseur 69 mm**~~ → **CORRIGÉE À LA SOURCE le 04/08/2026 (déc. PA)**. La fiche dit 68 mm (Titanair 2022 + AFPRO référence un « 610×610×68 H14 ») ; l'Excel disait 69, si bien qu'une demande à 68 mm renvoyait `hors_fabrication` (0 prix sur 160 combinaisons). Corrigé **par patch chirurgical, PAS par ré-export** (cf. l'alerte 🔴 ci-dessous) : `Calculateur_Netair.xltm` onglet **Prix_L_et_l C259:C326** (68 cellules) + **Tableau_Gammes E14**, et côté site `tables.json` (68 lignes + `ep_defaut`) et `golden-vectors.json` (340 vecteurs). Sauvegarde : `Calculateur_Netair.xltm.bak_avant_ep68_20260804`. **Preuve : 160 combinaisons, prix à 68 mm après = prix à 69 mm avant, au centime, 0 écart ; 195 tests verts.** ⚠️ Ces fichiers sont **hors du dépôt Git** (BLOC1) : la modification n'est pas couverte par le commit.
- [ ] **🔴 NETCEL V LAM — tarifer les classes sans courbe / mesurer leurs ΔP** : E11, E12, H13 et U15 sont **vendues** depuis le 04/08 mais **aucune n'a de courbe ΔP mesurée** — la courbe, le calculateur et les ΔP du tableau de la fiche restent ceux du **H14** (dit dans la note). À mesurer en R&D, sinon un client comparant deux classes verra la même perte de charge. ⚠️ **U15 = ULPA**, pas HEPA : vérifier que Netair sait effectivement produire et tester cette classe avant de la laisser au menu.
- [ ] **Produits sur devis** (NETMETAL, DUO, NETCARB AZUR/NIVAL/BAG, BORA) : les **saisir dans le calculateur** avec leurs **épaisseurs/classes/dimensions** (marqués sur devis, sans prix) → le configurateur affichera alors ces champs tout seuls.
- [ ] **NETPAK S BORA** : épaisseur **100 mm** (actuellement rustine `epaisseursDevis:[100]` côté site → à porter dans l'Excel).
- [ ] **NETPAK S BORA — étiquette ISO F7** : « ePM1 50 % (F7) » via rustine `etiquettesIso` côté site (la table ISO globale de l'Excel dit 55 %) → à porter dans l'Excel à la resynchro, et trancher AZUR/CILIA au passage.
- [ ] **EXPÉDITION — sémantique des codes (doc PA 01/07, à garder en tête)** : l'onglet expédition contient des **départements** (01→95, Corse 2A/2B, tous tarifés) **et** des **modes d'expédition** qui ne sont PAS des départements : `00` = mise à disposition (retrait sur place), `C20`/`C30`/`C40` = Colissimo à 20/30/40 € (choix humain selon **taille/poids estimés** du/des filtre(s)). **Livraison limitée à la France métropolitaine + Corse** (pas de DROM/outre-mer). Côté site : le menu du panier ne propose **que les 96 départements métropole+Corse** (les modes d'expédition et l'outre-mer en sont exclus).
- [ ] **PORT COLISSIMO/CHRONOPOST — piste MISE DE CÔTÉ (déc. PA 01/07)** : après cadrage (règles transporteurs : Colissimo max 30 kg / L+l+h ≤ 150 cm / longueur ≤ 100 cm ; Chronopost max 30 kg / L+2l+2h ≤ 300 cm / poids volumétrique = L×l×h÷5000 ; poids média dispo dans `Poids_filtres`), **décision : on reste au port par département, TOUT en palette**. À reprendre plus tard si on veut proposer le colis (avec **choix client** palette/Colissimo/Chronopost quand éligible) — il manquera alors : paliers de prix négociés PA (poids→20/30/40 €), **poids du cadre** (les kg/m² ne couvrent que le média), marge d'emballage.
- [ ] **MINIMUM DE FACTURATION 80 € HT (déc. PA 01/07) — à porter dans l'Excel** : sous **80 € HT de produits** (hors port), la **commande boutique est bloquée** (message « Montant minimum de commande : 80 € HT »). Actuellement **rustine centralisée** (`MIN_COMMANDE_HT` dans `site/src/lib/boutique.ts`, importée par le panier ET la page produit qui affiche « Commande minimum : 80 € HT ») → **à ajouter aux `Paramètres unitaires` de l'Excel** (comme le franco 750 €), puis lire dans `tables.json` après ré-export. S'applique à la **boutique uniquement** (le devis n'a pas de minimum).
- [ ] **CADRE = info TARIFAIRE** (déc. PA : **le cadre change le prix**). Donc chaque variante de cadre = un **code (ligne tarif) séparé** dans le calculateur, avec son prix. Le configurateur proposera alors les cadres et **basculera le code/prix** selon le cadre choisi (≠ aujourd'hui où le cadre est neutre côté prix → à brancher quand l'Excel le structure).

---

## 🔴 RÉFÉRENCES PRODUIT — À TRANCHER AVANT INCWO (ouvert le 16/07/2026 par PA)

> **PA : « je pense ce sujet très important, il ne faut pas l'oublier. On en reparle avant Incwo. »**
> **Ne pas paramétrer Incwo ni mettre le site en ligne avant d'avoir tranché.** La référence est la
> **clé pivot** entre le site, le devis et l'ERP : mal formulée, une fiche se corrige ; mal choisie, une
> référence se traîne des années sur les devis et les factures.

### Constat — 4 formats divergents pour le même filtre

| Source | Produit |
|---|---|
| `CODIFICATION_PRODUITS.md` (la règle) | `NETPLY-G4-592x592x`**`46`** |
| Configurateur du site | `NETPLY-G4-592x592x`**`48`**`-`**`A`** (suffixe cadre, absent de la règle) |
| Générateur de fiches (netplan, netcel-v-lam, netpak-s-duo) | `NETPLAN-`**`Coarse 65%`**`-G4-592x592x25` |
| **Excel `Calculateur_Netair.xlsx`** | **AUCUNE référence composée** |

**Le point le plus lourd : l'Excel n'a pas de référence.** Onglet `Tableau_Gammes` → colonnes séparées
`Code gamme` (**un chiffre** : 1, 2, 3, 101…), `Nom de la gamme`, `Efficacité`, `Épaisseur`. Il n'y a donc
rien à « faire correspondre » : la référence **est à construire**, côté prix comme côté Incwo.
`site/src/lib/pricing/data/tables.json` est généré depuis cet Excel et porte les mêmes clés (`code`, `nom`).

### 🔴 Ambiguïté bloquante — les variantes (CIAT)

```
Code 1   → NETPLY           methode: A          remises 9,5 % … 13,5 %
Code 101 → NETPLY (CIAT)    methode: sur_devis  aucune remise
```
Idem `NETFIL (CIAT)` (102) et `NETPLAN (CIAT)` (103). **Deux gammes, deux tarifications, le même nom.**
`NETPLY-G4-592x592x48` ne permet pas de les distinguer — l'une se vend au tarif catalogue, l'autre
uniquement sur devis. **Risque direct : un prix faux qui part chez un client.** Les fiches ignorent
totalement ces variantes.

### Préférence exprimée par PA (16/07/2026)

- Référence **longue, classe ISO incluse** : `NETPLAN-Coarse 65%-G4-592x592x25`
- **Suffixe cadre** `-A` / `-P` quand plusieurs cadres existent
- Exemple CILIA : `NETPAK S CILIA A ePM1 50% F7 592x592x48`
  ou `NETPAK-S-CILIA-A-ePM1 50%-F7-592x592x48` → **tirets ou espaces : à trancher**

### Réserves à examiner (Claude, 16/07) — à confronter aux contraintes réelles d'Incwo

1. **Contredit `CODIFICATION_PRODUITS.md`**, qui écrit explicitement : *« on utilise la classe EN 779 dans
   le code. La classe EN 16890 figure dans la désignation et la fiche technique, **pas dans le code
   article** »*. C'est une exception assumée à la règle « ISO primaire », justifiée par la compacité.
   **Si on retient la préférence PA, il faut réécrire la règle** — les deux ne peuvent pas coexister.
2. **`ePM1 50%` et `F7` sont la même information** (table de correspondance fixe et actée). Les écrire
   tous les deux = classe en double. `NETPAK-S-CILIA-A-ePM1 50%-F7-592x592x48` = 40 caractères, dont ~8
   de redondance. → Choisir : ISO seule, EN 779 seule, ou les deux en assumant la longueur.
3. **Espace et `%` dans un code article** : à valider contre Incwo (longueur max ? caractères admis ?),
   les imports/exports CSV, et un éventuel usage en code-barres. `%` a une signification particulière
   dans les URL. Contournable, mais à décider en connaissance de cause.
4. **Les variantes (CIAT) ne sont pas couvertes** par la proposition → comment les distinguer ?
5. **Épaisseurs 46/96 (règle) vs 48/98 (fiches et Excel)** → laquelle fait foi ?
6. **Sur-mesure** : `CODIFICATION_PRODUITS.md` prévoit ligne libre aux 2 premières commandes, fiche
   catalogue Incwo à la 3ᵉ. La référence sur-mesure suit-elle le même format ?

### Méthode proposée

**Incwo est l'arbitre** : il reçoit la commande du site, sort le devis, facture. La référence doit être
ce qu'Incwo portera comme code article ; tout le reste s'aligne dessus. Ordre : (1) contraintes Incwo,
(2) décisions PA, (3) réécriture de `CODIFICATION_PRODUITS.md`, (4) alignement du site, des fiches et de
l'Excel. **Session dédiée — ce n'est pas un chantier de rédaction.**

---

## Transverse (toute la gamme)

- [ ] **« (papier HEPA) » retiré du média sur NETCEL V LAM et NETCEL V AZUR (déc. PA 04/08/2026)** —
      **NETCEL V NIVAL le porte encore** (« Fibre de verre microfine (papier HEPA) »). Fiche en v1.0,
      passe de contenu non faite → à traiter **à sa passe**, pas avant. À noter : AZUR a été modifiée
      **sans bump de version** (déc. PA : retouche de trois mots deux jours après sa v1.1, écart consigné
      au registre — précédent BORA/CILIA/DUO).
- [ ] **Titre « DIMENSIONS & RÉFÉRENCES STANDARD » devenu inexact** : la colonne « Référence complète »
      est retirée de NETCEL V AZUR et NETCEL V LAM (déc. PA du 16/07, appliquée au passage de chaque fiche),
      mais le titre du bloc — qui vit dans `gabarit_base.html`, donc **commun aux 18 fiches** — annonce
      toujours des références. **Décision de gamme à prendre** : le changer touche les 18 fiches (et
      relance la batterie complète) ; le laisser maintient un titre qui promet une colonne absente sur
      les fiches déjà passées. Ne pas trancher fiche par fiche.
- [x] **Registre `Bibliotheque_Fiches_Techniques_Netair.xlsx` — XML CORROMPU, RÉPARÉ le 04/08/2026.**
      Deux « & » nus (« R&D ») et un « < » nu (« F7 < M5/M6 »), introduits par des passes antérieures
      (lignes NETPAK S AZUR / NETPAK S CILIA), rendaient le fichier **illisible par tout parseur XML**
      (openpyxl échouait ; Excel aurait proposé une réparation). Corrigé en `&amp;` / `&lt;` — **le texte
      affiché est inchangé**, vérifié cellule par cellule. ⚠️ **Leçon pour les prochaines passes : toujours
      échapper `&` et `<` avant d'écrire une chaîne inline dans un `.xlsx`, et revalider avec openpyxl.**
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
      | NETPAK S AZUR | ~~1229~~ → **1123 ✅** | ~~1375~~ → **1123 ✅** (17/07, `compact_p2` + optimisation calculateur) | ✅ ajouté 17/07 |
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

      **Restent 4 fiches à traiter** (AZUR réglée le 17/07 : 1123/1123 ✅ ; **LUMEN réglée le 26/07 :
      1123/1123 ✅** en passe v1.1 ; **NETBAG S traitée le 26/07 : 1286/1458 → 1146,6/1201,9, débords
      résiduels +6/+21 mm ASSUMÉS PA** — coût des 2 rangées de sélecteurs, `compact_fort` vérifié
      inapplicable au chemin série) — **NETCEL V AZUR réglée le 02/08 : 1123/1123 ✅ (passe v1.1,
      `compact_p2` + `calc_formats_fixes`, avec la courbe montée à 90 %)**. Restent : NETCEL V NIVAL (—/1375),
      NETCARB CILIA (—/1167), NETCARB AZUR (1129/—). Pour celles sans `compact_p2`, commencer par
      l'ajouter (≈ −33 mm) avant tout autre levier — il marche désormais sur les fiches série aussi.
      ⚠️ `compact_fort` suppose 2 classes distinctes et le gabarit standard : ne pas l'appliquer en
      aveugle (il lève une erreur s'il manque compact_p1/compact_p2, mais ne vérifie pas le reste).
- [ ] **🔴 Références du tableau « Dimensions » : à RETIRER, pas à corriger.** **Décision PA (16/07/2026) :
      « le client ne copiera pas ce qu'il voit dans le tableau mais le nom du filtre, soit NETPLY »** —
      les codes article servent à **Incwo**, pas au client (cohérent avec `CODIFICATION_PRODUITS.md` :
      ligne libre en devis aux 2 premières commandes, fiche catalogue à la 3ᵉ). NETPLY n'affiche plus de
      référence ; **3 fiches en affichent encore** : `netplan`, `netcel-v-lam`, `netpak-s-duo` → les
      retirer à leur passage.
      ⚠️ **Asymétrie à trancher** : le configurateur du site AFFICHE une référence au client
      (`NETPLY-G4-592x592x48-A`). Si le code n'a pas à être vu du client, pourquoi le site le montre-t-il ?
      À arbitrer avec Cowork.
      Pour mémoire, le défaut de format initial (toujours présent sur les 3 fiches ci-dessus) :
      elles génèrent `NETPLAN-Coarse 65%-G4-592x592x25` alors que la règle impose `NETPLAN-G4-592x592x25` :
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
      - **Ordre des normes** : ~~NETPLAN, NETMETAL, NETFIL~~, **NETFIBRE** affiche encore **EN 779 avant
        ISO 16890**, contrairement à la règle actée « ISO primaire » (que les badges respectent). PA a
        confirmé le 16/07 : **ISO d'abord**. NETPLAN et NETMETAL corrigés le 16-17/07, **NETFIL le 17/07**
        → **il ne reste que NETFIBRE**, à traiter à sa passe de contenu. À noter : NETFIL est mono-classe,
        son libellé reste donc au **singulier** (« Efficacité ISO 16890 » / « Efficacité EN 779 »), 1 classe
        ISO face à 1 classe EN 779 — les fiches multi-classes écrivent « Efficacités ». Divergence de
        libellé volontaire, à rouvrir seulement si on uniformise les 18.
- [x] **Humidité relative — libellé unifié « 100 % (sans condensation) » (déc. PA, 17/07/2026).** Appliqué
      le 17/07 aux **7 fiches concernées** : NETFIL (qui passait de 95 %, valeur non sourcée) + NETPLY,
      NETPLAN, NETMETAL, NETPAK S BORA, NETPAK S CILIA, NETPAK S DUO (qui disaient « 100 % » tout court).
      **Périmètre volontairement limité après audit des 18** — ne pas l'étendre en croyant finir le travail :
      les **3 fiches charbon actif** (NETCARB AZUR 70 %, NETCARB NIVAL 70 %, NETCARB CILIA 50 %) **ne
      changent pas** — le charbon actif est hygroscopique, la valeur basse **est** la contrainte réelle du
      produit et « sans condensation » n'a pas de sens à 50/70 % ; les **8 fiches sans ligne humidité**
      (NETBAG S, NETCARB BAG, les 3 NETCEL, NETFIBRE, NETPAK S AZUR, NETPAK S LUMEN) **restent sans ligne**,
      aucune valeur n'étant sourcée pour elles (PA doit les fournir en tant que fabricant). ⚠️ Le 100 % est
      **confirmé PA mais NON SOURCÉ** : aucune fiche Titanair de ces produits ne porte de ligne humidité.
- [ ] **Tirets cadratins « — » : 76 occurrences dans les 18 JSON** (18 sous-titres, 37 caractéristiques,
      12 points clés, 9 descriptifs). **PA n'en veut pas** (« ça fait réponse IA », 16/07/2026). Retirés
      des points clés et du descriptif de NETPLY. Restent les sous-titres (`Filtre plissé — Préfiltre
      synthétique`, **16/18 au 17/07** : NETMETAL « Filtre métallique » et **NETFIL « Filtre cousu sur fil »**
      n'en portent plus, mais par effet de bord — leur sous-titre a été raccourci sur décision produit, pas
      au titre de ce chantier) et les caractéristiques (ligne ΔP : `… — EN 13053`), où le tiret sépare deux
      champs plutôt qu'il ne fait du style. Le point médian `·` est déjà le séparateur maison ailleurs.
      **Chantier de charte à trancher, TOUJOURS NON OUVERT** — ne pas le déclarer lancé au motif que 2 fiches
      sur 18 n'ont plus de tiret. Corollaire connu : NETPLY et NETPLAN annoncent leur rôle au sous-titre
      (« Préfiltre synthétique »), NETMETAL et NETFIL non → **deux styles de sous-titre coexistent**, assumé.
- [ ] **📄 EXPORT PDF — un fichier PAR CLASSE D'EFFICACITÉ (décision PA, 16/07/2026).**
      **Motif** : sur les fiches multi-classes, les courbes s'affichent via des cases « Afficher : » et le
      calculateur via des boutons de classe. **Un PDF ne se clique pas** → il fige l'état par défaut.
      Constaté sur NETPLY : seule la case G4 est cochée au départ, donc le PDF ne montre **que la courbe
      G4**, alors que les badges annoncent 2 classes et que la légende mentionne « M5 · 48 mm » sans
      qu'aucune courbe M5 n'apparaisse. Un client recevrait une fiche qui se contredit.
      **Règle** : une classe = un PDF, avec la case correspondante cochée et les autres décochées.

      **Périmètre réel — 6 fiches sur 18, soit 32 PDF au lieu de 18** (recompté le 16/07 ; attention,
      la clé `series` est un **booléen**, les classes traçables sont dans `courbes[].cls`) :

      | Fiche | Classes | PDF |
      |---|---|---|
      | NETBAG S | M5 · M6 · F7 · F8 · F9 | 5 |
      | NETPAK S CILIA | M5 · M6 · F7 · F8 · F9 | 5 |
      | NETPAK S AZUR | F7 · F8 · F9 | 3 |
      | NETPAK S LUMEN | F7 · F8 · F9 | 3 |
      | NETCEL V AZUR | E10 · H13 | 2 |
      | NETPLY | G4 · M5 | 2 |
      | *les 12 autres (mono-classe)* | — | *1 chacune* |

      **Quand** : à la toute fin, après remplacement des photos Netair (décision PA : les PDF ne se font
      pas avant). **Ne pas produire de PDF avec les placeholders Titanair.**
      **Comment** : Chrome headless, testé et validé le 16/07 sur NETPLY —
      `"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" --headless=new --disable-gpu
      --no-pdf-header-footer --virtual-time-budget=4000 --print-to-pdf="<sortie>.pdf" "file://<fiche>.html"`
      → 2 pages A4 propres, photo + courbe + calculateur inclus, rien à corriger côté rendu.
      Reste à écrire : le pilotage de l'état des cases par classe avant impression (piste : un paramètre
      d'URL ou un réglage d'export lu au chargement), et le nommage des fichiers.
      **À noter aussi** : le calculateur se fige sur ses valeurs par défaut (139 €, 3400 m³/h, 24 h, 250 j).
      Acceptable — c'est une illustration —, mais à confirmer avec PA avant la campagne.
- [ ] **Humidité relative max.** : harmoniser/confirmer (100 % retenu par défaut sur média synthétique).
- [ ] **Versionnage des fiches — règle PA (16/07/2026) : rester en v1.x tant que le site n'est pas en
      ligne.** Aucune fiche n'ayant été publiée, il n'existe pas de « v1.0 diffusée » dont on s'écarterait :
      les refontes d'avant mise en ligne restent des révisions (v1.1, v1.2…). Le passage en v2.0 se
      justifiera après publication, ou sur un changement de produit. La **date** suit chaque révision.
      *(NETPLY : v1.0 22/06 → v1.1 16/07. Un v2.0 avait été posé puis corrigé.)*
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

**Contenu retravaillé et validé par PA le 16/07/2026** (descriptif · points clés · caractéristiques).
Arbitrages — *ne pas les rouvrir sans PA* :

- [ ] **🟠 G2/G3 annoncés SANS COURBE — décision PA du 16/07 : on les garde.** La fiche affiche
      « Coarse 40% · 50% · 65% » et « G2 · G3 · G4 (réf. : G4) », mais **seul le G4 est tracé** : le graphe
      G3 de la source Titanair était une **copie du G4** (vérifié via le cache Excel), donc écarté.
      ⚠️ **Décision CONTRAIRE à celle prise sur NETPLY le même jour** (G3 retiré, « pas de marché ») :
      ici le G2/G3 se vend en filtre plan. Cohérent avec `Gamme_References_Netair.xlsx` (G3/G4).
      **→ Courbes G2 et G3 à mesurer en R&D.** Tant qu'elles manquent, la fiche annonce trois classes
      et n'en documente qu'une.
- [ ] **🔴 « Sans couture ni colle » et « Incinérable » confirmés par PA, non sourcés.** Même situation que
      NETPLY : les fiches Titanair 2018 portent « LUT / BOND : OUI ». PA a tranché en tant que fabricant
      le 16/07 — le média n'est ni collé ni cousu, donc il se sépare du cadre acier, donc la ligne
      « Incinérable » est vraie. **Ne pas les retirer faute de source écrite.** À faire confirmer par le
      fournisseur si une preuve devient nécessaire.
- [x] **« Parois cellule : Acier galvanisé » retirée** (16/07) : sourcée par la fiche Titanair 2018, mais
      redondante avec « Structure : 2 grilles galvanisées » + « Cadre : acier galvanisé ép. 8/10 ».
      NETPLY n'en a pas.
- [x] **Descriptif précédent retiré** : il portait « **garantit** une excellente tenue mécanique et une
      longue durée de service » (« garantit » est un mot banni ; le reste est invérifiable) et
      « robuste et économique » (jugements sans information).
- [x] **Sur mesure confirmé par PA** (16/07) — aucune source écrite ne le mentionne.
- [x] Alignements de gamme appliqués : « Surface média » → « **Surface filtrante** » ; **ISO 16890 avant
      EN 779** ; « Classement au feu » remonté auprès des efficacités ; média précisé « (polyester) ».
      Pages : 286,4 et 290,6 mm — les deux tiennent dans l'A4 **sans** `compact_fort` (fiche mono-classe).

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
**Contenu retravaillé v1.1 (26/07/2026) — voir `_arbitrages_pad` de netbag-s.json AVANT toute retouche.**
Sous-titre « Filtre à poches souples », descriptif PA 2 phrases (« densité progressive » assumée non sourcée →
NETFIBRE harmonisée v1.2), points clés PA (« Faible perte de charge » retiré : ΔP 82-192 Pa), specs ISO d'abord
+ humidité, tableau sans référence + colonne EN 779 + note corrigée (l'ancienne « 2 × frontale » était fausse,
facteur réel ≈ 10-17×), courbe en débit bornée 4 000 = fin des mesures (F7 seule cochée, 85 %, légende courte),
calculateur borné 4 000 + défaut F7·380 (cas le plus contraignant). **Boutique : code 17 en mode calcul.**
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
- [ ] **Longueur 300 / 600 mm** (livret_2023) vs **380/550/650** (fiches 2018) : nomenclature à clarifier —
      et depuis le branchement du code 17 (26/07), s'ajoutent les **360/530/600 mm tarifés** sans courbe ni
      mention fiche (cf. § calculateur). Le 360 n'est proposé nulle part sur le site (déc. PA).
- [ ] **Dimensions 287×592** : cadre standard mais **surface média non fournie** (≈ 0,485 × valeur 592×592) → à mesurer.
- [ ] **Humidité relative max.** non spécifiée sur fiches 2018 (mise à 100 % par cohérence).
- [ ] **Nombre de poches** par cadre (selon longueur/classe) : non documenté.
- [ ] **Option « préfiltre intégré au cœur »** (livret_2023) : décider si commercialisée.
- [ ] **M6 / F7 / F8 (380 mm)** : terme `c` négatif (1ᵉʳ point bas-débit tassé) → léger pied de courbe < 0 (borné 0).
- [ ] **Photo** : `TITABAG/Titabag.jpg` détourée = placeholder → photo produit Netair.

### NETPAK S CILIA 🟡
Filtre compact miniplis (équiv. TITAPAK S PRISME A). **Contenu retravaillé v1.1 (23/07/2026) — voir
`_arbitrages_pad` de netpak-s-cilia.json AVANT toute retouche.** Multi-classes **M5→F9 × ép. 48/98**,
fiche **2 pages** depuis v1.1 (clés `dims_p1`, `sans_dp_table`, `calc_p2`, `courbe_cases`, `dims_pdc`).
Données ΔP **réelles** : M5/M6/F8/F9 = **TITAPAK S HPE PRISME A 2018** ; **F7 = TITAPAK S GR PRISME A** (média spécial, ePM1 50%).
Polynômes : `DONNEES_PDC` l.38-47.

- [ ] **🟠 F9 ép. 48 mm = F8 ép. 48 mm + 10 Pa EXACTEMENT** (33=23+10, 53=43+10, … sur les 7 points) → offset/copie suspecte dans l'Excel Titanair (en ép. 98, F8≠F9 proprement). **À trancher par une mesure R&D du F9 ép. 48.**
- [ ] **F8 ép. 98 mm — 7ᵉ point extrapolé** : 6 points mesurés (0,79→2,78 m/s) ; le point à 3,17 m/s (≈ 137 Pa) est calculé par le polynôme → à mesurer.
- [ ] **F7 (GREENTEX) — croisement ép. 48/ép. 98 à haute vitesse** : au-delà de ~2 m/s la courbe ép. 98 repasse **au-dessus** de l'ép. 48 (ep48 12·20·30·40·51·63·76 / ep98 10·19·29·40·52·67·86), contraire à l'attendu (plus épais = plus de surface = ΔP plus basse). Présent tel quel dans la fiche source GR PRISME A → à confirmer en R&D.
- [ ] **F7 (GREENTEX) ΔP < M5/M6** : média basse résistance → la courbe F7 passe sous M5/M6. Cohérent avec la techno GREENTEX mais à confirmer (mélange HPE/GR dans une même fiche).
- [x] **Surface média m²/m² — CORRIGÉE le 23/07/2026 (erreur détectée par PA)** : les « m² » des fiches
      2018 sont en réalité des **m²/m² de section** (preuve géométrique : 2×48 ÷ pitch 7,5 ≈ 12,8), pas des
      m² par cellule. L'affichage ≈33/68 créé le 22/06 (valeur ÷ 0,3505) était une **double division fausse**.
      Affiché depuis v1.1 : **12,55 / 25,65 m²/m²** = média F7 (déc. PA ; l'HPE des autres classes vaut
      11,68/23,87). La colonne Surface du tableau dimensions a été **supprimée** à la refonte (dims_pdc).
- [ ] **Cellulose pelliculée (-C)** : suffixe tranché par PA (23/07), proposée au configurateur **au même
      prix** que les autres cadres (cadre neutre) → **ligne tarifaire à créer dans l'Excel** quand les cadres
      seront structurés (cf. « CADRE = info TARIFAIRE »).
- [ ] **Étiquette ISO F7 au configurateur** : « ePM1 50 % (F7) » via la rustine `etiquettesIso` (la table ISO
      globale de l'Excel dit 55 %) → à porter dans l'Excel à la resynchro (comme BORA ; reste AZUR à trancher).
- [ ] **Photo** : TITAPAK PRISME A HD (© A. Périer) détourée sur blanc = placeholder → photo produit Netair.

### NETPAK S AZUR 🟡 — v1.1 « Validée PA » (passe de contenu 17/07/2026, arbitrages dans `_arbitrages_pad` du JSON)
Filtre à poches rigides polydièdre (équiv. TITAPAK SV-GD). Gamme affichée **M5 → F9** (déc. PA 17/07 —
aligné boutique/Excel), courbes tracées **F7/F8/F9** (moteur `series`), profondeur 292.
Données ΔP : caches Excel SV-GD 2018 (F7/F9) + FORMULE_PDC. Polynômes : `DONNEES_PDC` l.48-51.

- [ ] **🟠 F8 (ePM1 70 %) = arrondi(F9 × 0,95) sur les 7 points** → courbe **dérivée, non mesurée**.
      ⚠️ Réserve **ROUVERTE le 17/07** : le `_commentaire` affirmait « vraies mesures F8.xlsx » — FAUX
      (le fichier lit la colonne E d'un classeur partagé dont F9 lit la colonne D). Gardée sur décision
      PA (plausible), **à mesurer en R&D**.
- [ ] **M5 (ePM10 50 %)** : au catalogue ET sur la fiche (déc. PA) mais **sans aucune source produit**
      (absent de la doc SV-GD) ni courbe → à caractériser en R&D (courbe + efficacité).
- [ ] **M6 ePM2,5 50 %** : sourcée (livret DEHS 60-65 %) mais **aucune courbe 2018** → à mesurer.
- [ ] **Courbes affichées jusqu'à 4500 m³/h** (déc. PA) : mesures arrêtées à 4000 → **segment 4000-4500
      extrapolé** du polynôme, à valider en R&D si besoin de certification.
- [ ] La fiche n'affiche **plus** la note « courbes données pour F7/F8/F9 » (retirée, déc. PA 17/07).
- [x] **Parois « Plastique »** : l'ABS (déclaration fabricant non sourcée ; fiches 2018 : polystyrène)
      a été **retiré le 18/07/2026** (déc. PA, passe BORA) → spec « Plastique » + point clé « Cadre en
      plastique », fiche **v1.2** au registre, alignée sur le configurateur (écart résorbé).
- [ ] **Surface média développée non communiquée** (n.c.) par Titanair → retirée du tableau ; à
      obtenir/mesurer si on veut la réafficher.
- [ ] **Largeurs 490/287** : F9 mesuré en 490 ; F7/F8 en 490/287 non mesurés (extrapolés du 592).
- [ ] **Photo** : SV-GD réelle (© A. Périer) légèrement nettoyée = placeholder → photo produit Netair.

### NETPAK S LUMEN 🟡
Compact polydièdre **rechargeable** (équiv. TITAPAK S QUARTZ, argument RSE). **Contenu retravaillé v1.1 (26/07/2026) — voir
`_arbitrages_pad` de netpak-s-lumen.json AVANT toute retouche.** Plage **M5 → F9** partout (déc. PA), tableau de stock **F7/F9
seuls** dans les 2 formats sourcés (592×592 · 287×592 — le 490×592 est écarté, cf. décision caduque § calculateur). Courbes
tracées F7/F8/F9 (ePM1, moteur `series`, F7 seule cochée à l'ouverture), profondeur 292.
Données ΔP **réelles** : courbes vectorielles PDF QUARTZ 2018 (FT 2019-041), **cohérentes F7<F8<F9** (pas de piège). Polynômes : `DONNEES_PDC` l.52-54.

- [ ] **Variantes fournisseurs 2024-25** : FORMULE_PDC contient des courbes MFILTER (2024) et FILTECH (2024-25) **différentes** des fiches 2018 → le média a peut-être changé. **Priorité fiches 2018** retenue ; à reconfirmer avec le média actuel.
- [ ] **% ePM1** : le livret annonce F7 60 % / F9 90 % ; les fiches 2018 disent **55 % / 80 %** (retenu) → à clarifier.
- [ ] **Surface média développée non communiquée** (n.c.) → à obtenir.
- [ ] **Largeur 287** : non mesurée indépendamment (extrapolée du 592).
- [ ] **Courbes > 4 000 m³/h extrapolées** (v1.1) : l'axe va au débit max annoncé 4 500 (doc 2015) mais les mesures 2018 s'arrêtent à 4 000 → tronçon 4 000-4 500 calculé par le polynôme (même approche qu'AZUR). À mesurer si usage haut débit.
- [x] ~~**🟠 Offre « recharges » inexistante**~~ → **BRANCHÉE le 02/08** sur le code 10 de l'Excel (repéré PA) : menu « Filtre complet / Recharge (cassettes seules) » sur la page produit, réf. `Recharge_NETPAK_S_LUMEN-…`, prix au centime — cf. le point détaillé § calculateur (restent : unité vendue à confirmer, mention sur la fiche → v1.2, réconciliation `-CAS`).
- [ ] **Photo** : Quartz.jpg (concept recharge) — **marque « Titanair » visible** sur la cassette → à remplacer en priorité par photo produit Netair.

### NETPAK S BORA 🟡
Filtre compact à brides 100 mm (équiv. TITAPAK S DSK). **Contenu retravaillé v1.1 (18/07/2026) — voir
`_arbitrages_pad` de netpak-s-bora.json AVANT toute retouche.** Plage **G4 → F9** affichée (déc. PA — le
doc 2013 ne cite que M5/F7) ; **courbe F7 seule, ePM1 50 %** (média spécial recyclé, PAS 55 %).
Données ΔP **réelles** lues sur l'image `GR DSK F7.png`, recoupées FORMULE_PDC. Polynôme : `DONNEES_PDC` l.55.

- [ ] **Variante HPE ePM1 55 %** : les specs pointées étaient HPE 55 % mais la seule courbe exploitable est GREENTEX 50 % → BORA fait en GREENTEX. Si on veut une fiche HPE 55 %, **courbe HPE à récupérer** (image/PDF non vectoriel).
- [ ] **Courbe lue à l'œil** sur image (±2-3 Pa) ; recoupée FORMULE_PDC (5,83·v²+13,44·v−2,24) → à confirmer par les points mesurés exacts.
- [ ] **Plage mesurée ≤ 3100 m³/h** (panneau 100 mm) ; débit nominal fixé à 3000. ΔP > 3100 non mesurée.
- [ ] **Données fabricant PA non sourcées Titanair** (consignées en arbitrages, 18/07) : **pas d'interplis 6 mm** (vs ~3,5 mm fibre de verre), **plage G4 → F9**, média « papier polypropylène » (doc 2013 : microfibre PP), parois « Plastique » (fiche 2020 : polystyrène).
- [ ] **Étiquette ISO F7 au configurateur** : la table ISO globale de l'Excel dit 55 % → BORA affiche « ePM1 50 % (F7) » via la **rustine `etiquettesIso`** (produits-gammes.ts + [ref].astro) ; à **porter dans l'Excel à la resynchro** (et trancher AZUR — 55 % affiché conforme à sa fiche — et CILIA à cette occasion, cf. mémoire « F7 GREENTEX = ePM1 50% »).
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
Filtre absolu multidièdre (équiv. TITAPAK V-GD), 592×592×292. **Contenu retravaillé v1.1 (02/08/2026) — voir
`_arbitrages_pad` de netcel-v-azur.json AVANT toute retouche.** **Mode HEPA** (ΔP finale = 2×init).
Courbes **E10 + H13** réelles (caches Excel) : `DONNEES_PDC` l.57-58 — **H13 CORRIGÉE le 02/08** (l'extraction
comprimait l'axe débit de 20 % : 400-2400 au lieu de 500-3000 — erreur détectée PA ; DONNEES_PDC réaligné le
jour même). Plage **E10 → H14** (déc. fabricant), nominaux 3000/2500/1500, boutique formats standard.

- [x] ~~**H13 extrapolé > 2400 m³/h**~~ → **SANS OBJET depuis la correction** : H13 mesuré jusqu'à **3 000**. Nouvelle réserve : la courbe affichée va à 3 500 → **tronçon H13 3 000-3 500 extrapolé** (écart à la règle « fin des mesures » assumé PA 02/08 ; l'E10 est mesuré jusqu'à 3 500 ; le curseur du calculateur reste borné à 3 000).
- [x] ~~**🟠 Curseur débit s'initialise à 3400**~~ → **CORRIGÉ dans le moteur série (02/08)** : le curseur suit désormais toujours `debit_nom` (no-op octet à octet pour les fiches à nominal 3400).
- [ ] **Surface média 24 m² RETIRÉE de la fiche (prudence PA 02/08)** : sourcée cache Titanair 2018 mais non vérifiée sur le média actuel → à mesurer si on veut la réafficher. Enjeu réel : Camfil affiche 29,6 m² sur ce format et tient 250 Pa à 3 000 — un média Netair mesuré meilleur permettrait un affichage plus favorable.
- [ ] **287×592** : sourcé par le TARIF seul (les fiches 2018 ne connaissent que 592 et 490) → à confirmer fabricant.
- [ ] **Humidité 100 %** (Camfil dit 100 %, AFPRO 90 %) et **« Étanchéité contrôlée »** : données fabricant non sourcées Titanair.
- [ ] **Photo = même polydièdre SV-GD que NETPAK S AZUR** → trouver/faire une photo distincte du V-GD HEPA.
- [ ] **Nom « AZUR »** partagé avec NETPAK S AZUR (familles différentes, OK par convention) → confirmer.

### NETCEL V LAM 🟡
Filtre à flux laminaire (équiv. TITAPAK V LAM), 610×610×68, **moteur mono-classe** (chemin legacy).
**Contenu retravaillé v1.1 (04/08/2026) — voir `_arbitrages_pad` de netcel-v-lam.json AVANT toute retouche.**
**Mode HEPA** (ΔP finale = 2×init via `dp_final_mode:"x2"` ; la clé `hepa` est réservée au moteur série).
Courbe **H14** réelle (cache Excel 2022) : 97,91·v²+263,287·v−12,4 (R²=0,9999), ΔP ≈125 Pa @600 m³/h.

- [ ] **🔴 Courbes ΔP absentes pour E11 / E12 / H13 / U15** — classes **vendues** depuis le 04/08 (déc. PA) mais non mesurées : la courbe, le calculateur et les ΔP du tableau restent en **H14**. Deux classes différentes affichent donc aujourd'hui la même perte de charge. À mesurer en R&D. ⚠️ **U15 = ULPA** (≥ 99,9995 % MPPS), pas HEPA — confirmer que Netair sait produire et tester cette classe.
- [ ] **Séparateur hot melt donné à 80 °C en continu** — valeur fabricant (fiche 2022) **non vérifiée** : c'est une colle thermofusible, 80 °C en service continu est haut. À confirmer R&D. C'est cette T° qui justifie l'écart avec NETCEL V AZUR (60 °C, cadre plastique).
- [ ] **T° de NETCEL V AZUR à rouvrir (déc. PA 04/08)** : même média microfibres de verre, 60 °C contre 80 °C ici. L'écart est assumé et justifié par le cadre (alu vs plastique), mais AZUR doit être réexaminée dans une passe dédiée — **avec bump de version**, la fiche étant figée en v1.1.
- [ ] **Humidité 100 % (sans condensation)** ajoutée le 04/08 — **non sourcée** chez Titanair (Camfil dit 100 %, AFPRO 90 %), comme sur toute la gamme.
- [ ] **ΔP 125 Pa mieux-disante que la concurrence** : Camfil Megalam ProSafe MD (610×610×**66**) annonce **600 m³/h / 140 Pa**. Notre débit nominal est donc corroboré, mais notre ΔP est **11 % plus basse** pour 2 mm de plus. Plausible, à confirmer avant d'en faire un argument commercial.
- [ ] **Surface média 5,83 m² retirée** (déc. PA 04/08) : ne décrivait que le 610×610 alors que la grille vend **17 formats** (jusqu'au 1220×1220, ~4× la surface). À réafficher **par format** seulement si la R&D mesure le média réel.
- [ ] **11 des 17 formats tarifés ne sont pas dans la fiche** : la page 1 ne peut en porter que ~6 (mesuré : 99 px de blanc = 4,6 lignes ; 17 formats = 459 px). Les 6 retenus couvrent la gamme (305×305 → 1220×1220) et la note renvoie aux autres. À revoir si un format s'avère très demandé.
- [ ] **Axe de la courbe en VITESSE — écart assumé** à la convention v1.1 « axe débit » (NETBAG, NETCEL V AZUR) : les 6 formats vont de 150 à 2400 m³/h (rapport 1 à 16), un axe en débit ne vaudrait que pour un format. À rouvrir seulement si la convention de gamme est retranchée.
- [ ] **Photo** : placeholder HEPA → photo produit Netair.
- [ ] **Capacité / colmatage** à confirmer (réserve d'origine, non levée).

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
