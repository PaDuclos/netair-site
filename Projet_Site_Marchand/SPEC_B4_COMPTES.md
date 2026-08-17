# Spécification — Bloc B4 : Comptes clients & remise par famille

> Rédigée le **17/08/2026**, sur demande de Pierre-Alain. Branche `feature/b3-paiement`.
> Suite logique de [`SPEC_B3_PAIEMENT.md`](SPEC_B3_PAIEMENT.md) — **B4 réutilise l'infrastructure de B3**
> (hébergement serveur + base de données). Le faire avant B3 obligerait à monter cette infrastructure
> deux fois.
>
> ⚠️ **Statut : SPÉCIFICATION — aucune ligne de code écrite.**

---

## 0. Le constat de départ

| Élément | État réel (vérifié le 17/08/2026) |
|---|---|
| Page `/compte` | ✅ Existe, propre, à la charte — mais c'est **une vitrine, pas une fonction** : elle annonce « Espace client — bientôt disponible » |
| Connexion | ❌ **Aucune.** Pas d'inscription, pas de mot de passe, pas de base de clients |
| Icône « Se connecter » dans le menu | ✅ Présente (`Header.astro` l. 37-38), mène à cette page d'attente |
| Remise par famille | ❌ Rien — ni côté site, ni confirmé côté INCWO |

C'était **volontaire** (décision du 30/06) : poser l'emplacement dans le menu pour préparer B4,
sans faire semblant d'avoir une connexion qui n'existe pas.

---

## 1. Ce que B4 doit produire

> Un client peut créer un compte, retrouver ses commandes, **recommander en un clic** ses filtres
> habituels — et, si Netair a validé son compte, **voir automatiquement sa remise** par famille.

---

## 2. Les règles déjà décidées (28/06/2026) — à ne pas rouvrir sans raison

| Règle | Détail |
|---|---|
| **Achat sans compte possible** | Le client peut payer par carte en « invité ». Le compte n'est **jamais** obligatoire pour acheter |
| **Compte ouvert à tous** | Pas de filtrage à l'inscription |
| **À quoi sert le compte** | Historique de commandes, réassort, adresses de facturation et de livraison |
| **La remise** | Un compte **validé par Netair** débloque **une remise simple par famille** (ex. −X % sur les NETPLY). **Pas** de pourcentage global par client, **pas** de grille par produit |
| **Pourquoi pas de % par client** | Vos données Titanair l'ont montré : les remises réelles étaient trop irrégulières d'un produit à l'autre pour être résumées par un pourcentage unique |
| **Clients historiques** | Restent gérés au **canal devis** (négocié, humain, DEVIS AUTO). Ils peuvent acheter en boutique, mais au tarif catalogue. *« Prix segmenté, pas la personne. »* |

---

## 3. Le point d'architecture à ne pas rater

La remise **ne doit jamais** être appliquée dans le navigateur, pour la même raison qu'en B3 :
le navigateur est manipulable. Sinon n'importe qui s'accorde 80 % de remise.

**Où elle s'applique :** dans le recalcul serveur de B3 (`recalcul.ts`), **après** le tarif catalogue.

```
tarif catalogue (moteur B1, inchangé)
   → remise famille du compte connecté, lue côté serveur   ← couche B4
      → port + minimum de commande
         → TVA
            → montant envoyé à Stripe
```

Le moteur de prix B1 **n'est pas modifié** : il ne connaît que le tarif catalogue, et c'est très bien
ainsi (spec B1 §8). La remise est une **couche séparée par-dessus**.

---

## 4. D'où vient la remise ? Trois scénarios, à trancher

C'est **la vraie question ouverte** de ce bloc, et elle est en suspens depuis le 29/06
(« capacités exactes de l'API INCWO — à confirmer »).

| Scénario | Comment ça marche | Risque |
|---|---|---|
| **A — Lue en direct dans INCWO** | À chaque commande, le site interroge INCWO pour connaître la remise du client | Le site devient dépendant de la disponibilité d'INCWO au moment de payer. Si INCWO ne répond pas, le client ne peut pas commander |
| **B — Recopiée dans notre base** *(recommandé)* | La remise est saisie une fois dans notre base, et **synchronisée** depuis INCWO périodiquement ou à la main | Une remise modifiée dans INCWO met un moment à arriver — acceptable, ce sont des remises de catalogue, pas des prix négociés à la journée |
| **C — Saisie uniquement chez nous** | INCWO n'entre pas en jeu | Double saisie, donc divergence assurée à terme |

> **Recommandation : scénario B.** Il ne fait pas dépendre un paiement de la disponibilité d'un ERP,
> et il garde INCWO comme source de vérité.
>
> ⚠️ **Prérequis dans tous les cas : vérifier ce que l'API INCWO sait réellement renvoyer.**
> Le connecteur a renvoyé une erreur de protocole lors de mes essais du 17/08 — à retester.

---

## 5. Comment gère-t-on les connexions ?

Gérer soi-même des mots de passe est une **mauvaise idée** : c'est le genre de code où une erreur
discrète devient une fuite de données clients. On délègue à un service spécialisé.

| Option | Pour | Contre |
|---|---|---|
| **Supabase Auth** *(recommandé)* | **Déjà retenu en B3 pour la base de commandes** — une brique au lieu de deux. Hébergement **région UE**, palier gratuit, technologie ouverte (donc récupérable si vous partez) | — |
| **Auth0 / Clerk** | Très complets | Une dépendance de plus, hébergement souvent hors UE, palier gratuit vite limité |
| **Fait maison (Lucia…)** | Contrôle total | C'est nous qui portons le risque de sécurité. **Déconseillé** |

**RGPD** : hébergement des données clients **en Union européenne**, information dans la politique de
confidentialité (déjà rédigée, à compléter), et le registre RGPD (`BLOC3/RGPD/`) à mettre à jour avec
ce nouveau traitement.

---

## 6. Découpage en tâches

| # | Tâche | Dépend de |
|---|---|---|
| **U1** | Inscription / connexion / mot de passe oublié + pages associées | Infrastructure B3 (T1), choix §5 |
| **U2** | Profil : société, SIREN, adresses de facturation et de livraison | U1 |
| **U3** | Historique des commandes (relire ce que B3 a enregistré) | U1, B3-T4 |
| **U4** | **Réassort en un clic** — recomposer un panier depuis une commande passée | U3 |
| **U5** | Remise par famille : stockage, application **côté serveur**, affichage transparent au panier | U1, B3-T2, §4 tranché |
| **U6** | Écran de validation d'un compte par Netair (qui débloque la remise) | U5 |
| **U7** | RGPD : export et suppression des données d'un compte (obligations légales) | U1 |
| **U8** | Remplacer le contenu « bientôt disponible » de `/compte` par le vrai espace | U1→U4 |

⚠️ **U4 (réassort) mérite attention** : les filtres sont largement **sur mesure**. Rejouer une commande
suppose de re-vérifier que la configuration est **toujours fabriquée et tarifée** — un format retiré du
catalogue entre-temps doit produire un message clair, pas un prix erroné.

---

## 7. Points à trancher (avant de coder)

- [ ] **Le compte est-il requis au lancement, ou ouvre-t-on en paiement invité d'abord ?** *(question déterminante pour le calendrier)*
- [ ] **Origine de la remise** : scénario A, B ou C (§4 — recommandation : B)
- [ ] **Service de connexion** : Supabase Auth ou autre (§5)
- [ ] **Qui valide un compte, et sur quel critère ?** (SIREN vérifié ? client déjà connu ? décision manuelle ?)
- [ ] **Quelles familles ont une remise, et de combien ?** — donnée métier, à fournir
- [ ] **Un compte validé voit-il ses prix remisés partout** (pages produits comprises) **ou seulement au panier ?**

---

## 8. Ce qui reste bloqué quoi qu'il arrive

Les mêmes verrous qu'en B3, rappelés ici pour qu'ils ne s'oublient pas :

1. 🔴 **Chaîne Excel → site rompue** — verrou de mise en ligne (`PLAN.md` § ALERTE PERMANENTE)
2. 🔴 **Code 17 (NETBAG S)** — identité à confirmer avant le premier euro encaissé
3. 🟠 **CGV de vente en ligne** — à rédiger
4. 🟠 **Emails** — en attente de la boîte mail dédiée
