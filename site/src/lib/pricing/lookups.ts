/**
 * Recherche dans les grilles tarifaires (Bloc B1 — tâche T3).
 *
 * Ce module ne CALCULE pas de prix : il « lit les abaques ». À partir de clés déjà
 * connues (code gamme, épaisseur, dimensions, quantité), il retrouve la bonne ligne
 * dans la bonne table de `tables.json`. Le calcul (renforts, surface, ratio, port)
 * est l'affaire de l'engine (T4) et des modules port/poids (T5/T6).
 *
 * Principes (cf. SPEC_B1_MOTEUR_PRIX.md §2, §5) :
 * - `tables.json` est la SEULE source de chiffres ; rien n'est codé en dur.
 * - Les paliers de quantité et les bornes de dimensions sont LUS dans les données
 *   (ils varient d'une table à l'autre).
 * - Une fonction qui ne trouve rien renvoie `undefined` — jamais une valeur inventée.
 */

import tablesData from "./data/tables.json";

// --- Formes des données (internes ; distinctes du contrat public de types.ts) ---

/** Prix par classe d'efficacité : nombre si fabriqué, `null` si non assuré pour ce format. */
export type PrixParClasse = Record<string, number | null>;

/** Une ligne de la table maîtresse des gammes. */
export interface GammeRow {
  code: string;
  nom: string;
  famille: string;
  /** Ratio prix tarif (coût → prix catalogue). */
  ratio: number;
  /** Épaisseur par défaut de la gamme (mm). */
  ep_defaut: number;
  /** Classe d'efficacité par défaut (EN 779). */
  eff_defaut: string;
  /** Remises catégories 1→5 (réservées au Bloc B4 — non utilisées par le moteur de base). */
  remises: number[];
  coeff: number;
  frais_livraison: number;
}

interface LigneAvecPalier {
  /** Borne basse de quantité (incluse). */
  qmin: number;
  /** Borne haute de quantité (incluse ; sentinelle ≈ 1e9 = « et au-delà »). */
  qmax: number;
}

interface LigneAvecBornesDim {
  /** Petit côté : borne min/max (mm, incluses). */
  pd_min: number;
  pd_max: number;
  /** Grand côté : borne min/max (mm, incluses). */
  gd_min: number;
  gd_max: number;
}

/**
 * Épaisseur d'une ligne de grille. `null` pour les gammes sans épaisseur de média
 * (ex. NETFIL, NETFIBRE ROULEAU, recharges) — l'égalité `null === null` permet de
 * les retrouver en passant `null` en clé.
 */
export type Epaisseur = number | null;

/** Grille « petite × grande dimension » (prix par case et par classe). */
export interface PrixLxLRow extends LigneAvecPalier, LigneAvecBornesDim {
  index: number;
  code: string;
  ep: Epaisseur;
  prix: PrixParClasse;
}

/** Grille « prix à la pièce » (CILIA : main d'œuvre + emballage). */
export interface PrixPieceRow extends LigneAvecPalier, LigneAvecBornesDim {
  index: number;
  code: string;
  ep: Epaisseur;
  /** Prix unitaire fixe de la pièce. */
  pu: number;
  commentaire?: string;
}

/** Grille « par tranche de surface » (repli quand la dimension exacte n'est pas dans la grille L×l). */
export interface PrixSurfaceRow extends LigneAvecPalier {
  index: number;
  code: string;
  ep: Epaisseur;
  /** Tranche de surface (dm², bornes incluses). */
  surf_min: number;
  surf_max: number;
  prix: PrixParClasse;
}

/** Grille « hors format » : supplément au dm² au-delà de 50 dm². */
export interface PrixSurfaceHFRow extends LigneAvecPalier {
  index: number;
  code: string;
  ep: Epaisseur;
  prix: PrixParClasse;
}

/** Poids du média par gamme/épaisseur. */
export interface PoidsRow {
  index: number;
  code: string;
  ep: Epaisseur;
  /** Poids surfacique (kg/m²). */
  poids: number;
}

/** Une constante de l'onglet « Paramètres unitaires ». */
export interface ParamRow {
  libelle: string;
  valeur: number;
  unite?: string | null;
}

interface Tables {
  gammes: GammeRow[];
  prix_l_et_l: PrixLxLRow[];
  prix_piece: PrixPieceRow[];
  prix_surface: PrixSurfaceRow[];
  prix_surface_hf: PrixSurfaceHFRow[];
  poids: PoidsRow[];
  params: ParamRow[];
  /** Frais de port par département (code → €). */
  expedition: Record<string, number>;
  /** Seuil de franco de port (€). */
  franco: number;
  /** Durée de validité de l'offre (jours). */
  validite_jours: number;
}

/** Données chargées une seule fois ; source unique de chiffres pour tout le moteur. */
export const tables = tablesData as unknown as Tables;

// --- Aides partagées (réutilisées par plusieurs grilles) ---

/** La quantité tombe-t-elle dans le palier de cette ligne ? Bornes incluses. */
function dansPalier(ligne: LigneAvecPalier, quantite: number): boolean {
  return quantite >= ligne.qmin && quantite <= ligne.qmax;
}

/**
 * Le couple de dimensions tombe-t-il dans la case ? La grille se lit en
 * « petit côté × grand côté » ; les bornes sont incluses.
 */
function dansBornesDim(ligne: LigneAvecBornesDim, petite: number, grande: number): boolean {
  return (
    petite >= ligne.pd_min &&
    petite <= ligne.pd_max &&
    grande >= ligne.gd_min &&
    grande <= ligne.gd_max
  );
}

/** Range L et H en (petit côté, grand côté) — l'ordre attendu par les grilles dimensionnelles. */
export function ordonnerDimensions(
  largeur_mm: number,
  hauteur_mm: number,
): { petite: number; grande: number } {
  return {
    petite: Math.min(largeur_mm, hauteur_mm),
    grande: Math.max(largeur_mm, hauteur_mm),
  };
}

// --- Recherches ---

/** Ligne de la gamme par code, ou `undefined` si code inconnu. */
export function trouverGamme(code: string): GammeRow | undefined {
  return tables.gammes.find((g) => g.code === code);
}

/**
 * Case de la grille « petite × grande dimension » pour (code, épaisseur, dimensions, quantité).
 * `undefined` si aucune case ne couvre ces dimensions (→ l'engine basculera sur la surface).
 */
export function trouverLigneLxL(
  code: string,
  ep: Epaisseur,
  largeur_mm: number,
  hauteur_mm: number,
  quantite: number,
): PrixLxLRow | undefined {
  const { petite, grande } = ordonnerDimensions(largeur_mm, hauteur_mm);
  return tables.prix_l_et_l.find(
    (r) =>
      r.code === code &&
      r.ep === ep &&
      dansBornesDim(r, petite, grande) &&
      dansPalier(r, quantite),
  );
}

/** Ligne « prix à la pièce » pour (code, épaisseur, dimensions, quantité), ou `undefined`. */
export function trouverLignePiece(
  code: string,
  ep: Epaisseur,
  largeur_mm: number,
  hauteur_mm: number,
  quantite: number,
): PrixPieceRow | undefined {
  const { petite, grande } = ordonnerDimensions(largeur_mm, hauteur_mm);
  return tables.prix_piece.find(
    (r) =>
      r.code === code &&
      r.ep === ep &&
      dansBornesDim(r, petite, grande) &&
      dansPalier(r, quantite),
  );
}

/** Ligne « par tranche de surface » pour (code, épaisseur, surface en dm², quantité), ou `undefined`. */
export function trouverLigneSurface(
  code: string,
  ep: Epaisseur,
  surface_dm2: number,
  quantite: number,
): PrixSurfaceRow | undefined {
  return tables.prix_surface.find(
    (r) =>
      r.code === code &&
      r.ep === ep &&
      surface_dm2 >= r.surf_min &&
      surface_dm2 <= r.surf_max &&
      dansPalier(r, quantite),
  );
}

/** Ligne « hors format » (supplément au dm²) pour (code, épaisseur, quantité), ou `undefined`. */
export function trouverLigneSurfaceHF(
  code: string,
  ep: Epaisseur,
  quantite: number,
): PrixSurfaceHFRow | undefined {
  return tables.prix_surface_hf.find(
    (r) => r.code === code && r.ep === ep && dansPalier(r, quantite),
  );
}

/** Ligne de poids pour (code, épaisseur), ou `undefined`. */
export function trouverPoids(code: string, ep: Epaisseur): PoidsRow | undefined {
  return tables.poids.find((r) => r.code === code && r.ep === ep);
}

/**
 * Prix d'une classe dans une grille de prix. Trois issues distinctes (cf. règle d'or) :
 * - `number`    → prix trouvé ;
 * - `null`      → la classe existe mais n'est PAS fabriquée pour ce format → `classe_indisponible` ;
 * - `undefined` → la classe n'existe pas dans cette grille du tout.
 */
export function prixPourClasse(
  prix: PrixParClasse,
  classe: string,
): number | null | undefined {
  return Object.prototype.hasOwnProperty.call(prix, classe) ? prix[classe] : undefined;
}

/** Valeur d'une constante de l'onglet « Paramètres » par libellé exact, ou `undefined`. */
export function getParam(libelle: string): number | undefined {
  return tables.params.find((p) => p.libelle === libelle)?.valeur;
}

/**
 * Libellé lisible du palier de quantité d'une ligne — ex. "6-19", "500+".
 * L'export utilise 1e9 comme borne haute « et au-delà » ; tout `qmax` ≥ ce seuil
 * est traité comme ouvert. Les paliers finis réels restent bien en dessous (≤ 500).
 */
const QMAX_OUVERT = 1_000_000_000;
export function libellePalier(ligne: LigneAvecPalier): string {
  return ligne.qmax >= QMAX_OUVERT ? `${ligne.qmin}+` : `${ligne.qmin}-${ligne.qmax}`;
}
