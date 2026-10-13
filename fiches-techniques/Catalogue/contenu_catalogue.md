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

titre: NETAIR, l’expertise de la filtration de l’air
photo: ambiance-foret.jpg
texte:
Créée en 2026 par Pierre-Alain Duclos, fort de plus de 20 ans d’expérience dans la filtration de l’air, NETAIR est une entreprise implantée à Miribel, près de Lyon, spécialisée dans la conception et la fabrication de filtres pour les installations de ventilation et de traitement d’air.

Notre gamme couvre l’ensemble des besoins de filtration, du préfiltre au filtre absolu, en passant par les filtres à poches, les filtres à charbon actif et les solutions combinées. Nos produits sont disponibles en dimensions standard ou sur mesure.

Notre approche repose sur une conviction : une filtration performante doit associer qualité de l’air, efficacité énergétique et maîtrise des coûts d’exploitation.

Au-delà de la fourniture de filtres, NETAIR accompagne ses clients dans le choix et l’optimisation de leurs solutions de filtration, avec une attention particulière portée à la réduction des consommations d’énergie et de l’empreinte environnementale.

Chaque référence dispose d’une fiche technique détaillée permettant d’en connaître les caractéristiques et les performances. Nos propositions sont établies en fonction des besoins spécifiques de chaque installation.

Proximité, réactivité et conseil technique sont au cœur de notre engagement.

signature: Pierre-Alain Duclos, dirigeant

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
ISO ePM10 | Particules ≤ 10 µm · pollens, spores | M5
ISO ePM2,5 | Particules ≤ 2,5 µm · bactéries, fumées | M6
ISO ePM1 | Particules ≤ 1 µm · suies, particules de combustion | F7 · F8 · F9
EN 1822 | Filtres absolus · essai au MPPS | E10 · H13 · H14

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

adresse: Parc d'activité des Chênes, Route de Tramoyes, 01700 Miribel
telephone: 04 82 53 37 17
email: contact@netair.fr
site: www.netair.fr
mentions: SASU au capital de 1 000 € · SIREN 107 397 648 R.C.S. Lyon · APE 28.25Z
pied: Document non contractuel. Les caractéristiques peuvent évoluer sans préavis. Édition du {date_edition}.
