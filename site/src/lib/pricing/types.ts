/**
 * Contrat du moteur de prix du site marchand Netair (Bloc B1).
 *
 * Ce fichier ne contient QUE des définitions de types — aucune logique, aucun
 * chiffre. Il fixe les « formulaires » d'entrée et de sortie du moteur, partagés
 * par le navigateur (prix instantané) et le serveur (recalcul de sécurité).
 *
 * Référence : SPEC_B1_MOTEUR_PRIX.md §4 (contrat) et §3 (les 6 méthodes A→F).
 *
 * Principe « rien en dur » : aucun code gamme ni aucune classe n'est figé ici.
 * Les codes gamme changeront (filtres ajoutés/retirés au fil du retravail du
 * calculateur) ; le moteur les lit dans les données exportées, jamais dans le code.
 */

/** Demande adressée au moteur (ce que la page produit / le configurateur envoie). */
export interface DemandePrix {
  /**
   * Code de la gamme commandée, tel qu'il figure dans les données exportées
   * (`tables.json`) — ex. "1" (NETPLY), "101", "130". Volontairement une chaîne :
   * les codes ne sont pas figés et ne sont jamais comparés comme des nombres.
   */
  codeGamme: string;
  /** Largeur L, en millimètres. */
  largeur_mm: number;
  /** Hauteur H, en millimètres. */
  hauteur_mm: number;
  /** Profondeur / épaisseur P, en millimètres. */
  profondeur_mm: number;
  /**
   * Classe d'efficacité EN 779 demandée — ex. "G4", "F7", "H13".
   * Chaîne libre (non figée) : les classes valides sont lues dans les tables,
   * pas codées dans le programme.
   */
  classe: string;
  /** Quantité commandée (≥ 1). */
  quantite: number;
  /**
   * Département de livraison sur 2 chiffres — ex. "35". Optionnel : sans lui,
   * le moteur renvoie le prix nu (sans frais de port).
   */
  departement?: string;
}

/**
 * Issue d'un calcul. Un seul statut « positif » (`ok`) ; tous les autres
 * expliquent pourquoi aucun prix n'est rendu (règle d'or : jamais de prix inventé).
 */
export type StatutPrix =
  /** Prix calculé normalement — achat possible. */
  | "ok"
  /** Dimension hors des bornes fabricables de la famille (cf. SPEC §10, « cadre »). */
  | "hors_fabrication"
  /** Efficacité non fabriquée pour ce produit/format — pas de prix sur une combinaison non faite. */
  | "classe_indisponible"
  /** Code gamme non reconnu dans les données. */
  | "gamme_inconnue"
  /** Gamme « hors calculateur » : pas de prix instantané, seul le parcours demande de devis est actif. */
  | "sur_devis"
  /** Quantité sous le minimum de commande de la famille — achat bloqué. */
  | "quantite_insuffisante";

/**
 * Une brique du coût (avant ratio tarif) : renfort, base, surcoût d'épaisseur,
 * cadre, média, pièce, etc. La liste des briques dépend de la méthode appliquée.
 */
export interface ComposantCout {
  /** Intitulé lisible — ex. "renfort extérieur", "prix de base (L×l)", "média (surface)". */
  libelle: string;
  /** Montant HT de la brique, en euros. */
  montant: number;
}

/**
 * Référence à la ligne de table qui a fourni un chiffre — sert au test de
 * conformité et aux skills pour prouver « Excel = moteur ».
 */
export interface SourceTable {
  /** Nom de la table dans `tables.json` — ex. "prix_l_et_l", "prix_surface". */
  table: string;
  /** Index de la ligne dans cette table (champ `index` du JSON). */
  index: number;
}

/**
 * Traçabilité complète du calcul (la « preuve de calcul »). Renseignée quand le
 * statut est `ok` ; c'est sur ce détail que s'appuient le validator (plausibilité)
 * et le qa (conformité au centime).
 */
export interface DetailCalcul {
  /** Méthode de calcul appliquée — A→F selon SPEC §3. */
  methode: "A" | "B" | "C" | "D" | "E" | "F";
  /** Briques de coût (leur somme = `coutHT`). */
  composantsCout: ComposantCout[];
  /** Coût de revient unitaire HT assemblé (= `PRU HT`, avant ratio). */
  coutHT: number;
  /** Ratio prix tarif appliqué (col. `ratio` de la table des gammes). */
  ratioTarif: number;
  /**
   * Coefficient de revalorisation générale appliqué (SPEC §11), si présent.
   * Absent tant que le levier n'est pas activé dans l'Excel.
   */
  revalorisation?: number;
  /** Surface filtrante utilisée (dm²), quand la méthode s'appuie dessus. */
  surface_dm2?: number;
  /** Périmètre utilisé (m), quand la méthode s'appuie dessus. */
  perimetre_m?: number;
  /** Ligne(s) de table ayant fourni les chiffres (traçabilité). */
  sources: SourceTable[];
}

/** Réponse du moteur. */
export interface ResultatPrix {
  /** Issue du calcul (voir StatutPrix). */
  statut: StatutPrix;
  /** Prix unitaire HT, arrondi à 2 décimales. Présent si statut = `ok`. */
  prixUnitaireHT?: number;
  /** Prix total HT = unitaire × quantité. Présent si statut = `ok`. */
  prixTotalHT?: number;
  /** Frais de port HT selon département + franco. Présent si département fourni. */
  fraisPortHT?: number;
  /** true si total ≥ seuil franco (750 €) → port offert. */
  francoApplique?: boolean;
  /** Poids total de la commande, en kg. */
  poidsTotalKg?: number;
  /** Palier de quantité (tranche de prix) appliqué — ex. "6-19". */
  paletteQuantite?: string;
  /** Plancher de commande de la famille, si statut = `quantite_insuffisante`. */
  quantiteMini?: number;
  /** Durée de validité de l'offre, en jours (30). */
  dureeValiditeJours: number;
  /** Traçabilité du calcul, si statut = `ok`. */
  detail?: DetailCalcul;
  /** Explication lisible si statut ≠ `ok`. */
  message?: string;
}
