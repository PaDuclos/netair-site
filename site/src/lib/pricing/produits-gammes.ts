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

/** Un format de rouleau fixe (dimensions dans l'unité des tables, ici en mètres). */
export interface FormatRouleau {
  /** Libellé affiché — ex. "1 m × 10 m". */
  label: string;
  /** Petit côté (passé tel quel au moteur — l'unité est celle de la table). */
  largeur: number;
  /** Grand côté (idem). */
  hauteur: number;
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
  /** Formats proposés quand `saisie === "formats"`. */
  formats?: FormatRouleau[];
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
   * `true` si le produit n'a pas de cadre (média fibreux seul, ex. NETFIBRE) : le
   * configurateur masque alors le choix « Cadre ».
   */
  sansCadre?: boolean;
  /**
   * Cadres proposés pour ce produit (valeur technique + libellé). Si absent, le
   * configurateur propose les cadres par défaut. Permet d'aligner le choix sur la
   * fiche (ex. NETPLY = acier seul, pas de polypropylène).
   */
  cadres?: { valeur: string; libelle: string }[];
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
  netply: { code: "1", mode: "calcul", cadres: [{ valeur: "galva", libelle: "Acier galvanisé" }] }, // 🟢 plissé, méthode A · cadre acier seul (cf. fiche)
  netplan: { code: "3", mode: "calcul" }, // 🟢 plan, méthode A
  netfil: { code: "2", mode: "calcul" }, // 🟢 mètre linéaire, méthode B
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
        formats: [
          { label: "1 m × 10 m", largeur: 1, hauteur: 10 },
          { label: "1 m × 20 m", largeur: 1, hauteur: 20 },
          { label: "2 m × 10 m", largeur: 2, hauteur: 10 },
          { label: "2 m × 20 m", largeur: 2, hauteur: 20 },
          { label: "2 m × 30 m", largeur: 2, hauteur: 30 },
        ],
      },
    ],
  },
  "netpak-s-cilia": { code: "7", mode: "calcul" }, // 🟢 cadre+média+pièce, méthode D
  "netcarb-cilia": { code: "8", mode: "calcul" }, // 🟢 méthode D
  "netpak-s-lumen": { code: "9", mode: "calcul" }, // 🟢 lecture L×l, méthode F
  // 🟠 NETBAG S : DEUX produits distincts en tarif (11 = poches 292 mm, média lourd, M5, ~25-51 € ;
  // 17 = poches 360-600 mm, média léger, sans M5, ~7-11 €), et la fiche annonce G4/M5 non tarifés.
  // Contradiction fiche/tarif → sur devis tant que la R&D n'a pas tranché (CHECKLIST). Pas de prix devine.
  "netbag-s": { code: "", mode: "devis" },
  "netcel-v-azur": { code: "13", mode: "calcul" }, // 🟢 méthode F (24 « AZUR » est vide)
  "netcel-v-nival": { code: "15", mode: "calcul" }, // 🟢 méthode F
  "netpak-v-lam": { code: "14", mode: "calcul" }, // 🟢 méthode F

  // — Sur devis (gammes « hors calculateur ») —
  netmetal: { code: "29", mode: "devis" },
  "netpak-s-bora": { code: "16", mode: "devis" },
  "netpak-s-azur": { code: "", mode: "devis" }, // pas de code particulaire dans les tables
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
