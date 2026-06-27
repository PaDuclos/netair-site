# Cahier des charges — Site marchand Netair

> **Version 0.1 — 27/06/2026** · Statut : **brouillon validé en brainstorm, à relire**
> Auteur : Claude Code (sous direction de Pierre-Alain Duclos)
> Suivi du projet : [`SUIVI.md`](SUIVI.md)

---

## 1. Contexte & objectif

Netair dispose d'un **site vitrine** (Astro, statique, charte « Precision Blanche »). L'objectif est
d'en faire **évoluer une version marchande**, **en parallèle** (sans remplacer ni casser la vitrine),
permettant :
- la **vente en ligne** des filtres ;
- le **prix sur-mesure instantané** par dimensions (ex. NETPLY 327×892×48), calculé à partir de la
  logique du **calculateur Excel existant** (`BLOC1_Gamme_Produits/Grille_Couts_Internes/Calculateur_Netair.xlsx`) ;
- un **panier + paiement** ;
- des **comptes clients** avec remise personnalisée.

**Principe directeur** : on ne remplace pas la vitrine, on construit la couche marchande à côté, dans
le même esprit sobre et technique.

---

## 2. Décisions validées (brainstorm du 27/06/2026)

| # | Décision | Choix retenu |
|---|---|---|
| D1 | Modèle d'achat | **Hybride** : carte bancaire en *invité* pour tous + comptes *validés* pour les réguliers |
| D2 | Prix sur-mesure | **Instantané à l'écran** (logique du calculateur portée sur le web) |
| D3 | Prix & remises | **Public = tarif catalogue** ; client connecté = tarif × (1 − sa remise) |
| D4 | Type de remise | **Un % par client** (éventuellement par famille), **stocké dans INCWO** |
| D5 | Accès & comptes | **Mixte** : achat invité par carte pour tous ; comptes (avec remise) réservés aux clients **validés par Netair** |
| D6 | Approche technique | **Sur-mesure léger** (vs brique louée Snipcart / vs plateforme B2B lourde) — contrôle de l'expérience et de la marque |
| D7 | Source de vérité | **INCWO** pour les clients, remises et commandes (pas de base concurrente sur le site → pas de doublon) |
| D8 | Séquencement | **Par phases** ; **commencer par le moteur de prix** (aucun blocage légal, réutilisable) |

---

## 3. Périmètre

### Dans le périmètre
- Moteur de calcul de prix (standard + sur-mesure) répliquant la logique Excel.
- Pages produits marchandes + configurateur de dimensions.
- Panier + paiement carte (Stripe) en mode invité.
- Comptes clients + remise % (Phase 2).
- Synchronisation des commandes vers INCWO.
- Catalogue marchand (navigation, présentation produits).

### Hors périmètre (pour l'instant)
- Gestion de stock temps réel (les sur-mesure sont fabriqués à la commande).
- Marketplace / multi-vendeurs.
- Application mobile native.
- Comptabilité (gérée par INCWO).

---

## 4. Architecture (option « sur-mesure léger »)

> ⚠️ **Vérité technique** : la vitrine actuelle est *statique* (elle affiche, elle ne traite rien).
> Encaisser un paiement, gérer des comptes et calculer un prix sécurisé nécessite **un petit moteur
> côté serveur** (fonctions « serverless »). C'est vrai pour toute solution marchande.

Cinq briques, construites dans cet ordre :

1. **🧮 Moteur de prix** *(le cœur, brique 1)*
   - Entrée : gamme, dimensions (L×H×P), épaisseur, quantité, (département pour le port).
   - Sortie : prix unitaire, prix total, frais de port, poids, durée de validité.
   - Réplique les tables Excel : `Prix_L_et_l`, `Prix_Surface`, `Prix_Surface_HF` (prix au dm² hors format),
     `Prix_Pièce`, paliers de quantité (0/6/20/500), `Poids_filtres`, `Tableau_Tarifs_Expédition`, `Tableau_franco`.
   - **Validable contre l'Excel** (mêmes entrées → mêmes prix), comme l'audit du calculateur énergétique.
   - ⚠️ **Distinct de DEVIS AUTO** (vérifié 27/06/2026) : DEVIS AUTO ne calcule **pas** le prix de *vente*
     (il le prend dans l'historique réel ou via marge humaine — « jamais de prix inventé »). Il possède
     déjà son propre `cost_calculator.py` qui calcule le **coût de revient** depuis les dimensions. Notre
     moteur calcule, lui, le **tarif de vente** depuis les tables tarif. Les deux partagent la **même
     logique géométrique** (surface, périmètre/mL, pièce, ×2 plissé) → `cost_calculator.py` est une bonne
     **référence** pour porter le nôtre, mais ce sont **deux moteurs distincts** (deux nombres, deux bases de code).

2. **🛒 Boutique (front)** *(brique 2)*
   - Pages produits + **configurateur de dimensions** (saisie L×H×P → prix instantané) + panier.
   - En Astro, à côté de la vitrine, charte « Precision Blanche ».

3. **💳 Paiement** *(brique 3)*
   - **Stripe** en mode invité. Stripe porte toute la sécurité/conformité carte → **Netair ne stocke
     jamais de données bancaires**.

4. **👤 Comptes + remise %** *(brique 4 — Phase 2)*
   - Connexion client → lecture du **% de remise depuis INCWO** → prix remisé affiché.
   - Comptes créés/validés par Netair (clients réguliers).

5. **🔄 Synchro INCWO** *(brique 5)*
   - À la commande : création du devis/commande dans INCWO (source de vérité), via son API.

---

## 5. Étude de faisabilité (points durs & verdict)

| Point dur | Évaluation | Verdict |
|---|---|---|
| **Prix sur-mesure dynamique** | Le calculateur Excel est **à tables de correspondance** (pas une boîte noire) → la logique est extractible et portable. | 🟢 Faisable |
| **Validation des calculs** | Mêmes entrées → mêmes sorties que l'Excel, testable automatiquement. | 🟢 Faisable |
| **Paiement** | Délégué à Stripe (standard, robuste, pas de données carte chez nous). | 🟢 Faisable |
| **Comptes + remise % depuis INCWO** | INCWO a une API (déjà utilisée par DEVIS AUTO). Le % par client est une donnée simple. | 🟡 Faisable, à confirmer (détails API INCWO) |
| **Synchro commandes → INCWO** | Idem, via API. | 🟡 Faisable, à confirmer |
| **Exposer un prix public** | Révèle la grille tarifaire publique + engage fermement sur un sur-mesure fabriqué. | 🟠 Maîtrisable (bornes dimensions + durée de validité + prix public = catalogue, pas les remises) |
| **Société non immatriculée** | Pas de Stripe réel, pas de CGV, pas de vente possible **tant que pas de SIREN/compte pro**. | 🔴 **Blocage de mise en ligne** (pas de blocage de développement) |
| **Fiches non finalisées** | Le catalogue marchand a besoin des fiches finies (données + photos Netair). | 🟠 Dépendance |

**Conclusion de faisabilité** : le projet est **faisable**. Le **seul vrai blocage** est *légal/temporel*
(immatriculation) pour la **mise en vente**, pas pour la **construction**. La brique la plus risquée et la
plus structurante (le moteur de prix) est **sans blocage légal** → **on commence par elle** (la décision
ne dépend pas de DEVIS AUTO ; voir la mise au point §4 brique 1).

---

## 6. Design & expérience (pages produits + catalogue)

> Cadre : charte **« Precision Blanche »** (sobre, blanc, géométrie du sens, accent teal, pas de décoration superflue).
> Le marchand doit rester **cohérent avec la vitrine**, pas la trahir.

### Page produit marchande
- En-tête produit (nom, classe ISO/EN, badges) repris de la fiche technique.
- **Configurateur de dimensions** : champs L × H × P + épaisseur + quantité → **prix instantané** affiché
  (avec bornes min/max et message clair si hors fabrication).
- Rappel **durée de validité du prix** (onglet `Durée_validité` de l'Excel).
- Bouton « Ajouter au panier » + lien vers la **fiche technique complète** (réutilise l'existant).
- Délai de fabrication indiqué pour le sur-mesure (produit fait à la commande).

### Catalogue marchand
- Navigation par **famille** (préfiltres, poches, compacts, HEPA, charbon) cohérente avec les gammes.
- Vignettes produits sobres, prix « à partir de » indicatif.
- Filtre/recherche par usage, classe, dimension.

### Principes UX
- **Trouver vite** prime sur l'effet : public B2B technique (BE, installateurs).
- Pas de surcharge ; le configurateur de prix est la pièce maîtresse, il doit être limpide.
- Accessibilité + responsive (mobile/tablette) + cohérence visuelle avec la fiche technique.

> Note : le **catalogue « livre » des fiches (HTML+PDF)** est un projet distinct (cf. `fiches-techniques/PROCESS.md`),
> mais il devra **se raccorder** au catalogue marchand (mêmes familles, liens croisés).

---

## 7. Découpage en blocs (chaque bloc = un sous-projet à spécifier en détail)

| Bloc | Contenu | Dépendance | Blocage légal ? |
|---|---|---|:--:|
| **B1 — Moteur de prix** | Réplique des tables Excel + tests de validation + (option) API interne | Aucune | ❌ non |
| **B2 — Configurateur & pages produits** | UI de saisie dimensions + prix instantané, charte | B1 | ❌ non |
| **B3 — Panier & paiement** | Panier + Stripe (invité) | B2 | 🔴 immatriculation |
| **B4 — Comptes & remises** | Auth + lecture % INCWO + prix remisé | B2, INCWO | 🔴 immatriculation |
| **B5 — Synchro INCWO** | Commande → devis/commande INCWO | B3, INCWO | 🟠 INCWO souscrit |
| **B6 — Catalogue & design** | Navigation, intégration design, raccord fiches | B2 | ❌ non |

**Ordre conseillé** : B1 → B2/B6 (constructibles maintenant) → puis B3/B4/B5 (après immatriculation + INCWO).
Chaque bloc fera l'objet de sa **propre spécification détaillée** au moment de l'attaquer.

---

## 8. Coûts (tarifs vérifiés le 27/06/2026)

> Principe : démarrage à **coût fixe quasi nul** ; on ne paie (Stripe) qu'**en cas de vente**.

| Service | Rôle | Coût | Nature |
|---|---|---|---|
| **Stripe** | Paiement carte | **1,5 % + 0,25 €** par transaction (cartes zone euro/EEE) · 3,25 % + 0,25 € pour cartes hors EEE · **pas d'abonnement** | À l'usage |
| **Hébergement** (Netlify Starter) | Site + moteur côté serveur | **Gratuit** jusqu'à 125 000 appels de fonction/mois (usage commercial autorisé) · ~**20 $/mois** (Pro) au-delà | Gratuit au lancement |
| **Domaine `netair.fr`** | Adresse web | **Déjà payé** (OVH) | Existant |
| **INCWO** | ERP + API commandes/clients | **40 €/mois** (déjà décidé pour 2 users) · accès API **à confirmer** (inclus ?) | Existant |
| **Comptes clients** (Phase 2) | Connexion sécurisée | Options **gratuites** (open-source) ou service managé (palier gratuit puis payant) — **à arbitrer en B4** | Phase 2 |
| **Certificat SSL (https)** | Sécurité | **Gratuit** (inclus Netlify/OVH) | Inclus |

**Exemple concret** : une commande de 200 € payée par carte EEE → frais Stripe = 1,5 % × 200 + 0,25 = **3,25 €**.

**Économie du choix « sur-mesure léger »** : en passant **directement par Stripe** (plutôt que par une
brique louée type Snipcart, qui prélève ~2 % supplémentaires), on **évite une commission de revente**.

⚠️ **Attention** (non chiffrable ici) : le vrai coût d'un projet sur-mesure, c'est le **temps de
développement** (construction des briques), pas l'abonnement mensuel. Les coûts ci-dessus sont les
**coûts de fonctionnement** une fois en ligne.

---

## 9. Risques & points de vigilance

| Risque | Niveau | Parade |
|---|---|---|
| Vente impossible avant immatriculation (SIREN, compte pro, CGV) | 🔴 | Construire d'abord les briques sans blocage (B1, B2, B6) ; mise en ligne après BLOC0 |
| Erreur de prix (un mauvais portage des tables Excel) | 🔴 | Tests automatiques « entrées Excel = sorties site » sur chaque gamme |
| Exposition de la grille tarifaire publique | 🟠 | Public = tarif catalogue uniquement ; remises seulement après connexion |
| Engagement ferme sur un sur-mesure infabricable | 🟠 | Bornes min/max de dimensions + validation technique (règle codification) + durée de validité |
| Sécurité des comptes / RGPD (données clients) | 🟠 | Auth déléguée à un service éprouvé ; mentions légales + registre RGPD (skill `netair-juridique-fr`) |
| Dépendance INCWO (API) | 🟡 | Confirmer les capacités API en amont de B4/B5 |
| Doublon de données (prix/clients hors INCWO) | 🟡 | INCWO = source unique ; le site lit, ne duplique pas |
| Divergence de logique avec `cost_calculator.py` de DEVIS AUTO (même Excel répliqué 2× : tarif web + coût Python) | 🟡 | Garder l'Excel comme source unique ; tests croisés ; envisager une logique géométrique partagée à terme |

---

## 10. Prérequis & dépendances

- ✅ Calculateur Excel disponible (source de la logique de prix).
- ⏳ **Immatriculation société** (SIREN, compte bancaire pro) — pour Stripe + CGV + vente.
- ⏳ **Fiches techniques finalisées** (données + photos Netair) — pour le catalogue marchand.
- ⏳ **INCWO souscrit + API confirmée** — pour comptes/remises/commandes.
- ⏳ **CGV de vente en ligne + mentions légales e-commerce + RGPD** (skill `netair-juridique-fr`).

---

## 11. Prochaines étapes

1. **Relecture de ce cahier des charges** par Pierre-Alain.
2. **Spécification détaillée du Bloc 1 (moteur de prix)** — le premier constructible, sans blocage.
3. Plan d'implémentation du Bloc 1 (découpage en tâches).
4. Construction + validation contre l'Excel.
5. (Plus tard) Blocs suivants, au fil de l'immatriculation et des fiches.

---

## Sources (coûts)
- Stripe — tarifs France/EEE 2026 (1,5 % + 0,25 €) : https://stripe.com/pricing
- Hébergement serverless — Netlify Pricing (Starter gratuit, usage commercial) : https://www.netlify.com/pricing/
