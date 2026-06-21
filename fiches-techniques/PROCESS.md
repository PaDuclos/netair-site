# PROCESS — Fabrication des fiches techniques Netair

> Méthode validée sur **NETPLAN** (juin 2026). À lire au début de chaque session
> avant de créer/modifier une fiche. Outils : `Generateur/` → livrables `Fiches_Netair/`.

## Principe

L'utilisateur ne manipule pas le générateur : il donne ses consignes, Claude Code
édite un `.json` et lance le script. Le **gabarit n'est jamais retouché à la main par
produit** ; on ne change que les **zones variables** via `produits/<slug>.json`.
Garantie : régénérer `netply.json` reproduit `gabarit_base.html` à l'octet près
(test d'identité — à relancer après toute modif du moteur ou du gabarit).

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

- **NETPLY** — référence (gabarit), polynôme ✅
- **NETPLAN** — mono-classe G4, polynôme, 0-2 m/s, nominal 1,5 m/s ✅
- **NETMETAL** — mono-classe G3 / Coarse 50% (équiv. TITAMETAL KMZ/A alu, ép. 48), polynôme
  7,34·v²+2,44·v+5,57 (fit 5 pts 0,79–2,38 m/s), Vmax 2,4 · nominal 1,5 m/s (1900 m³/h) ✅
  — doc 2015 disait G1-G2 → priorité fiche 2018 ; photo placeholder Titanair à remplacer ;
  ΔP au-delà de 2,38 m/s non mesurée.
- Suivants : NETFIL, NETFIBRE, NETBAG S, … (cf. Bibliothèque)
