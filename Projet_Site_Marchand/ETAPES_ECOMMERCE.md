# Feuille de route e-commerce — découpage en étapes

> Rédigée le **17/08/2026** à la demande de Pierre-Alain : *« il faut découper ce projet par étape,
> et on y va pas à pas comme on a fait jusqu'à maintenant. »*
> Détail technique dans [`SPEC_B3_PAIEMENT.md`](SPEC_B3_PAIEMENT.md) et [`SPEC_B4_COMPTES.md`](SPEC_B4_COMPTES.md).

## Comment on avance

**Une étape à la fois.** Chaque étape se termine par quelque chose que **vous pouvez vérifier
vous-même**, et par un accord explicite avant de passer à la suivante. C'est la méthode qui a
fonctionné sur le moteur de prix (B1 : T1→T9, chacune relue avant la suivante).

**Aucune étape ne met le site en danger** : tout se fait sur des branches Git, la vitrine actuelle
n'est jamais exposée tant que vous n'avez pas dit oui.

---

## Vue d'ensemble

| Étape | Objet | Ce qu'il faut de vous | Taille |
|:--:|---|---|:--:|
| **0** | Le calcul de sécurité (recalcul serveur + TVA) | **Rien** | Moyenne |
| **1** | Le site apprend à faire tourner du code | Choix de l'hébergeur | Petite |
| **2** | Les commandes s'enregistrent quelque part | Choix + création de la base | Moyenne |
| **3** | Le paiement, **en mode test** (zéro euro réel) | Compte Stripe | Moyenne |
| **4** | Emails de confirmation | Boîte mail dédiée | Petite |
| **5** | Passage en réel — première vraie vente | Verrous à lever (voir ci-dessous) | Petite |
| **6→** | Comptes clients (B4) | Décisions du §4 de la spec B4 | Grosse |

**En parallèle, sans lien avec ce qui précède : [B9 — réservation en ligne](SUIVI.md) (Cal.com).**
Elle ne dépend pas du serveur et peut se faire à tout moment.

---

## Étape 0 — Le calcul de sécurité ⭐ **démarrable immédiatement**

**Pourquoi c'est la première.** C'est le cœur du sujet, et — c'est ce qui la rend idéale pour
commencer — **elle ne dépend de rien** : ni hébergeur, ni base, ni compte Stripe, ni décision de
votre part. C'est du calcul pur, vérifiable sur votre machine, exactement comme le moteur de prix.

**Ce qu'on écrit.** Le module qui reçoit un panier, **le recalcule intégralement** et décide s'il est
acceptable. Il vérifie chaque ligne (produit vendable ? classe disponible ? format fabriqué ?),
recalcule le port et le franco, contrôle le minimum de 80 € HT, et ajoute la TVA à 20 %.

> **Le principe qu'il fait respecter** : le navigateur n'envoie **que la configuration** du panier,
> jamais les prix. Le serveur recalcule tout lui-même. Sans ça, n'importe qui modifie l'affichage
> de son navigateur et paie un filtre 1 € au lieu de 108 €.

**Ce qui existe déjà et qu'on réutilise** : le moteur de prix B1, sans y toucher. Il a été écrit
exprès pour tourner des deux côtés.

**Ce que vous verrez à la fin** : une série de tests automatiques verts, dont des **tentatives de
fraude simulées** (panier au prix trafiqué, produit sur devis forcé à l'achat, quantité sous le
minimum, format hors fabrication) — chacune correctement refusée. Même format de preuve que les
1 245 vecteurs du moteur de prix.

**Il vous faut** : rien.

---

## Étape 1 — Le site apprend à faire tourner du code

Aujourd'hui le site est un paquet de pages figées : rien ne s'exécute côté Netair. Cette étape lui
ajoute la capacité d'exécuter du code à la demande, **sans changer une virgule de ce qui s'affiche**.

**Ce que vous verrez à la fin** : les 34 pages **strictement identiques** à aujourd'hui. Si quoi que
ce soit bouge visuellement, c'est un échec de l'étape.

**Il vous faut** : choisir l'hébergement. Ma recommandation — garder le **nom de domaine chez OVH**
(rien à déménager) et héberger le **site** chez **Netlify** ou **Cloudflare** : palier gratuit
suffisant au démarrage, aucun serveur à administrer, et réversible si ça ne convient pas.

---

## Étape 2 — Les commandes s'enregistrent

Il n'existe aujourd'hui **aucune base de données**. Sans elle, une commande payée n'existe nulle part.

**Ce que vous verrez à la fin** : une commande de test apparaît dans une liste, avec son numéro, ses
lignes, ses montants.

**Il vous faut** : créer le compte de base de données. Recommandation — **Supabase, région
européenne** : palier gratuit, technologie ouverte (donc récupérable si vous partez), et surtout
**le même outil servira les comptes clients de l'étape 6** — une brique au lieu de deux.

---

## Étape 3 — Le paiement, en mode test

Stripe fournit un **mode test** avec des numéros de carte fictifs : le parcours complet se déroule
pour de vrai, **sans qu'un centime ne bouge**.

**Ce que vous verrez à la fin** : vous composez un panier, vous payez avec une carte de test, et la
commande apparaît enregistrée avec le bon montant.

**Point important** : la carte bancaire ne transite **jamais** par le site Netair — c'est Stripe qui
héberge le formulaire sur ses propres pages. Cela vous évite entièrement le régime de conformité
bancaire PCI-DSS, qui est lourd pour une petite structure.

**Il vous faut** : créer le compte Stripe (SIREN et RIB sont disponibles). ⚠️ **C'est vous qui le
créez et qui saisissez les clés** — création de compte et coordonnées bancaires ne passent pas par moi.

---

## Étape 4 — Les emails de confirmation

Le client reçoit sa confirmation, Netair reçoit sa notification.

**Il vous faut** : la **boîte mail dédiée** que vous souscrivez (sujet ⏸️ en attente au 17/08).
⚠️ Rappel : le blocage `535 5.7.139` est posé au niveau du tenant Microsoft, pas dû à la boîte
partagée — prévoir de réactiver l'authentification SMTP dans l'administration Microsoft 365.

---

## Étape 5 — Passage en réel

Bascule du mode test au mode réel. **Techniquement courte, mais elle suppose trois verrous levés :**

| Verrou | État |
|---|---|
| 🔴 **Chaîne Excel → site rompue** | Reporté par vous le 17/08, **pas abandonné**. Tant que ce n'est pas réglé, on ne peut pas vendre à des prix sûrs |
| 🔴 **Code 17 (NETBAG S) non confirmé** | Des prix réels partent au panier sur une identité présumée. À vérifier dans l'Excel source |
| 🟠 **CGV de vente en ligne** | N'existent pas. À rédiger (je peux le faire), relecture professionnelle recommandée |

---

## Étape 6 et suivantes — Les comptes clients (B4)

Découpage détaillé dans [`SPEC_B4_COMPTES.md`](SPEC_B4_COMPTES.md) (U1→U8) : inscription, profil,
historique, réassort en un clic, remise par famille, validation des comptes par Netair, obligations
RGPD.

> **Rappel de la décision du 28/06** : l'achat en invité reste possible. Le compte n'est **jamais**
> obligatoire pour acheter. On peut donc parfaitement **vendre dès l'étape 5**, et ajouter les
> comptes ensuite — c'est le chemin le plus court vers la première vente.

---

## Ce qui peut avancer en parallèle

| Sujet | Dépendance |
|---|---|
| **B9 — Réservation en ligne (Cal.com)** | Aucune vis-à-vis du e-commerce. Il vous faut créer le compte Cal.com et connecter votre iCloud |
| **CGV de vente en ligne** | Rédigeables dès maintenant |
| **Regroupement des branches Git** | `main` est figé au 01/07, ~100 commits vivent à côté. À faire avant toute mise en production |
