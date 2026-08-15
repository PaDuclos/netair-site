/**
 * Pont produit du site → code-prix du moteur (Bloc B2).
 *
 * Le site présente des PRODUITS par identifiant (`netply`, `netbag-s`…) issus des
 * fiches techniques (`lib/familles.ts`). Le moteur de prix, lui, raisonne par
 * CODE-GAMME des tables Excel (`"1"` = NETPLY, `"3"` = NETPLAN…). Ce fichier est le
 * seul endroit qui relie les deux mondes.
 *
 * Pourquoi une table écrite à la main (et non devinée par le nom) :
 *  - les codes-gamme NE SONT PAS FIGÉS (le calculateur sera retravaillé, des filtres
 *    ajoutés/retirés) → un appariement par nom serait fragile ;
 *  - certains noms existent en plusieurs codes (NETBAG S = 11 ou 17, NETFIBRE = 4 ou 5)
 *    → seul un choix humain validé tranche.
 * À chaque retravail de l'Excel, on revérifie cette table (et les tests de conformité).
 *
 * `mode` pilote le comportement de la page produit :
 *  - `"calcul"` → prix instantané (la page appelle `calculerPrix`) ;
 *  - `"devis"`  → pas de prix public (gamme « hors calculateur ») : seul le parcours
 *    « demande de devis » est actif. La page et le configurateur restent identiques.
 */

/** Mode de commercialisation d'un produit sur la boutique. */
export type ModeProduit = "calcul" | "devis";

/**
 * Cadres/matières → suffixe dans la référence générée (ex. NETPLY-G4-592x592x48-A).
 * SOURCE DE VÉRITÉ UNIQUE : la page produit et les tests lisent cette table, personne ne
 * recopie la correspondance à la main.
 *
 * Ajouter un matériau (cellulose, polyester…) = trancher d'abord son suffixe côté codification
 * produits, puis l'ajouter ICI. Un cadre absent de cette table est signalé par `CadreValeur`
 * dans l'éditeur et refusé par `tests/pricing/produits-gammes.test.ts` (le build ne
 * type-check pas) : il ne peut pas perdre son suffixe en silence.
 *
 * ⚠️ Provisoire : la composition des codes articles est SUSPENDUE depuis le 16/07/2026 (cf.
 * l'encadré de `CODIFICATION_PRODUITS.md` et CHECKLIST « RÉFÉRENCES PRODUIT — À TRANCHER AVANT
 * INCWO »). Ces suffixes sont validés pour le configurateur, pas gravés pour Incwo.
 *
 * NETMETAL = 2 lettres [cadre][tricot] (A = acier galvanisé, L = aluminium, I = inox 304),
 * décision PA du 17/07/2026 : le produit se vend par couple cadre+tricot, pas par matériau seul.
 */
export const CADRE_SUFFIXE = {
  galva: "A",
  pp: "P",
  cellulose: "C",
  acier_acier: "AA",
  acier_alu: "AL",
  inox_inox: "II",
} as const;

/** Valeur de cadre autorisée — dérivée de `CADRE_SUFFIXE`, jamais réécrite à la main. */
export type CadreValeur = keyof typeof CADRE_SUFFIXE;

/** Un cadre proposé au client dans le configurateur. */
export interface CadreOffre {
  valeur: CadreValeur;
  /** Libellé affiché, repris de la fiche (« Acier galvanisé », « Plastique »…). */
  libelle: string;
}

/** Un format de rouleau fixe (dimensions dans l'unité des tables, ici en mètres). */
export interface FormatRouleau {
  /**
   * Libellé affiché, en LONGUEUR × LARGEUR — ex. "20 m × 2 m" (décision PA 17/07/2026) :
   * un rouleau se dit par sa longueur déroulée, puis sa laize.
   *
   * ⚠️ L'ordre du libellé est INDÉPENDANT de `largeur`/`hauteur` ci-dessous, qui sont les
   * entrées du moteur : les intervertir changerait le prix. Le libellé alimente aussi le
   * suffixe de référence (ex. NETFIBRE-G4-20m×2m).
   */
  label: string;
  /** Petit côté / laize (passé tel quel au moteur — l'unité est celle de la table). */
  largeur: number;
  /** Grand côté / longueur déroulée (idem). */
  hauteur: number;
  /** Format pré-sélectionné à l'ouverture. À défaut, le premier de la liste. */
  defaut?: boolean;
  /**
   * Cadres réellement fabriqués DANS CE FORMAT, quand ils ne sont pas tous disponibles
   * partout (ex. NETCEL V NIVAL : les cadres 592 n'existent qu'en acier galvanisé, les 610
   * dans les deux matières). Sous-ensemble des `cadres` du produit. Absent = tous.
   *
   * ⚠️ Le cadre n'entre PAS dans le calcul du prix (cf. NETBAG S) : cette liste ne sert
   * qu'à ne pas laisser commander une combinaison qui n'existe pas.
   */
  cadres?: CadreValeur[];
}

/**
 * Variante d'un même produit qui change de gamme tarifaire ET/OU de mode de saisie.
 * Ex. NETFIBRE : « Panneau » (saisie de dimensions L×H, code 4) vs « Rouleau »
 * (choix parmi des formats fixes, code 5). Les deux sont vendus sur la même page.
 */
export interface VarianteProduit {
  /** Identifiant court — ex. "panneau", "rouleau". */
  id: string;
  /** Libellé du conditionnement affiché dans le sélecteur. */
  label: string;
  /** Code-gamme tarifaire de cette variante. */
  code: string;
  /** Mode de saisie : dimensions libres (mm) ou choix d'un format fixe. */
  saisie: "dimensions" | "formats";
  /**
   * Formats proposés quand `saisie === "formats"`. Si absent, ils sont générés
   * automatiquement depuis la grille tarifaire du code (dimensions standard).
   */
  formats?: FormatRouleau[];
  /**
   * Base de la référence générée pour CETTE variante, quand elle diffère du nom du produit.
   * Ex. recharges LUMEN : « Recharge_NETPAK_S_LUMEN » (format technique à tirets bas, déc. PA
   * 02/08/2026) — sans elle, une recharge F7 592×592 serait indiscernable d'un filtre complet
   * au panier.
   */
  refBase?: string;
  /**
   * Cette variante n'a PAS de cadre, même si le produit en déclare un (`cadreFixe`/`cadres`).
   * Ex. recharge LUMEN : cassettes seules, le support est justement ce que le client conserve
   * (déc. PA 02/08/2026) — le champ « Cadre » est masqué et la ligne de panier ne le cite pas.
   */
  sansCadre?: boolean;
  /**
   * Épaisseurs propres à cette variante, quand elles diffèrent de la grille tarifaire.
   * Ex. NETBAG S : la variante « standard » ne propose que les longueurs de poche à la fois
   * MESURÉES (courbe sur la fiche) et TARIFÉES — 380 et 550 — tandis que la variante
   * « sur mesure », qui part en devis, ouvre les 4 longueurs annoncées par la fiche.
   */
  epaisseurs?: number[];
  /**
   * Présente les formats du plus grand au plus petit : le premier de la liste est
   * la sélection par défaut, et le cadre plein format (ex. 592×592) est le cas
   * d'usage courant. Les dimensions restent lues dans la grille tarifaire.
   */
  formatsGrandDabord?: boolean;
  /**
   * Format pré-sélectionné à l'ouverture, désigné par ses dimensions (l'ordre des deux
   * valeurs est indifférent). Utile quand les formats viennent de la grille tarifaire et
   * ne peuvent donc pas porter `defaut` : sur un laminaire, le module de plafond 610×610
   * est le cas d'usage courant, alors qu'il tombe au milieu d'une liste de 17 formats.
   * Un format introuvable dans la grille lève à la construction de la page.
   */
  formatDefaut?: { largeur: number; hauteur: number };
  /** Libellé du menu de formats (défaut « Dimensions »). Ex. « Format de rouleau ». */
  labelChamp?: string;
}

/** Lien d'un produit du site vers sa gamme tarifaire. */
export interface GammeProduit {
  /** Code-gamme tel qu'il figure dans `tables.json` (chaîne, jamais comparée comme un nombre). */
  code: string;
  /** `calcul` = prix instantané ; `devis` = demande de devis seule. */
  mode: ModeProduit;
  /**
   * Conditionnements multiples (optionnel). Présent quand un même produit se vend
   * sous plusieurs gammes tarifaires (ex. NETFIBRE panneau vs rouleau). Le configurateur
   * affiche alors un sélecteur « Conditionnement » ; `code`/`mode` ci-dessus = la variante par défaut.
   */
  variantes?: VarianteProduit[];
  /**
   * Classes d'efficacité à NE PAS proposer sur la boutique pour ce produit, même si
   * elles figurent (peut-être par erreur) dans les tables tarifaires. Décision d'offre,
   * pas une logique moteur : la correction définitive d'un tarif douteux se fait à la
   * source (Excel) après vérification R&D. Voir `fiches-techniques/CHECKLIST.md`.
   */
  classesExclues?: string[];
  /**
   * ── Cadre : 3 cas EXCLUSIFS, à trancher produit par produit d'après sa fiche ──
   * Chaque filtre est différent : ne jamais généraliser d'un produit à l'autre (décision PA).
   *
   *  1. `cadres`     → le client CHOISIT (menu). Ex. NETPAK S CILIA acier OU plastique,
   *                    NETMETAL cadre+tricot. Réservé aux vrais choix commerciaux.
   *  2. `cadreFixe`  → cadre réel mais IMPOSÉ : affiché en information, non modifiable.
   *                    Ex. NETPLY / NETPLAN = acier galvanisé. Alimente quand même le suffixe
   *                    de référence (le cadre existe, il n'est simplement pas au choix).
   *  3. `sansCadre`  → RIEN à afficher : pas de cadre à offrir (média seul, ex. NETFIBRE ;
   *                    média cousu sur armature intégrée, ex. NETFIL) ou parois fixes non
   *                    vendues comme telles (NETCEL V LAM aluminium, NETCEL V AZUR polyester).
   *
   * Un produit `mode: "calcul"` DOIT en déclarer exactement un — il n'y a pas de cadre par
   * défaut. Invariant vérifié par `tests/pricing/produits-gammes.test.ts`.
   */
  sansCadre?: boolean;
  /**
   * Cadre unique imposé : affiché en lecture seule, jamais en menu (cas 2 ci-dessus).
   * Un menu à une seule option ferait croire à un choix qui n'existe pas.
   */
  cadreFixe?: CadreOffre;
  /**
   * Libellé du champ (défaut « Cadre »). Ex. NETMETAL vend un couple cadre + tricot :
   * le mot juste est « Matière ».
   */
  labelCadre?: string;
  /**
   * Cadres réellement AU CHOIX du client (cas 1 ci-dessus), alignés sur la ligne « Cadre » /
   * « Parois cellule » de la fiche. Un cadre unique n'est pas un choix : utiliser `cadreFixe`.
   *
   * Il n'y a volontairement PAS de cadre par défaut. Un défaut « acier + polypropylène » a
   * longtemps servi de repli et n'était juste que pour 2 produits sur 18 — il faisait proposer
   * en silence des cadres inexistants (NETFIL en polypropylène…) et générait des références
   * fantômes.
   *
   * `valeur` est contrainte par `CADRE_SUFFIXE` : un matériau sans suffixe de référence
   * tranché (cellulose, polyester…) est rejeté par les tests.
   */
  cadres?: CadreOffre[];
  /**
   * Liste blanche d'efficacités : si présente, SEULES ces classes sont proposées
   * (ex. laminaire verrouillé sur H14). Appliquée avant `classesExclues`.
   */
  classesIncluses?: string[];
  /**
   * Épaisseurs à proposer pour un produit EN « sur devis » (qui n'a pas de tarif d'où
   * les déduire). Permet de capturer l'épaisseur dans la demande de devis (ex. BORA = 100 mm).
   * Stopgap : à terme l'épaisseur vient du calculateur. Cf. CHECKLIST.
   */
  epaisseursDevis?: number[];
  /**
   * Épaisseur pré-sélectionnée à l'ouverture (défaut : la première du menu).
   *
   * L'ordre du menu est croissant, pour la lisibilité — il ne dit donc rien de l'épaisseur
   * la plus vendue. Sans ce réglage, un client qui ne touche pas au menu demanderait un devis
   * sur la plus fine par simple inertie. Ex. NETMETAL = 25 mm (décision PA 17/07/2026).
   */
  epaisseurDefaut?: number;
  /**
   * Libellé du champ d'épaisseur (défaut « Épaisseur »). Sur un filtre à poches, la dimension
   * en jeu est la LONGUEUR de poche (jusqu'à 650 mm) : « Épaisseur » serait impropre.
   */
  labelEpaisseur?: string;
  /**
   * Efficacités (EN 779) à proposer pour un produit EN « sur devis », pour que le client
   * précise son besoin de filtration dans la demande de prix (ex. BORA = G4→F9).
   * Stopgap : à terme elles viennent du calculateur. Cf. CHECKLIST.
   */
  efficacitesDevis?: string[];
  /**
   * Classes que la FICHE annonce mais que la grille tarifaire ne couvre pas (ex. NETBAG S :
   * G4 et M5 ont des courbes mesurées, pas de prix). Ajoutées au menu d'un produit
   * calculable : le moteur répond `classe_indisponible`, donc aucun prix n'est affiché, et
   * le client peut malgré tout l'ajouter à sa demande de devis. Sans elles, la fiche
   * annoncerait une classe que la boutique ne saurait même pas nommer.
   */
  classesSurDevis?: string[];
  /**
   * Étiquette ISO 16890 propre au produit, par classe EN 779 (libellé complet affiché).
   * Prime sur la table ISO globale de l'Excel quand le média du produit a une efficacité
   * différente (ex. BORA : média spécial → « ePM1 50 % (F7) » là où la table globale
   * dit 55 %). La fiche technique fait foi (décision PA 18/07/2026).
   */
  etiquettesIso?: Record<string, string>;
  /**
   * Dimensions L×H ouvertes par défaut dans le configurateur. Utile pour les produits
   * dont la grille tarifaire ne couvre pas le 592×592 générique (ex. laminaire = formats
   * standard) : on ouvre alors sur une dimension réellement tarifée plutôt que sur un
   * « hors fabrication ». Absent → 592×592.
   */
  dimensionDefaut?: { largeur: number; hauteur: number };
}

/**
 * Correspondance produit → gamme tarifaire, validée par Pierre-Alain le 30/06/2026.
 *
 * 🟢 = code certain · 🟠 = à reconfirmer au déploiement (deux codes portent le même nom).
 * Les produits `devis` n'ont pas besoin d'un code pour fonctionner (la page n'appelle
 * pas le moteur) ; le code est renseigné quand il existe, à titre informatif.
 */
export const GAMME_PRODUIT: Record<string, GammeProduit> = {
  // — Calculables (prix instantané) —
  // 🟢 plissé / plan, méthode A · cadre acier galvanisé IMPOSÉ : affiché, pas au choix (PA 17/07)
  netply: { code: "1", mode: "calcul", cadreFixe: { valeur: "galva", libelle: "Acier galvanisé" } },
  netplan: { code: "3", mode: "calcul", cadreFixe: { valeur: "galva", libelle: "Acier galvanisé" } },
  // 🟢 mètre linéaire, méthode B · pas de cadre à choisir : le média est cousu sur une simple
  // armature en fil d'acier galvanisé Ø 4,5 mm, qui fait partie du produit (décision PA 17/07).
  netfil: { code: "2", mode: "calcul", sansCadre: true },
  // NETFIBRE se vend en 2 conditionnements (Option B) : panneau découpé sur mesure
  // (code 4, méthode C, prix au dm²) ou rouleau entier (code 5, méthode E, prix par format).
  netfibre: {
    code: "4",
    mode: "calcul",
    // G3 retiré de l'offre : tarif 0,015 €/dm² jugé erroné (5,7× moins cher que G4) → CHECKLIST R&D.
    classesExclues: ["G3"],
    // NETFIBRE = média fibreux seul, sans cadre → pas de choix de cadre.
    sansCadre: true,
    variantes: [
      { id: "panneau", label: "Panneau découpé sur mesure", code: "4", saisie: "dimensions" },
      {
        id: "rouleau",
        label: "Rouleau entier",
        code: "5",
        saisie: "formats",
        labelChamp: "Format de rouleau",
        // Un SEUL format pour le moment (déc. PA 17/07) : le 20 m × 2 m, celui qu'annonce la
        // fiche. Les 4 autres (10×1, 20×1, 10×2, 30×2) sont retirés de la vente le temps de
        // vérifier leurs tarifs — incohérence au m² relevée le 17/07 (20 m × 1 m à 5,26 €/m²
        // vs 10 m × 2 m à 8,42 €/m² pour la même surface). Cf. CHECKLIST.
        // Libellé en longueur × largeur : un rouleau se dit par sa longueur déroulée, puis sa
        // laize. `defaut` porté par le 20 m × 2 m pour qu'il reste le format d'ouverture le
        // jour où les autres reviennent (sans lui, le tri imposerait le plus petit).
        formats: [{ label: "20 m × 2 m", largeur: 2, hauteur: 20, defaut: true }],
      },
    ],
  },
  // 🟢 cadre+média+pièce, méthode D · seul produit réellement offert en acier OU plastique (cf. fiche)
  "netpak-s-cilia": {
    code: "7",
    mode: "calcul",
    // Cadres alignés sur la fiche v1.1 (déc. PA 23/07/2026) : « Plastique » (et non
    // « Polypropylène »), cellulose pelliculée ajoutée au même prix (le cadre est neutre
    // côté prix tant que l'Excel ne le structure pas — cf. CHECKLIST « CADRE = info
    // TARIFAIRE ») ; suffixe -C acté côté codification. F7 = ePM1 50 % (média spécial,
    // la fiche fait foi — même override que BORA).
    cadres: [
      { valeur: "galva", libelle: "Acier galvanisé" },
      { valeur: "pp", libelle: "Plastique" },
      { valeur: "cellulose", libelle: "Cellulose pelliculée" },
    ],
    etiquettesIso: { F7: "ePM1 50 % (F7)" },
  },
  // 🟢 méthode D · parois cellule acier galvanisé (cf. fiche). L'option « cellulose pelliculée
  // incinérable » de la fiche n'est pas encore proposée : elle demande une lettre de suffixe de
  // référence à trancher (codification). Cf. CHECKLIST.
  "netcarb-cilia": { code: "8", mode: "calcul", cadreFixe: { valeur: "galva", libelle: "Acier galvanisé" } },
  // Polydièdre : dimensions en menu déroulant (formats générés depuis la grille), cadre plastique
  // fixe. Deux conditionnements (déc. PA 02/08/2026) : le filtre complet (code 9) et la RECHARGE —
  // jeu de cassettes seul, support conservé (code 10 « RECHARGES NETPAK S LUMEN » de l'Excel,
  // coeff/ratio propres, lignes sans épaisseur). Réf. recharge : formulation PA + classe + format.
  "netpak-s-lumen": {
    code: "9",
    mode: "calcul",
    cadreFixe: { valeur: "pp", libelle: "Plastique" },
    variantes: [
      { id: "standard", label: "Filtre complet", code: "9", saisie: "formats", labelChamp: "Dimensions (L × H)" },
      { id: "recharge", label: "Recharge (cassettes seules)", code: "10", saisie: "formats", refBase: "Recharge_NETPAK_S_LUMEN", sansCadre: true, labelChamp: "Dimensions (L × H)" },
    ],
  },
  // 🟠 NETBAG S : DEUX produits distincts en tarif (11 = poches 292 mm, média lourd, M5, ~25-51 € ;
  // 17 = poches 360-600 mm, média léger, sans M5, ~7-11 €), et la fiche annonce G4/M5 non tarifés.
  // Contradiction fiche/tarif → sur devis tant que la R&D n'a pas tranché (CHECKLIST). Pas de prix devine.
  // Sur devis, mais le client précise tout ce qui est chiffrable : les 2 cadres standard de la
  // fiche (le sur-mesure passe par la demande libre — déc. PA 26/07/2026), sa classe parmi
  // G4→F9 et sa longueur de poche parmi 380/500/550/650. Défaut 380 mm, comme le calculateur
  // de la fiche (cas le plus contraignant, pas le plus flatteur).
  // Tarifé sur le code 17 (déc. PA 26/07/2026) — le 11, homonyme dans l'Excel, est en réalité
  // AZUR. Deux variantes : les 2 cadres standard sont chiffrés en ligne, le hors-standard part
  // en devis (le moteur répond `hors_fabrication`, le bouton devis reste actif).
  // ⚠️ Divergence fiche ↔ tarif assumée : le tarif 17 vend 360/380/530/550/600 mm, la fiche
  // mesure 380/500/550/650. La variante standard ne propose donc que 380 et 550 — les seules
  // à la fois mesurées ET tarifées. G4 et M5 (courbes mais pas de prix) partent en devis.
  // À rouvrir quand l'Excel sera aligné : cf. CHECKLIST.
  "netbag-s": {
    code: "17",
    mode: "calcul",
    sansCadre: true, // cadre acier galvanisé ou plastique : pas de suffixe de référence tranché
    classesSurDevis: ["G4", "M5"],
    epaisseurDefaut: 380,
    labelEpaisseur: "Longueur de poche",
    variantes: [
      {
        id: "standard",
        label: "Dimensions standard",
        code: "17",
        saisie: "formats",
        labelChamp: "Dimensions standard (L × H)",
        epaisseurs: [380, 550],
        formats: [
          { label: "592 × 592 mm", largeur: 592, hauteur: 592, defaut: true },
          { label: "287 × 592 mm", largeur: 287, hauteur: 592 },
        ],
      },
      {
        id: "surmesure",
        label: "Sur mesure",
        code: "17",
        saisie: "dimensions",
        epaisseurs: [380, 500, 550, 650],
      },
    ],
  },
  // 🟢 méthode F (24 « AZUR » est vide) · parois cellule polyester fixe (cf. fiche) : pas de
  // choix de cadre à offrir — le polyester n'a pas de suffixe de référence (codification).
  // Offre limitée aux classes EPA/HEPA de la fiche (déc. PA 02/08/2026) : l'onglet Excel 13
  // tarife AUSSI M6→F9 (multidièdre particulaire) que la fiche ne documente pas — dont un
  // F8 490×592 à 3,50 € manifestement erroné (~31,50 attendu) qui partait au panier à 12 €.
  // Plage fiche E10 → H14 (déc. fabricant) : H14 sans prix ni courbe → au menu via
  // classesSurDevis, part en demande de devis. Correction Excel à la source : cf. CHECKLIST.
  // Dimensions STANDARD uniquement (déc. PA 02/08/2026, « comme NETPAK S AZUR ») : un filtre
  // absolu testé se fabrique en formats normalisés — la fiche v1.1 n'a plus de ligne
  // « sur mesure ». Formats lus dans la grille (287/490/592×592), plein format en tête.
  "netcel-v-azur": {
    code: "13",
    mode: "calcul",
    sansCadre: true,
    classesIncluses: ["E10", "E11", "E12", "H13"],
    classesSurDevis: ["H14"],
    variantes: [
      { id: "standard", label: "Multidièdre", code: "13", saisie: "formats", formatsGrandDabord: true, labelChamp: "Dimensions (L × H)" },
    ],
  },
  // 🟢 méthode F · polydièdre absolu.
  // CADRE AU CHOIX (déc. PA 15/08/2026) : les 4 fiches source Titanair de ce filtre ne
  // connaissent que le plastique/polystyrène — l'acier galvanisé est une DÉCISION FABRICANT,
  // comme la plage E10→H14 d'AZUR. Le cadre reste neutre côté prix tant que l'Excel ne le
  // structure pas (même traitement que NETBAG S) ; « Plastique » en tête = matière sourcée.
  // DIMENSIONS STANDARD : les 4 cadres retenus avec la fiche v1.1. Les 305×305, 381×381 et
  // 450×450 de la grille sont écartés de l'offre (« des filtres qui ne passent jamais », PA).
  // ⚠️ Formats déclarés EN DUR, à dessein : `formatsDuCode` filtre sur la PREMIÈRE classe du
  // menu (E10), tarifée sur 2 cadres seulement — le menu se serait réduit à 610×610 et 610×305.
  // ⚠️ E10/E11/E12 ne sont pas tarifées sur 592×592 ni 287×592 : ces 6 combinaisons répondent
  // « Cette efficacité n'est pas disponible dans ce format » (message honnête, jamais un prix
  // faux). À lever en tarifant ces classes dans l'Excel — cf. CHECKLIST § NETCEL V NIVAL.
  "netcel-v-nival": {
    code: "15",
    mode: "calcul",
    cadres: [
      { valeur: "pp", libelle: "Plastique" },
      { valeur: "galva", libelle: "Acier galvanisé" },
    ],
    variantes: [
      {
        id: "standard",
        label: "Polydièdre",
        code: "15",
        saisie: "formats",
        // Cadres par format (PA 15/08/2026) : les 610 existent en plastique ET en acier,
        // les 592 en acier SEULEMENT. Sans ça le configurateur laissait commander un
        // 592×592 plastique, qui n'existe pas.
        formats: [
          { label: "610 × 610 × 292 mm", largeur: 610, hauteur: 610, defaut: true, cadres: ["pp", "galva"] },
          { label: "592 × 592 × 292 mm", largeur: 592, hauteur: 592, cadres: ["galva"] },
          { label: "305 × 610 × 292 mm", largeur: 305, hauteur: 610, cadres: ["pp", "galva"] },
          { label: "287 × 592 × 292 mm", largeur: 287, hauteur: 592, cadres: ["galva"] },
        ],
        labelChamp: "Dimensions (L × H)",
      },
    ],
  },
  // 🟢 méthode F — laminaire : pas de sur-mesure, dimensions en menu déroulant (formats
  // standard générés depuis la grille) et efficacité verrouillée sur H14.
  "netcel-v-lam": {
    code: "14",
    mode: "calcul",
    // Offre ouverte aux 5 classes tarifées par l'onglet 14 (déc. PA 04/08/2026), alors que la
    // fiche v1.1 ne documente que le H14 : écart fiche ↔ boutique ASSUMÉ, consigné au CHECKLIST.
    // ⚠️ U15 = ULPA (EN 1822), pas HEPA — les badges et le sous-titre de la fiche parlent H14.
    // Aucune de ces 4 classes n'a de courbe ΔP mesurée : le calculateur de la fiche reste H14.
    classesIncluses: ["E11", "E12", "H13", "H14", "U15"],
    sansCadre: true, // caisson laminaire à cadre aluminium fixe (pas de choix de cadre)
    variantes: [
      // 610×610 = module de plafond soufflant, cas d'usage courant : il ouvre le menu alors
      // qu'il tombe au milieu des 17 formats de la grille (déc. PA 04/08/2026).
      { id: "standard", label: "Laminaire", code: "14", saisie: "formats", formatDefaut: { largeur: 610, hauteur: 610 }, labelChamp: "Dimensions standard" },
    ],
  },

  // — Sur devis (gammes « hors calculateur ») —
  // Le client choisit un COUPLE cadre + tricot (PA 17/07) : les 3 combinaisons réellement
  // vendues parmi les matériaux de la fiche (cadre acier galva ou inox 304 ; tricot alu, acier
  // galva ou inox 304). Sur devis : le choix n'est pas tarifé, il part dans la demande de prix.
  netmetal: {
    code: "29",
    mode: "devis",
    // Épaisseurs de la fiche (« 10 · 15 · 20 · 25 · 30 · 48 mm ») : le code 29 est sur devis,
    // le calculateur ne les porte pas → stopgap pour que le client précise son besoin.
    epaisseursDevis: [10, 15, 20, 25, 30, 48],
    epaisseurDefaut: 25, // décision PA 17/07/2026 (et non 10 mm, la plus fine, par simple inertie du menu)
    labelCadre: "Matière",
    cadres: [
      { valeur: "acier_acier", libelle: "Cadre acier · tricot acier" },
      { valeur: "acier_alu", libelle: "Cadre acier · tricot aluminium" },
      { valeur: "inox_inox", libelle: "Cadre inox · tricot inox" },
    ],
  },
  // panneau à brides, sur devis : épaisseur 100 mm + efficacité G4→F9 (le client précise son besoin)
  "netpak-s-bora": { code: "16", mode: "devis", epaisseursDevis: [100], efficacitesDevis: ["G4", "M5", "M6", "F7", "F8", "F9"], etiquettesIso: { F7: "ePM1 50 % (F7)" } },
  // AZUR = catégorie 11 de l'Excel (libellé erroné « NETBAG S » dans l'Excel → à corriger, cf. CHECKLIST).
  // Specs concordantes : profondeur 292, dimensions 287×592 / 490×592 / 592×592, classes M5→F9.
  "netpak-s-azur": {
    code: "11",
    mode: "calcul",
    cadreFixe: { valeur: "pp", libelle: "Plastique" },
    variantes: [{ id: "standard", label: "Polydièdre", code: "11", saisie: "formats", formatsGrandDabord: true, labelChamp: "Dimensions (L × H)" }],
  },
  "netpak-s-duo": { code: "20", mode: "devis" },
  "netcarb-azur": { code: "21", mode: "devis" },
  "netcarb-nival": { code: "23", mode: "devis" }, // 🟠 « NETCARB » générique, à confirmer
  "netcarb-bag": { code: "22", mode: "devis" },
};

/**
 * Renvoie la gamme tarifaire d'un produit du site, ou `undefined` si le produit
 * n'est pas répertorié (la page reste alors prudente : aucun prix proposé).
 */
export function gammeDuProduit(produitId: string): GammeProduit | undefined {
  return GAMME_PRODUIT[produitId];
}

/** Nombre de cas « cadre » déclarés par un produit — doit valoir exactement 1 si calculable. */
export function casCadreDeclares(g: GammeProduit): number {
  return [g.cadres?.length ? 1 : 0, g.cadreFixe ? 1 : 0, g.sansCadre ? 1 : 0].reduce((a, b) => a + b, 0);
}

/**
 * Produits dont la déclaration de cadre est invalide, avec la raison.
 *
 * Deux fautes possibles :
 *  - un produit calculable ne déclare AUCUN des 3 cas → il n'existe pas de cadre par défaut,
 *    il n'a donc rien de juste à afficher ;
 *  - un produit en déclare PLUSIEURS → contradictoire (quel cadre part dans la référence ?).
 *
 * On préfère casser le build (cf. appel dans `[ref].astro`) plutôt que de laisser un cadre faux
 * atteindre un client. Renvoie TOUS les fautifs, pas seulement le premier.
 */
export function produitsSansCadresDeclares(catalogue: Record<string, GammeProduit> = GAMME_PRODUIT): string[] {
  return Object.entries(catalogue)
    .filter(([, g]) => {
      const n = casCadreDeclares(g);
      // Un produit sur devis peut n'en déclarer aucun (il n'affiche alors pas le champ).
      return g.mode === "calcul" ? n !== 1 : n > 1;
    })
    .map(([id, g]) => {
      const attendu = g.mode === "calcul" ? "exactement 1" : "au plus 1";
      return `${id} (${casCadreDeclares(g)} cas déclarés, attendu ${attendu})`;
    });
}

/**
 * Formats dont la liste `cadres` sort du menu de cadres du produit.
 *
 * Le configurateur filtre le menu selon le format choisi. Si un format demande un cadre que
 * le produit ne propose pas, le filtre ne rendrait RIEN — et le code client retomberait
 * silencieusement sur le menu complet, proposant donc des cadres qui n'existent pas dans ce
 * format : la protection sauterait sans que personne ne le voie. On casse le build à la place
 * (cf. appel dans `[ref].astro`). Renvoie TOUS les fautifs, pas seulement le premier.
 */
export function formatsAuxCadresInconnus(catalogue: Record<string, GammeProduit> = GAMME_PRODUIT): string[] {
  const fautes: string[] = [];
  for (const [id, g] of Object.entries(catalogue)) {
    const offerts = new Set((g.cadres ?? []).map((c) => c.valeur));
    for (const v of g.variantes ?? []) {
      for (const f of v.formats ?? []) {
        const inconnus = (f.cadres ?? []).filter((c) => !offerts.has(c));
        if (inconnus.length > 0) {
          fautes.push(`${id} / ${v.id} / « ${f.label} » : cadre(s) ${inconnus.join(", ")} hors du menu du produit`);
        }
      }
    }
  }
  return fautes;
}
