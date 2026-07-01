/**
 * Demande de devis persistante (Bloc B3 — canal « devis », maquette).
 *
 * Jumeau du panier (`cart.ts`) pour le second canal de vente : la demande de devis.
 * Mêmes principes — liste mémorisée dans le navigateur (`localStorage`), partagée entre
 * toutes les pages, abonnement `onChange`. Différence : **pas de prix** (les lignes
 * partent en devis chiffré par Netair), donc pas de total ni de re-calcul.
 *
 * ⚠️ Maquette : l'envoi réel (email / DEVIS AUTO) n'est pas branché — il se grefera ensuite.
 */

/** Une ligne de la demande de devis (sans prix). `ref` = clé d'unicité. */
export interface DevisItem {
  /** Référence générée du filtre configuré. Clé unique. */
  ref: string;
  /** Nom du produit. */
  produit: string;
  /** Quantité souhaitée (≥ 1). */
  qty: number;
  /** Libellé court de la configuration (efficacité · dimensions · cadre). */
  detail: string;
}

const CLE = "netair_devis_v1";
const EVENEMENT = "netair-devis-change";

/** Lecture défensive de la demande de devis (jamais d'exception si données corrompues). */
export function getDevis(): DevisItem[] {
  if (typeof localStorage === "undefined") return [];
  try {
    const brut = localStorage.getItem(CLE);
    const data = brut ? JSON.parse(brut) : [];
    return Array.isArray(data) ? data.filter(estValide) : [];
  } catch {
    return [];
  }
}

function estValide(x: unknown): x is DevisItem {
  const i = x as DevisItem;
  return !!i && typeof i.ref === "string" && typeof i.qty === "number";
}

function ecrire(items: DevisItem[]): void {
  if (typeof localStorage === "undefined") return;
  localStorage.setItem(CLE, JSON.stringify(items));
  window.dispatchEvent(new CustomEvent(EVENEMENT));
}

/** Ajoute une ligne. Même référence déjà présente → on cumule les quantités. */
export function addDevisItem(item: DevisItem): void {
  const items = getDevis();
  const existant = items.find((i) => i.ref === item.ref);
  if (existant) existant.qty += item.qty;
  else items.push({ ...item, qty: Math.max(1, item.qty) });
  ecrire(items);
}

/** Retire une ligne de la demande. */
export function removeDevisItem(ref: string): void {
  ecrire(getDevis().filter((i) => i.ref !== ref));
}

/** Fixe la quantité d'une ligne (≥ 1). Une quantité ≤ 0 retire la ligne. */
export function setDevisQty(ref: string, qty: number): void {
  if (qty <= 0) return removeDevisItem(ref);
  const items = getDevis();
  const it = items.find((i) => i.ref === ref);
  if (it) {
    it.qty = qty;
    ecrire(items);
  }
}

/** Vide la demande de devis (ex. après envoi). */
export function clearDevis(): void {
  ecrire([]);
}

/** Nombre total de lignes/quantités dans la demande. */
export function devisCount(): number {
  return getDevis().reduce((n, i) => n + i.qty, 0);
}

/** S'abonne aux changements (même onglet + autres onglets). Renvoie la fonction de désabonnement. */
export function onDevisChange(cb: () => void): () => void {
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
