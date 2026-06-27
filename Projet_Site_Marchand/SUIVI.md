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
| 27/06/2026 | Remises | Public = catalogue ; client connecté = ×(1 − %) |
| 27/06/2026 | Type de remise | % par client, stocké dans INCWO |
| 27/06/2026 | Accès | Mixte (invité par carte + comptes validés Netair) |
| 27/06/2026 | Approche technique | Sur-mesure léger (Stripe direct, pas Snipcart) |
| 27/06/2026 | Séquencement | Par phases, moteur de prix d'abord |

---

## Questions ouvertes (à trancher)

- [ ] Capacités exactes de l'**API INCWO** (lecture remise client, création commande) — à confirmer.
- [ ] Service d'**authentification** pour les comptes (B4) : open-source vs managé.
- [ ] **Hébergement** : garder OVH pour la vitrine + Netlify pour le marchand, ou tout regrouper ?
- [ ] **CGV de vente en ligne** + mentions e-commerce + RGPD (→ skill `netair-juridique-fr`).
- [ ] Bornes **min/max de dimensions** fabricables par gamme (pour le configurateur).
- [ ] Politique de **délais de fabrication** à afficher pour le sur-mesure.

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
