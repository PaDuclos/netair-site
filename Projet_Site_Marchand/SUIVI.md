# Suivi — Projet Site marchand Netair

> Tableau de bord vivant du projet. Mis à jour à chaque avancée.
> Cahier des charges : [`CAHIER_DES_CHARGES.md`](CAHIER_DES_CHARGES.md)

**État global : 🟢 Maquette validée → Bloc B1 (moteur de prix) spécifié** — cahier des charges rédigé ; maquette validée (branche `feature/boutique-maquette`) ; **spécification du moteur de prix rédigée + 3 skills qualité créés** (branche `feature/moteur-prix`), prêt à coder.

> **Reprise rapide (nouvelle session)** : lire ce fichier + [`CAHIER_DES_CHARGES.md`](CAHIER_DES_CHARGES.md).
> Maquette = `site/src/pages/boutique/[ref].astro` sur la branche `feature/boutique-maquette` ; à voir sur `http://localhost:4321/boutique/netply` (prix **fictifs**). Prochaine action ci-dessous.

---

## Avancement par bloc

| Bloc | Description | Statut | Bloqué par |
|---|---|---|---|
| **B1 — Moteur de prix** | Réplique des tables Excel + tests | 🔄 Spécifié + 3 skills + **T1→T4 faits** (export + `types.ts` + `lookups.ts` + aiguillage + `engine.ts` ; Vitest 34 tests, relus reviewer+validator) — reste T5 (port) → T9 | — (constructible) |
| **B2 — Configurateur & pages produits** | Saisie dimensions → prix instantané | 🔄 Maquette enrichie (fiche complète + achat + demande de devis multi-produits ; prix fictif) | B1 pour le vrai prix |
| **B3 — Panier & paiement** | Panier + Stripe (invité) | ⏳ À venir | Immatriculation |
| **B4 — Comptes & remises** | Auth + % client depuis INCWO | ⏳ À venir | Immatriculation, INCWO |
| **B5 — Synchro INCWO** | Commande → INCWO | ⏳ À venir | INCWO souscrit |
| **B6 — Catalogue & design** | Navigation + intégration charte | ⏳ À venir | B2, fiches finalisées |

Légende : ⏳ à faire · 🔄 en cours · ✅ terminé · ⛔ bloqué

---

## Décisions (journal)

| Date | Décision | Détail |
|---|---|---|
| 27/06/2026 | Modèle d'achat | Hybride (carte invité + comptes validés) |
| 27/06/2026 | Sur-mesure | Prix instantané public |
| 27/06/2026 | ~~Type de remise~~ | ~~% par client~~ — **annulé le 28/06** (données : remises irrégulières par produit) |
| 27/06/2026 | Accès | Mixte (invité par carte + comptes validés Netair) |
| 27/06/2026 | Approche technique | Sur-mesure léger (Stripe direct, pas Snipcart) |
| 27/06/2026 | Séquencement | Par phases, moteur de prix d'abord |
| **28/06/2026** | **Prix en boutique** | **Tarif catalogue propre et cohérent** ; la boutique ne reproduit pas le pricing négocié |
| **28/06/2026** | **Deux canaux** | Boutique (libre-service, prix propre) **vs** Devis (négocié, humain + DEVIS AUTO) |
| **28/06/2026** | **Clients historiques** | Gérés en **canal devis/humain**, pas via la boutique |
| **28/06/2026** | **Remises comptes** | Au plus une remise **simple par famille** pour les nouveaux clients |
| **28/06/2026** | **Accès compte** | **Compte ouvert à tous** ; invité possible ; la validation Netair débloque la remise famille |
| **28/06/2026** | **Historiques & boutique** | Pas bannis : ils peuvent acheter au catalogue ; seuls leurs tarifs négociés restent au devis (« prix segmenté, pas la personne ») |
| **28/06/2026** | **Skills qualité** | Créer une version **Netair** (reviewer code + **validator métier**, qa optionnel) **au démarrage du Bloc 1** — s'inspirer des skills DEVIS AUTO (utiles, dans `DEVIS AUTO/_corbeille/`) sans les copier (marqués Titanair) |
| **28/06/2026** | **Un seul site** | Vitrine + boutique = une seule application déployée une fois (pas de site V2 séparé) |
| **28/06/2026** | **Ordre de démarrage** | Maquette (fiche produit + panier, faux prix) **d'abord** → puis moteur de prix B1 + skills |
| **29/06/2026** | **Page produit unifiée** | Une seule page = descriptif + caractéristiques + fiche technique **+** configurateur (plus de doublon vitrine/boutique) |
| **29/06/2026** | **Devis via le configurateur** | « Demander un devis » mène au configurateur (pas à la page contact générique) → capture produit/dimensions/quantité |
| **29/06/2026** | **Demande de devis multi-produits** | Liste « façon liste de courses » : plusieurs filtres + quantités, **sans prix affiché** (« prix sur devis »), puis mini-formulaire coordonnées → confirmation |
| **29/06/2026** | **Techno moteur de prix** | **TypeScript** — un seul module utilisable navigateur (prix instantané) **et** serveur (recalcul de sécurité avant paiement) |
| **29/06/2026** | **Définition du prix boutique** | **Prix HT = coût (tables Excel) × « Ratio prix tarif »** (onglet `Tableau_Gammes`) ; remises par famille reportées au B4 |
| **29/06/2026** | **Source des tables** | **Export Excel → JSON versionné** + **test de conformité** permanent « entrées Excel = sorties moteur » (garde anti-divergence sur la version Excel) |
| **29/06/2026** | **Skills qualité Netair** | **3 skills créés** dans `.claude/skills/` : `netair-site-reviewer` (code), `netair-pricing-validator` (métier), `netair-pricing-qa` (conformité Excel) — inspirés de DEVIS AUTO, **ré-écrits Netair** (aucune copie) |
| **29/06/2026** | **Mise à jour des tarifs** | **Deux leviers** : `% de revalorisation générale` (une case dans l'Excel) **+** cases ciblées. Publication vers le site = **commande manuelle contrôlée** (régénère + rejoue les tests), **pas de direct automatique** — 3 garde-fous (sécurité, test, rapidité). Détail : [`SPEC_B1`](SPEC_B1_MOTEUR_PRIX.md) §11 |
| **29/06/2026** | **Règle prix boutique (point §10.1 RÉSOLU)** | Tracé dans le calculateur DEVIS AUTO (onglet « Devis interne ») : coût = `PRU HT` (col. DB, assemblage géométrique) → × `Ratio prix tarif` (DD) = `PTU HT` (DE) = **col. DR en mode tarif pur**. La boutique prend ce **tarif pur** ; marges/catégories/remises manuelles = canal devis, exclues. Détail : [`SPEC_B1`](SPEC_B1_MOTEUR_PRIX.md) §3 |
| **29/06/2026** | **Points §10.3/4/5 RÉSOLUS** | **Gammes hors calculateur** → statut `sur_devis` (pas d'achat, demande de devis seulement, architecture identique). **Efficacités non fabriquées** → non proposées (absentes du menu) ; sinon `classe_indisponible`. **Arrondi** classique à 2 décimales. |
| **29/06/2026** | **Cadre par famille (§10.2) élargi** | Le « cadre » à fournir = **(a) dimensions mini/maxi** **et (b) quantité minimale de commande**, par famille (≠ paliers de prix). Sous le mini de quantité → **achat bloqué + message « quantité minimale : X »** (statut `quantite_insuffisante`). **En attente** : les valeurs (Pierre-Alain). |
| **29/06/2026** | **Modèle pour le codage du moteur** | **Tout en Opus** (choix de Pierre-Alain — sécurité maximale sur un sujet critique). **Déroge** volontairement au `CLAUDE.md` du site (« code en Haiku ») ; les 3 skills relisent quand même tout. CLAUDE.md à mettre à jour pour cohérence. |
| **29/06/2026** | **T1 — export Excel → données** | `site/scripts/export_excel.py` (Python/openpyxl, 0 dépendance npm) lit `Calculateur_Netair.xlsx` → `site/src/lib/pricing/data/tables.json` + `tables.meta.json` (carte d'identité : source, version interne, empreinte sha256). Classes/paliers lus dynamiquement (rien en dur), cases « non assurées » → `null`. **Vérifié** (comptages = onglets ; NETPLY 3,44 €, ratio 3,333, franco 750…) et **relu** (`netair-site-reviewer` : ⚠️ validé avec réserves → réserve MOYEN corrigée : erreurs claires si onglet/colonne renommé). |
| **29/06/2026** | **T4 Étape B — engine.ts (premiers prix)** | Aiguilleur + 6 méthodes A→F + prix = `arrondi2(coût × ratio)`, `coût = arrondi2((1+charge)×assemblage)`. **Découverte** : la charge `(1+frais_livraison)` (ex. NETPLY +10 %) était **oubliée dans l'exemple de la spec** → vrai prix NETPLY 287×592 G4 ×10 = **12,60 €** (pas 11,47 €) ; spec §3 corrigée. Types unifiés (`MethodeCalcul`), `lookups` corrigé (épaisseur `null` = toute épaisseur). **34 tests verts** (ancres méthode A validées par `cost_calculator.py` ; B→F en cohérence). Relu **reviewer** (⚠️ socle validé, 0 bug bloquant ; 2 dettes T8 : hors-format + preuve B→F vs Excel) **et validator** (CONFORME AVEC RÉSERVES : prix plausibles). _Port/poids = T5/T6._ **Pas encore commité (en attente d'accord PA).** |
| **29/06/2026** | **T4 Étape A — aiguillage des gammes** | Préalable à `engine.ts` : l'export (`export_excel.py`) lit la colonne « Méthode calcul » d'`Infos_Netair` et ajoute un champ **`methode`** (A→F / `sur_devis`) à chaque gamme — **rien en dur** (le moteur lira la méthode dans les données). Sécurité : libellé inconnu/famille hors calculateur → `sur_devis` (+ **avertissement** à l'export si libellé non reconnu). Ligne « Libre » (code 0) filtrée → **34 gammes** (A:2 B:1 C:1 D:2 E:1 F:8, sur_devis:19). `GammeRow.methode` typé. Relu (`netair-site-reviewer` ⚠️→ réserves traitées : alerte ajoutée ; unification du type `MethodeCalcul` reportée à l'Étape B). **22 tests verts**. CIAT/ECO en `sur_devis` (seront supprimés du calculateur — décision PA). |
| **29/06/2026** | **T3 — lookups.ts + Vitest** | `site/src/lib/pricing/lookups.ts` : recherche dans les grilles (gamme, L×l, surface, hors-format, pièce, poids, paliers, `prixPourClasse` à 3 issues), **rien en dur**. **Outil de test Vitest** ajouté (devDependency — jamais livré ; cache npm système corrompu → installé via cache dédié) + script `npm test` ; **20 tests** (valeurs issues de l'Excel) **verts**. Relu (`netair-site-reviewer` : 🔧 À CORRIGER → **corrigé** : `ep` peut être `null` pour NETFIL/recharges/etc. → type `Epaisseur = number\|null`, +2 tests) → ✅. |
| **29/06/2026** | **T2 — types.ts (contrat du moteur)** | `site/src/lib/pricing/types.ts` : `DemandePrix`, `StatutPrix` (6 statuts), `ResultatPrix`, `DetailCalcul` (traçabilité pour validator/qa). **Décision appliquée** : `codeGamme` en **texte** (codes gamme **non figés** : calculateur pas encore retravaillé, filtres à ajouter/retirer → rien en dur). Spec §4/§10 **et** `PLAN.md` (BLOC 1) alignés. Relu (`netair-site-reviewer` : ⚠️ validé avec réserves — écart spec corrigé). Compile (esbuild OK). _(Champ `paletteQuantite` renommé `palierQuantite` ensuite — voir T4.)_ |

---

## Questions ouvertes (à trancher)

- [ ] Capacités exactes de l'**API INCWO** (lecture remise client, création commande) — à confirmer.
- [ ] Service d'**authentification** pour les comptes (B4) : open-source vs managé.
- [ ] **Hébergement** : garder OVH pour la vitrine + Netlify pour le marchand, ou tout regrouper ?
- [ ] **CGV de vente en ligne** + mentions e-commerce + RGPD (→ skill `netair-juridique-fr`).
- [ ] Bornes **min/max de dimensions** fabricables par gamme (pour le configurateur).
- [ ] Politique de **délais de fabrication** à afficher pour le sur-mesure.
- [ ] **Cohérence avec DEVIS AUTO** : le moteur tarif (web) et `cost_calculator.py` (Python, coût) répliquent le même Excel → définir comment éviter la divergence (source unique, tests croisés, logique partagée ?).

---

## Dépendances externes

| Dépendance | Statut | Impact |
|---|---|---|
| Immatriculation société (SIREN, compte pro) | ⏳ en cours | Bloque mise en vente (B3/B4) |
| Fiches techniques finalisées (données + photos) | 🔄 en cours | Bloque catalogue (B6) |
| INCWO souscrit + API | ⏳ à faire | Bloque B4/B5 |

---

## Prochaine action

✅ **Spec B1 complète** + **3 skills** + **§10 quasi tout résolu** (reste : le « cadre » = dimensions mini/maxi **et** quantité mini par famille → Pierre-Alain fournira les valeurs ; ne bloque pas).
✅ **T1 fait** : export Excel→`tables.json` (+meta), vérifié + relu. Branche `feature/moteur-prix`.
✅ **T2 fait** : `types.ts` (contrat : `DemandePrix` / `ResultatPrix` / 6 statuts / `DetailCalcul`), relu, spec + `PLAN.md` alignés (`codeGamme` texte, codes non figés).
✅ **T3 fait** : `lookups.ts` (recherche dans les grilles, `prixPourClasse` à 3 issues, `ep` nullable) + **Vitest** (20 tests verts) ; relu et corrigé (réserve ÉLEVÉE levée).
✅ **T4 fait (A + B)** : aiguillage des gammes + `engine.ts` (6 méthodes + prix), 34 tests verts, relu reviewer + validator. Découverte : facteur de charge `(1+frais_livraison)` (spec §3 corrigée). **En attente de commit (accord PA).**
➡️ **Prochaine étape = T5** : `shipping.ts` — frais de port par **département** (table expédition) + **franco 750 €** (total HT ≥ 750 → port 0). Puis T6 poids, T7 point d'entrée `calculerPrix()`, **T8/T9 vecteurs dorés** (⚠️ y solder les 2 dettes : preuve « Excel = moteur » sur B→F + cas **hors-format** surface > 50 dm²).
🛠️ **Codage en Opus** (décision 29/06). Après chaque tâche → `netair-site-reviewer`. `validator` dès T4, `qa` à T8/T9 (cf. cadence SPEC_B1 §6).
🔁 À brancher plus tard (après serveur/immatriculation) : envoi réel de la demande de devis, pré-remplissage côté contact. **Maquette** (sélecteur efficacité + configurateur compact) sur branche `feature/boutique-maquette`.

---

## Journal d'avancement

| Date | Événement |
|---|---|
| 27/06/2026 | Brainstorm initial + rédaction du cahier des charges v0.1 + ce suivi |
| 28/06/2026 | Politique de prix affinée (2 canaux) · un seul site · ordre maquette→moteur · **maquette fiche produit créée** (branche `feature/boutique-maquette`) |
| 29/06/2026 | **Maquette enrichie & validée par Pierre-Alain** : page produit unifiée (descriptif + specs + fiche technique réintégrés), configurateur avec **2 canaux** (panier d'achat + demande de devis), **demande de devis multi-produits** (liste sans prix → mini-formulaire → confirmation). Parcours testés OK. |
| 29/06/2026 | **Démarrage Bloc B1 (moteur de prix)** : analyse complète des 12 onglets de `Calculateur_Netair.xlsx` (6 méthodes de calcul identifiées) ; **spécification détaillée rédigée** (`SPEC_B1_MOTEUR_PRIX.md`) ; **4 décisions de cadrage** (TypeScript · prix = coût × ratio tarif · export Excel→JSON + tests · 3 skills) ; **3 skills qualité Netair créés** (`netair-site-reviewer`, `netair-pricing-validator`, `netair-pricing-qa`). Branche `feature/moteur-prix`. |
