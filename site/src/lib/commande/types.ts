/**
 * Contrat du recalcul serveur d'une commande boutique (Bloc B3 — étape 0).
 *
 * Ce fichier ne contient QUE des définitions de types — aucune logique, aucun chiffre.
 * Référence : SPEC_B3_PAIEMENT.md §2 (sécurité) et §3 (chaîne complète).
 *
 * ⚠️ RÈGLE FONDATRICE : le navigateur n'envoie que la CONFIGURATION d'un panier,
 * jamais les prix. Le serveur recalcule tout lui-même et son résultat fait foi.
 * Aucun champ de prix n'est donc accepté en entrée — sauf `totalAfficheHT`, qui sert
 * UNIQUEMENT à détecter un écart avec le client (et à refuser), jamais à calculer.
 */

/**
 * Une ligne de panier telle qu'elle arrive du navigateur.
 *
 * On reçoit le PRODUIT du site (`netply`, `netcel-v-azur`…) et non le code-gamme
 * tarifaire. C'est délibéré : le code-gamme seul contournerait les restrictions
 * d'offre (classes retirées de la vente, formats non proposés) qui vivent dans
 * `pricing/produits-gammes.ts`. Le serveur résout lui-même produit → code.
 */
export interface LignePanierRecue {
  /** Identifiant produit du site — clé de `GAMME_PRODUIT`. Ex. "netply". */
  produitId: string;
  /**
   * Conditionnement choisi, quand le produit en déclare (`variantes`).
   * Obligatoire dans ce cas : c'est lui qui détermine le code-gamme tarifaire
   * (ex. NETFIBRE panneau = code 4, rouleau = code 5 — deux prix très différents).
   */
  varianteId?: string;
  /** Largeur L, en millimètres (unité des tables pour les rouleaux : le mètre). */
  largeur_mm: number;
  /** Hauteur H, même unité que `largeur_mm`. */
  hauteur_mm: number;
  /** Profondeur / épaisseur P, en millimètres. */
  profondeur_mm: number;
  /** Classe d'efficacité EN 779 — ex. "G4", "F7", "H13". */
  classe: string;
  /** Quantité commandée : entier ≥ 1. */
  quantite: number;
}

/** Le panier complet reçu du navigateur. */
export interface PanierRecu {
  /** Lignes du panier (au moins une). */
  lignes: LignePanierRecue[];
  /** Département de livraison sur 2 caractères — ex. "35", "2A". Obligatoire pour encaisser. */
  departement: string;
  /**
   * Total produits HT **affiché au client**. Sert uniquement de contrôle : si le
   * serveur trouve autre chose, la commande est refusée (« nos tarifs ont changé »)
   * plutôt qu'alignée en silence sur l'une ou l'autre valeur.
   * Absent → le contrôle est simplement ignoré.
   */
  totalAfficheHT?: number;
}

/** Pourquoi une commande (ou une ligne) est refusée. Jamais de refus sans motif. */
export type MotifRefus =
  /** Charge utile inexploitable (pas un objet, `lignes` absent ou pas un tableau). */
  | "panier_invalide"
  /** Une entrée de `lignes` n'est pas un objet exploitable. */
  | "ligne_invalide"
  /** Dimensions non numériques, nulles, négatives ou infinies. */
  | "dimensions_invalides"
  /** Quantité au-delà du plafond de sécurité d'une commande en ligne. */
  | "quantite_excessive"
  /** Aucune ligne exploitable. */
  | "panier_vide"
  /** `produitId` absent du catalogue du site. */
  | "produit_inconnu"
  /** Produit vendu sur devis uniquement — pas d'achat en ligne. */
  | "produit_sur_devis"
  /** Conditionnement manquant ou inconnu pour ce produit. */
  | "variante_inconnue"
  /** Classe retirée de l'offre (`classesIncluses` / `classesExclues`). */
  | "classe_hors_offre"
  /** Classe annoncée par la fiche mais non tarifée (`classesSurDevis`) — devis seul. */
  | "classe_sur_devis"
  /** Épaisseur hors de celles proposées par le conditionnement. */
  | "epaisseur_hors_offre"
  /** Dimensions hors des formats proposés (produit vendu en formats fixes). */
  | "format_hors_offre"
  /** Quantité non entière, nulle ou négative. */
  | "quantite_invalide"
  /** Le moteur n'a rendu aucun prix (hors fabrication, classe indisponible…). */
  | "prix_indisponible"
  /** Aucun département fourni — impossible de totaliser. */
  | "departement_manquant"
  /** Département non tarifé : on ne débite pas un client sur un total inconnu. */
  | "livraison_sur_devis"
  /** Total produits sous le minimum de facturation. */
  | "sous_minimum"
  /** Le total du serveur diffère de celui affiché au client. */
  | "total_divergent";

/** Une ligne rejetée, avec de quoi l'expliquer au client sans jargon. */
export interface LigneRefusee {
  /** Position de la ligne dans le panier reçu (0-based). */
  index: number;
  /** Produit concerné, tel que reçu. */
  produitId: string;
  /** Motif machine. */
  motif: MotifRefus;
  /** Explication lisible. */
  message: string;
  /** Statut rendu par le moteur de prix, quand c'est lui qui a refusé. */
  statutMoteur?: string;
}

/** Une ligne acceptée, au prix recalculé par le serveur. */
export interface LigneValidee {
  index: number;
  produitId: string;
  varianteId?: string;
  /** Code-gamme résolu par le serveur (jamais reçu du navigateur). */
  codeGamme: string;
  classe: string;
  largeur_mm: number;
  hauteur_mm: number;
  profondeur_mm: number;
  quantite: number;
  /** Prix unitaire HT recalculé — fait foi. */
  prixUnitaireHT: number;
  /** Prix total HT de la ligne — fait foi. */
  prixTotalHT: number;
  /** Palier de quantité appliqué, si le moteur en a retenu un. */
  palierQuantite?: string;
}

/** Commande acceptée : tous les montants sont ceux du serveur. */
export interface CommandeAcceptee {
  statut: "ok";
  lignes: LigneValidee[];
  /** Somme des lignes, HT. */
  totalProduitsHT: number;
  /** Frais de port HT (0 si franco). */
  fraisPortHT: number;
  /** true si le total produits atteint le seuil de franco. */
  francoApplique: boolean;
  /** Total HT = produits + port. */
  totalHT: number;
  /** Montant de TVA. */
  montantTVA: number;
  /** Taux appliqué (0.20). */
  tauxTVA: number;
  /** Total TTC = ce qui sera présenté au paiement. */
  totalTTC: number;
}

/** Commande refusée : aucun montant, un motif, et le détail des lignes fautives. */
export interface CommandeRefusee {
  statut: "refuse";
  motif: MotifRefus;
  message: string;
  /** Vide quand le refus porte sur le panier entier (minimum, port, divergence). */
  lignesRefusees: LigneRefusee[];
}

/** Réponse du recalcul serveur. */
export type CommandeValidee = CommandeAcceptee | CommandeRefusee;
