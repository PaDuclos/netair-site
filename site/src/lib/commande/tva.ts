/**
 * TVA et arrondis monétaires (Bloc B3 — étape 0).
 *
 * La boutique livre la France métropolitaine et la Corse uniquement (déc. PA 01/07/2026,
 * `departements.ts`), et vend des filtres industriels à des professionnels : taux normal.
 *
 * ⚠️ À FAIRE CONFIRMER PAR LE SKILL `netair-juridique-fr` AVANT LA PREMIÈRE VENTE RÉELLE :
 *  - la Corse applique des taux particuliers à certaines catégories de biens — à vérifier
 *    qu'aucune ne concerne les filtres de ventilation (a priori non : taux normal) ;
 *  - la TVA porte bien sur le total HT **frais de port inclus** (le transport suit le régime
 *    de l'opération principale) — c'est ce qui est implémenté ici.
 * Tant que ce n'est pas confirmé, ce module reste la SEULE source du taux : une correction
 * se fait ici et nulle part ailleurs.
 */

/** Taux normal de TVA appliqué à la boutique. */
export const TAUX_TVA = 0.2;

/**
 * Arrondi monétaire à 2 décimales.
 *
 * `Number.EPSILON` corrige les surprises du calcul flottant : sans lui, `Math.round(1.005 * 100)`
 * peut rendre 100 au lieu de 101, parce que 1.005 n'est pas représentable exactement en binaire.
 * Un centime perdu ici deviendrait un écart entre le montant annoncé et le montant débité.
 */
export function arrondi2(montant: number): number {
  return Math.round((montant + Number.EPSILON) * 100) / 100;
}

/** Montant de TVA correspondant à un total HT. */
export function montantTVA(totalHT: number): number {
  return arrondi2(totalHT * TAUX_TVA);
}

/**
 * Total TTC à partir d'un total HT.
 *
 * Calculé comme HT + TVA arrondie (et non HT × 1,2 arrondi) : c'est la seule façon
 * de garantir que les trois montants affichés au client — HT, TVA, TTC — soient
 * cohérents entre eux au centime près.
 */
export function totalTTC(totalHT: number): number {
  return arrondi2(arrondi2(totalHT) + montantTVA(totalHT));
}
