# Handoff — Fiches techniques produits Netair

## Objectif

Ce paquet contient **le gabarit** d'une fiche technique produit Netair, finalisé et validé (produit **NETPLY**), ainsi que toutes les instructions pour **générer les autres fiches à l'identique** (même mise en page, mêmes couleurs, même calculateur énergétique interactif), en ne changeant que les **données propres à chaque produit**.

L'objectif n'est **pas** de redévelopper le design dans un autre framework : le gabarit est un fichier **HTML autonome** qui s'ouvre directement dans un navigateur et s'imprime en PDF A4 (2 pages). Pour chaque nouveau produit, **on duplique ce fichier et on remplace uniquement les zones « variables »** décrites plus bas. Tout le reste (structure, CSS inline, logique JS du calculateur et de la courbe) doit rester **strictement identique**.

> Si vous préférez industrialiser la production (10+ fiches), voir la section **« Option : génération par données »** en fin de document — extraire les variables dans un objet JS/JSON et générer le HTML par script, sans jamais toucher au gabarit visuel.

---

## Fichiers du paquet

```
design_handoff_fiche_technique/
├── README.md                     ← ce document
└── gabarit/
    ├── Fiche technique NETPLY.html   ← LE GABARIT (fiche NETPLY finalisée, 2 pages A4)
    └── assets/
        ├── netply-photo.jpg          ← photo produit détourée (fond blanc pur)
        └── netply-photo-orig.jpg     ← photo d'origine non retouchée (référence)
```

- **Polices** : chargées depuis Google Fonts (CDN) dans le `<head>` — `Instrument Sans` (UI) + `IBM Plex Mono` (références / chiffres). Aucune police locale à fournir.
- **Logo Netair** : intégré en **base64** directement dans le HTML (2 occurrences, en-tête page 1 et page 2). Rien à charger.
- **Photo produit** : référencée via `<img src="assets/<produit>-photo.jpg">`. Voir « Photo produit ».

---

## Fidélité

**Haute-fidélité (hifi).** Le gabarit est final : couleurs, typographie, espacements (en mm pour l'A4), tableau, calculateur et courbe sont définitifs. Toute nouvelle fiche doit être **pixel-identique** au gabarit, seules les valeurs produit changent.

---

## Structure du document

Chaque fiche = **2 pages A4** (`210mm × 297mm`), empilées verticalement dans `.cmp-col`. Conteneur `.a4` : fond blanc, padding `13mm 12mm`, pied de page bleu marine de `10mm`. Le CSS `@media print` produit **une page A4 par `.a4`** (marges 0).

### Page 1 — Présentation & specs
1. **En-tête** : logo Netair + nom produit (40px, navy) + sous-titre + 3 badges normes (à droite).
2. Filet navy `2px`.
3. **Photo produit** (gauche, 70mm) + **Description** & **Points clés** (droite, 2 colonnes).
4. **Caractéristiques techniques** : tableau 2 colonnes, 9 lignes (lignes paires fond `#F2F6FB`).
5. **Dimensions & références standard** : tableau 8 colonnes (en-tête navy), une ligne par dimension/classe + ligne « Sur mesure » + note de méthode.
6. **Pied de page** : `Netair SAS` · `Fiche n° FT-…` · `version — date — Page 1/2`.

### Page 2 — Performances & calculateur
1. **En-tête page 2** : nom produit (22px) + « Performances aérauliques & énergétique » + 3 badges (montrant la transition `G4 → M5`).
2. **Courbe vitesse / perte de charge** : SVG interactif (4 courbes ΔP ∝ vᵉˣᵖ), cases à cocher G4 / M5, points fixes au point de référence **3400 m³/h**, **survol** affichant `x,xx m/s - N m³/h` avec lignes pointillées horizontale/verticale.
3. **Calculateur énergétique** : panneau de réglages (gauche) + panneau de résultats (droite).

---

## ⚙️ Calculateur énergétique — comportement (NE PAS modifier la logique)

Réglages (état initial entre parenthèses) :
- **Débit d'air** : `3400 m³/h`
- **Durée de fonctionnement** : `24 h/jour` (slider 0 → 24, pas 0,5)
- **Nombre de jours** : `250 jours` (affiche le total d'heures/an = durée × jours en regard)
- **Rendement ventilateur** : `55 %`
- **Prix élec.** : `0,18 €/kWh`
- Sélecteurs **épaisseur** (48 / 98 mm) et **efficacité** (Coarse 65% (G4) / ePM10 50% (M5))

Sorties (cartes de résultats) : **Consommation (kWh)**, **Coût énergétique (€)** « sur N h », **Impact carbone (kg CO₂)**. Les 3 cartes ΔP (initiale / moyenne / finale) sont en fond clair (pas d'encadré coloré).

Méthode de calcul (constantes dans le `<script>` de page 2) :
```js
SCALE = { g4:{48:55, 98:38}, m5:{48:78, 98:54} }; // ΔP initiale (Pa) à 3400 m³/h sur 592×592
EXP   = { g4:1.65, m5:1.62 };                      // ΔP ∝ (v/Vnom)^exp
ADD   = { g4:50,  m5:100 };                        // EN 13053 : +50 Pa (Coarse) / +100 Pa (ePM)
Vmax  = 3.17;                                       // borne haute de la plage (m/s)
Aref  = 0.592*0.592;  Vnom = (3400/3600)/Aref;     // ≈ 2,69 m/s
// ΔP finale = min(ΔPinit + ADD, ΔPinit × 3)   ← on prend la PLUS PETITE des deux règles
// ΔP moyenne = (ΔPinit + ΔPfinale) / 2
// Puissance = (débit/3600) × ΔPmoy / (rendement/100)
// kWh = P/1000 × heures ; Coût = kWh × prix ; CO₂ = kWh × 0,052
```
Le facteur CO₂ utilisé est **0,052 kg/kWh** (`co2Num = kwhNum * 0.052`). *(NB : le client a évoqué 79 g/kWh ; conserver la valeur présente dans le gabarit sauf instruction contraire — c'est une constante facile à ajuster sur une seule ligne.)*

> ⚠️ **La courbe est volontairement découplée du calculateur** : régler le calculateur **ne doit pas** déplacer les points de la courbe. Les points restent figés au point de référence 3400 m³/h. Ne pas réintroduire de lien.

---

## 🔁 Zones VARIABLES (à changer pour chaque produit)

Tout le reste est **fixe**. Pour une nouvelle fiche, dupliquer le gabarit et ne remplacer que :

| # | Zone | Où | Exemple NETPLY |
|---|------|-----|----------------|
| 1 | **Nom produit** | en-tête P1 (40px) + en-tête P2 (22px) + `<title>` + thumbnail SVG | `NETPLY` |
| 2 | **Sous-titre** | sous le nom, P1 | `Filtre plissé — Préfiltre synthétique` |
| 3 | **Badges normes** (×3) | en-tête P1 et P2 | `ISO 16890 : Coarse 65% / ePM10 50%`, `EN 779 : G4 / M5`, `EN 13053` |
| 4 | **Photo produit** | `assets/<produit>-photo.jpg` + `alt` | `assets/netply-photo.jpg` |
| 5 | **Description** | paragraphe P1 | texte produit |
| 6 | **Points clés** (×4) | grille 2×2 P1 | Faible perte de charge, Longue durée de vie, … |
| 7 | **Caractéristiques techniques** | tableau 9 lignes P1 | Média, Structure, Cadre, Joint, Feu, Surface média, Température, Humidité, Incinérable |
| 8 | **Dimensions & références** | tableau P1 | voir ci-dessous |
| 9 | **Pied de page** | `Fiche n°`, version, date, sur P1 et P2 | `FT-NETPLY-001`, `v1.0 — 20/06/2026` |
| 10 | **Constantes calcul** | `SCALE`, `EXP`, `ADD`, badges courbe, libellés classes | valeurs aérauliques mesurées du produit |

### Tableau « Dimensions & références » — règles de calcul
Colonnes : `L (mm)` · `H (mm)` · `P (mm)` · `S. filtrante (m²)` · `Débit (m³/h)` · `ΔP (Pa)` · `Efficacité ISO 16890` · `Référence complète`.
- **Ordre** : d'abord toutes les lignes **G4 (Coarse 65%)**, puis toutes les **M5 (ePM10 50%)**.
- **Surface filtrante** = `2 × (L × H)` (surface frontale × 2).
- **Débit** = débit nominal proportionnel à la surface frontale (réf. `592×592 → 3400 m³/h` ; ex. `287×592 → 1700`).
- **ΔP (Pa)** = **valeur fixe par classe** (réf. à 3400 m³/h) : `G4 = 55`, `M5 = 78`.
- **Efficacité** : `Coarse 65% (G4)` ou `ePM10 50% (M5)`.
- **Référence complète** : `NETPLY-<efficacité>-<classe>-<L>x<H>x<P>` (police IBM Plex Mono), ex. `NETPLY-Coarse 65%-G4-592x592x48`.
- Dernière ligne : **« Sur mesure » / « sur demande — délai à confirmer »** (fond `#E6F5F7`).
- Note de méthode sous le tableau (texte gris `#8b97a6`).

---

## 🎨 Tokens de design (identiques sur toutes les fiches)

**Couleurs**
| Rôle | Hex |
|------|-----|
| Bleu marine primaire (titres, en-têtes tableau, filets, pied) | `#0F3261` |
| Teal accent (filets courts, puces, courbe M5) | `#0897A5` |
| Courbe navy 48 mm / 98 mm | `#0F3261` / `#6B8FC2` |
| Courbe teal 48 mm / 98 mm | `#0897A5` / `#7FCBD3` |
| Fond de page (hors A4) | `#e7e5df` |
| Carte A4 | `#ffffff` |
| Texte principal / secondaire / tertiaire | `#1f2a38` / `#3a4654` / `#5A6573` |
| Texte ténu (notes) | `#8b97a6` |
| Rayure tableau | `#F2F6FB` |
| Teinte teal (ligne sur mesure) | `#E6F5F7` |
| Bordures claires | `#E4EBF3` / `#C9D7E8` / `#E1E7EF` |

**Typographie** — `Instrument Sans` (400/500/600/700) pour tout l'UI ; `IBM Plex Mono` (400/500) pour les références produit et les valeurs numériques du calculateur.
- Nom produit P1 `40px/700`, P2 `22px/700` ; titres de section `11px/700`, `letter-spacing 1.2px`, `text-transform:uppercase` ; corps `12,5–13px`, `line-height 1.55` ; tableaux `10–12,5px`.

**Mise en page** — A4 `210×297mm`, padding `13mm 12mm`, pied `10mm`. Filets de section : navy `2px` (séparateur en-tête) / `1px` (souligné de titre). Rayons : cartes `8px`, badges `20px` (pleins). Ombre A4 `0 4px 24px rgba(15,50,97,.14)` (retirée à l'impression).

---

## Photo produit — préparation

La photo doit être **détourée sur fond blanc pur** (le produit semble incrusté dans la page), en **préservant le cadre et le média** sans dégrader la netteté. Méthode utilisée pour NETPLY (à reproduire) :
1. Fond studio quasi-blanc (≈ 246–253) → bascule des pixels clairs vers `#FFFFFF` par **croissance de région depuis les bords** (le contour sombre du cadre sert de barrière).
2. Seuil plancher calé **sous** la luminance du cadre métallique (≈ 244) pour ne jamais mordre sur le métal.
3. Redimension max **2400 px** de large, export JPEG qualité ~0,93 (300 dpi pour l'emplacement 70 mm).

L'`<img>` a déjà `src="assets/<produit>-photo.jpg"`. Un bouton « cliquer pour importer » (input file) existe en secours mais **n'écrit plus** dans le localStorage : la source de vérité est le fichier dans `assets/`.

---

## Impression / export PDF

Ouvrir le HTML dans un navigateur → `Cmd/Ctrl + P` → format **A4**, marges **aucune**, cocher « graphiques d'arrière-plan ». Le CSS `@media print` gère le saut de page (1 page A4 par bloc `.a4`).

---

## Option : génération par données (pour produire beaucoup de fiches)

Pour industrialiser, extraire les zones variables (#1–#10) dans un objet par produit, p. ex. :
```js
const PRODUIT = {
  nom: "NETPLY",
  soustitre: "Filtre plissé — Préfiltre synthétique",
  badges: ["ISO 16890 : Coarse 65% / ePM10 50%", "EN 779 : G4 / M5", "EN 13053"],
  photo: "assets/netply-photo.jpg",
  description: "…",
  pointsCles: ["Faible perte de charge", "Longue durée de vie", "Cadre carton ou métal", "Sans fibre de verre"],
  specs: [["Média filtrant","Synthétique non-tissé"], /* … */],
  dimensions: [ { L:592,H:592,P:48, eff:"Coarse 65%", classe:"G4", dp:55 }, /* … */ ],
  calc: { SCALE:{g4:{48:55,98:38}, m5:{48:78,98:54}}, EXP:{g4:1.65,m5:1.62}, ADD:{g4:50,m5:100} },
  fiche: { num:"FT-NETPLY-001", version:"v1.0", date:"20/06/2026" }
};
```
puis générer le HTML à partir du gabarit (templating) **sans changer une seule règle de style ni la logique du calculateur**. Les débits du tableau et la surface filtrante se calculent à partir des dimensions (cf. règles plus haut).

---

## À vérifier sur chaque fiche générée
- [ ] Les 2 pages tiennent chacune sur **une A4** sans débordement.
- [ ] Tableau dimensions : G4 puis M5, débits proportionnels, ΔP fixe par classe, réf. en Mono.
- [ ] Calculateur : valeurs initiales correctes, ΔP finale = `min(+ADD, ×3)`, courbe **non liée** aux réglages.
- [ ] Survol de la courbe : `m/s - m³/h` lisible, pointillés H/V.
- [ ] Photo détourée sur **blanc pur**, cadre & média intacts.
- [ ] Pied de page : n° de fiche, version, date, pagination cohérents.
