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

## FAMILLES

> Textes des pages d'ouverture de famille, propres à la plaquette (le site garde les siens,
> dans site/src/lib/familles.ts). Clé = identifiant de la famille ; une famille absente
> d'ici reprend le texte du site.

prefiltres:
Les préfiltres retiennent les particules grossières et protègent les équipements de ventilation ainsi que les étages de filtration situés en aval. Selon les besoins de l’installation, ils peuvent également être utilisés comme unique étage de filtration.

NETAIR propose des préfiltres plissés, plans, métalliques, cousus sur fil et des médias filtrants, en dimensions standard ou sur mesure, adaptés aux centrales de traitement d’air, aux réseaux de ventilation et aux ventilo-convecteurs.

---

## NORMES

titre: Lire une classe d'efficacité
intro:
Depuis juillet 2018, la norme EN ISO 16890 remplace l’ancienne norme EN 779 pour la classification des filtres de ventilation générale. Elle évalue leur efficacité de filtration sur différentes fractions de particules en suspension dans l’air : PM10, PM2,5 et PM1.

Les filtres sont classés selon leur efficacité mesurée, exprimée en pourcentage. Les catégories ISO ePM10, ISO ePM2,5 et ISO ePM1 correspondent à une efficacité minimale de 50 % pour la fraction de particules considérée.

Dans ce catalogue, les classes EN ISO 16890 sont indiquées en priorité, accompagnées des anciennes désignations EN 779 à titre indicatif. Les filtres à très haute efficacité sont classés séparément selon la norme EN 1822 (EPA, HEPA et ULPA).

entete_tableau: Catégorie | Particules visées | Anciennes classes EN 779 (indicatif)
tableau:
ISO Coarse | Particules grossières | G1 à G4
ISO ePM10 | Particules ≤ 10 µm | M5
ISO ePM2,5 | Particules ≤ 2,5 µm | M6
ISO ePM1 | Particules ≤ 1 µm | F7 à F9

entete_tres_haute: Norme | Domaine | Classes EN 1822
tableau_tres_haute:
EN 1822 | Filtration à très haute efficacité | E10 à U17

note_tableau:
Les correspondances entre les anciennes classes EN 779 et les classes EN ISO 16890 sont données à titre indicatif. Seuls les résultats d’essais réalisés selon la norme EN ISO 16890 permettent de déterminer la classe d’efficacité réelle d’un filtre.

encadre:
Le choix d’un filtre doit tenir compte de la qualité de l’air extérieur, des exigences de qualité de l’air intérieur et des caractéristiques de l’installation. Pour la filtration fine, les filtres ISO ePM1 ≥ 50 % constituent une solution couramment utilisée.

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
