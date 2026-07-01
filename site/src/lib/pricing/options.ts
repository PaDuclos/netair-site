/**
 * Menus adaptés au produit (Bloc B2).
 *
 * Pour un code-gamme donné, ce module dit quelles EFFICACITÉS et quelles ÉPAISSEURS
 * sont réellement tarifées dans les tables — afin que le configurateur ne propose
 * jamais une combinaison qui n'existe pas (règle d'or : pas de prix sur l'infabricable).
 *
 * Tout est LU dans `tables.json` (via `lookups.ts`) : rien n'est codé en dur. Les
 * efficacités proposées = l'union des classes ayant au moins un prix non nul pour ce
 * code ; les épaisseurs = les valeurs `ep` présentes. Si une classe n'est tarifée que
 * sur certaines dimensions, elle reste au menu mais le calcul renverra le cas échéant
 * `classe_indisponible` pour le format saisi (deux niveaux, cf. SPEC_B1 §4).
 */

import { tables } from "./lookups";
import type { PrixParClasse } from "./lookups";

/** Une option d'efficacité du menu : valeur technique (EN 779) + libellé affiché. */
export interface OptionClasse {
  /** Valeur envoyée au moteur — ex. "G4", "F7". */
  valeur: string;
  /** Libellé lisible conforme à la charte — ex. "Coarse 65 % (G4)", "ePM10 50 % (M5)". */
  libelle: string;
}

/** Menus disponibles pour un produit. */
export interface OptionsProduit {
  /** Efficacités tarifées, ordonnées de la moins à la plus filtrante. */
  classes: OptionClasse[];
  /** Épaisseurs tarifées (mm), ordre croissant. Vide = la gamme n'a pas de choix d'épaisseur. */
  epaisseurs: number[];
}

/** Une dimension standard d'un produit à formats (ex. laminaire). */
export interface FormatDimension {
  /** Libellé affiché — ex. "610 × 610 mm". */
  label: string;
  /** Petit côté (mm), passé au moteur. */
  largeur: number;
  /** Grand côté (mm), passé au moteur. */
  hauteur: number;
}

/**
 * Dimensions standard tarifées d'un code (depuis la grille L×l), pour les produits
 * vendus en formats fixes (ex. laminaire). Si `classeRequise` est fournie, ne garde
 * que les dimensions où cette classe a un prix. Triées par taille croissante.
 */
export function formatsDuCode(code: string, classeRequise?: string): FormatDimension[] {
  const vues = new Set<string>();
  const out: FormatDimension[] = [];
  for (const r of tables.prix_l_et_l) {
    if (r.code !== code) continue;
    if (classeRequise && r.prix[classeRequise] == null) continue;
    const largeur = r.pd_min;
    const hauteur = r.gd_min;
    const cle = `${largeur}x${hauteur}`;
    if (vues.has(cle)) continue;
    vues.add(cle);
    // La profondeur (ep) figée figure dans le libellé quand elle existe (ex. polydièdres 292 mm
    // → "592 × 592 × 292 mm" ; laminaire 69 mm). Pour les gammes sans ep, "L × H mm".
    const profondeur = typeof r.ep === "number" ? ` × ${r.ep}` : "";
    out.push({ label: `${largeur} × ${hauteur}${profondeur} mm`, largeur, hauteur });
  }
  return out.sort((a, b) => a.largeur - b.largeur || a.hauteur - b.hauteur);
}

/**
 * Ordre d'affichage des classes (du moins au plus filtrant). Sert uniquement au tri ;
 * les classes inconnues de cette liste sont placées à la fin, dans l'ordre alphabétique.
 */
const ORDRE_CLASSES = [
  "G2", "G3", "G4", "M5", "M6", "F7", "F8", "F9",
  "E10", "E11", "E12", "H13", "H14", "U15",
];

/** Table de correspondance EN 779 ↔ ISO 16890 (libellés bruts de l'Excel). */
const ISO = tables.iso16890;

/**
 * Construit le libellé d'une classe : « ISO normalisé (classe EN 779) ».
 * Quand l'ISO est identique à la classe (E10, H13, U15…), on n'affiche que la classe.
 * Normalise la casse et les espaces de l'Excel : "COARSE 65%" → "Coarse 65 %".
 */
export function libelleClasse(classe: string): string {
  const brut = ISO[classe];
  if (!brut || brut === classe) return classe;
  const propre = brut
    .replace(/\s+/g, " ")          // espaces multiples → simple
    .replace(/\s*%/, " %")          // "65%" → "65 %"
    .trim()
    .replace(/^COARSE/i, "Coarse"); // casse de la famille « Coarse »
  return `${propre} (${classe})`;
}

/** Classes ayant au moins un prix non nul dans un lot de lignes « prix par classe ». */
function classesTarifees(prix: PrixParClasse, dans: Set<string>): void {
  for (const [classe, valeur] of Object.entries(prix)) {
    if (valeur !== null && valeur !== undefined) dans.add(classe);
  }
}

/**
 * Efficacités et épaisseurs réellement tarifées pour un code-gamme.
 * Pour un code inconnu ou sans tarif : listes vides (le configurateur restera prudent).
 */
export function optionsDuCode(code: string): OptionsProduit {
  const classes = new Set<string>();
  const epaisseurs = new Set<number>();

  const collecter = (
    lignes: { code: string; ep: number | null; prix: PrixParClasse }[],
  ) => {
    for (const r of lignes) {
      if (r.code !== code) continue;
      classesTarifees(r.prix, classes);
      if (typeof r.ep === "number") epaisseurs.add(r.ep);
    }
  };

  collecter(tables.prix_l_et_l);
  collecter(tables.prix_surface);
  collecter(tables.prix_surface_hf);

  const classesTriees = [...classes].sort((a, b) => {
    const ia = ORDRE_CLASSES.indexOf(a);
    const ib = ORDRE_CLASSES.indexOf(b);
    if (ia === -1 && ib === -1) return a.localeCompare(b);
    if (ia === -1) return 1;
    if (ib === -1) return -1;
    return ia - ib;
  });

  return {
    classes: classesTriees.map((valeur) => ({ valeur, libelle: libelleClasse(valeur) })),
    epaisseurs: [...epaisseurs].sort((a, b) => a - b),
  };
}
