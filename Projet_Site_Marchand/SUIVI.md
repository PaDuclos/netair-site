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
| **B1 — Moteur de prix** | Réplique des tables Excel + tests | 🔄 Spécifié ([`SPEC_B1`](SPEC_B1_MOTEUR_PRIX.md)) + 3 skills qualité créés — prêt à coder | — (constructible) |
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

✅ Maquette relue et **validée par Pierre-Alain** (29/06/2026).
✅ **Spécification B1 rédigée** ([`SPEC_B1_MOTEUR_PRIX.md`](SPEC_B1_MOTEUR_PRIX.md)) + **3 skills qualité créés** (branche `feature/moteur-prix`).
➡️ **Relire la SPEC_B1** (notamment §3 méthodes, §6 plan, §10 points à confirmer), puis **lancer le codage** (phase Code/Haiku) : T1 export Excel→JSON, puis lookups, méthodes, port, poids, tests dorés.
⚠️ **Point à trancher pendant le codage** : verrouiller le ratio coût→tarif et la définition exacte du « coût » en croisant 3-4 lignes réelles de l'Excel (cf. SPEC_B1 §10).
🔁 À brancher plus tard (après serveur/immatriculation) : envoi réel de la demande de devis (email / DEVIS AUTO), pré-remplissage côté contact.

---

## Journal d'avancement

| Date | Événement |
|---|---|
| 27/06/2026 | Brainstorm initial + rédaction du cahier des charges v0.1 + ce suivi |
| 28/06/2026 | Politique de prix affinée (2 canaux) · un seul site · ordre maquette→moteur · **maquette fiche produit créée** (branche `feature/boutique-maquette`) |
| 29/06/2026 | **Maquette enrichie & validée par Pierre-Alain** : page produit unifiée (descriptif + specs + fiche technique réintégrés), configurateur avec **2 canaux** (panier d'achat + demande de devis), **demande de devis multi-produits** (liste sans prix → mini-formulaire → confirmation). Parcours testés OK. |
| 29/06/2026 | **Démarrage Bloc B1 (moteur de prix)** : analyse complète des 12 onglets de `Calculateur_Netair.xlsx` (6 méthodes de calcul identifiées) ; **spécification détaillée rédigée** (`SPEC_B1_MOTEUR_PRIX.md`) ; **4 décisions de cadrage** (TypeScript · prix = coût × ratio tarif · export Excel→JSON + tests · 3 skills) ; **3 skills qualité Netair créés** (`netair-site-reviewer`, `netair-pricing-validator`, `netair-pricing-qa`). Branche `feature/moteur-prix`. |
