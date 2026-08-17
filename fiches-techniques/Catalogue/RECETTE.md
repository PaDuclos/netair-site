# Catalogue produits Netair — mode d'emploi et recette

## En une phrase

**Tout ce qui décrit un produit ou une famille est lu ; seuls la couverture, l'édito,
la page normes et la 4ᵉ de couverture sont écrits à la main.**

## Les trois sources

| Source | Ce qu'elle apporte | Qui la modifie |
|---|---|---|
| `../Generateur/produits/*.json` | nom, sous-titre, descriptif, points clés, caractéristiques, photo, badges de normes, n° et version de fiche | la passe de contenu produit — **les mêmes fichiers que les 18 fiches techniques** |
| `../../site/src/lib/familles.ts` | noms des familles, textes de présentation, rattachement des produits, ordre | le site vitrine |
| `contenu_catalogue.md` | couverture, édito, page « Lire une classe d'efficacité », 4ᵉ de couverture | **toi — c'est le seul fichier manuel** |

Rien n'est recopié d'une source à l'autre. Une donnée corrigée dans un JSON produit
apparaît dans le catalogue **et** dans la fiche technique à la régénération suivante.

## Régénérer

```bash
python3 generer_catalogue.py
```

Produit `Catalogue_Netair.html` et `Catalogue_Netair.pdf` (30 pages A4 portrait).
Le PDF est imprimé par Google Chrome sans fenêtre : même moteur d'affichage que
l'aperçu à l'écran, donc aucune surprise entre les deux.

Pour aligner aussi les fiches techniques :

```bash
python3 ../Generateur/generer_tous.py
```

## La recette — à rejouer après chaque passe de contenu

Elle répond à une seule question : **la plaquette se régénère-t-elle vraiment, ou
faut-il la retoucher ?**

1. Modifier une valeur dans un fichier produit, par exemple
   `../Generateur/produits/netcarb-cilia.json`.
2. Régénérer :
   ```bash
   python3 generer_catalogue.py && python3 ../Generateur/generer_tous.py
   ```
3. Vérifier que la nouvelle valeur est **dans le HTML** :
   ```bash
   grep -c "la nouvelle valeur" Catalogue_Netair.html
   ```
4. Vérifier qu'elle est **dans le PDF** — le texte est réellement extrait du PDF,
   il n'est pas cru sur parole :
   ```bash
   pdftotext Catalogue_Netair.pdf - | grep -c "la nouvelle valeur"
   ```
5. Vérifier que la **fiche technique** porte la même valeur :
   ```bash
   grep -c "la nouvelle valeur" "../Fiches_Netair/Fiche technique NETCARB CILIA.html"
   ```
6. Vérifier que **l'ancienne valeur a disparu** du PDF :
   ```bash
   pdftotext Catalogue_Netair.pdf - | grep -c "l'ancienne valeur"   # doit afficher 0
   ```

Les étapes 3 à 6 doivent toutes réussir **sans aucune retouche manuelle**.
`pdftotext` vient de poppler (`brew install poppler`).

### Résultat du 17/08/2026

Joué sur NETCARB CILIA, en modifiant trois valeurs à la fois (sous-titre,
caractéristique « Capacité d'adsorption », premier point clé) :

| Contrôle | Résultat |
|---|---|
| Nouvelles valeurs dans le HTML du catalogue | ✅ 3 / 3 |
| Nouvelles valeurs dans le texte extrait du PDF | ✅ 3 / 3 |
| Mêmes valeurs dans la fiche technique NETCARB CILIA | ✅ 3 / 3 |
| Ancien sous-titre encore présent dans le PDF | ✅ 0 occurrence |
| Retouches manuelles nécessaires | ✅ aucune |

Les valeurs de test ont ensuite été retirées : `git diff` sur le fichier produit
est vide.

## Ce que le générateur refuse de faire

Il s'arrête avec une erreur claire plutôt que de sortir un document faux :

- un produit dont un champ attendu manque ou est vide ;
- un produit dont la photo est introuvable ;
- un produit présent dans `produits/` mais rattaché à aucune famille dans
  `familles.ts` — **un produit ne peut pas disparaître du catalogue en silence**,
  ce qui arriverait sinon au premier filtre ajouté à la gamme ;
- un bloc absent de `contenu_catalogue.md` ;
- `familles.ts` devenu illisible (changement de forme du fichier).

Il **prévient** sans s'arrêter quand un produit risque de déborder de sa page :
descriptif de plus de 760 caractères, plus de 6 points clés, plus de
14 caractéristiques. Limites mesurées sur le gabarit ; le plus long descriptif
actuel, NETCARB AZUR, tient à 752 caractères — la marge est mince.

## Compteurs automatiques

Dans les textes de `contenu_catalogue.md`, `{nb_produits}`, `{nb_familles}` et
`{date_edition}` sont remplacés à la génération. Ne jamais écrire ces nombres en
toutes lettres : le jour où un 19ᵉ filtre arrive, la phrase se corrige toute seule.

## Points ouverts

- **Photos** : ce sont encore les images de travail des fiches techniques. Trois
  d'entre elles servent à plusieurs produits (vérifié par empreinte) —
  `NETCEL V LAM` = `NETPAK S CILIA` = `NETPAK S DUO`, `NETCEL V AZUR` =
  `NETPAK S AZUR`, `NETBAG S` = `NETCARB BAG`. À remplacer avant diffusion.
  Aucune modification de code ne sera nécessaire : le catalogue lit le champ
  `photo` du JSON.
- **`www.netair.fr`** figure en 4ᵉ de couverture : à retirer de
  `contenu_catalogue.md` tant que le site n'est pas en ligne.
- **Numéro de TVA** volontairement absent : il est calculé et non confirmé, et
  n'est pas obligatoire sur un catalogue.
- **Téléphone** volontairement absent (décision du 15/07/2026).
