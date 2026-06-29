# Spécification — Bloc B1 : Moteur de prix

> **Version 1.0 — 29/06/2026** · Statut : **spécification, à relire**
> Cahier des charges : [`CAHIER_DES_CHARGES.md`](CAHIER_DES_CHARGES.md) (§4 brique 1, §7 bloc B1) · Suivi : [`SUIVI.md`](SUIVI.md)
> Source des tables (données) : `BLOC1_Gamme_Produits/Grille_Couts_Internes/Calculateur_Netair.xlsx`
> Source de la chaîne de calcul (formules) : `DEVIS AUTO/reference/Calculateur_devis_auto.xltm`, onglet
> **« Devis interne »** — coût `PRU HT` (col. DB) → `Ratio prix tarif` (DD) → tarif `PTU HT` (DE) = `PT : PVU HT` mode tarif (col. **DR**)
> Référence géométrique du coût : `DEVIS AUTO/src/cost_calculator.py` (**moteur distinct** — voir §9)

---

## 0. Décisions de cadrage (validées le 29/06/2026)

| # | Décision | Choix |
|---|---|---|
| C1 | Technologie du moteur | **TypeScript** — module unique utilisable dans le navigateur (prix instantané) **et** côté serveur (recalcul de sécurité avant paiement) |
| C2 | Définition du prix boutique | **Prix HT = coût × « Ratio prix tarif »** (= col. DR du calculateur en **mode tarif pur** = `PTU HT`). Coût = `PRU HT` (assemblage géométrique). Marges/catégories/remises manuelles = canal devis, **exclues**. Remises par famille = **Bloc B4**. *(confirmé 29/06)* |
| C3 | Synchronisation avec l'Excel | **Export Excel → fichier de données versionné (JSON)** + **test de conformité** permanent « entrées Excel = sorties moteur » |
| C4 | Skills qualité | **3 skills** créés au démarrage : `netair-site-reviewer`, `netair-pricing-validator`, `netair-pricing-qa` |
| C5 | Mise à jour des tarifs | **Deux leviers** : un **% de revalorisation générale** (une seule case dans l'Excel) **+** la modification de **cases ciblées**. La publication vers le site est un **geste manuel contrôlé** (une commande), pas un direct automatique (voir §11) |

---

## 1. Rôle du moteur (en une phrase)

> À partir d'une **gamme**, de **dimensions** (L × H × P), d'une **classe d'efficacité**, d'une **quantité** et
> d'un **département de livraison**, le moteur renvoie : **prix unitaire HT, prix total HT, frais de port,
> poids, et durée de validité** — exactement selon la logique de l'Excel.

C'est le **cœur** du site marchand (brique 1). Tout le reste (configurateur, panier, paiement) s'appuie dessus.

---

## 2. Ce que contient l'Excel (la matière première)

L'Excel **n'est pas** un calculateur à bouton : c'est une **bibliothèque de 12 tables**. Le « calcul » est une
**méthode** qui pioche dans ces tables. Rôle de chaque onglet :

| Onglet | Rôle | Utilisé par le moteur |
|---|---|---|
| `Prix_L_et_l` | Prix par **case de dimensions** (petite × grande), par épaisseur, par palier de quantité, par classe | ✅ cœur |
| `Prix_Surface` | Prix par **tranche de surface** (dm²), quand la dimension exacte n'est pas dans la grille | ✅ cœur |
| `Prix_Surface_HF` | Prix **« hors format »** : supplément au dm² au-delà de 50 dm² | ✅ cœur |
| `Prix_Pièce` | Prix **fixe à la pièce** (main d'œuvre, emballage, grille) — pour les compacts CILIA | ✅ cœur |
| `Poids_filtres` | **Poids** du média en kg/m² par gamme/épaisseur | ✅ port |
| `Tableau_Tarifs_Expédition` | **Frais de port** par **département** (00 → 95) | ✅ port |
| `Tableau_franco` | **Seuil de franco de port** = **750 €** (au-delà, port offert) | ✅ port |
| `Tableau_Gammes` | Table maîtresse : famille, code, **ratio prix tarif**, **remises catégorie 1-5**, frais de livraison | ✅ cœur (ratio) + B4 (remises) |
| `Paramètres unitaires` | Constantes : renforts, surcoûts épaisseur, MO, emballage, ratio PRISME, **franco 750 €**, **validité 30 j** | ✅ cœur |
| `Durée_validité` | **Durée de validité** de l'offre = **30 jours** | ✅ sortie |
| `ISO_16890` | Correspondance EN 779 ↔ ISO 16890 (G4 ↔ Coarse 65 %, etc.) | ℹ️ affichage |
| `Infos_Netair` | Métadonnées + **table « Méthode calcul » par code gamme** | ℹ️ référence |

### Mécanismes transversaux
- **Paliers de quantité** : le prix unitaire baisse par tranche (typiquement `0-5 / 6-19 / 20-499 / 500+` ;
  certaines tables utilisent `0-5 / 6-20 / 21-500 / 501+`). **À répliquer table par table, pas en dur.**
- **Franco de port** : si le total HT ≥ **750 €** → frais de port = **0 €**.
- **Validité** : prix valable **30 jours** (information affichée).

---

## 3. La méthode de calcul, par famille

La colonne « Méthode calcul » de l'onglet `Infos_Netair` donne la règle exacte de chaque code gamme.
Le moteur implémente **6 méthodes** (un « dispatcher » choisit selon le code gamme) :

### Méthode A — Plissés / plans avec renfort (codes 1, 101, 3, 103 → NETPLY, NETPLAN)
```
coût = renfort(selon taille) + surcoût_épaisseur + prix_base
prix_base = case Prix_L_et_l (si dimension dans la grille)
            sinon prix Prix_Surface (par tranche de surface)
            + Prix_Surface_HF si surface > 50 dm² (supplément au dm²)
```
- **Renfort** (NETPLY) : petite dim > 850 → renfort intérieur (3,84 €) ; sinon grande > 800 **ou** surface > 50 → renfort extérieur (1,51 €) ; sinon 0.
  *(NETPLAN : renfort ext = 2,32 € / int = 5,90 €.)*
- **Surcoût épaisseur** : +1,55 € pour épaisseurs non standard (45 / 95 mm).
- NETPLAN : **pas** de surcoût épaisseur.

### Méthode B — Périmètre / mètre linéaire (codes 2, 102 → NETFIL)
```
coût = prix_au_mètre_linéaire × périmètre
périmètre (m) = (L + H) × 2 / 1000
```

### Méthode C — Surface au dm² (code 4 → NETFIBRE)
```
coût = prix_au_dm² × surface
surface (dm²) = L × H / 10000
```

### Méthode D — Cadre + média + pièce (codes 7, 8 → NETPAK / NETCARB CILIA)
```
coût = prix_cadre + prix_média + prix_pièce
prix_cadre = prix_au_mL (Prix_L_et_l)  × périmètre
prix_média = prix_au_dm² (Prix_Surface) × surface
prix_pièce = MO + emballage (± grille) (Prix_Pièce)
```
Code 7 : classes M5/M6/F7/F8/F9 · Code 8 : F7 uniquement.

### Méthode E — Prix pièce simple (code 5 → NETFIBRE ROULEAU)
```
coût = prix pièce (lecture directe, G4)
```

### Méthode F — Lecture L×l directe (codes 9, 10, 11, 12, 13, 14, 15, 17, 130, 150)
```
coût = case Prix_L_et_l (NETBAG, NETCEL, NETPAK LUMEN/LAM, recharges…)
```

> **Du coût au prix de vente (décision C2 — confirmé le 29/06/2026)** :
> `prix_unitaire_HT = coût × ratio_prix_tarif[gamme]` (ex. NETPLY ratio = 3,333).
>
> Confirmé en traçant le **calculateur DEVIS AUTO**, onglet **« Devis interne »** (table `Tableau_calculateur`) :
> - **`PRU HT`** (col. DB) = le **coût de revient** unitaire = `ROUND(PU{code gamme} ; 2)`, c.-à-d. l'assemblage
>   géométrique par gamme (renfort + base + cadre + média + pièce). **C'est exactement le « coût » du moteur.**
> - **`Ratio prix tarif`** (col. DD) = lu dans `Tableau_Gammes`.
> - **`PTU HT`** (col. DE) = `PRU × Ratio` = le **prix tarif catalogue** → **c'est notre prix boutique**.
> - **`PT : PVU HT`** (col. **DR**) = le prix de vente final affiché ; en **mode tarif pur** (sans marge manuelle,
>   ni catégorie client, ni remise manuelle) **DR = PTU = PRU × Ratio**.
>
> La boutique prend **DR en mode tarif pur**. Les branches *marge manuelle / catégorie client / remise manuelle*
> du calculateur sont des outils de **négociation** → **canal devis**, **hors** boutique (cf. cahier §2bis, D9).
> Aucune valeur n'est inventée ; le ratio et l'assemblage du coût sont **verrouillés par le test de conformité** (§7).

### Exemple illustratif (à verrouiller par le test)
NETPLY · 287 × 592 × 48 · classe **G4** · quantité **10** · livraison dép. 35 :
1. surface = 287 × 592 / 10000 = **16,99 dm²** → pas de renfort (≤ 50 dm² et < 800), pas de surcoût (48 mm)
2. case `Prix_L_et_l` (285-289 × 590-594, palier 6-19, G4) = **3,44 € (coût)**
3. prix unitaire HT = 3,44 × 3,333 ≈ **11,47 €**
4. total HT = 11,47 × 10 = **114,70 €** → < 750 € → port dû
5. poids = 4,5 kg/m² × 16,99 dm² /100 × 10 ≈ … → port dép. 35 = **75 €**
6. **Total = 114,70 € HT + 75 € port** · valable **30 jours**

*(Chiffres à confirmer par le test ; ils illustrent le pipeline, pas une grille définitive.)*

---

## 4. Contrat du moteur (entrées / sorties)

### Entrée
```ts
interface DemandePrix {
  codeGamme: string;        // ex. "1" (NETPLY) — tel quel dans tables.json ; codes NON figés (cf. note ci-dessous)
  largeur_mm: number;       // L
  hauteur_mm: number;       // H
  profondeur_mm: number;    // P (épaisseur)
  classe: string;           // "G4", "F7"… (EN 779)
  quantite: number;         // ≥ 1
  departement?: string;     // "35" — pour le port ; optionnel (prix nu sans port si absent)
}
```

> **Codes gamme NON figés (29/06/2026)** : `codeGamme` est une **chaîne** (ex. `"1"`, `"101"`, `"130"`), exactement
> comme dans `tables.json`. Le calculateur n'est pas encore retravaillé : des filtres seront ajoutés/retirés et **les
> codes changeront**. Conséquence pour le moteur : **aucun code n'est écrit en dur** — la méthode de calcul par code
> est lue dans les données ; après chaque retravail de l'Excel, on régénère `tables.json` et on rejoue les tests.
> *(Tracé aussi dans `PLAN.md`, BLOC 1.)*

### Sortie
```ts
interface ResultatPrix {
  statut: "ok" | "hors_fabrication" | "classe_indisponible" | "gamme_inconnue" | "sur_devis" | "quantite_insuffisante";
  prixUnitaireHT?: number;     // arrondi 2 décimales
  prixTotalHT?: number;        // unitaire × quantité
  fraisPortHT?: number;        // selon département + franco
  francoApplique?: boolean;    // true si total ≥ 750 € → port offert
  poidsTotalKg?: number;
  paletteQuantite?: string;    // tranche/palier de prix appliqué, ex. "6-19"
  quantiteMini?: number;       // plancher de commande de la famille (si statut "quantite_insuffisante")
  dureeValiditeJours: number;  // 30
  detail?: DetailCalcul;       // traçabilité : renfort, base, ratio, table source…
  message?: string;            // explication si statut ≠ "ok"
}
```

> **Règle d'or (héritée des skills DEVIS AUTO)** : **jamais de prix inventé**. Si une dimension/classe
> n'a pas de prix dans les tables → statut explicite (`hors_fabrication` / `classe_indisponible`),
> **jamais** un prix approximatif ou 0 €.

**Les statuts (décidés le 29/06/2026) :**
- `ok` — prix calculé normalement (achat possible).
- `hors_fabrication` — dimension hors des bornes fabricables (cf. §10, bornes à fournir).
- `classe_indisponible` — efficacité non fabriquée pour ce produit/format → **l'efficacité n'est pas proposée**
  dans le menu ; si l'indisponibilité dépend de la dimension saisie, message « non disponible dans ce format ».
- `gamme_inconnue` — code gamme non reconnu.
- `sur_devis` — gamme **« hors calculateur »** (`Tableau_Gammes` famille 4 : NETMETAL, NETPAK S BORA,
  NETCARB AZUR, NETPAK S DUO…) : **pas de prix instantané ni d'achat**, seul le parcours **demande de devis**
  est actif. La page et le configurateur restent **identiques** (mêmes champs) → réactivation simple si une
  méthode de prix est ajoutée plus tard.
- `quantite_insuffisante` — quantité saisie **sous le minimum de commande de la famille** : **achat bloqué**,
  message « quantité minimale : X » (valeur dans `quantiteMini`). À distinguer des **paliers de prix** (qui, eux,
  font seulement varier le prix unitaire). Minima à fournir (cf. §10, « cadre »).

---

## 5. Architecture des fichiers (proposée)

```
site/src/lib/pricing/
├── data/
│   ├── tables.json            # export versionné de l'Excel (généré, jamais édité à la main)
│   └── tables.meta.json       # version Excel, date d'export, empreinte
├── engine.ts                  # dispatcher + les 6 méthodes A→F
├── lookups.ts                 # recherche dans les tables (L×l, surface, HF, pièce, palier)
├── shipping.ts                # frais de port (département + franco 750 €)
├── weight.ts                  # poids depuis Poids_filtres
├── types.ts                   # DemandePrix, ResultatPrix, DetailCalcul
└── index.ts                   # point d'entrée public : calculerPrix(demande)

site/scripts/
└── export-excel.mjs           # lit Calculateur_Netair.xlsx → produit data/tables.json

site/tests/pricing/
├── golden.test.ts             # « entrées Excel = sorties moteur » (vecteurs dorés)
├── golden-vectors.json        # cas générés depuis l'Excel (gamme × dim × classe × qté)
└── edge.test.ts               # cas limites (hors format, classe absente, qté 1/franco…)
```

**Principe** : `tables.json` est la **seule source de chiffres** du moteur ; il est **généré** depuis l'Excel
par `export-excel.mjs`. Le moteur ne lit jamais l'Excel directement (robustesse, rapidité, testabilité).

---

## 6. Plan d'implémentation (découpage en tâches)

| # | Tâche | Livrable | Validé par |
|---|---|---|---|
| T1 | ✅ **FAIT** — Export Excel → JSON | `site/scripts/export_excel.py` (Python) + `tables.json` + `tables.meta.json` | vérif humaine + `netair-site-reviewer` |
| T2 | ✅ **FAIT** — Types & contrat | `types.ts` | `netair-site-reviewer` ⚠️ validé avec réserves (spec alignée : `codeGamme` string) |
| T3 | ✅ **FAIT** — Lookups (L×l, surface, HF, pièce, paliers) | `lookups.ts` + `tests/pricing/lookups.test.ts` (20 tests, Vitest) | `netair-site-reviewer` 🔧→✅ (réserve ÉLEVÉE `ep: number\|null` corrigée) |
| T4 | **Méthodes A→F + dispatcher** | `engine.ts` | reviewer |
| T5 | **Port & franco** | `shipping.ts` | reviewer + validator |
| T6 | **Poids** | `weight.ts` | reviewer |
| T7 | **Point d'entrée** `calculerPrix()` | `index.ts` | reviewer |
| T8 | **Vecteurs dorés** (extraits de l'Excel) | `golden-vectors.json` | validator métier |
| T9 | **Tests de conformité + cas limites** | `golden.test.ts`, `edge.test.ts` | `netair-pricing-qa` |
| T10 | **Revue finale + verdict** | rapport reviewer + validator + qa | les 3 skills |

> Workflow : **Spec → Code → Review**. ⚠️ Décision 29/06 : le **code se fait en Opus** (et non Haiku),
> choix de Pierre-Alain pour la sécurité maximale sur un sujet critique (déroge au `CLAUDE.md` du site).
> Chaque tâche de code passe par le `netair-site-reviewer` avant d'être considérée terminée.

### Quand déclencher les skills (cadence qualité — verrouillée le 29/06/2026)

| Skill | Déclencheur | Vérifie |
|---|---|---|
| `netair-site-reviewer` | **après chaque tâche de code** (T1 ✅ … T7) + tout code du site | le **code** (bugs, robustesse, rien en dur, conformité spec) |
| `netair-pricing-validator` | dès que le moteur **sort des prix** (**à partir de T4**, et au branchement réel en B2) | la **plausibilité métier** d'un prix (pas de 0 €, bon palier, port cohérent) |
| `netair-pricing-qa` | **T8/T9**, **avant toute mise en ligne**, et **à chaque republication** après MAJ tarif (§11) | le verdict **« Excel = moteur au centime »**, preuves à l'appui |

Règle courte : *j'écris du code → reviewer · le moteur sort un prix → validator · avant de publier → qa*.
**Pas de skill « auditeur »** dans la panoplie Netair (jugé redondant avec `qa` + `reviewer`).

---

## 7. Tests « entrées Excel = sorties moteur » (le filet de sécurité)

C'est le garde-fou n°1 contre une erreur de prix (risque 🔴 du cahier des charges).

1. **Génération des vecteurs dorés** : un script parcourt l'Excel et produit, pour un large échantillon
   (chaque gamme × plusieurs dimensions × chaque classe valide × chaque palier de quantité), le triplet
   `entrée → coût attendu → prix tarif attendu`. Ces valeurs **viennent de l'Excel**, pas du moteur.
   **Référence de comparaison** = onglet « Devis interne » du calculateur : `PRU HT` (col. DB) pour le coût,
   et `PTU HT` (col. DE) = `PT : PVU HT` en mode tarif (col. DR) pour le prix catalogue.
2. **Comparaison** : `golden.test.ts` rejoue chaque vecteur dans le moteur et compare au centime
   (tolérance d'arrondi définie, ex. ±0,01 €).
3. **Cas limites** (`edge.test.ts`) : dimension hors grille, classe non assurée par le fournisseur
   (« Caractéristiques non assurées… » → `classe_indisponible`), quantité 1, franchissement du franco 750 €,
   département inconnu, surface > 50 dm² (hors format).
4. **Garde anti-divergence** : si `tables.meta.json` (version/empreinte de l'Excel) change, le test
   **échoue tant que les vecteurs dorés n'ont pas été régénérés** → impossible d'oublier une MAJ tarif.

> Modèle mental : c'est la même discipline que le **test d'identité NETPLY** du générateur de fiches
> (régénérer reproduit le gabarit à l'octet près). Ici : **rejouer l'Excel reproduit le prix au centime près.**

---

## 8. Sécurité du prix (rappel architecture)

- Le prix affiché dans le navigateur est **pratique** (instantané) mais **non fiable seul** (le navigateur
  est manipulable). Avant tout paiement, le **même moteur** est rejoué **côté serveur** (fonction serverless)
  et **fait foi**. Même code TypeScript des deux côtés → zéro divergence (bénéfice de la décision C1).
- Le moteur **n'expose que le tarif catalogue**. Les remises négociées **n'existent pas** dans ce moteur
  (canal devis, cf. §2bis du cahier). Les remises par **famille** (comptes validés) seront une **couche
  séparée en B4**, appliquée après le tarif catalogue.

---

## 9. Distinction avec DEVIS AUTO (à ne jamais confondre)

| | `cost_calculator.py` (DEVIS AUTO) | Moteur de prix (ce projet) |
|---|---|---|
| Calcule | **coût de revient** (PRU) | **tarif de vente** (catalogue) |
| Langage | Python | TypeScript |
| Tourne | dans le pipeline email Titanair | dans le site Netair (navigateur + serveur) |
| Logique géométrique | **partagée** (surface, périmètre, ×2 plissé, paliers) | **partagée** (même géométrie) |
| Chiffre produit | un coût | un prix de vente = coût × ratio |

→ `cost_calculator.py` est une **excellente référence** pour porter la géométrie, mais ce sont **deux moteurs
distincts** (deux nombres, deux bases de code). **Source unique = l'Excel** ; **tests croisés** pour éviter
toute divergence de la logique géométrique commune (risque 🟡 du cahier).

---

## 10. Points à confirmer (avant ou pendant l'implémentation)

- [x] **Ratio coût → tarif** — ✅ **RÉSOLU (29/06/2026)**. Prix boutique = **coût × ratio prix tarif**, où le
      « coût » = `PRU HT` (col. DB de l'onglet « Devis interne » : l'assemblage géométrique par gamme, renforts +
      MO inclus). Le prix catalogue = `PTU HT` (col. DE) = `PT : PVU HT` en **mode tarif pur** (col. DR), **sans**
      marge manuelle / catégorie client / remise manuelle (celles-ci = canal devis). Détail : §3.
- [ ] **Le « cadre » par famille** (pour les statuts `hors_fabrication` et `quantite_insuffisante`) —
      ⏳ **EN ATTENTE** : Pierre-Alain fournira **(a)** les **dimensions mini/maxi** fabricables **et (b)** la
      **quantité minimale de commande**, par famille. Comportement décidé (29/06) : sous le mini de quantité →
      **achat bloqué + message « quantité minimale : X »** (≠ paliers de prix). Ne bloque pas le reste du codage.
- [x] **Gammes « hors calculateur »** — ✅ **RÉSOLU (29/06/2026)**. Statut **`sur_devis`** : pas d'achat ni de prix
      instantané, seul le parcours **demande de devis** reste actif ; page + configurateur **identiques** (cf. §4).
- [x] **Classes « non assurées par le fournisseur »** — ✅ **RÉSOLU (29/06/2026)**. On **ne propose pas** l'efficacité
      infabricable (absente du menu) ; si l'indisponibilité dépend de la dimension → `classe_indisponible` + message
      « non disponible dans ce format ». Jamais de prix sur une combinaison non fabriquée.
- [x] **Arrondi** — ✅ **RÉSOLU (29/06/2026)**. **Arrondi classique à 2 décimales** sur le prix final (HT).
- [ ] **Revalorisation** : emplacement de la case « % de revalorisation générale » dans l'Excel et son ordre
      d'application (avant ou après le ratio prix tarif) — voir §11.

---

## 11. Mise à jour des tarifs (hausses de prix) — décision C5

### Le principe : pas de « direct » automatique, une publication contrôlée
Le site ne lit **pas** l'Excel en direct. Il lit une **copie figée** (`tables.json`) générée depuis l'Excel.
Une modification de tarif dans l'Excel n'apparaît donc sur le site **qu'après une étape de publication**.

```
Excel modifié  →  [commande de publication]  →  tables.json régénéré
                                              →  tests de conformité rejoués
                                              →  mise en ligne
```

**Pourquoi ce n'est pas live (3 garde-fous)** :
1. **Sécurité** — une faute de frappe dans l'Excel ne part pas instantanément chez les clients.
2. **Filet de test** — à chaque publication, le contrôle « Excel = site » se relance et bloque toute incohérence.
3. **Rapidité** — lire une petite copie est instantané ; lire un gros Excel à chaque visite serait lent et fragile.

### Les deux leviers de hausse (décision C5 : « les deux »)

| Levier | Usage | Où dans l'Excel |
|---|---|---|
| **% de revalorisation générale** | Hausse globale (ex. +3 % annuel sur tout le catalogue) — **une seule case à changer** | onglet `Paramètres unitaires` : nouvelle ligne **« Revalorisation générale »** (ex. `1,03`) |
| **Cases ciblées** | Hausse fine sur une gamme / un fournisseur précis | les valeurs des tables `Prix_*` et/ou le `Ratio prix tarif` de `Tableau_Gammes` |

Formule de prix mise à jour :
```
prix unitaire HT = coût × ratio_prix_tarif × revalorisation_générale
```
*(L'ordre exact d'application de la revalorisation — sur le coût ou sur le tarif — est à figer dans le test de conformité, cf. §10.)*

### La publication = une commande simple (décision C5)
Un raccourci unique (dans l'esprit des fichiers `.command` existants du dépôt, ex. `Apercu_site.command`),
qui en un geste :
1. relit l'Excel et régénère `tables.json` (+ `tables.meta.json`) ;
2. **rejoue les tests de conformité** (refus si un écart apparaît) ;
3. prépare la mise en ligne.

> Pierre-Alain garde **le contrôle du moment** où les nouveaux prix deviennent publics. Tant que la commande
> n'est pas lancée, le site continue d'afficher les anciens prix — aucune surprise.
