/**
 * Point d'entrée public du moteur de prix (Bloc B1 — tâche T7).
 *
 * `calculerPrix(demande)` est le guichet unique appelé par le site (configurateur,
 * prix instantané) ET par le serveur (recalcul de sécurité avant paiement) — même
 * code des deux côtés. Il assemble le prix (engine.ts) et le port (shipping.ts).
 *
 * Le poids n'est PAS calculé (T6 abandonné : le port est par département, pas au kilo ;
 * `poidsTotalKg` reste donc indéfini).
 *
 * ⚠️ Franco PAR PRODUIT : le franco (≥ 750 €) est évalué sur le total HT de CETTE
 * demande. Le franco au niveau d'un panier multi-produits relève du Bloc B3.
 */

import type { DemandePrix, ResultatPrix } from "./types";
import { calculerPrixHT } from "./engine";
import { calculerPort } from "./shipping";

export type { DemandePrix, ResultatPrix } from "./types";

/**
 * Calcule le prix catalogue HT complet d'une demande (prix + port si département fourni).
 * Renvoie toujours `dureeValiditeJours`. N'invente jamais de prix (cf. statuts).
 */
export function calculerPrix(demande: DemandePrix): ResultatPrix {
  const resultat = calculerPrixHT(demande);

  // Port : seulement si un prix existe (ok) ET qu'un département est fourni.
  const departement = demande.departement?.trim();
  if (resultat.statut !== "ok" || resultat.prixTotalHT === undefined || !departement) {
    return resultat;
  }

  const port = calculerPort(departement, resultat.prixTotalHT);
  if (port.portSurDevis) {
    // Département non tarifé : le prix reste valable, le port part en devis.
    return { ...resultat, message: port.message };
  }
  return {
    ...resultat,
    fraisPortHT: port.fraisPortHT,
    francoApplique: port.francoApplique,
  };
}
