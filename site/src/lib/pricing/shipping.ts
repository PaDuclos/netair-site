/**
 * Frais de port + franco de port (Bloc B1 — tâche T5).
 *
 * À partir d'un département de livraison et du total HT déjà calculé, détermine le
 * port. Lit UNIQUEMENT les données (`tables.expedition`, `tables.franco`) ; rien en dur.
 *
 * Règles (cf. SPEC_B1 §2) :
 * - total HT ≥ seuil de franco (750 €) → port offert ;
 * - sinon → tarif du département ;
 * - département absent de la table (ex. outre-mer) → port sur devis (le prix produit
 *   reste valable) ;
 * - pas de département fourni → pas de port (géré en amont, T7).
 *
 * Le calcul du total et l'assemblage dans le résultat final se font en T7 (index.ts).
 */

import { tables } from "./lookups";

/** Issue du calcul de port pour un département donné. */
export interface ResultatPort {
  /** Montant du port HT. Absent si port sur devis. */
  fraisPortHT?: number;
  /** true si le total atteint le seuil de franco → port offert. */
  francoApplique: boolean;
  /** true si le département n'est pas tarifé (livraison sur devis). */
  portSurDevis: boolean;
  /** Explication si port sur devis. */
  message?: string;
}

/** Normalise un code département : majuscules, espaces retirés, un chiffre → deux (« 1 » → « 01 »). */
function normaliserDepartement(departement: string): string {
  const t = departement.trim().toUpperCase();
  return /^\d$/.test(t) ? `0${t}` : t;
}

/** Tarif de port du département (€), ou `undefined` s'il n'est pas dans la table. */
export function tarifDepartement(departement: string): number | undefined {
  const tarif = tables.expedition[normaliserDepartement(departement)];
  return typeof tarif === "number" ? tarif : undefined;
}

/**
 * Seuil de franco applicable au département. Aujourd'hui : valeur unique `tables.franco`
 * (750 €) pour tous. ⭐ SEUL endroit à faire évoluer le jour où un franco par département
 * est ajouté à l'Excel (ex. Corse 2A/2B = 2000 €) — il sera alors lu dans les données
 * régénérées par le bouton de publication, jamais codé en dur ici.
 */
export function seuilFranco(_departement: string): number {
  return tables.franco;
}

/**
 * Frais de port pour (département, total HT).
 * Ordre : département inconnu → sur devis ; sinon franco si total ≥ seuil ; sinon tarif.
 */
export function calculerPort(departement: string, totalHT: number): ResultatPort {
  const tarif = tarifDepartement(departement);
  if (tarif === undefined) {
    return {
      francoApplique: false,
      portSurDevis: true,
      message: `Frais de port sur devis pour le département « ${departement.trim()} ».`,
    };
  }
  if (totalHT >= seuilFranco(departement)) {
    return { fraisPortHT: 0, francoApplique: true, portSurDevis: false };
  }
  return { fraisPortHT: tarif, francoApplique: false, portSurDevis: false };
}
