# Système de design Netair — « Precision Blanche » (validé)

Date : 2026-06-23
Statut : **validé par Pierre-Alain** (clôt les points ouverts §3 de la spec fondations)
Spec de référence : `2026-06-22-fondations-site-design.md`
Méthode : produit via le skill `ui-ux-pro-max` (diagnostic « Trust & Authority »)
et le skill `netair-com-fr` (voix « Precision Blanche ») ; décisions tranchées par l'utilisateur.

## Décisions verrouillées

| Sujet | Décision validée |
|---|---|
| **Style** | « Trust & Authority » / « Precision Blanche » : fond blanc dominant, preuve technique, accent parcimonieux, accessibilité AAA. |
| **Typographie** | **Titres : Barlow Condensed** (capitales serrées, esprit ingénieur) · **Corps : Inter**. Auto-hébergées (`@fontsource`), `font-display: swap`, aucun appel Google Fonts externe (perf + RGPD). |
| **Dégradés** | **Halos doux façon « Version 2 »** : très légers halos de couleur en fond de section + dégradé subtil bleu→turquoise sur le bouton principal uniquement. (Lève la contradiction avec la règle « aucun dégradé » : on autorise ces deux usages mesurés, rien d'autre.) |
| **Hero accueil** | **Texte fort à gauche + visuel produit à droite** = **mosaïque de 3 filtres** (un préfiltre, un compact, un HEPA) détourés sur blanc. |

## Couleurs (charte officielle — ne jamais inventer)

| Rôle | Hex | Usage |
|---|---|---|
| Marine | `#0F3261` | Texte, titres, aplats de structure |
| Turquoise | `#0897A5` | Accent : « lame » verticale, liens, repères |
| Bleu | `#0070C8` | Bouton d'action principal (CTA) |
| Blanc | `#FFFFFF` | Fond dominant |
| Gris neutres | (échelle) | Texte secondaire, filets de séparation |

Règle d'usage : beaucoup de blanc, marine pour la lecture, **une seule** touche de turquoise par zone.

## Espacements & rythme

- Grille de base **8 px** (8/16/24/32/48/64…).
- Largeur de contenu max ≈ **1140 px**, centrée, larges marges.
- Rythme vertical strict ; hiérarchie par taille/espace/contraste, pas par couleur.

## Composants

- **Navbar** : logo sur blanc + **lame turquoise verticale** à gauche (remplace l'ancien bandeau bleu) ; nav + CTA « Demander un devis ».
- **Bouton principal** : bleu (dégradé subtil bleu→turquoise autorisé), coins arrondis légers, ombre douce.
- **Carte produit** : fond blanc, fin contour gris, **badge classe** (`ePM1 65% (G4)`), légère élévation au survol (~250 ms).
- **Sections** : titres en **capitales condensées** (Barlow Condensed) précédés d'un repère turquoise.

## Animations

- Discrètes et porteuses de sens : fondu au défilement, survol des cartes, soulignés tracés.
- Durées **150–300 ms**, easing `ease-out` à l'entrée.
- `prefers-reduced-motion` respecté (accessibilité).

## Tokens Tailwind (à implémenter en Phase 3)

```js
// tailwind.config.mjs (extrait)
colors: {
  marine:    '#0F3261',
  turquoise: '#0897A5',
  bleu:      '#0070C8',
  blanc:     '#FFFFFF',
},
fontFamily: {
  display: ['Barlow Condensed', 'sans-serif'], // titres
  body:    ['Inter', 'sans-serif'],            // corps
},
```

## Arborescence retenue

```
/                      Accueil (hero mosaïque + preuves + gammes + pourquoi + CTA)
/gammes                Vue d'ensemble des 7 familles
/gammes/[famille]      prefiltres · filtres-plans · poches-souples · compacts · hepa · charbon-actif · combines
/produits/[ref]        Page produit (synthèse, specs lues du JSON, lien fiche technique)
/a-propos              Raison d'être · modèle · engagements (dont NETPAK S LUMEN / RSE)
/contact               Demande de devis (formulaire minimal RGPD)
/mentions-legales      via netair-juridique-fr
/confidentialite       via netair-juridique-fr
```

## Textes validés

Les textes rédactionnels (hero, sections accueil, descriptifs des 7 familles, gabarit
page produit, à propos, contact) ont été rédigés à la voix « Precision Blanche » et
**validés**. Ils sont la source pour l'intégration. Règle absolue : **aucun chiffre
technique écrit à la main** — les valeurs produits sont lues depuis les `*.json`.
