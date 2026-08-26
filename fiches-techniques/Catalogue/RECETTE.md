# Catalogue produits Netair — mode d'emploi et recette

## En une phrase

**Tout ce qui décrit un produit ou une famille est lu ; seuls la couverture, l'édito,
la page normes et la 4ᵉ de couverture sont écrits à la main.**

## Les trois sources

| Source | Ce qu'elle apporte | Qui la modifie |
|---|---|---|
| `../Generateur/produits/*.json` | nom, sous-titre, descriptif, points clés, caractéristiques, photo, badges de normes, n° et version de fiche, **coefficients de perte de charge** | la passe de contenu produit — **les mêmes fichiers que les 18 fiches techniques** |
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
descriptif de plus de 760 caractères, plus de 9 points clés, plus de
18 caractéristiques. Limites mesurées sur le gabarit ; le plus long descriptif
actuel, NETCARB AZUR, tient à 752 caractères — la marge est mince. Il signale
aussi deux courbes qui porteraient la même étiquette.

## Les courbes de perte de charge

Chaque page produit porte sa courbe **débit / perte de charge**, **toutes classes
confondues**, tracée à partir des mêmes polynômes que la fiche technique.
`lecture_courbes.py` importe `force_origin` et `AREF` du générateur de fiches : il
n'y a pas deux physiques, donc les deux documents ne peuvent pas diverger. Vérifié
en comparant la perte de charge nominale calculée à celle inscrite dans chaque
fiche — **écart maximal 1,23 Pa sur 20 courbes**, soit l'arrondi des entiers
stockés.

Les fiches rangent leurs courbes de trois façons différentes selon les produits
(`classes`, `courbes`+`series`, `classes_list`+`multi_classe`) ; le module les
ramène à une forme unique. De 1 courbe (NETPLAN) à 10 (NETBAG S, NETPAK S CILIA).

**Fusion des doublons.** Sur la plupart des produits, les deux « épaisseurs » du
gabarit portent le même polynôme : les tracés identiques sont réunis en un seul,
dont l'étiquette rassemble les classes et épaisseurs concernées (« G2 / G3 ·
48 mm »). Deux traits superposés n'apprendraient rien.

**Couleurs.** Reprises des JSON quand ils en portent (NETBAG S en définit dix) ;
sinon une palette de repli tirée de ces mêmes teintes. Aucune couleur inventée.

**Légende.** Deux lignes par entrée jusqu'à 4 courbes, une seule ligne au corps
ajusté au-delà — une étiquette comme « F9 + charbon actif · 520 mm » ne tient pas
sur une ligne à côté de sa valeur.

⚠️ **Piège à connaître.** Les clés « 48 » et « 98 » des polynômes sont une
convention interne du gabarit des fiches, pas toujours des millimètres réels :
NETPLAN se décline de 8 à 25 mm, NETFIL fait 4,5 mm, NETCEL V LAM 68 mm.
L'épaisseur affichée vient du champ `epaisseur` de la classe quand il existe, et
seulement à défaut de la clé. De même, NETCEL V LAM a une surface frontale à lui
(`aref` 0,3721 m² au lieu de 0,3505) : la conversion vitesse → débit la respecte.

**Contrôle d'étiquettes.** Deux courbes différentes ne doivent jamais porter le
même nom, sinon le lecteur ne sait pas laquelle est laquelle. Quand ça arrive, le
générateur les départage par la clé brute du JSON **et le signale**. Un cas
aujourd'hui : NETCARB CILIA déclare une épaisseur unique de 48 mm mais porte deux
polynômes distincts — à trancher lors de sa passe de contenu.

## Liens cliquables

Le sommaire, les pages de gamme et le tableau de synthèse renvoient directement à
la page du produit. Ce sont de vrais liens internes au PDF, invisibles à
l'impression. Pour vérifier qu'ils ont bien survécu à l'export :

```bash
python3 -c "d=open('Catalogue_Netair.pdf','rb').read(); print(d.count(b'/Link'), 'liens')"
```

## Compteurs automatiques

Dans les textes de `contenu_catalogue.md`, `{nb_produits}`, `{nb_familles}` et
`{date_edition}` sont remplacés à la génération. Ne jamais écrire ces nombres en
toutes lettres : le jour où un 19ᵉ filtre arrive, la phrase se corrige toute seule.

## Points ouverts

- **Photos** : le catalogue prend en priorité la version **détourée** publiée par
  le site (`site/public/produits/detour/`, fond transparent), et retombe sur la
  photo d'origine sinon — les 4 NETCARB n'ont pas encore de détourage. Le cadre
  photo est **blanc et non gris** : la moitié des images ont elles-mêmes un fond
  blanc, qui dessinait un rectangle visible sur un fond de carte gris.
  Ce sont toujours des images de travail, et trois servent à plusieurs produits
  (vérifié par empreinte) — `NETCEL V LAM` = `NETPAK S CILIA` = `NETPAK S DUO`,
  `NETCEL V AZUR` = `NETPAK S AZUR`, `NETBAG S` = `NETCARB BAG`. À remplacer avant
  diffusion, sans aucune modification de code.
- **Numéro de TVA** volontairement absent : il est calculé et non confirmé, et
  n'est pas obligatoire sur un catalogue.
- **Téléphone** volontairement absent (décision du 15/07/2026).
