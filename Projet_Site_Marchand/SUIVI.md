# Suivi — Projet Site marchand Netair

> Tableau de bord vivant du projet. Mis à jour à chaque avancée.
> Cahier des charges : [`CAHIER_DES_CHARGES.md`](CAHIER_DES_CHARGES.md)

**État global : 🟡 Conception** — brainstorm fait, cahier des charges rédigé, en attente de relecture.

---

## Avancement par bloc

| Bloc | Description | Statut | Bloqué par |
|---|---|---|---|
| **B1 — Moteur de prix** | Réplique des tables Excel + tests | ⏳ À spécifier | — (constructible) |
| **B2 — Configurateur & pages produits** | Saisie dimensions → prix instantané | ⏳ À venir | B1 |
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

➡️ **Relecture du cahier des charges par Pierre-Alain**, puis **spécification détaillée du Bloc 1 (moteur de prix)**.

---

## Journal d'avancement

| Date | Événement |
|---|---|
| 27/06/2026 | Brainstorm initial + rédaction du cahier des charges v0.1 + ce suivi |
