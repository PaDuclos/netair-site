/**
 * Panier d'achat persistant (Bloc B3 — maquette, sans paiement réel).
 *
 * Un seul panier pour tout le site : les articles sont mémorisés dans le navigateur
 * (`localStorage`), donc ils survivent au changement de page ET à la fermeture de
 * l'onglet. Tout composant (page produit, en-tête, page /panier) lit/écrit ce module
 * et s'abonne à `onChange` pour se rafraîchir.
 *
 * ⚠️ Maquette : le paiement (Stripe) n'est pas branché — il se grefera après
 * immatriculation. Ici on gère uniquement le contenu du panier et le tunnel d'affichage.
 */

/** Un article du panier. La `ref` (référence générée) sert de clé d'unicité. */
export interface CartItem {
  /** Référence générée du filtre configuré — ex. "NETPLY-G4-592x592x48-A". Clé unique. */
  ref: string;
  /** Nom du produit — ex. "NETPLY". */
  produit: string;
  /** Quantité commandée (≥ 1). */
  qty: number;
  /** Prix unitaire HT (au moment de l'ajout). */
  unit: number;
  /** Libellé court de la configuration — ex. "Coarse 65 % (G4) · 592×592 · 48 mm · Acier galvanisé". */
  detail: string;
  /**
   * Configuration envoyée au moteur (sans la quantité), pour re-calculer le prix
   * unitaire quand la quantité change au panier (paliers). Optionnel (articles ajoutés
   * avant cette fonctionnalité : on garde alors le prix d'ajout).
   */
  demande?: {
    codeGamme: string;
    largeur_mm: number;
    hauteur_mm: number;
    profondeur_mm: number;
    classe: string;
  };
}

const CLE = "netair_panier_v1";
const EVENEMENT = "netair-panier-change";

/** Lecture défensive du panier depuis le stockage (jamais d'exception en cas de données corrompues). */
export function getCart(): CartItem[] {
  if (typeof localStorage === "undefined") return [];
  try {
    const brut = localStorage.getItem(CLE);
    const data = brut ? JSON.parse(brut) : [];
    return Array.isArray(data) ? data.filter(estItemValide) : [];
  } catch {
    return [];
  }
}

function estItemValide(x: unknown): x is CartItem {
  const i = x as CartItem;
  return !!i && typeof i.ref === "string" && typeof i.qty === "number" && typeof i.unit === "number";
}

function ecrire(items: CartItem[]): void {
  if (typeof localStorage === "undefined") return;
  localStorage.setItem(CLE, JSON.stringify(items));
  // Prévenir les abonnés de la même page (l'événement `storage` natif ne se déclenche
  // que dans les AUTRES onglets ; on émet donc notre propre événement pour l'onglet courant).
  window.dispatchEvent(new CustomEvent(EVENEMENT));
}

/**
 * Ajoute un article. Si la même référence est déjà au panier, on cumule les quantités
 * (même filtre, même config = une seule ligne).
 */
export function addItem(item: CartItem): void {
  const items = getCart();
  const existant = items.find((i) => i.ref === item.ref);
  if (existant) {
    existant.qty += item.qty;
    existant.unit = item.unit; // garde le prix courant
  } else {
    items.push({ ...item, qty: Math.max(1, item.qty) });
  }
  ecrire(items);
}

/** Retire complètement une ligne du panier. */
export function removeItem(ref: string): void {
  ecrire(getCart().filter((i) => i.ref !== ref));
}

/**
 * Fixe la quantité d'une ligne (≥ 1). Une quantité ≤ 0 retire la ligne.
 * `unit` (optionnel) met à jour le prix unitaire en même temps — utilisé quand le
 * changement de quantité fait basculer de palier de prix (re-calculé par l'appelant).
 */
export function setQty(ref: string, qty: number, unit?: number): void {
  if (qty <= 0) return removeItem(ref);
  const items = getCart();
  const it = items.find((i) => i.ref === ref);
  if (it) {
    it.qty = qty;
    if (typeof unit === "number") it.unit = unit;
    ecrire(items);
  }
}

/** Vide le panier (ex. après confirmation de commande). */
export function clearCart(): void {
  ecrire([]);
}

/** Nombre total d'articles (somme des quantités). */
export function cartCount(): number {
  return getCart().reduce((n, i) => n + i.qty, 0);
}

/** Total HT du panier (somme prix unitaire × quantité). */
export function cartTotalHT(): number {
  return getCart().reduce((s, i) => s + i.unit * i.qty, 0);
}

/**
 * S'abonne aux changements du panier (même onglet ET autres onglets). Renvoie une
 * fonction de désabonnement.
 */
export function onCartChange(cb: () => void): () => void {
  const local = () => cb();
  const autreOnglet = (e: StorageEvent) => {
    if (e.key === CLE) cb();
  };
  window.addEventListener(EVENEMENT, local);
  window.addEventListener("storage", autreOnglet);
  return () => {
    window.removeEventListener(EVENEMENT, local);
    window.removeEventListener("storage", autreOnglet);
  };
}
