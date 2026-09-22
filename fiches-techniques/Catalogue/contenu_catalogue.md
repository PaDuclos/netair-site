# Contenu manuel du catalogue Netair

> **C'est le SEUL fichier de ce dossier à modifier à la main.**
>
> Tout ce qui décrit un produit (nom, sous-titre, descriptif, points clés, specs,
> photo, normes) est lu dans `Generateur/produits/*.json`. Tout ce qui décrit une
> famille (titre, texte de présentation, ordre, rattachement des produits) est lu
> dans `site/src/lib/familles.ts`. Ni l'un ni l'autre ne se recopie ici.
>
> Après modification : `python3 generer_catalogue.py`
>
> **Format.** Un bloc commence par `## NOM_DU_BLOC`. À l'intérieur, une ligne
> `cle: valeur` ouvre un champ ; les lignes suivantes s'y ajoutent jusqu'au champ
> suivant. Les noms de champs sont toujours en minuscules avec des underscores —
> une ligne de texte qui commence par une majuscule ne risque donc jamais d'être
> prise pour un champ.
>
> **Compteurs automatiques.** Dans n'importe quel texte, `{nb_produits}`,
> `{nb_familles}` et `{date_edition}` sont remplacés à la génération. Ne jamais
> écrire ces nombres en toutes lettres : le jour où un 19e filtre arrive, la
> phrase se corrigerait toute seule.

---

## COUVERTURE

titre: Filtration de l'air
sous_titre: Catalogue produits
accroche: L'air propre, notre engagement
photo: couverture-montagne.jpg
mention_bas: Édition du {date_edition} · {nb_produits} références

---

## EDITO

titre: Netair en quelques lignes
photo: ambiance-foret.jpg
texte:
Netair conçoit et fournit des filtres pour les centrales de traitement d'air.

La gamme couvre les étages de filtration, du préfiltre métallique lavable aux
filtres absolus, avec les filtres à charbon actif pour le traitement des gaz et
des odeurs. {nb_produits} références réparties en {nb_familles} familles, en
dimensions standard ou sur mesure.

Chaque référence dispose d'une fiche technique : composition, classes
d'efficacité selon EN ISO 16890 et EN 779, courbe de perte de charge et
calculateur de consommation énergétique.

Les devis sont établis au cas par cas, sur dimensions et classes réelles.
Livraison par transporteur.

signature: Pierre-Alain Duclos — Président

---

## NORMES

titre: Lire une classe d'efficacité
intro:
Depuis juillet 2018, la norme EN ISO 16890 remplace l'EN 779. Elle classe les
filtres selon leur efficacité sur les particules en suspension (PM10, PM2,5,
PM1) plutôt que sur un essai à poussière synthétique. Un filtre relève d'une
catégorie s'il retient au moins 50 % des particules de la taille considérée.

Dans ce catalogue, la classe EN ISO 16890 est toujours donnée en premier, la
classe EN 779 entre parenthèses ou en second. Les filtres absolus relèvent d'une
troisième norme, l'EN 1822, et se désignent par leur classe seule (E10, H13, H14).

tableau:
ISO Coarse | Poussières grossières (> 10 µm) | G1 · G2 · G3 · G4
ISO ePM10 | Particules ≤ 10 µm — pollens, spores | M5
ISO ePM2,5 | Particules ≤ 2,5 µm — bactéries, fumées | M6
ISO ePM1 | Particules ≤ 1 µm — suies, particules de combustion | F7 · F8 · F9
EN 1822 | Filtres absolus — essai au MPPS | E10 · H13 · H14

note_tableau:
Équivalences EN 779 données à titre indicatif (Eurovent · AICVF · VDI). Pour un
produit disposant d'un procès-verbal d'essai EN ISO 16890, c'est l'efficacité
réellement mesurée qui fait foi.

encadre:
Pour la protection des occupants, la référence usuelle est une efficacité
ePM1 ≥ 50 %, soit l'équivalent d'un ancien F7.

---

## DOS

titre: Netair
accroche: L'air propre, notre engagement
texte:
Filtres pour centrales de traitement d'air.
Standard et sur mesure, sur devis.

adresse: 142 Route du Tilleul — 69270 Cailloux-sur-Fontaines
email: contact@netair.fr
site: www.netair.fr
mentions: SASU au capital de 1 000 € · SIREN 107 397 648 R.C.S. Lyon · APE 28.25Z
pied: Document non contractuel. Les caractéristiques peuvent évoluer sans préavis. Édition du {date_edition}.
