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

/** Lien d'un produit du site vers sa gamme tarifaire. */
export interface GammeProduit {
  /** Code-gamme tel qu'il figure dans `tables.json` (chaîne, jamais comparée comme un nombre). */
  code: string;
  /** `calcul` = prix instantané ; `devis` = demande de devis seule. */
  mode: ModeProduit;
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
  netply: { code: "1", mode: "calcul" }, // 🟢 plissé, méthode A
  netplan: { code: "3", mode: "calcul" }, // 🟢 plan, méthode A
  netfil: { code: "2", mode: "calcul" }, // 🟢 mètre linéaire, méthode B
  netfibre: { code: "4", mode: "calcul" }, // panneau découpé (méthode C, surface) — la fiche du site décrit le panneau ; le rouleau (code 5) sera ajouté en variante (Option B)
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
