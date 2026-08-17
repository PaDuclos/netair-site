# Spécification — Bloc B3 : Paiement & enregistrement des commandes

> Rédigée le **17/08/2026**, sur demande de Pierre-Alain (« il faut avancer le projet du e-commerce :
> paiement, compte client »). Branche `feature/b3-paiement`.
> À lire avec [`CAHIER_DES_CHARGES.md`](CAHIER_DES_CHARGES.md) et [`SPEC_B1_MOTEUR_PRIX.md`](SPEC_B1_MOTEUR_PRIX.md).
> Le bloc **B4 (comptes clients)** fait l'objet de sa propre spec : [`SPEC_B4_COMPTES.md`](SPEC_B4_COMPTES.md).
>
> ⚠️ **Statut : SPÉCIFICATION — aucune ligne de code écrite.** Le workflow du projet
> (`Site_Web/CLAUDE.md`) impose : *spec → validation → code → revue*. Rien ne sera codé sans accord.

---

## 0. Le constat de départ — ce qui existe vraiment aujourd'hui

Vérifié dans le dépôt le 17/08/2026, pas déclaré :

| Élément | État réel |
|---|---|
| `site/astro.config.mjs` | **Aucun adaptateur, aucun `output: 'server'`** → le site est **100 % statique** |
| Conséquence | **Aucun code Netair ne tourne sur un serveur.** Tout ce qui existe s'exécute dans le navigateur du visiteur |
| Tunnel de commande (`panier.astro`, l. 263-278) | Le bouton « Valider la commande » **n'envoie rien nulle part** : il masque le formulaire et affiche un texte de confirmation en JavaScript |
| Conséquence | **Aucune commande n'est enregistrée**, ni chez Netair, ni ailleurs. Le panier vit dans le navigateur du client (`localStorage`) et disparaît avec lui |
| `site/server/contact-endpoint.ts` | Modèle de code serveur **écrit mais hors build**, jamais activé — même verrou |
| Base de données | **Il n'y en a aucune** |
| Compte Stripe | **Inexistant** |

> **À retenir en une phrase :** la boutique sait aujourd'hui *calculer* un prix juste et *composer*
> un panier, mais elle n'a **ni serveur, ni mémoire, ni moyen d'encaisser**. B3 consiste
> exactement à lui donner ces trois choses.

---

## 1. Ce que B3 doit produire (en une phrase)

> Un client peut composer son panier, payer par carte, et **la commande existe** :
> enregistrée chez Netair, confirmée par email au client, à un prix que le client
> **n'a pas pu manipuler**.

---

## 2. Le point de sécurité central — à ne jamais transiger

C'était déjà écrit dans la spec B1 (§8), c'est ici que ça s'applique :

> Le prix affiché dans le navigateur est **pratique**, mais **jamais fiable**. Le navigateur d'un
> visiteur est modifiable en quelques secondes : n'importe qui peut afficher 1 € au lieu de 108 €.

**Règle absolue de B3 : le serveur ne fait JAMAIS confiance au prix envoyé par le navigateur.**

Concrètement, le navigateur n'envoie **que la configuration** de chaque ligne — gamme, dimensions,
classe d'efficacité, épaisseur, quantité, département de livraison. **Aucun prix ne circule.**
Le serveur rejoue lui-même `calculerPrix()` et `calculerPort()` — **le même code TypeScript**,
c'est tout l'intérêt de la décision C1 du 29/06 — et **son résultat fait foi**.

Si le prix recalculé par le serveur diffère de celui affiché au client, la commande est **refusée**
avec un message clair (« nos tarifs ont changé, merci de vérifier votre panier »), jamais silencieusement
alignée sur l'un ou l'autre.

---

## 3. La chaîne complète, étape par étape

Expliqué sans jargon : ce qui se passe entre le clic et la commande.

| # | Ce que fait le client | Ce qui se passe côté Netair |
|---|---|---|
| 1 | Compose son panier | Rien — tout est dans son navigateur, prix indicatifs |
| 2 | Clique « Passer commande » | Le navigateur envoie **la configuration du panier, sans prix**, à notre serveur |
| 3 | — | Le serveur **recalcule tout** : chaque ligne, le port, le franco, le minimum de 80 € HT, la TVA. Il vérifie que chaque produit est bien vendable |
| 4 | — | Le serveur crée une **session de paiement Stripe** avec **ses** montants, et renvoie un lien |
| 5 | Est redirigé chez Stripe, saisit sa carte | **Le numéro de carte ne passe jamais par le site Netair** — c'est Stripe qui l'encaisse sur ses propres pages. Netair n'a donc aucune donnée bancaire à protéger |
| 6 | Voit « paiement accepté » | Stripe prévient notre serveur (« webhook »). **C'est ce signal qui fait foi**, pas le retour du navigateur — un client peut fermer son écran juste après avoir payé |
| 7 | Reçoit un email de confirmation | Le serveur **enregistre la commande**, envoie la confirmation, et (plus tard, en B5) la pousse dans INCWO |

**Pourquoi passer par les pages de Stripe plutôt que d'encaisser nous-mêmes ?** Parce que dès qu'un
numéro de carte transite par votre site, vous entrez dans un régime de conformité bancaire lourd
(PCI-DSS). En laissant Stripe héberger le formulaire de carte, Netair n'y est **pas soumis**.
C'est le choix standard, et le moins risqué.

---

## 4. Les trois briques d'infrastructure à choisir

Ce sont **les seules vraies décisions** de ce bloc. Le reste en découle.

### 4.1 Un hébergement qui sait exécuter du code

Aujourd'hui le site est un paquet de fichiers figés. Pour encaisser, il faut un hébergement capable
de **faire tourner du code à la demande** (ce qu'on appelle des « fonctions serverless » : de petits
bouts de programme qui ne s'exécutent qu'au moment où on en a besoin, et qu'on ne paie qu'à l'usage).

| Option | Pour | Contre |
|---|---|---|
| **Netlify** ou **Cloudflare Pages** | Adaptateur Astro officiel, palier gratuit largement suffisant au démarrage, mise en ligne automatique à chaque commit | Un prestataire de plus |
| **Vercel** | Idem, très bonne intégration Astro | Société américaine (à regarder côté RGPD) |
| **OVH** (où est déjà `netair.fr`) | Tout au même endroit | Héberger du Node.js chez OVH demande un serveur privé (VPS) à administrer soi-même — plus lourd, et à maintenir |

> **Recommandation** : garder le **nom de domaine chez OVH** (rien à bouger) et héberger le **site**
> chez Netlify ou Cloudflare. C'est le chemin le plus court, réversible, et sans serveur à administrer.
> Cela répond aussi à la question ouverte du 29/06 (« OVH + Netlify ou tout regrouper ? »).

### 4.2 Un endroit où ranger les commandes

Il n'y a **aucune base de données** aujourd'hui. Sans elle, une commande payée n'existe nulle part.

> **Recommandation : Supabase** (hébergement en **région européenne** possible, palier gratuit,
> technologie ouverte donc pas de dépendance définitive). Avantage décisif : **le même outil fournit
> aussi les comptes clients du bloc B4** — une brique au lieu de deux, une facture au lieu de deux.

### 4.3 Un compte Stripe

⚠️ **Je ne peux pas le créer** — la création de compte et la saisie de coordonnées bancaires vous
reviennent, c'est une limite que je ne franchis pas. Les informations nécessaires sont toutes
disponibles : SIREN 107 397 648, RIB BPAURA, adresse du siège.

---

## 5. Ce qui doit être écrit (architecture des fichiers)

```
site/
├── astro.config.mjs          ← MODIFIÉ : ajout de l'adaptateur + output 'server'
├── src/pages/api/
│   ├── commande.ts           ← reçoit le panier, RECALCULE, crée la session Stripe
│   └── stripe-webhook.ts     ← reçoit la confirmation de Stripe, enregistre la commande
├── src/pages/commande/
│   ├── merci.astro           ← page de retour après paiement réussi
│   └── annulee.astro         ← page de retour si le client abandonne
├── src/lib/commande/
│   ├── recalcul.ts           ← rejoue le moteur sur un panier reçu — LE point de sécurité
│   ├── tva.ts                ← TVA 20 % (France métropole + Corse uniquement)
│   └── types.ts              ← contrat : PanierRecu / CommandeValidee / motifs de refus
└── src/lib/db/
    └── commandes.ts          ← enregistrement et relecture des commandes
```

**Rien du moteur de prix existant n'est modifié.** B3 le *réutilise* — c'est précisément
pour ça qu'il a été écrit en TypeScript utilisable des deux côtés.

---

## 6. Découpage en tâches

Chaque tâche est vérifiable seule et passe par `netair-site-reviewer` avant la suivante.

| # | Tâche | Dépend de |
|---|---|---|
| **T1** | Passer le site en mode serveur (adaptateur) **sans rien casser** — les 34 pages doivent rester identiques | Choix hébergeur (§4.1) |
| ~~**T2**~~ | ~~`recalcul.ts` — rejouer le moteur sur un panier reçu + tests~~ ✅ **FAIT le 17/08/2026** (étape 0, voir §10) | — *(aucune dépendance : c'est du calcul pur)* |
| ~~**T3**~~ | ~~TVA 20 % + totaux HT/TTC~~ ✅ **FAIT le 17/08/2026** (`tva.ts`). Reste à **afficher** le TTC dans `/panier`, qui dit encore « TVA calculée à la commande » | T8 |
| **T4** | Enregistrement des commandes (base) + numérotation | §4.2 |
| **T5** | `POST /api/commande` → session Stripe avec les montants **serveur** | T2, T3, compte Stripe |
| **T6** | Webhook Stripe → commande payée, avec protection contre les doublons | T4, T5 |
| **T7** | Email de confirmation au client + notification à Netair | T6, ⚠️ voir §8 |
| **T8** | Pages retour (`merci` / `annulee`) + branchement du bouton du panier | T5 |
| **T9** | Recette de bout en bout en **mode test Stripe** (cartes de test, aucun euro réel) | tout |

**B5 (envoi de la commande dans INCWO)** se branche **après** T6, et pourra réutiliser tout ce qui a
été appris sur l'API INCWO dans DEVIS AUTO (voir BLOC 2 de `PLAN.md` — notamment le piège
`Content-Type: application/xml` strict, et les lignes à créer une par une).

---

## 7. Ce que je ne peux pas faire à votre place

| Action | Pourquoi |
|---|---|
| Créer le compte **Stripe** | Création de compte + coordonnées bancaires — je ne le fais pas |
| Créer les comptes **hébergeur / base de données** | Idem |
| Saisir les **clés secrètes** | Elles ne doivent jamais passer par moi ni être écrites dans le dépôt. Vous les saisissez dans l'interface de l'hébergeur |
| Rédiger et **valider juridiquement** les CGV de vente en ligne | Je peux les **rédiger** (skill `netair-juridique-fr`), mais une relecture professionnelle est recommandée avant mise en ligne |

---

## 8. Réserves et dépendances (à ne pas découvrir en route)

| # | Point | Impact |
|---|---|---|
| 1 | 🔴 **La chaîne Excel → site est rompue** | ⛔ **Verrou de mise en ligne.** On peut tout construire et tout tester, mais **pas vendre pour de vrai** tant que les prix ne sont pas fiabilisés. Voir `PLAN.md` § ALERTE PERMANENTE |
| 2 | 🔴 **Code 17 (NETBAG S) non confirmé** | Des prix réels partent au panier sur une identité présumée. À vérifier **avant** le premier euro encaissé |
| 3 | 🟠 **CGV de vente en ligne inexistantes** | Obligatoires. Case à cocher **non pré-cochée** au moment de payer. À rédiger |
| 4 | 🟠 **Rétractation** | Entre professionnels, dans le cadre de leur activité, elle **ne s'applique pas**. Mais un très petit client achetant hors de son activité principale peut y avoir droit (art. L221-3) → **à faire trancher** par le skill juridique, pas par moi |
| 5 | 🟠 **Envoi des emails** | Le sujet est ⏸️ en attente de votre boîte mail dédiée. **T7 en dépend** — mais T1→T6 peuvent avancer sans |
| 6 | 🟡 **Google Fonts + CDN Tailwind** | Transmettent l'IP des visiteurs hors UE → à auto-héberger avant mise en ligne (déjà consigné) |
| 7 | 🟡 **Branches Git non fusionnées** | `main` est figé au 01/07 ; ~100 commits vivent sur des branches parallèles. À regrouper avant toute mise en production |

---

## 9. Points à trancher (avant de coder)

- [ ] **Hébergement** : Netlify · Cloudflare · Vercel · OVH VPS (§4.1 — recommandation : Netlify ou Cloudflare)
- [ ] **Base de données** : Supabase région UE, ou autre (§4.2)
- [ ] **Périmètre du lancement** : paiement invité seul d'abord, ou attendre les comptes (B4) ?
- [ ] **Acomptes / paiement à la commande** : tout payé d'avance en boutique, ou possibilité de virement pour les gros paniers ?
- [ ] **Numérotation des commandes** : indépendante, ou alignée sur celle d'INCWO (`SO…`) ?
- [ ] **Que fait-on d'une commande boutique dans INCWO** : commande client directe, ou devis à confirmer par vous ?

---

## 10. Étape 0 — réalisée le 17/08/2026

**Livré** : `site/src/lib/commande/` (`types.ts` · `tva.ts` · `offre.ts` · `recalcul.ts`) et
`site/tests/commande/` — **256 tests verts** (dont ~60 neufs), build 34 pages OK.
Aucun fichier existant modifié : le moteur de prix B1 n'a pas été touché.

### La faille fermée — les restrictions d'offre ne vivaient que dans le navigateur

Découverte en écrivant l'étape : `pricing/produits-gammes.ts` retire de la vente des
combinaisons qui restent **tarifées dans l'Excel**, et ces retraits n'étaient appliqués que
par l'**interface**. Un panier fabriqué à la main les achetait donc au prix erroné.

Deux cas prouvés par les tests, sur les erreurs déjà consignées au CHECKLIST :

| Combinaison | Prix rendu par le moteur | Après contrôle d'offre |
|---|---|---|
| NETCEL V AZUR **F8 490×592** | **12,00 €** (au lieu de ~108 € métier) | ❌ refusée |
| NETFIBRE panneau **G3** | **1,51 €** (au lieu de 8,57 €) | ❌ refusée |

`offre.ts` ré-applique côté serveur `classesIncluses`, `classesExclues`, `classesSurDevis`,
les formats standard et les épaisseurs de conditionnement — en **lisant la même source** que
l'interface, sans rien dupliquer.

### Quatre défauts trouvés en revue et corrigés

| Gravité | Défaut | Correction |
|---|---|---|
| **ÉLEVÉ** | Le module **levait une exception** sur charge utile malformée (`lignes` nul, ligne `null`, panier non-objet) — sur un point d'entrée HTTP, c'est une panne offerte au premier venu | Validation défensive : refus propre, jamais d'exception |
| **ÉLEVÉ** | Le serveur **dépendait d'une valeur magique du navigateur** : l'interface envoie une épaisseur neutre de 48 pour les gammes sans épaisseur (`[ref].astro` l. 731). Un client envoyant 0 voyait sa commande **légitime** refusée | Le serveur rétablit lui-même la profondeur neutre, d'après les données |
| **MOYEN** | Une quantité de 1 000 000 000 était acceptée et chiffrée à **19 milliards d'euros** | Plafond `QUANTITE_MAX_LIGNE = 10 000` ⚠️ **à confirmer par PA** (garde-fou technique, pas une règle commerciale) |
| **FAIBLE** | Dimensions en texte / `NaN` / négatives refusées par le moteur, mais avec son vocabulaire interne | Contrôle explicite en amont, message de boutique |

### Deux points laissés ouverts, à traiter au bon moment

1. 🔶 **Le panier actuel ne peut pas encore produire une charge utile valide.**
   `cart.ts` (`CartItem.demande`) mémorise le **code-gamme**, pas le `produitId` ni le
   `varianteId` — or c'est précisément le produit et son conditionnement que le serveur exige,
   puisque le code-gamme seul contournerait les restrictions d'offre. **Le contrat du panier
   est donc à étendre en T8**, au moment de brancher le bouton. Sans ça, rien ne casse
   aujourd'hui (le module n'est appelé nulle part), mais la commande ne partira pas.
2. 🔶 **TVA en Corse** : `tva.ts` applique 20 % partout. À faire confirmer par
   `netair-juridique-fr` qu'aucune catégorie particulière ne s'applique aux filtres —
   ainsi que l'assiette (TVA sur le total **port inclus**, ce qui est implémenté).

### Choix de conception assumés

- **Une ligne fautive fait tomber toute la commande** — jamais de panier amputé en silence :
  le client paierait autre chose que ce qu'il a composé.
- **Département non tarifé → refus de payer.** La page `/panier` laisse passer (elle
  n'encaisse rien) ; le serveur, lui, s'apprête à débiter une carte, et on ne prélève pas sur
  un total inconnu. *(Cas théorique : le menu du panier ne propose que les 96 départements tarifés.)*
- **Le total affiché au client n'entre dans aucun calcul.** Il sert uniquement de contrôle :
  en cas d'écart, refus explicite (« nos tarifs ont changé »), jamais d'alignement silencieux.
