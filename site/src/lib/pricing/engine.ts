/**
 * Moteur de calcul du prix (Bloc B1 — tâche T4, étape B).
 *
 * Aiguilleur + 6 méthodes A→F. À partir d'une DemandePrix, calcule le coût de
 * revient (PRU HT) puis le prix catalogue (PRU × ratio). Lit UNIQUEMENT les
 * abaques via lookups.ts ; ne fait JAMAIS de port ni de poids (→ T5/T6/T7).
 *
 * Référence de la géométrie : `DEVIS AUTO/src/cost_calculator.py` (validé contre de
 * vrais devis). Décisions de fidélité — cf. SPEC_B1 §3 :
 *  - Coût (PRU HT) = (1 + charge gamme) × assemblage géométrique, où la « charge
 *    gamme » est la colonne `frais_livraison` du Tableau_Gammes (ex. NETPLY +10 %).
 *    ⚠️ L'exemple chiffré de la spec §3 (11,47 €) l'avait OMIS ; le bon coût NETPLY
 *    287×592 G4 ×10 = 1,1×3,44 = 3,78 €, prix = 3,78×3,333 = 12,60 € (réf. validée).
 *  - Prix unitaire = arrondi2(PRU × ratio × revalorisation). Revalorisation absente
 *    aujourd'hui (param non présent) → facteur 1.
 *  - Méthode A (renfort) : non encore 100 % pilotée par les données — voir configRenfortA.
 *  - Hors-format (Prix_Surface_HF) : NON appliqué (absent de la référence validée) → à
 *    confirmer par les vecteurs dorés (T8).
 */

import type {
  DemandePrix,
  ResultatPrix,
  DetailCalcul,
  ComposantCout,
  SourceTable,
  MethodeCalcul,
} from "./types";
import {
  tables,
  trouverGamme,
  trouverLigneLxL,
  trouverLigneSurface,
  trouverLignePiece,
  prixPourClasse,
  libellePalier,
  ordonnerDimensions,
  getParam,
  type GammeRow,
  type PrixParClasse,
} from "./lookups";

// ── Petits utilitaires ──────────────────────────────────────────────────────

/** Arrondi classique à 2 décimales (cf. SPEC §10). */
function arrondi2(x: number): number {
  return Math.round(x * 100) / 100;
}

/** Surface frontale en dm². */
function surfaceDm2(largeur_mm: number, hauteur_mm: number): number {
  return (largeur_mm * hauteur_mm) / 10000;
}

/** Périmètre en mètres = (L + H) × 2 / 1000. */
function perimetreM(largeur_mm: number, hauteur_mm: number): number {
  return ((largeur_mm + hauteur_mm) * 2) / 1000;
}

/**
 * Prix utilisable d'une classe : un nombre strictement positif, sinon `null`.
 * `null` couvre les trois cas non-vendables (classe non fabriquée, classe absente,
 * valeur ≤ 0) — règle d'or : pas de prix sur une combinaison non fabriquée.
 */
function prixUtilisable(prix: PrixParClasse, classe: string): number | null {
  const v = prixPourClasse(prix, classe);
  return typeof v === "number" && v > 0 ? v : null;
}

// ── Résultat interne d'une méthode ──────────────────────────────────────────

interface SuccesCalcul {
  ok: true;
  methode: MethodeCalcul;
  composants: ComposantCout[];
  /** Coût d'assemblage géométrique, AVANT la charge gamme (1+x). */
  coutAssemblage: number;
  surface_dm2?: number;
  perimetre_m?: number;
  sources: SourceTable[];
  palier: string;
}
interface EchecCalcul {
  ok: false;
  statut: "hors_fabrication" | "classe_indisponible";
  message: string;
}
type ResultatCalcul = SuccesCalcul | EchecCalcul;

const horsFabrication: EchecCalcul = {
  ok: false,
  statut: "hors_fabrication",
  message: "Dimensions hors des cases fabricables pour cette gamme.",
};
function classeIndisponible(classe: string): EchecCalcul {
  return {
    ok: false,
    statut: "classe_indisponible",
    message: `Efficacité ${classe} non disponible dans ce format.`,
  };
}

// ── Méthode A : plissés / plans avec renfort (NETPLY, NETPLAN) ───────────────

/**
 * Paramètres de renfort + surcoût épaisseur de la méthode A.
 * ⚠️ Seul endroit non 100 % piloté par les données : le jeu de paramètres dépend de
 * la gamme (NETPLAN vs NETPLY). On le résout par le nom (« PLAN »), car les libellés
 * de paramètres sont propres au produit. À remplacer par une config par gamme dans
 * l'Excel lors du retravail du calculateur.
 */
function configRenfortA(gamme: GammeRow): {
  renfortExt: number;
  renfortInt: number;
  surcoutEpaisseur: boolean;
} {
  const estPlan = gamme.nom.toUpperCase().includes("PLAN");
  if (estPlan) {
    return {
      renfortExt: getParam("NETPLAN renfort extérieur :") ?? 0,
      renfortInt: getParam("NETPLAN renfort intérieur :") ?? 0,
      surcoutEpaisseur: false,
    };
  }
  return {
    renfortExt: getParam("TITAPLY renfort extérieur :") ?? 0,
    renfortInt: getParam("TITAPLY renfort intérieur :") ?? 0,
    surcoutEpaisseur: true,
  };
}

function methodeA(demande: DemandePrix, gamme: GammeRow): ResultatCalcul {
  const { largeur_mm: L, hauteur_mm: H, profondeur_mm: P, classe, quantite: q } = demande;
  const { petite, grande } = ordonnerDimensions(L, H);
  const surface = surfaceDm2(L, H);
  const cfg = configRenfortA(gamme);

  let renfort = 0;
  let renfortLabel = "";
  if (petite > 850) {
    renfort = cfg.renfortInt;
    renfortLabel = "renfort intérieur";
  } else if (grande > 800 || surface > 50) {
    renfort = cfg.renfortExt;
    renfortLabel = "renfort extérieur";
  }

  let surcout = 0;
  if (cfg.surcoutEpaisseur && (P === 45 || P === 95)) {
    surcout = getParam(`Surcoût TITAPLY épaisseur ${P}mm :`) ?? 0;
  }

  // Prix de base : L×l, sinon repli sur la grille surface (prix par pièce, PAS × surface).
  let base: number | undefined;
  let source: SourceTable | undefined;
  let palier: string | undefined;

  const rLL = trouverLigneLxL(gamme.code, P, L, H, q);
  if (rLL) {
    const p = prixUtilisable(rLL.prix, classe);
    if (p != null) {
      base = p;
      source = { table: "prix_l_et_l", index: rLL.index };
      palier = libellePalier(rLL);
    }
  }
  if (base === undefined) {
    const rS = trouverLigneSurface(gamme.code, P, surface, q);
    if (rS) {
      const p = prixUtilisable(rS.prix, classe);
      if (p != null) {
        base = p;
        source = { table: "prix_surface", index: rS.index };
        palier = libellePalier(rS);
      }
    }
  }
  if (base === undefined || source === undefined || palier === undefined) {
    const rAny = rLL ?? trouverLigneSurface(gamme.code, P, surface, q);
    return rAny ? classeIndisponible(classe) : horsFabrication;
  }

  const composants: ComposantCout[] = [];
  if (renfort > 0) composants.push({ libelle: renfortLabel, montant: renfort });
  if (surcout > 0) composants.push({ libelle: `surcoût épaisseur ${P} mm`, montant: surcout });
  composants.push({
    libelle: source.table === "prix_l_et_l" ? "prix de base (L×l)" : "prix de base (surface)",
    montant: base,
  });

  return {
    ok: true,
    methode: "A",
    composants,
    coutAssemblage: renfort + surcout + base,
    surface_dm2: surface,
    sources: [source],
    palier,
  };
}

// ── Méthode B : périmètre / mètre linéaire (NETFIL) ──────────────────────────

function methodeB(demande: DemandePrix, gamme: GammeRow): ResultatCalcul {
  const { largeur_mm: L, hauteur_mm: H, profondeur_mm: P, classe, quantite: q } = demande;
  const perimetre = perimetreM(L, H);
  const r = trouverLigneLxL(gamme.code, P, L, H, q);
  if (!r) return horsFabrication;
  const pml = prixUtilisable(r.prix, classe);
  if (pml == null) return classeIndisponible(classe);

  const montant = pml * perimetre;
  return {
    ok: true,
    methode: "B",
    composants: [{ libelle: "média au mètre linéaire × périmètre", montant }],
    coutAssemblage: montant,
    perimetre_m: perimetre,
    sources: [{ table: "prix_l_et_l", index: r.index }],
    palier: libellePalier(r),
  };
}

// ── Méthode C : surface au dm² (NETFIBRE) ────────────────────────────────────

function methodeC(demande: DemandePrix, gamme: GammeRow): ResultatCalcul {
  const { largeur_mm: L, hauteur_mm: H, profondeur_mm: P, classe, quantite: q } = demande;
  const surface = surfaceDm2(L, H);
  const r = trouverLigneSurface(gamme.code, P, surface, q);
  if (!r) return horsFabrication;
  const pdm2 = prixUtilisable(r.prix, classe);
  if (pdm2 == null) return classeIndisponible(classe);

  const montant = pdm2 * surface;
  return {
    ok: true,
    methode: "C",
    composants: [{ libelle: "média au dm² × surface", montant }],
    coutAssemblage: montant,
    surface_dm2: surface,
    sources: [{ table: "prix_surface", index: r.index }],
    palier: libellePalier(r),
  };
}

// ── Méthode D : cadre + média + pièce (CILIA — codes 7/8) ────────────────────

function methodeD(demande: DemandePrix, gamme: GammeRow): ResultatCalcul {
  const { largeur_mm: L, hauteur_mm: H, profondeur_mm: P, classe, quantite: q } = demande;
  const epNorm = P <= 60 ? 48 : 98;
  const perimetre = perimetreM(L, H);
  const surface = surfaceDm2(L, H);

  const rLL = trouverLigneLxL(gamme.code, epNorm, L, H, q);
  if (!rLL) return horsFabrication;
  const pml = prixUtilisable(rLL.prix, classe);
  if (pml == null) return classeIndisponible(classe);
  const cadre = pml * perimetre;

  const rS = trouverLigneSurface(gamme.code, epNorm, surface, q);
  if (!rS) return horsFabrication;
  const pdm2 = prixUtilisable(rS.prix, classe);
  if (pdm2 == null) return classeIndisponible(classe);
  const media = pdm2 * surface;

  const sources: SourceTable[] = [
    { table: "prix_l_et_l", index: rLL.index },
    { table: "prix_surface", index: rS.index },
  ];

  // Pièce = MO + emballage (± grille). Repli sur les paramètres si pas de ligne pièce.
  let piece: number;
  const rP = trouverLignePiece(gamme.code, epNorm, L, H, q);
  if (rP) {
    piece = rP.pu;
    sources.push({ table: "prix_piece", index: rP.index });
  } else {
    const mo = getParam(`Coût main d'œuvre ${epNorm}mm :`) ?? 0;
    const emb = getParam(`Coût emballage ${epNorm}mm :`) ?? 0;
    piece = mo + emb;
  }

  return {
    ok: true,
    methode: "D",
    composants: [
      { libelle: "cadre (mL × périmètre)", montant: cadre },
      { libelle: "média (dm² × surface)", montant: media },
      { libelle: "pièce (MO + emballage)", montant: piece },
    ],
    coutAssemblage: cadre + media + piece,
    surface_dm2: surface,
    perimetre_m: perimetre,
    sources,
    palier: libellePalier(rLL),
  };
}

// ── Méthode E : prix pièce simple (NETFIBRE ROULEAU — code 5) ────────────────

function methodeE(demande: DemandePrix, gamme: GammeRow): ResultatCalcul {
  const { largeur_mm: L, hauteur_mm: H, profondeur_mm: P, classe, quantite: q } = demande;
  // Les dimensions de la grille code 5 peuvent être en mètres (rouleau 1 m × 10 m) :
  // essai en mm, repli en mètres. (Comportement de la référence — à clarifier en prod.)
  let r = trouverLigneLxL(gamme.code, P, L, H, q);
  if (!r) r = trouverLigneLxL(gamme.code, P, L / 1000, H / 1000, q);
  if (!r) return horsFabrication;
  const p = prixUtilisable(r.prix, classe);
  if (p == null) return classeIndisponible(classe);

  return {
    ok: true,
    methode: "E",
    composants: [{ libelle: "prix pièce (rouleau)", montant: p }],
    coutAssemblage: p,
    sources: [{ table: "prix_l_et_l", index: r.index }],
    palier: libellePalier(r),
  };
}

// ── Méthode F : lecture L×l directe (NETBAG, NETCEL, LUMEN…) ──────────────────

function methodeF(demande: DemandePrix, gamme: GammeRow): ResultatCalcul {
  const { largeur_mm: L, hauteur_mm: H, profondeur_mm: P, classe, quantite: q } = demande;
  const r = trouverLigneLxL(gamme.code, P, L, H, q);
  if (!r) return horsFabrication;
  const p = prixUtilisable(r.prix, classe);
  if (p == null) return classeIndisponible(classe);

  return {
    ok: true,
    methode: "F",
    composants: [{ libelle: "prix (lecture L×l)", montant: p }],
    coutAssemblage: p,
    sources: [{ table: "prix_l_et_l", index: r.index }],
    palier: libellePalier(r),
  };
}

const METHODES: Record<MethodeCalcul, (d: DemandePrix, g: GammeRow) => ResultatCalcul> = {
  A: methodeA,
  B: methodeB,
  C: methodeC,
  D: methodeD,
  E: methodeE,
  F: methodeF,
};

// ── Point d'entrée : prix catalogue HT (hors port/poids) ─────────────────────

/**
 * Calcule le prix catalogue HT d'une demande. NE traite pas le port ni le poids
 * (ajoutés en T5/T6 via index.ts). Renvoie toujours `dureeValiditeJours`.
 */
export function calculerPrixHT(demande: DemandePrix): ResultatPrix {
  const validite = tables.validite_jours;
  const gamme = trouverGamme(demande.codeGamme);

  if (!gamme) {
    return {
      statut: "gamme_inconnue",
      dureeValiditeJours: validite,
      message: `Code gamme inconnu : ${demande.codeGamme}.`,
    };
  }
  if (gamme.methode === "sur_devis") {
    return {
      statut: "sur_devis",
      dureeValiditeJours: validite,
      message: `${gamme.nom} : prix sur devis (gamme hors calculateur).`,
    };
  }

  const { largeur_mm: L, hauteur_mm: H, profondeur_mm: P, quantite: q } = demande;
  const dimsOk = [L, H, P].every((x) => Number.isFinite(x) && x > 0);
  if (!dimsOk || !Number.isFinite(q) || q < 1) {
    return {
      statut: "hors_fabrication",
      dureeValiditeJours: validite,
      message: "Dimensions et quantité doivent être strictement positives (quantité ≥ 1).",
    };
  }

  const calc = METHODES[gamme.methode](demande, gamme);
  if (!calc.ok) {
    return { statut: calc.statut, dureeValiditeJours: validite, message: calc.message };
  }

  // Coût (PRU HT) = (1 + charge gamme) × assemblage. charge = frais_livraison (0 si absente).
  const charge = Number.isFinite(gamme.frais_livraison) ? gamme.frais_livraison : 0;
  const coutHT = arrondi2((1 + charge) * calc.coutAssemblage);

  // Revalorisation générale (levier §11) : appliquée seulement si le paramètre existe.
  const reval = getParam("Revalorisation générale :");
  const facteurReval = typeof reval === "number" && reval > 0 ? reval : undefined;

  const prixUnitaireHT = arrondi2(coutHT * gamme.ratio * (facteurReval ?? 1));
  const prixTotalHT = arrondi2(prixUnitaireHT * q);

  const composants = [...calc.composants];
  if (charge > 0) {
    composants.push({
      libelle: `charge gamme (+${Math.round(charge * 100)} %)`,
      montant: arrondi2(charge * calc.coutAssemblage),
    });
  }

  const detail: DetailCalcul = {
    methode: calc.methode,
    composantsCout: composants,
    coutHT,
    ratioTarif: gamme.ratio,
    revalorisation: facteurReval,
    surface_dm2: calc.surface_dm2,
    perimetre_m: calc.perimetre_m,
    sources: calc.sources,
  };

  return {
    statut: "ok",
    prixUnitaireHT,
    prixTotalHT,
    palierQuantite: calc.palier,
    dureeValiditeJours: validite,
    detail,
  };
}
