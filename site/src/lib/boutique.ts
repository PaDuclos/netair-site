/**
 * Réglages boutique (côté site) pas encore portés dans le calculateur Excel.
 *
 * ⚠️ RUSTINE : le minimum de facturation devra vivre dans les `Paramètres unitaires`
 * de l'Excel (comme le franco 750 €), puis être lu dans `tables.json` après ré-export.
 * En attendant, une **valeur unique ici** → une seule source pour le panier ET la
 * page produit (plus de nombre en double à maintenir).
 */

/** Minimum de facturation (€ HT, produits hors port) : sous ce plancher, la commande boutique est bloquée. */
export const MIN_COMMANDE_HT = 80;
